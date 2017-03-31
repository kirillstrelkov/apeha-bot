# encoding=utf8

import time
import traceback
from threading import Event

from selenium.common.exceptions import WebDriverException

from src.apeha.bot.fight.fight_utils import get_best_application
from src.apeha.bot.settings import BotSettings, save_settings
from src.apeha.utils import print_exception
from src.web.utils.webutils import get_browser
from src.web.views.frames import FramePersInfo, ApehaMain, FrameAction, \
    FrameFight, FrameCreateClone


class StopException(Exception):
    pass


class ApehaBot(object):
    stop_event = Event()

    def __init__(self, default_settings=None, use_saved_ids_from_settings=False):
        if not default_settings:
            self.default_settings = BotSettings()
        else:
            self.default_settings = default_settings

        self.use_saved_ids_from_settings = use_saved_ids_from_settings

    def to_stop(self):
        if self.stop_event.is_set():
            raise StopException

    def _go_back_to_castle(self, frame, clan):
        try:
            self.to_stop()
            frame._switch_to_frame()
            frame._click_main_square()
            frame._click_castle_alley()
            frame._go_to_castle_from_alley(clan)
        except WebDriverException:
            print u"Не смог добежать до замка"

    def _go_back_to_castle_and_wait_for_hp_mana(self, f_action, f_info, clan):
        self.to_stop()
        hp_cur, hp_max = f_info.get_hp_cur_and_max()
        mana_cur, mana_max = f_info.get_mana_cur_and_max()
        if mana_cur == mana_max and hp_cur == hp_max:
            return
        else:
            if mana_cur > self.default_settings.fighting_settings.MANA_FOR_HP and hp_cur != hp_max:
                f_info.cast_fill_hp()
                if len(get_browser()._driver.window_handles) > 1:
                    get_browser().close_current_window_and_focus_to_previous_one()

            self._go_back_to_castle(f_action, clan)
            f_action._sit_down_in_chair()
            self._wait_for_hp_and_mana(f_info)
            f_action._stand_up_from_chair()

    def _select_or_create_application(self, frame, level):
        self.to_stop()
        frame._click_chaos_fight()
        apps = frame._get_applications()
        app = get_best_application(apps,
                                   level,
                                   self.default_settings.fighting_settings)

        if app:
            frame._enter_application(app)
        else:
            frame._create_application(level)

    def _cure_injury_if_injured(self, f_info, f_action):
        while f_info.is_injured():
            self.to_stop()
            f_info.cure_with_ability()
            f_action.browser.refresh_page()

            if not f_info.is_injured():
                break

            injury = f_info.get_injury()
            f_action.cure_with_roll(injury)

    def _take_off_put_on_items(self, f_action, strict=True):
        self.to_stop()
        item_ids = []
        if strict:
            try:
                item_ids = f_action.take_off_item_and_get_ids()
                if not item_ids:
                    item_ids = self.default_settings.item_ids
                f_action.put_on_items_by_ids(item_ids)
            except:
                pass
        return item_ids

    def _repair_items_and_put_on(self, f_action, f_info, item_ids, rating):
        self.to_stop()
        try:
            if rating != f_info.get_rating() and len(item_ids) > 0:
                cash = f_info.get_cash()
                if cash and len(cash) == 2 and cash[-1] > 0:
                    print u"Найденно %f синих соткок на руках" % cash[-1]
                    print u"!!!Починку предметов пропускаю!!!"
                else:
                    f_action.repair_items()
                f_action.put_on_items_by_ids(item_ids)
        except:
            f_action._click_main_square()

    def _wait_for_hp_and_mana(self, f_info):
        self.to_stop()
        is_full = f_info.is_ready_to_fight()
        if not is_full:
            print u"Жду восстановления жизней и маны"

        while (not is_full):
            time.sleep(self.default_settings.timeouts.PERS_READY_TIMEOUT)
            is_full = f_info.is_ready_to_fight()

    def _login(self, username, password):
        self.to_stop()
        try:
            main = ApehaMain(self.default_settings)
            main.login(username, password)
        except Exception:
            traceback.print_exc()
            raise Exception(u"Не могу залогиниться")

    def _start_and_end_fight(self, f_action, f_info, f_fight, fight_bot, name, item_ids, rating, astral_level,
                             block_ids):
        self.to_stop()
        print u"Бой начался"
        try:
            fight_bot.fight(name, astral_level, block_ids)
        except WebDriverException:
            traceback.print_exc()
        finally:
            self.__exit_astral(f_fight, fight_bot)
            f_fight.wait_for_fight_ended()
        f_fight.end_fight()

    def __exit_astral(self, f_fight, fight_bot):
        print(u'Выхожу из астрала')
        in_astral = True
        while f_fight.is_fighting() and in_astral:
            self.to_stop()
            in_astral = fight_bot.__select_previous_astral_and_is_in_astral()
            time.sleep(self.default_settings.timeouts.ASTRAL_REFRESH_TIMEOUT)

    def __select_tactics_if_needed(self):
        self.to_stop()
        f_info = FramePersInfo(self.default_settings)
        f_info.select_tactics(self.default_settings.default_tactics)
        return True

    def run(self, username, password, astral_level, block_ids=None):
        try:
            f_action = FrameAction(self.default_settings)
            f_fight = FrameFight(self.default_settings)
            f_info = FramePersInfo(self.default_settings)
            fight_bot = FightBot(f_fight, f_info, self.default_settings, self.stop_event)

            self._login(username, password)
            rating = f_info.get_rating()
            if abs(self.default_settings.rating - rating) <= 0.2:
                item_ids = self.default_settings.item_ids
            elif self.use_saved_ids_from_settings:
                item_ids = self.default_settings.item_ids
                f_action.take_off_item_and_get_ids()
                f_action.put_on_items_by_ids(item_ids)
            else:
                item_ids = self._take_off_put_on_items(f_action)

            self.default_settings.item_ids = item_ids

            rating = f_info.get_rating()
            self.default_settings.rating = rating

            save_settings(self.default_settings)

            while True:
                try:
                    self.to_stop()
                    rating = f_info.get_rating()
                    info = f_info.get_player_info()

                    self._cure_injury_if_injured(f_info, f_action)
                    self._go_back_to_castle_and_wait_for_hp_mana(f_action, f_info, info.clan)

                    # Gets personal info
                    info = f_info.get_player_info()

                    f_action._click_main_square()
                    f_action._go_to_newbie_room_from_main_square()
                    self._select_or_create_application(f_action, info.level)

                    # Move to my castle if possible
                    self._go_back_to_castle(f_action, info.clan)

                    # Waiting for run started
                    f_fight.wait_for_fight()
                    if f_fight.is_time_left_visible():
                        self._start_and_end_fight(f_action, f_info, f_fight, fight_bot, info.name, item_ids, rating,
                                                  astral_level, block_ids)
                        self._repair_items_and_put_on(f_action, f_info, item_ids, rating)
                    else:
                        print u"Бой не начался пробую еще раз"
                except StopException as e:
                    raise e
                except:
                    print_exception()
                    get_browser().refresh_page()
                    if len(get_browser()._driver.window_handles) > 1:
                        get_browser().close_current_window_and_focus_to_previous_one()
                        get_browser().switch_to_default_content()
                    f_action._stand_up_from_chair()
        except StopException:
            print u"Бот остановлен"


class FightBot(object):
    def __init__(self, f_fight, f_info, default_settings, stop_event):
        self.f_fight = f_fight
        self.f_info = f_info
        self.default_settings = default_settings
        self.stop_event = stop_event

    def to_stop(self):
        if self.stop_event.is_set():
            raise StopException

    def _get_players(self, fcc, nickname=None, team=None):
        self.to_stop()
        players = None
        for _ in range(5):
            try:
                if team:
                    players = fcc._get_players_using_team(team)
                if nickname and not players:
                    players = fcc._get_players_using_nickname(nickname)
                break
            except Exception:
                print_exception()
                continue

        return players

    def __select_next_astral_and_is_in_astral(self, cur_level, max_level):
        self.to_stop()
        astral_cur = self.f_info.get_astral_cur_and_max()[0]
        if astral_cur > self.default_settings.fighting_settings.MIN_ASTRAL_MANA_TO_USE and cur_level != max_level:
            cur_astral_level = self.f_info.select_next_astral_level()
            return cur_astral_level
        else:
            return cur_level

    def __select_previous_astral_and_is_in_astral(self):
        self.to_stop()
        cur_astral_level = self.f_info.select_previous_astral_level()
        if cur_astral_level == self.default_settings.fighting_settings.ASTRAL_LEVELS[0]:
            return False
        else:
            return True

    def __to_freeze(self, players, num_of_enemies, num_of_aliases):
        self.to_stop()
        noe = len(players.enemy_team)
        noa = len(players.my_team)
        return noe == num_of_enemies or noa == num_of_aliases

    def __use_mana(self, players, cur_round=-1):
        self.to_stop()
        cur_num_of_enemies = len(players.enemy_team)
        cur_num_of_aliases = len(players.my_team)
        enemies_are_cloning = cur_num_of_enemies > len(players.enemy_originals)
        aliases_are_cloning = cur_num_of_aliases > len(players.alias_originals)
        have_alias = cur_num_of_aliases > 1
        return cur_round == 1 or \
               have_alias and (enemies_are_cloning and
                               aliases_are_cloning or
                               aliases_are_cloning and
                               cur_num_of_aliases / float(cur_num_of_enemies) < 2.0)

    def fight(self, name, astral_level, block_ids):
        self.to_stop()
        in_astral = False
        cur_astral_level = 0
        useless_rounds = 0
        cur_round = 1

        fcc = FrameCreateClone(self.f_fight, self.default_settings)
        team_color = None

        hp_cur = self.f_info.get_hp_cur_and_max()[0]
        while hp_cur > 0:
            self.to_stop()

            mana_cur = self.f_info.get_mana_cur_and_max()[0]
            hp_cur, hp_max = self.f_info.get_hp_cur_and_max()
            hp_rate = float(hp_cur) / hp_max

            if hp_cur == 0 or not self.f_fight.is_attack_or_block_visible():
                break

            players = self._get_players(fcc, nickname=name, team=team_color)
            if not players:
                break
            if len(players.enemy_originals) == 1 and len(players.alias_originals) == 1:
                break

            if not team_color:
                team_color = players.team_color

            if self.__use_mana(players, cur_round):
                try:
                    if (mana_cur >= self.default_settings.fighting_settings.MANA_FOR_CLONE and
                                hp_rate >= self.default_settings.fighting_settings.MIN_HP_RATIO):
                        cur_astral_level = self.__select_next_astral_and_is_in_astral(cur_astral_level, astral_level)
                        in_astral = cur_astral_level > 0

                        self.f_info.cast_create_clone()
                        fcc.create_clone(name, players, self.default_settings.clone_placement)
                        useless_rounds = 0
                    elif (mana_cur >= self.default_settings.fighting_settings.MANA_FOR_HP and
                                  hp_rate < self.default_settings.fighting_settings.MIN_HP_RATIO):
                        self.f_info.cast_fill_hp()
                        useless_rounds = 0
                finally:
                        browser = get_browser()
                        driver = browser._driver
                        if len(driver.window_handles) > 1:
                            try:
                                browser.close_current_window_and_focus_to_previous_one()
                            except WebDriverException:
                                driver.switch_to_alert()
                                browser.alert_accept()

            else:
                useless_rounds += 1
                if useless_rounds == self.default_settings.fighting_settings.ROUNDS_TO_FREEZE:
                    break

            self.f_fight.block_myself(block_ids)

            self.to_stop()
            self.f_fight.wait_for_round_ended()
            cur_round += 1

        self.to_stop()
