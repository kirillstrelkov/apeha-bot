# encoding=utf8
import codecs
import os
import pickle

INJURIES_AND_ROLLS = {
    u"Легкая травма": u"Лечение легкой травмы",
    u"Средняя травма": u"Лечение средней травмы",
    u"Тяжелая травма": u"Лечение тяжелой травмы",
}


class ClonePlacement(object):
    TO_ALIASES_ME_FIRST = u"Ставить клонов к себе потом к союзникам"
    TO_ALIASES_TOP = u"Ставить клонов к союзникам начиная сверху"
    TO_ALIASES_RANDOM = u"Ставить клонов к союзникам рандомно"
    TO_EMENIES_TOP = u"Ставить клонов к противникам начиная сверху"
    TO_EMENIES_BOTTOM = u"Ставить клонов к противникам начиная снизу"
    TO_EMENIES_RANDOM = u"Ставить клонов к противникам рандомно"
    ALL = [TO_ALIASES_ME_FIRST, TO_ALIASES_TOP, TO_ALIASES_RANDOM,
           TO_EMENIES_TOP, TO_EMENIES_BOTTOM, TO_EMENIES_RANDOM]


class Tactics(object):
    STANDARD = u"Стандартная"
    DEFENSIVE = u"Защитная"
    OFFENSIVE = u"Атакующая"
    AGRESSIVE = u"Агрессивная"
    ALL = [STANDARD, DEFENSIVE, OFFENSIVE, AGRESSIVE]


class SpellTexts(object):
    CURRENT_ASTRAL_LVL_TEXT = u"Текущий слой астрала:"
    MAGBOOK_FILL_HP_TEXT = u"Восстановить здоровье"
    MAGBOOK_CREATE_CLONE1 = u"Создать клон"
    MAGBOOK_CREATE_CLONE2 = u"Вызвать помощника"
    MAGBOOK_CREATE_CLONE3 = u"Призвать слугу"


class _Timeouts(object):
    APP_TIMEOUT = 1 * 60
    FIGHT_TIMEOUT = 1.0 * 60
    APPLICATION_WAIT_TIMEOUT = 10 * 60
    PERS_READY_TIMEOUT = 1 * 60
    ASTRAL_REFRESH_TIMEOUT = 3 * 60
    WAIT_FOR_FIGHT_REFRESH_TIMEOUT = 5
    MAX_TIMEOUT_PER_WAIT_FOR_VISIBLE = 2 * 60


class _FightingSettings(object):
    MANA_FOR_CLONE = 75
    MANA_FOR_HP = 50
    MIN_HP_RATIO = 0.75

    ROUNDS_TO_FREEZE = 20

    ASTRAL_LEVELS = [0, 1, 2, 3]

    APP_NUMBER_OF_PLAYERS = 8
    MIN_ASTRAL_MANA_TO_USE = 10

    MY_BLOCKING_TICK_IDS = ["00", "01", "12", "14"]
    UNWANTED_PLAYERS = []


class BotSettings(object):
    FILEPATH = os.path.join(os.path.expanduser("~"), '.settings_apehapy')

    # main settings which should be used everywhere
    def __init__(self):
        self.fighting_settings = _FightingSettings()
        self.timeouts = _Timeouts()
        self.clone_placement = ClonePlacement.TO_ALIASES_ME_FIRST
        self.rating = 1020.2
        self.item_ids = [29614430, 30953754, 50664801, 53547874,
                         49643727, 66191327, 50079096, 7720059,
                         56274248, 33872312, 54094213, 48363762,
                         61720658, 28913708, 26968651, 12899862,
                         23430181, 60529820, 38485632, 51044537,
                         48735644, 48746647, 49810750, 54063846,
                         60388735, 48724953, 52823274, 34543397,
                         50727478, 44910294, 56527986, 49192644]
        self.default_tactics = Tactics.DEFENSIVE
        self.default_astral_level = 3


__MODE_RB = 'rb'
__MODE_WB = 'wb'
__ENCODING = 'utf8'


def get_settings(path=None):
    if not path:
        path = BotSettings.FILEPATH

    if os.path.exists(path):
        with codecs.open(path, __MODE_RB, __ENCODING) as ofile:
            content = ofile.read()
            return pickle.loads(content)
    else:
        return BotSettings()


def save_settings(settings, path=None):
    if not path:
        path = BotSettings.FILEPATH

    with codecs.open(path, __MODE_WB, __ENCODING) as ofile:
        ofile.write(pickle.dumps(settings))
        ofile.flush()
