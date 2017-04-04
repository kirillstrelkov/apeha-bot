# encoding=utf8

import re
from pprint import pformat

from math import cos, sin, radians

from src.apeha.bot.settings import SpellTexts, _FightingSettings
from src.apeha.utils import ApehaRegExp


class Team(object):
    BLUE = 0
    RED = 1


class Players(object):
    def __init__(self, team_color, all_players, enemy_team, my_team, enemy_originals, alias_originals):
        self.team_color = team_color
        self.all_players = all_players
        self.enemy_team = enemy_team
        self.my_team = my_team
        self.enemy_originals = enemy_originals
        self.alias_originals = alias_originals

    def __str__(self):
        return pformat(self.__dict__)


class PlayerNeighbours(object):
    """
        Holds information about current coordinates and 6 other neighbours.
            F             A
        E       (0,0)       B
            D            C
    """
    TOTAL = 360
    RADIUS = 30
    RADIUS_DOUBLE = RADIUS * 2

    CLOCKWISE = 'clockwise'
    ANTI_CLOCKWISE = 'counter_clockwise'

    CLOCKWISE_SET = [(cos(radians(angle)) * RADIUS,
                      sin(radians(angle)) * RADIUS) for angle in range(-60, 300, 60)]
    ANTICLOCKWISE_SET = [(cos(radians(angle)) * RADIUS,
                          sin(radians(angle)) * RADIUS) for angle in range(240, -120, -60)]

    CLOCKWISE_SET2 = [(cos(radians(angle)) * RADIUS_DOUBLE,
                      sin(radians(angle)) * RADIUS_DOUBLE) for angle in range(-60, 300, 30)]
    ANTICLOCKWISE_SET2 = [(cos(radians(angle)) * RADIUS_DOUBLE,
                          sin(radians(angle)) * RADIUS_DOUBLE) for angle in range(240, -120, -30)]

    @classmethod
    def get_set(cls, wise, radius=RADIUS):
        if radius == cls.RADIUS:
            if wise == cls.ANTI_CLOCKWISE:
                return cls.ANTICLOCKWISE_SET
            elif wise == cls.CLOCKWISE:
                return cls.CLOCKWISE_SET
            else:
                raise NotImplementedError
        elif radius == cls.RADIUS_DOUBLE:
            if wise == cls.ANTI_CLOCKWISE:
                return cls.ANTICLOCKWISE_SET2
            elif wise == cls.CLOCKWISE:
                return cls.CLOCKWISE_SET2
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError



class Application(object):
    def __init__(self, min_level, max_level, max_size, players, _type, _map, obstacle, timout, webelement=None):
        self.webelement = webelement
        self.min_level = min_level
        self.max_level = max_level
        self.max_size = max_size
        self.players = players
        self.type = _type
        self.map = _map
        self.obstacle = obstacle
        self.size = len(players)
        self.timeout = timout
        self.avg_rating = self.__get_avg_rating()

    def __get_avg_rating(self):
        ratings = []
        for player in self.players:
            found = re.findall("\[(\d+)\]", player)
            if found and len(found) > 0:
                ratings.append(int(found[0]))

        return sum(ratings) / float(len(ratings))

    def __str__(self):
        return u"\n".join(['%s' % i for i in
                           [self.min_level, self.max_level, self.type, self.map, self.obstacle, self.size,
                            self.players]]).encode('utf8')


def create_application(left_text, right_text):
    players = left_text.splitlines()
    rlines = right_text.splitlines()

    max_size = int(re.search('/(\d+)', rlines[0]).group(1))

    cols = rlines[1].split()
    r = re.search('(\d+)-(\d+)', cols[0])
    min_level = int(r.group(1))
    max_level = int(r.group(2))
    _type = cols[1]
    obstacle = len(cols) > 2
    _map = rlines[2]

    if len(rlines) > 3:
        found = re.findall(u'На ход\s*(\d+):(\d+)', rlines[-1])
        if found and len(found) > 0:
            _min, sec = found[0]
        else:
            _min, sec = 3, 0
    else:
        _min, sec = 3, 0

    return Application(min_level, max_level, max_size, players,
                       _type, _map, obstacle, int(_min) * 60 + int(sec))


def get_best_application(apps, min_level, fighting_settings=None):
    if not fighting_settings:
        fighting_settings = _FightingSettings()
    filtered_apps = [a for a in apps if (a.min_level >= min_level + fighting_settings.APP_MIN_LEVEL_DIFF and
                                         a.timeout >= fighting_settings.APP_MIN_TIMEOUT and
                                         a.max_size >= fighting_settings.APP_MIN_SIZE and
                                         not a.obstacle and
                                         a.map.count(fighting_settings.APP_MAP_STANDARD) == 2)]
    apps = []
    for app in filtered_apps:
        is_good_app = True
        for player in app.players:
            player_name = re.sub(ApehaRegExp.NICKNAME_HP_ENDING, '', player)
            is_good_app = is_good_app and player_name not in fighting_settings.UNWANTED_PLAYERS
            if not is_good_app:
                break

        if is_good_app:
            apps.append(app)

    apps = sorted(apps, key=lambda x: (x.avg_rating, x.size, -x.max_size))

    if len(apps) > 0:
        return apps[-1]
    else:
        return None


def get_astral_level_from(text):
    current_lvl = SpellTexts.CURRENT_ASTRAL_LVL_TEXT + u" (\d+)"
    match = re.search(current_lvl, text)
    if match:
        return int(match.group(1))
    else:
        return None


def get_nicknames(text):
    lines = text.split("]")
    nicknames = []

    for line in lines:
        match = re.search("\w{2} (.+) \d+ \[", line)
        if match and match.groups() > 0:
            nicknames.append(match.group(1))

    return nicknames


def get_time_left_in_seconds(text):
    nums = re.findall("\d+", text)
    if len(nums) == 2:
        mins, secs = int(nums[0]), int(nums[1])
        return mins * 60 + secs
    else:
        return 0
