# encoding=utf8
import codecs
import os
import pickle

import jsonpickle

jsonpickle.set_preferred_backend("json")
jsonpickle.set_encoder_options("json", indent=4)

INJURIES_AND_ROLLS = {
    "Легкая травма": "Лечение легкой травмы",
    "Средняя травма": "Лечение средней травмы",
    "Тяжелая травма": "Лечение тяжелой травмы",
}


class ClonePlacement(object):
    TO_ALIASES_ME_FIRST = "Ставить клонов к себе потом к союзникам"
    TO_ALIASES_TOP = "Ставить клонов к союзникам начиная сверху"
    TO_ALIASES_RANDOM = "Ставить клонов к союзникам рандомно"
    TO_EMENIES_TOP = "Ставить клонов к противникам начиная сверху"
    TO_EMENIES_BOTTOM = "Ставить клонов к противникам начиная снизу"
    TO_EMENIES_RANDOM = "Ставить клонов к противникам рандомно"
    ALL = [
        TO_ALIASES_ME_FIRST,
        TO_ALIASES_TOP,
        TO_ALIASES_RANDOM,
        TO_EMENIES_TOP,
        TO_EMENIES_BOTTOM,
        TO_EMENIES_RANDOM,
    ]


class Tactics(object):
    STANDARD = "Стандартная"
    DEFENSIVE = "Защитная"
    OFFENSIVE = "Атакующая"
    AGRESSIVE = "Агрессивная"
    ALL = [STANDARD, DEFENSIVE, OFFENSIVE, AGRESSIVE]


class SpellTexts(object):
    CURRENT_ASTRAL_LVL_TEXT = "Текущий слой астрала:"
    MAGBOOK_FILL_HP_TEXT = "Восстановить здоровье"
    MAGBOOK_CREATE_CLONE1 = "Создать клон"
    MAGBOOK_CREATE_CLONE2 = "Вызвать помощника"
    MAGBOOK_CREATE_CLONE3 = "Призвать слугу"


class _Timeouts(object):
    def __init__(self):
        self.APP_TIMEOUT = 1 * 60
        self.FIGHT_REFRESH_TIMEOUT = 1.0 * 13
        self.APPLICATION_WAIT_TIMEOUT = 10 * 60
        self.PERS_READY_TIMEOUT = 1 * 60
        self.ASTRAL_REFRESH_TIMEOUT = 3 * 60
        self.WAIT_FOR_FIGHT_REFRESH_TIMEOUT = 3
        self.MAX_TIMEOUT_PER_WAIT_FOR_VISIBLE = 2 * 60


class _FightingSettings(object):
    def __init__(self):
        self.BROWSER_HEADLESS = False
        self.MANA_FOR_CLONE = 75
        self.MANA_FOR_HP = 50
        self.MIN_HP_RATIO = 0.75

        self.ROUNDS_TO_FREEZE = 20

        self.ASTRAL_LEVELS = [0, 1, 2, 3]

        self.MIN_ASTRAL_MANA_TO_USE = 10

        # self.MY_BLOCKING_TICK_IDS = ["00", "01", "12", "14"]
        self.UNWANTED_PLAYERS = []

        self.APP_NUMBER_OF_PLAYERS = 8
        self.APP_MIN_TIMEOUT = 30
        self.APP_MIN_LEVEL_DIFF = 3
        self.APP_MIN_SIZE = 3
        self.APP_MAP_STANDARD = "станд"


class BotSettings(object):
    FILEPATH = os.path.join(os.path.expanduser("~"), ".apehapy_settings.json")

    # main settings which should be used everywhere
    def __init__(self):
        self.fighting_settings = _FightingSettings()
        self.timeouts = _Timeouts()
        self.clone_placement = ClonePlacement.TO_ALIASES_ME_FIRST
        self.rating = 0.0
        self.item_ids = []
        self.default_tactics = Tactics.DEFENSIVE
        self.default_astral_level = 3


__MODE_RB = "rb"
__MODE_WB = "wb"
__ENCODING = "utf8"


def get_settings(path=None):
    if not path:
        path = BotSettings.FILEPATH

    if os.path.exists(path):
        with codecs.open(path, __MODE_RB, __ENCODING) as ofile:
            content = ofile.read()
            return jsonpickle.decode(content)
    else:
        return BotSettings()


def save_settings(settings, path=None):
    if not path:
        path = BotSettings.FILEPATH

    with codecs.open(path, __MODE_WB, __ENCODING) as ofile:
        ofile.write(jsonpickle.encode(settings))
        ofile.flush()
