# encoding=utf8

import time
import traceback
from threading import Event
from selenium.common.exceptions import WebDriverException

from src.web.utils.webutils import  \
    get_browser

from src.web.views.frames import FramePersInfo, ApehaMain, FrameAction, \
    FrameFight, FrameCreateClone
from src.apeha.fight.fight_utils import get_best_application, MIN_HP_RATIO, \
    MANA_FOR_HP, MANA_FOR_CLONE, MIN_ASTRAL_MANA_TO_USE, ASTRAL_LEVELS, \
    PERS_READY_TIMEOUT, ASTRAL_REFRESH_TIMEOUT, ROUNDS_TO_FREEZE, Tactics
from src.apeha.common.utils import print_exception

RATING = 1016.8
ITEM_IDS = [29614430, 49210983, 30953754, 50664801, 53547874, 49643727, 53547831, 50079096, 7720059, 56274248, 33872312, 54094213, 28913708, 26968651, 33648559, 12899862, 23430181, 60529820, 45384884, 38485632, 51044537, 49810750, 48746647, 48735644, 54063846, 60388735, 48724953, 52823274, 34543397, 50727478, 44910294, 56527986, 49192644]


class StopException(Exception):
    pass


class ApehaBot(object):
    stop_event = Event()
    
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
            if mana_cur > MANA_FOR_HP and hp_cur != hp_max:
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
        app = get_best_application(apps, level)
        
        if app:
            frame._enter_application(app)
        else:
            frame._create_application(level)
    
    def _cure_injury_if_injured(self, f_info, f_action):
        self.to_stop()
        while f_info.is_injured():
            f_info.cure_with_ability()
            f_action._click_refresh()
            
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
                f_action.put_on_items_by_ids(item_ids)
            except:
                pass
        return item_ids
    
    def _repair_items_and_put_on(self, f_action, f_info, item_ids, rating):
        self.to_stop()
        try:
            if rating != f_info.get_rating() and len(item_ids) > 0:
                f_action.repair_items()
                f_action.put_on_items_by_ids(item_ids)
        except:
            f_action._click_main_square()
    
    def _wait_for_hp_and_mana(self, f_info):
        self.to_stop()
        is_full = f_info.is_ready_to_fight()
        if not is_full:
            print u"Жду восстановления жизней и маны"
        
        while(not is_full):
            time.sleep(PERS_READY_TIMEOUT)
            is_full = f_info.is_ready_to_fight()
    
    def _login(self, username, password):
        self.to_stop()
        try:
            main = ApehaMain()
            main.login(username, password)
        except Exception:
            traceback.print_exc()
            raise Exception(u"Не могу залогиниться")
    
    def _start_and_end_fight(self, f_action, f_info, f_fight, fight_bot, name, item_ids, rating, astral_level, block_ids):
        self.to_stop()
        print u"Бой начался"
        try:
            fight_bot.fight(name, astral_level, block_ids)
        except WebDriverException:
            traceback.print_exc()
        finally:
            f_fight.wait_for_fight_ended()
        f_fight.end_fight()
        self._repair_items_and_put_on(f_action, f_info, item_ids, rating)
    
    def run(self, username, password, astral_level, block_ids=None):
        try:
            f_action = FrameAction()
            f_fight = FrameFight()
            f_info = FramePersInfo()
            fight_bot = FightBot(f_fight, f_info, self.stop_event)
            
            self._login(username, password)
            rating = f_info.get_rating()
            if abs(RATING - rating) <= 0.2:
                item_ids = ITEM_IDS
            else:
                item_ids = self._take_off_put_on_items(f_action)
            
            while(True):
                try:
                    self.to_stop()
                    rating = f_info.get_rating()
                    info = f_info.get_player_info()
                    
                    self._cure_injury_if_injured(f_info, f_action)
                    self._go_back_to_castle_and_wait_for_hp_mana(f_action, f_info, info.clan)
                    
                    # Gets presonal info
                    info = f_info.get_player_info()
                    
                    f_action._click_main_square()
                    f_action._go_to_newbie_room_from_main_square()
                    self._select_or_create_application(f_action, info.level)
                    
                    # Move to my castle if possible
                    self._go_back_to_castle(f_action, info.clan)
                    
                    # Waiting for run started
                    f_fight.wait_for_fight()
                    if f_fight.is_time_left_visible():
                        self._start_and_end_fight(f_action, f_info, f_fight, fight_bot, info.name, item_ids, rating, astral_level, block_ids)
                    else:
                        print u"Бой не начался пробую еще раз"
                except Exception:
                    print_exception()
                    get_browser().refresh_page()
                    if len(get_browser()._driver.window_handles) > 1:
                        get_browser().close_current_window_and_focus_to_previous_one()
                        get_browser().switch_to_default_content()
        except StopException:
            print u"Бот остановлен"

class FightBot(object):
    def __init__(self, f_fight, f_info, stop_event):
        self.f_fight = f_fight
        self.f_info = f_info
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
        if astral_cur > MIN_ASTRAL_MANA_TO_USE and cur_level != max_level:
            cur_astral_level = self.f_info.select_next_astral_level()
            return cur_astral_level
        else:
            return cur_level
    
    def __select_previous_astral_and_is_in_astral(self):
        self.to_stop()
        cur_astral_level = self.f_info.select_previous_astral_level()
        if cur_astral_level == ASTRAL_LEVELS[0]:
            return False
        else:
            return True
    
    def __select_tactics_if_needed(self, tactics_is_set):
        self.to_stop()
        if not tactics_is_set:
            self.f_info.select_defensive_tactics(Tactics.DEFENSIVE)
            return True
        else:
            return tactics_is_set
    
    def __to_freeze(self, players, num_of_enemies, num_of_aliases):
        self.to_stop()
        noe = len(players.enemy_team)
        noa = len(players.my_team)
        return noe == num_of_enemies or noa == num_of_aliases
    
    def __use_mana(self, players):
        self.to_stop()
        cur_num_of_emenies = len(players.enemy_team)
        cur_num_of_aliases = len(players.my_team)
#         print prev_num_of_enemies, cur_num_of_emenies , prev_num_of_aliases , cur_num_of_aliases
#         print cur_num_of_aliases , cur_num_of_emenies - prev_num_of_enemies , cur_num_of_aliases - prev_num_of_aliases
#        players.enemy_originals players.alias_originals
        enemies_are_cloning = cur_num_of_emenies > len(players.enemy_originals)
        aliases_are_cloning = cur_num_of_aliases >= len(players.alias_originals)
        have_alias = cur_num_of_aliases > 1
        return have_alias and (enemies_are_cloning and aliases_are_cloning
                               or aliases_are_cloning 
                               and cur_num_of_aliases / float(cur_num_of_emenies) < 2.0)
    
    def fight(self, name, astral_level, block_ids):
        self.to_stop()
        tactics_is_set = False
        in_astral = False
        cur_astral_level = 0
        useless_rounds = 0
        
        fcc = FrameCreateClone(self.f_fight)
        players = None
        team_color = None
        
        hp_cur = self.f_info.get_hp_cur_and_max()[0]
        while(hp_cur > 0):
            self.to_stop()
            tactics_is_set = self.__select_tactics_if_needed(tactics_is_set)
            
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
            
            if self.__use_mana(players):
                try:
                    if mana_cur >= MANA_FOR_CLONE and hp_rate >= MIN_HP_RATIO:
                        cur_astral_level = self.__select_next_astral_and_is_in_astral(cur_astral_level, astral_level)
                        in_astral = cur_astral_level > 0
                        
                        self.f_info.cast_create_clone()
                        fcc.create_clone(players.alias_originals, team_color)
                        useless_rounds = 0
                    elif mana_cur >= MANA_FOR_HP and hp_rate < MIN_HP_RATIO:
                        self.f_info.cast_fill_hp()
                        useless_rounds = 0
                finally:
                    if len(get_browser()._driver.window_handles) > 1:
                        close_current_window_and_focus_to_previous_one()
                
            else:
                useless_rounds += 1
                if useless_rounds == ROUNDS_TO_FREEZE:
                    break
            
            # IF peremanili skip blocking
            self.f_fight.block_myself(block_ids)
            # while if not my round and time  update players
#             while(self.f_fight.get_time_left_in_secs() > 20 and not self.f_fight.is_attack_or_block_visible()):
#                 players = self._get_players(fcc, team=team_color)
#                 time.sleep(1)
            
            self.to_stop()
            self.f_fight.wait_for_round_ended()
        
        while(self.f_fight.is_fighting() and in_astral):
            self.to_stop()
            in_astral = self.__select_previous_astral_and_is_in_astral()
            time.sleep(ASTRAL_REFRESH_TIMEOUT)
    
        self.to_stop()
