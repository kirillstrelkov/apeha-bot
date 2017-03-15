# encoding=utf8

import re
from pprint import pformat

from src.apeha.bot.settings import SpellTexts, _FightingSettings


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
        Hold information about current coordinates and 6 other neighbours.
            F             A
        E       (0,0)       B
            D            C
    """
    RADIUS = 20

    def __init__(self):
        x, y = 0, 0
        big_radius = int(1.5 * self.RADIUS)
        self.A = (x + self.RADIUS, y - big_radius)
        self.B = (x + 2 * self.RADIUS, y)
        self.C = (x + self.RADIUS, y + big_radius)
        self.D = (x - self.RADIUS, y + big_radius)
        self.E = (x - 2 * self.RADIUS, y)
        self.F = (x - self.RADIUS, y - big_radius)
        self.RIGHT_SET = (self.A, self.B, self.C)
        self.LEFT_SET = (self.F, self.E, self.D)
        self.CLOCKWISE_SET = self.RIGHT_SET + self.LEFT_SET[-1::-1]
        self.ANTICLOCKWISE_SET = self.LEFT_SET + self.RIGHT_SET[-1::-1]


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


def get_best_application(apps, min_level, unwanted_player=None):
    if not unwanted_player:
        unwanted_player = []
    filtered_apps = [a for a in apps if (a.min_level >= min_level + _FightingSettings.APP_MIN_LEVEL_DIFF and
                                         a.timeout > _FightingSettings.APP_MIN_TIMEOUT and
                                         a.max_size > _FightingSettings.APP_MIN_SIZE)]
    apps = []
    for app in filtered_apps:
        is_good_app = True
        for player in app.players:
            player_name = re.sub(r'\s+\[\d+\]$', '', player)
            is_good_app = is_good_app and player_name not in unwanted_player
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
