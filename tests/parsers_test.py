# encoding=utf8
import codecs
import os
from unittest.case import TestCase

from src.apeha.market.parsers import JewerlyParser, LineParser


class LineParserTest(TestCase):
    def test_price_simple(self):
        price = "Цена: 30.00"
        price = LineParser().get_price_from_line(price)
        assert str(price) == "30.00"
        assert price.main == 30.00

    def test_price_complex(self):
        price = "Цена: 30.00 + 0.99"
        price = LineParser().get_price_from_line(price)
        assert str(price), "30.00 + 0.99"
        assert price.main == 30.00
        assert price.blue == 0.99

    def test_get_property(self):
        line = "Удача: +7"
        prop = LineParser().get_property_from_line(line)
        assert line, str(prop)
        assert "Удача" == prop.name
        assert "+7" == prop.value

    def test_get_stone_mod(self):
        line = "Удача: +7"
        mod = LineParser().get_stone_mod(line)
        assert "+7" == mod


class JewerlyParserTest(TestCase):
    def test_simple_parser(self):
        text = """
Амазонит ограненный Лавка: [Hm] Вне Весомости 13 [i]
Цена: 30.00
Количество: 2
Удача: +7
        """
        parser = JewerlyParser(text)
        stone = parser.get_stones()[0]
        assert stone.name == "Амазонит ограненный"
        assert stone.mod == "Удача: +7"
        assert stone.owner == "[Hm] Вне Весомости 13"
        assert str(stone.price) == "30.00"

    def test_simple2_parser(self):
        text = """
Александрит ограненный Лавка: [Or] NazgulBD 13 [i]
Цена: 1.00 + 10.00
Количество: 9
Сила: +7
        """
        parser = JewerlyParser(text)
        stone = parser.get_stones()[0]
        assert stone.name == "Александрит ограненный"
        assert stone.mod == "Сила: +7"
        assert stone.owner == "[Or] NazgulBD 13"
        assert str(stone.price) == "1.00 + 10.00"

    def test_parse(self):
        f = codecs.open(
            os.path.join(os.path.dirname(__file__), "jewelry.txt"), "rb", "utf8"
        )
        lines = f.readlines()
        parser = JewerlyParser("".join(lines))
        stones = parser.get_stones()

        prices = []
        for stone in stones:
            prices.append(stone.price)

        prices = sorted(prices)
        assert str(prices[0]) == "4.00"
        assert str(prices[-1]) == "1.00 + 17.00"

        stone1 = stones[0]
        stone2 = stones[1]
        assert stone1 > stone2

    def test_parse_unfaceted_simple(self):
        text = """Александрит Лавка: [Gn] SPQRCOR 11 [i]
Цена: 10.00
Количество: 1
"""
        text2 = """Александрит Лавка: [Hm] slava7 16 [i]
Цена: 1.00 + 2.00
Количество: 26
"""

        parser = JewerlyParser(text, False)
        stones = parser.get_stones()
        assert len(stones) > 0
        stone = stones[0]
        assert stone.name == "Александрит"
        assert str(stone.price) == "10.00"

        parser = JewerlyParser(text2, False)
        stones = parser.get_stones()
        assert len(stones) > 0
        stone = stones[0]
        assert stone.name == "Александрит"
        assert str(stone.price) == "1.00 + 2.00"

    def test_parse_unfaceted(self):
        text = """
Александрит Лавка: [Gn] SPQRCOR 11 [i]
Цена: 10.00
Количество: 1

Александрит Лавка: [Or] ninzza 12 [i]
Цена: 50.00
Количество: 4

Александрит Лавка: [El] канапляшка 16 [i]
Цена: 20.00
Количество: 23

Александрит Лавка: [Hm] MC555 16 [i]
Цена: 35.00
Количество: 2

Александрит Лавка: [Gn] _ЮЛЯШКА_ 12 [i]
Цена: 10.00
Количество: 8

Александрит Лавка: [Hm] AlexeyMG1 13 [i]
Цена: 20.00
Количество: 1

Александрит Лавка: [Hm] Swisstex 14 [i]
Цена: 8.00
Количество: 1

Александрит Лавка: [Hm] Caember 12 [i]
Цена: 8.00
Количество: 1

Александрит Лавка: [Gn] Федот 16 [i]
Цена: 1.00 + 2.00
Количество: 2

Александрит Лавка: [Hm] Swisstex 14 [i]
Цена: 15.00
Количество: 1

Александрит Лавка: [Or] RK 48 11 [i]
Цена: 13.00
Количество: 1

Александрит Лавка: [Hm] Swisstex 14 [i]
Цена: 10.00
Количество: 1

Александрит Лавка: [Gn] _ЮЛЯШКА_ 12 [i]
Цена: 12.00
Количество: 1

Александрит Лавка: [El] superdevochka 13 [i]
Цена: 7.00
Количество: 1

Александрит Лавка: [El] Ustasa 11 [i]
Цена: 10.00
Количество: 1

Александрит Лавка: [Or] lusorGiNN 11 [i]
Цена: 50.00
Количество: 2

Александрит Лавка: [Hm] forshmak 13 [i]
Цена: 11.00
Количество: 2

Александрит Лавка: [Gn] +Дредноут+ 12 [i]
Цена: 10.00
Количество: 19

Александрит Лавка: [Hm] slava7 16 [i]
Цена: 1.00 + 2.00
Количество: 26

Александрит Лавка: [El] АМ 16 [i]
Цена: 1.00 + 2.00
Количество: 12
"""

        parser = JewerlyParser(text, False)
        stones = parser.get_stones()
        assert len(stones) == 20
