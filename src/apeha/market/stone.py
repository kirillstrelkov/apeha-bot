# encoding=utf8
from string import Template

from src.apeha.market.price import Price
from src.apeha.utils import unicode_str


class Stone(object):
    def __init__(self, name, mod):
        self.name = name
        self.mod = mod

    def __cmp__(self, other):
        comp = cmp(self.mod, other.mod)

        if comp == 0:
            comp = cmp(self.name, other.name)

        return comp


class MarketStone(Stone):
    def __init__(self, name, mod, price, owner):
        Stone.__init__(self, name, mod)
        assert type(price) == Price
        self.price = price
        self.owner = owner

    def __str__(self):
        template = u"""$name
Лавка: $owner
Цена: $price
"""

        tmp = Template(template)
        string = tmp.substitute(
            {"name": self.name,
             "owner": self.owner,
             "price": self.price,
             }
        )
        if self.mod:
            string += unicode_str(self.mod)

        return string

    def __cmp__(self, other):
        comp = Stone.__cmp__(self, other)

        if comp == 0:
            comp = cmp(self.price, other.price)
            if comp == 0:
                comp = cmp(self.price, other.price)

        return comp
