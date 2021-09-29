# encoding=utf8
from functools import total_ordering
from string import Template

from src.apeha.market.price import Price


@total_ordering
class Stone(object):
    def __init__(self, name, mod):
        self.name = name
        self.mod = mod

    def __eq__(self, other):
        return (self.name, self.mod) == (other.name, other.mod)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return f"{self.name} {self.mod}"

    def __lt__(self, other):
        return self.mod < other.mod


class MarketStone(Stone):
    def __init__(self, name, mod, price, owner):
        Stone.__init__(self, name, mod)
        assert type(price) == Price
        self.price = price
        self.owner = owner

    def __str__(self):
        template = """$name
Лавка: $owner
Цена: $price
"""

        tmp = Template(template)
        string = tmp.substitute(
            {
                "name": self.name,
                "owner": self.owner,
                "price": self.price,
            }
        )
        if self.mod:
            string += str(self.mod)

        return string

    def __eq__(self, other):
        return (self.name, self.mod, self.price) == (other.name, other.mod, other.price)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.price < other.price or self.mod < other.mod

    def __repr__(self):
        return Stone.__repr__(self) + f"{self.price} {self.owner}"
