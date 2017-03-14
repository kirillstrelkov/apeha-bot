# encoding=utf8

import re

from src.apeha.market.data.stones import FACETED, STONES
from src.apeha.market.price import Price
from src.apeha.market.stats import Property
from src.apeha.market.stone import MarketStone


class LineParser(object):
    def __get_croped_line(self, cropping_line, line):
        index = line.find(cropping_line)

        if index != -1:
            return line[index + len(cropping_line):].strip()
        else:
            return None

    def get_price_from_line(self, line):
        price = u"Цена:"
        regexp = "(\d+\.\d+)\s*\+?\s*(\d+\.\d+)?"
        line = self.__get_croped_line(price, line)

        if line:
            r = re.search(regexp, line)
            main = float(r.group(1))
            if r.group(2):
                blue = float(r.group(2))
                return Price(main, blue)
            else:
                return Price(main)
        else:
            return None

    def get_property_from_line(self, line):
        regexp = "[-+]?\d+%?"
        name = None

        for prop in STONES.values():
            if prop in line:
                name = prop
                break

        r = re.search(regexp, line)
        if name and r:
            return Property(name, r.group())

        return None

    def get_store_owner(self, line):
        store = u"Лавка:"
        link = u"[i]"

        line = line.replace(link, '')
        return self.__get_croped_line(store, line)

    def get_stone_name(self, line):
        faceted = FACETED.lower()
        if faceted in line:
            return self.__get_rcroped_line(FACETED.lower(), line)
        else:
            return self.__get_rcroped_line(" ", line)

    def get_stone_mod(self, line):
        prop = self.get_property_from_line(line)
        if prop:
            return prop.value
        else:
            return None


class JewerlyParser(LineParser):
    def __init__(self, text, is_faceted=True):
        LineParser.__init__(self)
        self.__text = text
        self.__is_faceted = is_faceted

    def get_stones(self):
        stones = []

        name, mod, price, owner = None, None, None, None
        for line in self.__text.splitlines():
            if len(line.strip()) == 0:
                continue
            if not name:
                name = self.get_stone_name(line)
            if not owner:
                owner = self.get_store_owner(line)

            if name and owner:
                if not price:
                    price = self.get_price_from_line(line)
                if not mod and self.__is_faceted:
                    mod = self.get_property_from_line(line)
                    if mod:
                        mod = u'%s' % mod

            # print "%s | %s | %s | %s" % (name, mod , price, owner)

            if self.__is_faceted and name and mod and price and owner:
                stones.append(MarketStone(name, mod, price, owner))
                name, mod, price, owner = None, None, None, None
            elif not self.__is_faceted and name and price and owner:
                stones.append(MarketStone(name, None, price, owner))
                name, mod, price, owner = None, None, None, None

        return stones
