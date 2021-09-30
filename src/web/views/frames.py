# encoding=utf8

import random
import re
import time
from time import sleep

from easelenium.utils import get_random_value
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from src.apeha.bot.fight.fight_utils import (
    PlayerNeighbours,
    Players,
    Team,
    create_application,
    get_astral_level_from,
    get_nicknames,
    get_time_left_in_seconds,
)
from src.apeha.bot.info import PlayerInfo
from src.apeha.bot.settings import INJURIES_AND_ROLLS, ClonePlacement, SpellTexts
from src.apeha.utils import (
    ApehaRegExp,
    get_float_from_text,
    get_number_from_text,
    print_exception,
)
from src.web.utils.webutils import get_browser


class RootBrowser(object):
    def __init__(self, settings):
        if settings:
            headless = settings.fighting_settings.BROWSER_HEADLESS
        else:
            headless = False

        self.browser = get_browser(headless=headless)
        self.settings = settings


class ApehaMain(RootBrowser):
    SITE = "http://www.apeha.ru"
    LOGIN = (By.NAME, "login")
    PASSWORD = (By.NAME, "pwd")
    BTN_LOGIN = (By.CSS_SELECTOR, "div[onclick*=loginform]")
    A_AFTER_LOGIN = (By.CSS_SELECTOR, "#after_login div[onclick*=newWin]")

    def __init__(self, settings):
        RootBrowser.__init__(self, settings)
        self.browser.get(self.SITE)

    def login(self, username, password):
        self.browser.type(self.LOGIN, username)
        self.browser.type(self.PASSWORD, password)
        self.browser.click(self.BTN_LOGIN)

        attr = self.browser.get_attribute(self.A_AFTER_LOGIN, "onclick")
        quote = '"'
        start = attr.index(quote) + 1
        url = attr[start : attr.index(quote, start)]
        # print(url)
        self.browser.get(url)


class Frame(RootBrowser):
    def __init__(self, frame, settings):
        RootBrowser.__init__(self, settings)
        self.__frame = frame

    def _switch_to_frame(self):
        try:
            self.browser.switch_to_default_content()
            self.browser.switch_to_frame(self.__frame)
        except:
            pass


class FramePersInfo(Frame):
    INFO = (By.ID, "IMG_info")

    MANA = (By.ID, "VAL_mana")
    HP = (By.ID, "VAL_hp")
    NICK = (By.ID, "VAL_nick")
    ASTRAL = (By.ID, "VAL_astral")
    RATING = (By.ID, "VAL_rnk")
    LEVEL = (By.ID, "VAL_lvl")

    BTN_PERS = (By.ID, "BUTT_pers")
    BTN_STAT = (By.ID, "BUTT_stat")
    INJURY = (By.CSS_SELECTOR, "#dinjcell b.krit")

    MAG_BOOK = (By.CSS_SELECTOR, "[target='MagBook']")
    ABILITY = (By.CSS_SELECTOR, "[target='Ability']")
    __CLAN_LINK = (By.CSS_SELECTOR, "nobr a:not(.info)")
    __ASTRAL_LINE = (By.XPATH, u'//b[../../td/img[@src="img/astral.gif"]]')
    TACTICS_TYPE = (By.CSS_SELECTOR, "select[name='tactic']")
    TACTICS_APPLY = (By.CSS_SELECTOR, "input[value='Установить']")

    BTN_NEXT = (By.CSS_SELECTOR, "button[title='Следующая']")

    def __init__(self, settings):
        frame = (By.NAME, "d_pers")
        Frame.__init__(self, frame, settings)
        self.f_astral = FrameAstral(settings)

    def __get_current_and_max_values(self, element):
        self._switch_to_frame()
        self.browser.click(self.BTN_PERS)
        # print("* Clicking at 'Персонаж'")
        ints = re.findall(r"\d+", self.browser.get_text(element))
        assert len(ints) == 2
        return int(ints[0]), int(ints[1])

    def get_rating(self):
        self._switch_to_frame()
        self.browser.wait_for_visible(self.RATING, timeout=20)
        return float(self.browser.get_text(self.RATING))

    def get_astral_cur_and_max(self):
        return self.__get_current_and_max_values(self.ASTRAL)

    def get_mana_cur_and_max(self):
        return self.__get_current_and_max_values(self.MANA)

    def get_hp_cur_and_max(self):
        return self.__get_current_and_max_values(self.HP)

    def cure_with_ability(self):
        self._switch_to_frame()
        self.browser.switch_to_new_window(self.browser.click, self.ABILITY)
        try:
            self.f_astral.cure_injury()
        finally:
            self.browser.close_current_window_and_focus_to_previous_one()

    def is_injured(self):
        self._switch_to_frame()
        text = self.get_injury()
        return text is not None

    def get_injury(self):
        self._switch_to_frame()
        text = None

        self.browser.click(self.BTN_STAT)
        print("* Clicking at 'Статистика'")
        if self.browser.is_present(self.INJURY) and self.browser.is_visible(
            self.INJURY
        ):
            text = self.browser.get_text(self.INJURY)

        return text

    def get_cash(self):
        self._switch_to_frame()
        main_cash_css = (By.CSS_SELECTOR, "#dtxtcell > table > tbody > tr:nth-child(1)")
        blue_cash_css = (By.CSS_SELECTOR, "#dtxtcell > table > tbody > tr:nth-child(2)")

        self.browser.click(self.BTN_STAT)
        print("* Clicking at 'Статистика'")
        try:
            main_cash = 0
            blue_cash = 0
            self.browser.wait_for_visible(main_cash_css, timeout=10)
            if self.browser.is_visible(main_cash_css):
                main_cash = get_float_from_text(self.browser.get_text(main_cash_css))
            if self.browser.is_visible(blue_cash_css):
                blue_cash = get_float_from_text(self.browser.get_text(blue_cash_css))

            return main_cash, blue_cash
        except WebDriverException:
            pass

        return None

    def is_ready_to_fight(self):
        self._switch_to_frame()
        try:
            m_cur, m_max = self.get_mana_cur_and_max()
            hp_cur, hp_max = self.get_hp_cur_and_max()

            return m_max - m_cur == 0 == hp_cur - hp_max and not self.is_injured()
        except Exception as e:
            print(str(e))
            return False

    def get_player_info(self):
        self._switch_to_frame()
        self.browser.click(self.BTN_PERS)
        mana = self.browser.get_text(self.MANA)
        hp = self.browser.get_text(self.HP)
        name = self.browser.get_text(self.NICK)
        astral = self.browser.get_text(self.ASTRAL)
        rating = self.browser.get_text(self.RATING)
        level = int(self.browser.get_text(self.LEVEL))

        self.browser.switch_to_new_window(self.browser.click, self.INFO)
        clan = self.browser.get_text(self.browser.find_elements(self.__CLAN_LINK)[-1])
        astral_level = int(
            re.search(r"\d+", self.browser.get_text(self.__ASTRAL_LINE)).group()
        )
        self.browser.close_current_window_and_focus_to_previous_one()

        return PlayerInfo(name, level, clan, hp, mana, astral, rating, astral_level)

    def select_tactics(self, tactics):
        self._switch_to_frame()
        self.browser.switch_to_new_window(self.browser.click, self.INFO)
        try:
            self.browser.select_option_by_text_from_dropdown(self.TACTICS_TYPE, tactics)
            self.browser.click(self.TACTICS_APPLY)
        finally:
            self.browser.close_current_window_and_focus_to_previous_one()

    def select_next_astral_level(self):
        return self.__select_astral_level(1)

    def select_previous_astral_level(self):
        return self.__select_astral_level(-1)

    def __select_astral_level(self, i):
        self._switch_to_frame()
        level = None
        self.browser.switch_to_new_window(self.browser.click, self.ABILITY)

        try:
            cur_lvl = self.f_astral.get_astral_level()
            if cur_lvl == 0 and i < 0:
                level = 0
            else:
                lvl = cur_lvl + i
                self.f_astral.click_astral_level(lvl)
                level = self.f_astral.get_astral_level()
        finally:
            self.browser.close_current_window_and_focus_to_previous_one()
            return level

    def __magbook_click_spell(self, *spell_texts):
        def click_spell():
            trs = self.browser.find_elements((By.TAG_NAME, "tr"))
            for tr in trs:
                for text in spell_texts:
                    if text in self.browser.get_text(tr):
                        element = tr.find_element_by_css_selector("b input")
                        self.browser.click(element)
                        return True

            return False

        clicked = click_spell()
        if (
            not clicked
            and self.browser.is_present(self.BTN_NEXT)
            and self.browser.is_visible(self.BTN_NEXT)
        ):
            self.browser.click(self.BTN_NEXT)
            clicked = click_spell()

    def __cast_spell(self, create_clone=True):
        def click(e):
            while True:
                try:
                    self.browser.click(e)
                    return
                except StaleElementReferenceException:
                    pass

        self._switch_to_frame()
        self.browser.wait_for_visible(self.MAG_BOOK)
        self.browser.switch_to_new_window(click, self.MAG_BOOK)
        if create_clone:
            self.__magbook_click_spell(
                SpellTexts.MAGBOOK_CREATE_CLONE1,
                SpellTexts.MAGBOOK_CREATE_CLONE2,
                SpellTexts.MAGBOOK_CREATE_CLONE3,
            )
        else:
            self.__magbook_click_spell(SpellTexts.MAGBOOK_FILL_HP_TEXT)

    def cast_create_clone(self):
        self.__cast_spell()

    def cast_fill_hp(self):
        self.__cast_spell(False)


class FrameCreateClone(RootBrowser):
    CREATE_CLONE = (By.CSS_SELECTOR, "input[onclick*='MakeCast']")
    MAP = (By.ID, "mapspan")
    IMG_PLAYER = (By.CSS_SELECTOR, "#mapspan img")
    MAP_MARKER = (By.ID, "mrkr")

    XPATH_IMG_BY_NICK = "//img[contains(@title, '%s [')]"
    CSS_IMG_BY_NICK = "img[title*='%s [']"
    CSS_IMG_BY_STYLE = "#mapspan img[style*='%s'][style*='%s']"

    NICK = (By.ID, "VAL_nick")
    NICKNAMES = (By.ID, "aliveshow")
    CLONE_TEXT = "клон"

    REGEXP_IMG_TOP_LEFT_ALIGN = re.compile(r"top:.(\d+)px.*left:.(\d+)px")

    def __init__(self, frame, settings):
        RootBrowser.__init__(self, settings)
        self.frame = frame

    def _get_players_with_clones(self):
        self.frame._switch_to_frame()
        self.frame._click_refresh()
        text = self.browser.get_text(self.NICKNAMES)
        nicknames = get_nicknames(text)
        w_and_s = {}

        for nickname in nicknames:
            selector = self.__get_css_selector_for_player_by_name(nickname)
            els = self.browser.find_elements(selector)
            if len(els) > 0:
                webelement = els[0]
                w_and_s[webelement] = selector

        selectors = []
        try:
            sorted_keys = sorted(w_and_s.keys(), key=lambda x: x.location["y"])
            for key in sorted_keys:
                selectors.append(w_and_s[key])
        except Exception:
            print("Can't sort")

        if len(selectors) == 0:
            selectors = w_and_s.values()

        return selectors

    def _get_team_by_nickname(self, nickname, players=None):
        self.frame._switch_to_frame()
        if not players:
            players = self._get_players_with_clones()

        player = self._get_player(nickname, players)
        if player:
            team = self.__get_team_color(player)
            return team
        else:
            return None

    def _get_players_using_nickname(self, nickname):
        self.frame._switch_to_frame()
        players = self._get_players_with_clones()
        player = self._get_player(nickname, players)
        team = self.__get_team_color(player)
        return self.__get_players(team, players)

    def _get_players_using_team(self, team):
        self.frame._switch_to_frame()
        return self.__get_players(team)

    def _get_sorted_players(self, name, players, clone_placement):
        enemy_originals = players.enemy_originals
        alias_originals = players.alias_originals
        if clone_placement == ClonePlacement.TO_EMENIES_TOP:
            return enemy_originals + players.enemy_team
        elif clone_placement == ClonePlacement.TO_EMENIES_BOTTOM:
            return enemy_originals[-1::-1] + players.enemy_team
        elif clone_placement == ClonePlacement.TO_EMENIES_RANDOM:
            random.shuffle(enemy_originals)
            return enemy_originals + players.enemy_team
        elif clone_placement == ClonePlacement.TO_ALIASES_ME_FIRST:
            me_as_element = self.__get_css_selector_for_player_by_name(name)
            return [me_as_element] + alias_originals
        elif clone_placement == ClonePlacement.TO_ALIASES_RANDOM:
            random.shuffle(alias_originals)
            return alias_originals
        else:
            return alias_originals

    def __get_players(self, team, players=None):
        if not players:
            players = self._get_players_with_clones()
        #         print(players)

        all_players = []
        enemy_team = []
        my_team = []
        enemy_originals = []
        alias_originals = []

        #         print("here1")
        for player in players:
            if self.browser.is_visible(player):
                all_players.append(player)
                is_alias = self.__is_alias(player, team)
                is_clone = self.__is_clone(player)
                if is_clone:
                    if is_alias:
                        my_team.append(player)
                    else:
                        enemy_team.append(player)
                else:
                    if is_alias:
                        my_team.append(player)
                        alias_originals.append(player)
                    else:
                        enemy_team.append(player)
                        enemy_originals.append(player)
                    #         print("here2")

                    #         print("all_players", all_players)
                    #         print("enemy_team", enemy_team)
                    #         print("my_team", my_team)
                    #         print("enemy_originals", enemy_originals)
                    #         print("alias_originals", alias_originals)
        return Players(
            team, all_players, enemy_team, my_team, enemy_originals, alias_originals
        )

    def __get_css_selector_for_player_by_name(self, nickname):
        selector = self.CSS_IMG_BY_NICK % nickname
        return By.CSS_SELECTOR, selector

    def __get_css_selector_for_player(self, player):
        name = self._get_player_name(player)
        if name:
            return self.__get_css_selector_for_player_by_name(name)
        else:
            return None

    def __is_enemy(self, player, my_team):
        player_team = self.__get_team_color(player)
        return player_team != my_team

    def __is_alias(self, player, my_team):
        player_team = self.__get_team_color(player)
        return player_team == my_team

    def __is_clone(self, player):
        return self.CLONE_TEXT in self.browser.get_attribute(player, "title")

    def _get_player(self, nickname, players):
        self.frame._switch_to_frame()
        for p in players:
            if self._get_player_name(p) == nickname:
                return p

        return None

    def __get_team_color(self, element):
        self.frame._switch_to_frame()

        text = self.browser.get_attribute(element, "src")
        if "pbm1" in text or "pb1" in text:
            return Team.RED
        elif "pbm0" in text or "pb0" in text:
            return Team.BLUE
        else:
            return None

    def _select_open_spot(self, player, my_team, radius):
        self.frame._switch_to_frame()

        if Team.RED == my_team:
            nset = PlayerNeighbours.get_set(PlayerNeighbours.CLOCKWISE, radius)
        else:
            nset = PlayerNeighbours.get_set(PlayerNeighbours.ANTI_CLOCKWISE, radius)

        self.browser.mouse.left_click_by_offset(player, 0, 0)
        for nx, ny in nset:
            self.browser.mouse.left_click_by_offset(player, nx, ny)
            # cur_selected_nick = self.__get_selected_nick()  # NOTE: for debug only
            if self.__is_selected_spot_open():
                return True

        return False

    def __get_selected_nick(self):
        top, left = [
            int(m)
            for m in self.REGEXP_IMG_TOP_LEFT_ALIGN.findall(
                self.browser.get_attribute(self.MAP_MARKER, "style")
            )[0]
        ]
        if self.__is_selected_spot_open():
            return None
        else:
            return self.browser.get_attribute(
                (By.CSS_SELECTOR, self.CSS_IMG_BY_STYLE % (top + 1, left)), "title"
            )

    def __is_selected_spot_open(self):
        if not self.browser.is_visible(self.MAP_MARKER):
            return False

        top, left = [
            int(m)
            for m in self.REGEXP_IMG_TOP_LEFT_ALIGN.findall(
                self.browser.get_attribute(self.MAP_MARKER, "style")
            )[0]
        ]
        return not self.browser.is_present(
            (By.CSS_SELECTOR, self.CSS_IMG_BY_STYLE % (top + 1, left)),
        )

    def _get_player_name(self, element):
        self.frame._switch_to_frame()
        try:
            title = self.browser.get_attribute(element, "title")
        except StaleElementReferenceException:
            return None

        title = re.sub(ApehaRegExp.NICKNAME_HP_ENDING, "", title)
        title = re.sub(ApehaRegExp.NICKNAME_RACE_START, "", title)
        return title

    def _create_clone_around(self, player, my_team, radius=PlayerNeighbours.RADIUS):
        self.frame._switch_to_frame()
        if self._select_open_spot(player, my_team, radius):
            sleep(0.2)
            self.browser.click(self.CREATE_CLONE)
            try:
                self.browser._driver.switch_to_alert()
                self.browser.alert_accept()
                return False
            except WebDriverException:
                return False
            return True
        else:
            return False

    def create_clone(self, name, players, clone_placement):
        self.frame._switch_to_frame()
        team_color = players.team_color
        players_selectors = self._get_sorted_players(name, players, clone_placement)

        for radius in (PlayerNeighbours.RADIUS, PlayerNeighbours.RADIUS_DOUBLE):
            for player in players_selectors:
                if self.browser.is_visible(player) and self._create_clone_around(
                    player, team_color, radius
                ):
                    return True

        return False


class FrameAstral(RootBrowser):
    ASTRAL_GO_TO_NEXT = (By.CSS_SELECTOR, "input[value='Перейти на %d слой']")
    ASTRAL_EXIT = (By.CSS_SELECTOR, "input[value='Выйти из астрала']")
    CURE_INJURY = "Вылечить травму"
    APPLY = "input[value='Применить']"

    def __init__(self, settings):
        RootBrowser.__init__(self, settings)

    def cure_injury(self):
        trs = self.browser.find_elements((By.CSS_SELECTOR, "table.item tr"))

        for tr in trs:
            if self.browser.is_visible(
                tr
            ) and self.CURE_INJURY in self.browser.get_text(tr):
                index = trs.index(tr)

                e = self.browser.find_descendants(
                    trs[index + 1], (By.CSS_SELECTOR, self.APPLY)
                )
                if len(e) > 0:
                    self.browser.click(e[0])
                break

    def get_astral_level(self):
        tables = self.browser.find_elements((By.TAG_NAME, "table"))

        for t in tables:
            if self.browser.is_visible(t):
                text = self.browser.get_text(t)
                if SpellTexts.CURRENT_ASTRAL_LVL_TEXT in text:
                    return get_astral_level_from(text)

        return None

    def click_astral_level(self, level):
        if level == 0:
            self.browser.click(self.ASTRAL_EXIT)
        else:
            selector = self.ASTRAL_GO_TO_NEXT[0], self.ASTRAL_GO_TO_NEXT[1] % level
            self.browser.click(selector)


class FrameAction(Frame):
    URL_SMITHY = "smith.html"
    URL_SQUARE = "place.html"
    SQUARE = (By.CSS_SELECTOR, "input[value='На площадь']")
    STREET = (By.CSS_SELECTOR, "input[value='На улицу']")
    OTHER_CASTLES = (By.CSS_SELECTOR, "input[value='К другим замкам']")

    HOME = (By.CSS_SELECTOR, "input[value='В Дом бойцов']")
    ROLLS = (By.CSS_SELECTOR, "input[value='Свитки']")
    MARKET = (By.CSS_SELECTOR, "input[value='На Рынок']")
    SMITHY = (By.CSS_SELECTOR, "input[value='В Кузницу']")
    ARENA = (By.CSS_SELECTOR, "input[value='На Арену']")
    TR = (By.CSS_SELECTOR, "table.item tr")
    REFRESH = (By.CSS_SELECTOR, "button[title='Обновить']")

    NEWBIE_ROOM = (By.CSS_SELECTOR, "input[onclick=\"goRC('arena_room_1.html')\"]")
    CHAOS_FIGHT = (By.CSS_SELECTOR, "input[value='Хаотические']")

    CASTLE_BY_CLAN = (By.CSS_SELECTOR, "input[value='К замку \"%s\"']")
    CASTLE_ALLEY = (By.CSS_SELECTOR, "input[value='К замкам кланов']")
    TWO_CASTLES = (By.CSS_SELECTOR, "table.contr table")
    CASTLE_ROOMS = (By.CSS_SELECTOR, "table.ax td")
    STAND_UP = (By.CSS_SELECTOR, "input[value='Встать']")
    SIT_DOWN = (By.CSS_SELECTOR, "input[value='Присесть']")

    APPLICATIONS = (By.XPATH, "//table[contains(@id, 'breq')]")
    APP_MIN_LEVEL = (By.CSS_SELECTOR, "select[name='Battle{minlvl}']")
    APP_NUM_PLAYERS = (By.CSS_SELECTOR, "select[name='Battle{maxp}']")
    APP_TIMEOUT = (By.CSS_SELECTOR, "select[name='Battle{tm}']")
    APP_APPLY = (By.CSS_SELECTOR, "input[value='Подать заявку']")

    HOME_HELMETS = (By.CSS_SELECTOR, "input[value='Шлемы']")
    HOME_AMULETS = (By.CSS_SELECTOR, "input[value='Амулеты']")
    HOME_ARMORS = (By.CSS_SELECTOR, "input[value='Латы']")
    HOME_GLOVES = (By.CSS_SELECTOR, "input[value='Перчатки']")
    HOME_BELTS = (By.CSS_SELECTOR, "input[value='Пояса']")
    HOME_SHIELDS = (By.CSS_SELECTOR, "input[value='Щиты']")
    HOME_ARMS = (By.CSS_SELECTOR, "input[value='Оружие']")
    HOME_BOOTS = (By.CSS_SELECTOR, "input[value='Поножи']")
    HOME_RINGS = (By.CSS_SELECTOR, "input[value='Кольца']")
    HOME_BRACES = (By.CSS_SELECTOR, "input[value='Наручи']")

    def __init__(self, settings):
        frame = (By.NAME, "d_act")
        Frame.__init__(self, frame, settings)

    def _click_home(self):
        self._switch_to_frame()
        if self.browser.is_present(self.HOME) and self.browser.is_visible(self.HOME):
            self.browser.click(self.HOME)

    def _click_refresh(self):
        self._switch_to_frame()
        time1 = time.time()
        while time.time() - time1 < 2 * 60:
            try:
                self.browser.click(self.REFRESH)
                print("* Clicking at 'Обновить'")
                return True
            except WebDriverException:
                time.sleep(1)

    def _get_item_ids(self):
        sleep(0.5)
        elements = self.browser.find_elements(
            (By.CSS_SELECTOR, "[onclick *= 'actUnWear']")
        )
        return [
            get_number_from_text(self.browser.get_attribute(e, "onclick"))
            for e in elements
        ]

    def _take_off_all_items(self):
        taken_off_ids = []
        ids = self._get_item_ids()
        for _id in ids:
            self.browser.mouse.left_click_by_offset(
                (By.CSS_SELECTOR, "[onclick *= 'actUnWear(%s)']" % _id), -5, -5
            )
            # self.browser.click(e)
            print("Снимаю вещь id='%s'" % _id)
            taken_off_ids.append(_id)

        return taken_off_ids

    def __get_ids_in_current_cat(self):
        item = (By.CSS_SELECTOR, "table.item tr.item input[name*='actUser-Wear']")
        elements = self.browser.find_elements(item)
        ids = [int(element.get_attribute("value")) for element in elements]
        return ids

    def __put_on(self, _id):
        item_css = (By.CSS_SELECTOR, "table.item tr.item")
        items_count = len(self.browser.find_elements(item_css))

        for i in range(items_count):
            item = self.browser.find_elements(item_css)[i]
            is_element_with_id = (
                len(item.find_elements_by_css_selector("input[value='%d']" % _id)) > 0
            )
            if is_element_with_id:
                self.browser.click(
                    item.find_element_by_css_selector("input[value*='Надеть']")
                )
                return True

        return False

    def take_off_item_and_get_ids(self):
        self._click_main_square()
        self._click_home()
        return self._take_off_all_items()

    def put_on_items_by_ids(self, ids):
        self._click_main_square()
        self._click_home()
        self._put_on_by_ids(ids)

    def _put_on_by_ids(self, ids):
        categories = [
            self.HOME_AMULETS,
            self.HOME_HELMETS,
            self.HOME_AMULETS,
            self.HOME_ARMORS,
            self.HOME_GLOVES,
            self.HOME_BELTS,
            self.HOME_SHIELDS,
            self.HOME_ARMS,
            self.HOME_BOOTS,
            self.HOME_RINGS,
            self.HOME_BRACES,
            self.HOME_RINGS,
        ]
        put_items = 0

        while True:
            try:
                for cat in categories:
                    self.browser.click(cat)
                    sleep(0.5)
                    ids_in_cat = self.__get_ids_in_current_cat()
                    for id_in_cat in ids_in_cat:
                        if id_in_cat in ids and self.__put_on(id_in_cat):
                            put_items += 1
                break
            except:
                print_exception()
                self.browser.refresh_page()
                self.browser.switch_to_default_content()
                self._switch_to_frame()

        return put_items == len(ids)

    def _is_to_main_street(self):
        return self.browser.is_present(self.STREET) and self.browser.is_visible(
            self.STREET
        )

    def _click_main_square(self):
        self._switch_to_frame()

        def click_if_visible(element):
            if self.browser.is_present(element) and self.browser.is_visible(element):
                self.browser.click(element)

        click_if_visible(self.OTHER_CASTLES)
        click_if_visible(self.STREET)
        click_if_visible(self.SQUARE)

    def _click_smithy(self):
        self._switch_to_frame()
        self.browser.click(self.SMITHY)

    def _click_market(self):
        self._switch_to_frame()
        self.browser.click(self.MARKET)

    def _click_castle_alley(self):
        self._switch_to_frame()
        self.browser.click(self.CASTLE_ALLEY)

    def _click_chaos_fight(self):
        self._switch_to_frame()
        self.browser.click(self.CHAOS_FIGHT)

    def _go_to_castle_from_alley(self, clan):
        self._switch_to_frame()
        element = self.CASTLE_BY_CLAN[0], self.CASTLE_BY_CLAN[1] % clan
        self.browser.click(element)
        self.browser.wait_for_not_visible(element)

        elements = self.browser.find_elements(self.TWO_CASTLES)
        for e in elements:
            trs = e.find_elements(By.TAG_NAME, "tr")
            for tr in trs:
                if clan in self.browser.get_text(tr):
                    enter_btn = self.browser.find_descendant(
                        e, (By.CSS_SELECTOR, "input[value='Войти']")
                    )
                    self.browser.click(enter_btn)

                    sleep(0.5)
                    rooms = self.browser.find_elements(self.CASTLE_ROOMS)
                    for room in rooms:
                        room_name = "Тронный зал"
                        if self.browser.is_visible(room) and (
                            self.browser.is_visible(
                                (By.CSS_SELECTOR, "img[alt='{}']".format(room_name))
                            )
                            or room_name == self.browser.get_text(room)
                        ):
                            self.browser.click(room.find_element(By.TAG_NAME, "input"))
                            break

                    return

    def _sit_down_in_chair(self):
        self._click_refresh()
        if self.browser.is_visible(self.SIT_DOWN):
            self.browser.click(self.SIT_DOWN)

    def _stand_up_from_chair(self):
        self._click_refresh()
        sleep(0.5)
        if self.browser.is_visible(self.STAND_UP):
            self.browser.click(self.STAND_UP)

    def _go_to_newbie_room_from_main_square(self):
        self._switch_to_frame()
        self.browser.click(self.ARENA)
        self.browser.click(self.NEWBIE_ROOM)

    def _is_castle_visible(self, clan):
        self._switch_to_frame()
        element = self.CASTLE_BY_CLAN[0], self.CASTLE_BY_CLAN[1] % clan
        return self.browser.is_present(element) and self.browser.is_visible(element)

    def _enter_application(self, app):
        self._switch_to_frame()
        inputs = app.webelement.find_elements_by_tag_name("input")
        inputs = [e for e in inputs if self.browser.is_visible(e)]
        self.browser.click(inputs[0])

    def _get_applications(self):
        self._switch_to_frame()
        apps = []
        we_apps = self.browser.find_elements(self.APPLICATIONS)

        for we_app in we_apps:
            tds = we_app.find_elements(By.TAG_NAME, "td")
            if self.browser.is_visible(tds[0]) and self.browser.is_visible(tds[1]):
                left = self.browser.get_text(tds[0])
                right = self.browser.get_text(tds[1])
                app = create_application(left, right)
                app.webelement = we_app
                apps.append(app)

        return apps

    def _create_application(self, level):
        self._switch_to_frame()
        self.browser.select_option_by_text_from_dropdown(self.APP_MIN_LEVEL, str(level))
        self.browser.select_option_by_text_from_dropdown(
            self.APP_NUM_PLAYERS,
            str(self.settings.fighting_settings.APP_NUMBER_OF_PLAYERS),
        )
        self.browser.select_option_by_value_from_dropdown(
            self.APP_TIMEOUT, str(self.settings.timeouts.APP_TIMEOUT)
        )
        self.browser.click(self.APP_APPLY)

    def _cure_with_roll(self, injury):
        sleep(0.5)
        trs = self.browser.find_elements(self.TR)
        title = INJURIES_AND_ROLLS[injury]

        for tr in trs:
            text = self.browser.get_text(tr)
            if title in text:
                e = tr.find_elements(By.CSS_SELECTOR, "input[value='Использовать']")
                if len(e):
                    self.browser.click(e[0])
                break

    def cure_with_roll(self, injury):
        self._switch_to_frame()
        self._click_main_square()
        self.browser.click(self.HOME)
        self.browser.click(self.ROLLS)
        self._cure_with_roll(injury)
        self._click_main_square()

    def _repair_all_items(self):
        def get_btns():
            sleep(0.5)
            full_repair = (By.CSS_SELECTOR, "input[value='Чинить']")
            return self.browser.find_elements(full_repair)

        while True:
            btns = get_btns()
            before = len(btns)
            # print(before)
            if before > 0:
                btn = btns[0]
                if self.browser.is_visible(btn):
                    self.browser.click(btn)
                    after = len(get_btns())
                    #                     print(before, after)
                    if before == after:
                        break
            else:
                break

    def repair_items(self):
        self._switch_to_frame()
        self._click_main_square()
        self._click_smithy()
        self._repair_all_items()
        self._click_main_square()


class FrameFight(FrameAction):
    TIME_LEFT = (By.ID, "time_left")
    MAP = (By.ID, "map")

    ATTACK_OR_BLOCK = (By.CSS_SELECTOR, "#d_map input[value='Удар/Блок']")
    APPLY = (By.CSS_SELECTOR, "#d_ub input[value='Применить']")
    BLOCKING_TICK = (
        By.XPATH,
        "//div[@id='d_ub']//img[@class='bchk0' and contains(@id, 'bl')]",
    )
    VIEW_LOG = (By.CSS_SELECTOR, "button[title='Просмотр повтора']")

    END_FIGHT = (By.XPATH, "//input[contains(@onclick, 'goRC')]")

    def __init__(self, settings):
        FrameAction.__init__(self, settings)
        self.f_pers = FramePersInfo(settings)

    def end_fight(self):
        self._switch_to_frame()
        if self.browser.is_visible(self.END_FIGHT):
            self.browser.click(self.END_FIGHT)
        else:
            self.browser.refresh_page()

    def wait_for_fight(self):
        self._switch_to_frame()
        print("Жду начало боя")
        time1 = time.time()

        while not self.is_time_left_visible() and (
            time.time() - time1 <= self.settings.timeouts.APPLICATION_WAIT_TIMEOUT
        ):
            time.sleep(self.settings.timeouts.WAIT_FOR_FIGHT_REFRESH_TIMEOUT)

    def is_attack_or_block_visible(self):
        self._switch_to_frame()
        return self.browser.is_visible(self.ATTACK_OR_BLOCK)

    def wait_for_round_ended(self):
        print("Жду конца раунда")
        time1 = time.time()
        self._switch_to_frame()
        time_spent = time.time() - time1
        timeouts = self.settings.timeouts
        while (
            not self.browser.is_visible(self.ATTACK_OR_BLOCK)
            and time_spent <= timeouts.APP_TIMEOUT
            and self.is_fighting()
        ):
            time.sleep(1)
            time_spent = time.time() - time1

            if int(
                time_spent
            ) % timeouts.FIGHT_REFRESH_TIMEOUT <= 3 and self.browser.is_visible(
                self.REFRESH
            ):
                self._click_refresh()

            self._switch_to_frame()

        print("Новый раунд")

    def get_time_left_in_secs(self):
        self._switch_to_frame()
        if self.browser.is_visible(self.TIME_LEFT):
            text = self.browser.get_text(self.TIME_LEFT)
            return get_time_left_in_seconds(text)
        else:
            return 0

    def is_time_left_visible(self):
        self._switch_to_frame()
        return self.browser.is_present(self.TIME_LEFT)

    def is_fighting(self):
        self._switch_to_frame()
        return self.is_time_left_visible() and not self.browser.is_visible(
            self.VIEW_LOG
        )

    def wait_for_fight_ended(self):
        self._switch_to_frame()
        print("Жду конца боя")

        while self.is_fighting():
            time.sleep(self.settings.timeouts.APP_TIMEOUT)
            if self.browser.is_visible(self.REFRESH):
                self.browser.click(self.REFRESH)

    def _select_blocks(self, ticks_ids):
        assert len(ticks_ids) == 4
        ticks = self.browser.find_elements(self.BLOCKING_TICK)
        ticks_to_click = []

        for t in ticks:
            for _id in ticks_ids:
                if self.browser.get_attribute(t, "id").endswith(_id):
                    ticks_to_click.append(t)
                    break

        for t in ticks_to_click:
            self.browser.click(t)

    def _select_blocks_randomly(self):
        ticks = self.browser.find_elements(self.BLOCKING_TICK)
        left_ticks = [
            t for t in ticks if self.browser.get_attribute(t, "id").startswith("bl0")
        ]

        tick1 = get_random_value(left_ticks)
        tick2 = get_random_value(left_ticks, tick1)

        right_ticks = []
        idt1 = self.browser.get_attribute(tick1, "id")
        idt2 = self.browser.get_attribute(tick2, "id")
        for t in ticks:
            _id = self.browser.get_attribute(t, "id")
            if _id.startswith("bl1") and idt1[-1] != _id[-1] and _id[-1] != idt2[-1]:
                right_ticks.append(t)

        tick3 = get_random_value(right_ticks)
        tick4 = get_random_value(right_ticks, tick3)

        self.browser.click(tick1)
        self.browser.click(tick2)
        self.browser.click(tick3)
        self.browser.click(tick4)

    def _apply_blocks(self, block_ids):
        if self.browser.is_visible(self.APPLY):
            if block_ids:
                self._select_blocks(block_ids)
            else:
                self._select_blocks_randomly()
            if self.browser.is_visible(self.APPLY):
                self.browser.click(self.APPLY)

    def block_myself(self, block_ids):
        if self.is_fighting():
            while not self.browser.is_visible(self.APPLY):
                self.browser.click(self.ATTACK_OR_BLOCK)
            self._apply_blocks(block_ids)


class FrameChat(Frame):
    MESSAGES = (By.CSS_SELECTOR, "#messages")

    def __init__(self, settings):
        frame = (By.NAME, "d_chat")
        Frame.__init__(self, frame, settings)
        self.latest_message = None

    def get_messages(self, function=None):
        self._switch_to_frame()

        messages = self.browser.get_text(self.MESSAGES).splitlines()

        if self.latest_message and self.latest_message in messages:
            index = messages.index(self.latest_message) + 1
            messages = messages[index:]

        if len(messages) > 0:
            self.latest_message = messages[-1]

        if function:
            messages = [m for m in messages if function(m)]

        return messages


class FrameUserList(Frame):
    def __init__(self, settings):
        frame = (By.NAME, "d_ulist")
        Frame.__init__(self, frame, settings)


class FrameChatAction(Frame):
    def __init__(self, settings):
        frame = (By.NAME, "d_chatact")
        Frame.__init__(self, frame, settings)


class FrameTopMenu(Frame):
    def __init__(self, settings):
        frame = (By.NAME, "d_menu")
        Frame.__init__(self, frame, settings)
