# encoding=utf8
import codecs
from unittest.case import TestCase
from src.apeha.market.text.parsers import LineParser
from src.apeha.market.parsers.jewelry_parser import JewerlyParser
from src.apeha.utils import unicode_str


class LineParserTest(TestCase):
    def test_price_simple(self):
        price = u"Цена: 30.00"
        price = LineParser().get_price_from_line(price)
        self.assertEqual(unicode_str(price), "30.00")
        self.assertEqual(price.main, 30.00)

    def test_price_complex(self):
        price = u"Цена: 30.00 + 0.99"
        price = LineParser().get_price_from_line(price)
        self.assertEqual(unicode_str(price), u"30.00 + 0.99")
        self.assertEqual(price.main, 30.00)
        self.assertEqual(price.blue, 0.99)
        
    def test_get_property(self):
        line = u"Удача: +7"
        prop = LineParser().get_property_from_line(line)
        self.assertEqual(line, unicode_str(prop))
        self.assertEqual(u"Удача", prop.name)
        self.assertEqual(u"+7", prop.value)
        
    def test_get_stone_mod(self):
        line = u"Удача: +7"
        mod = LineParser().get_stone_mod(line)
        self.assertEqual(u"+7",mod)

class JewerlyParserTest(TestCase):
    def test_simple_parser(self):
        text = u"""
Амазонит ограненный Лавка: [Hm] Вне Весомости 13 [i]
Цена: 30.00
Количество: 2
Удача: +7
        """
        parser = JewerlyParser(text)
        stone = parser.get_stones()[0]
        self.assertEqual(stone.name, u"Амазонит ограненный")
        self.assertEqual(stone.mod, u"Удача: +7")
        self.assertEqual(stone.owner, u"[Hm] Вне Весомости 13")
        self.assertEqual(unicode_str(stone.price), "30.00")
             
    def test_simple2_parser(self):
        text = u"""
Александрит ограненный Лавка: [Or] NazgulBD 13 [i]
Цена: 1.00 + 10.00
Количество: 9
Сила: +7
        """
        parser = JewerlyParser(text)
        stone = parser.get_stones()[0]
        self.assertEqual(stone.name, u"Александрит ограненный")
        self.assertEqual(stone.mod, u"Сила: +7")
        self.assertEqual(stone.owner, u"[Or] NazgulBD 13")
        self.assertEqual(unicode_str(stone.price), u"1.00 + 10.00")
        
    def test_parse(self):
        f = codecs.open('jewelry.txt', 'rb', 'utf8')
        lines = f.readlines()
        parser = JewerlyParser(u"".join(lines))
        stones = parser.get_stones()
        
        prices = []
        for stone in stones:
            prices.append(stone.price)
        
        prices = sorted(prices)
        self.assertEqual(unicode_str(prices[0]), "4.00")
        self.assertEqual(unicode_str(prices[-1]), "1.00 + 17.00")
        
        stone1 = stones[0]
        stone2 = stones[1]
        self.assertEqual( cmp(stone1, stone2), 1)

    def test_parse_unfaceted_simple(self):
        text = u"""Александрит Лавка: [Gn] SPQRCOR 11 [i]
Цена: 10.00
Количество: 1
"""
        text2 = u"""Александрит Лавка: [Hm] slava7 16 [i]
Цена: 1.00 + 2.00
Количество: 26
"""

        parser = JewerlyParser(text, False)
        stones = parser.get_stones()
        self.assertTrue(len(stones) > 0)
        stone = stones[0]
        self.assertEqual(stone.name, u"Александрит")
        self.assertEqual(unicode_str(stone.price), u"10.00")
        
        parser = JewerlyParser(text2, False)
        stones = parser.get_stones()
        self.assertTrue(len(stones) > 0)
        stone = stones[0]
        self.assertEqual(stone.name, u"Александрит")
        self.assertEqual(unicode_str(stone.price), u"1.00 + 2.00")

    def test_parse_unfaceted(self):
        text = u"""
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
        self.assertEqual(len(stones), 20)
