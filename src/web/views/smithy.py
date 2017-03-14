# encoding=utf8

import re

from selenium.webdriver.common.by import By

from src.apeha.market.data.stones import STONES, FACETED, MOD_AND_LEVELS
from src.apeha.market.parsers import JewerlyParser
from src.apeha.utils import get_number_from_text, unicode_str
from src.web.views.frames import FrameAction, FrameChat


def fancy_print(value, symbol="=", length=50):
    _len = len(value) + 2
    if _len >= length:
        print value
    else:
        times = (length - _len) / 2
        print symbol * times, value, symbol * times


class Smithy(FrameAction):
    JEWELRY = (By.CSS_SELECTOR, u"input[value='Гранильные']")
    SEARCH_ITEM = (By.CSS_SELECTOR, u"input[value='Поиск товаров']")
    NAME_VALUE = (By.CSS_SELECTOR, u"input[name='iname']")
    MOD_VALUE = (By.CSS_SELECTOR, u"select[name='mod']")
    SEARCH = (By.CSS_SELECTOR, u"input[value='Найти']")
    TABLE_DATA = (By.CSS_SELECTOR, u"table.item")
    NEXT = (By.CSS_SELECTOR, u"input[value='Дальше']")
    PREVIOUS = (By.CSS_SELECTOR, u"input[value='Назад']")

    def __init__(self):
        FrameAction.__init__(self)

    def _click_jewelry(self):
        self.browser.click(self.JEWELRY)

    def _click_search_item(self):
        self.browser.click(self.SEARCH_ITEM)

    def _type(self, value):
        self.browser.type(self.NAME_VALUE, value)

    def _select_mod(self, mod):
        self.browser.type(self.MOD_VALUE, mod)

    def print_stones(self, data):
        fancy_print("Information about stones in jewelries")
        for k in sorted(data.keys()):
            print k
            v = data[k]
            for k in sorted(v.keys()):
                print "\t%s" % k
                iv = v[k]
                for s in iv:
                    print "\t%13s\t%s" % (s.price, s.owner)

    def get_stones(self, limit=10, faceted=True):
        data = {}
        """data ->     {'7':{
                                'Амазонит ограненный': [<MarketStone>, <MarketStone>],
                                },
                            }
        """

        self._click_main_square()
        self._click_smithy()
        self._click_jewelry()
        self._click_search_item()

        for k in STONES.keys():
            if faceted:
                value = u"%s %s" % (k, FACETED)
                mods = self.browser.get_texts_from_dropdown(self.MOD_VALUE)[1:]
            else:
                value = u"%s" % k
                mods = self.browser.get_texts_from_dropdown(self.MOD_VALUE)[:1]

            for mod in mods:
                self.browser.select_option_by_text_from_dropdown(self.MOD_VALUE, mod)

                self._type(value)
                self.browser.click(self.SEARCH)

                if self.browser.is_present(self.TABLE_DATA) and self.browser.is_visible(self.TABLE_DATA):
                    stones = []
                    text = self.browser.get_text(self.TABLE_DATA)
                    stones += JewerlyParser(text, faceted).get_stones()

                    while (self.browser.is_visible(self.NEXT)):
                        self.browser.click(self.NEXT)
                        if self.browser.is_present(self.TABLE_DATA) and self.browser.is_visible(self.TABLE_DATA):
                            text = self.browser.get_text(self.TABLE_DATA)
                            stones += JewerlyParser(text, faceted).get_stones()

                    def is_level_correct(stone):
                        owner = stone.owner
                        level = get_number_from_text(owner[owner.rindex(' '):])
                        _mod = get_number_from_text(mod)
                        _min, _max = MOD_AND_LEVELS[_mod]

                        return _min <= level <= _max

                    if faceted:
                        stones = [s for s in stones if is_level_correct(s)]
                    stones = sorted(stones)[:limit]

                    if mod in data.keys():
                        data[mod][value] = stones
                    else:
                        data[mod] = {value: stones}

        return data


class SmithyChat(FrameChat):
    MESSAGES = (By.CSS_SELECTOR, u"#messages")

    def __init__(self, settings, facet=7):
        FrameChat.__init__(self, settings)
        self.facet = facet

    def is_message(self, text):
        column = ":"

        if text.find(column) == -1:
            return False
        text = text[text.index(column) + 1:]

        if text.find(column) == -1:
            return False
        text = text[text.index(column) + 1:]
        text = text.strip()
        text = text.lower()

        facet2 = unicode_str(self.facet * 5)
        facet = unicode_str(self.facet)

        if u"свободный" in text or \
                        u"вставлю" in text or \
                        u"вставляю" in text or \
                        u"вставк" in text or \
                        u"заказ" in text or \
                        u"свободен" in text:
            if u"нужен" not in text:
                return False

        if facet in text:
            index = text.index(facet) + 1
            if index < len(text):
                # print text, text[index]
                return re.match("[0-9]{1}", text[index]) == None
            else:
                return True

        if facet2 in text:
            return True

        return False

    def get_messages(self):
        return FrameChat.get_messages(self, self.is_message)
