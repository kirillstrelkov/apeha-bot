# encoding=utf8

from unittest.case import TestCase

from src.apeha.bot.settings import BotSettings
from src.web.views.smithy import SmithyChat


class SmithyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.smithy = SmithyChat(BotSettings())

    @classmethod
    def tearDownClass(cls):
        cls.smithy.browser.quit()

    def test_chatlog1(self):
        log = u"""16:52  ДЕРБИ_: Свободный кузнец +7/+35 % Выполню СРОЧНЫЙ ЗАКАЗ! :hello:
16:52  drugs666: :znaika:вставлю сейчас +7/+35% за низкие серые цены :rupor:принимаю не срочные заказы
16:54  Mahaon77: :rupor: Принимаю заказы на вставку +7/ +35%. :smash:
16:57  *БЫЧАРА*: свободный кузнец 35/7 воткну ща, на опт скидки, низкие цены :super:
16:57  -Злодей-: :rupor:Продам неогран! все выставленно в гранилке!Налоги с меня:bgtup:
17:03  *Dimasik*: :bigok1::glyuk:СвОбОдНыЙ КуЗнЕц вставка +7/±35 , прямо Сейчас :)))) в приват)):smash:
17:16  Мститель-: :bukazoid: Продаю НЕОГРАН с гранилки. Быстрая ВСТАВКА камней 7/35!
17:17  NeoGameUA: :rupor: свободный кузнец 7/±35 серые сотки ,вставка сразу. В приват!
17:21  Dima42: работаю сурово на +7/±35. (в приват!). все камни в наличии... могу сделать вещи на заказ
17:28  zloba: :znaika: вкузнечиваю камни на 15/75% :znaika:
17:30  Луну под Кожу: 7|35? Вставка сразу! :jazzman:
17:32  iriskakiskis: Свободный кузнец +7/±35% :smash:
17:32  SAIshnik: вставлю 7/+35
17:44  Mahaon77: :rupor: Принимаю заказы на вставку +7/ +35%. :smash:
17:45  ~Serega~: кто прставит пирит +75? срочно:rupor::rupor:
18:02  *БЫЧАРА*: свободный кузнец 35/7 воткну ща, на опт скидки, низкие цены :super:
18:06  ~Serega~: а что на +75 моды никто не делает чтоль?:sad2:
18:06  Хам Трамвайный: 7/35% свободный кузнец))
18:13  *БЫЧАРА*: свободный кузнец 35/7 воткну ща, на опт скидки, низкие цены :super:
18:14  iriskakiskis: Свободный кузнец +7/±35% :smash:
18:26  *БЫЧАРА*: свободный кузнец 35/7 воткну ща, на опт скидки, низкие цены :super:
18:52  *Dimasik*: :evilking:СвОбОдНыЙ КуЗнЕц вставка +7/±35 , прямо Сейчас все камни в наличии :)))) в приват))
18:52  *БЫЧАРА*: свободный кузнец 35/7 воткну ща, на опт скидки, низкие цены :super:
18:52  _SPAM_: на +7 силы???кто?
19:00  FANTOM bel: to [Lord Michael] как для новичка , то цены :67:
19:06  -ЁЖИК-: кузнец 7/35 , вставка сразу, в приват, оптовикам скидки- больше ставишь, меньше платишь
19:14  Мститель-: :bukazoid: Продаю НЕОГРАН с гранилки. Быстрая ВСТАВКА камней 7/35!
19:24  Ангел Чарли: свободный кузнец 7-35 все камни в наличии
20:00  -ЁЖИК-: кузнец 7/35 , вставка сразу, в приват, оптовикам скидки- больше ставишь, меньше платишь
20:04  iriskakiskis: Свободный кузнец +7/±35% :smash:
20:16  zloba: :znaika: вкузнечиваю камни на 15/75% :znaika:
20:33  **Wolf**: -75 крита или удачи может кто сделать? В приват
20:41  zloba: :znaika: вкузнечиваю камни на 15/75% :znaika:
20:46  Хам Трамвайный: 7/35% свободный кузнец))"""
        for line in log.splitlines():
#             print smithy.is_smithy_message(line), line
            if "_SPAM_" in line or "FANTOM bel" in line:
                self.assertTrue(self.smithy.is_message(line))
            else:
                self.assertFalse(self.smithy.is_message(line))

    def test_chatlog(self):
        t1 = u"20:33  **Wolf**: -75 крита или удачи может кто сделать? В приват"
        self.assertFalse(self.smithy.is_message(t1))
        
        t1 = u"20:33  7**Wolf**: -75 крита или удачи может кто сделать? В приват"
        self.assertFalse(self.smithy.is_message(t1))
    
    def test_chatlog2(self):
        t = u"21:46  RoxYy: :rupor:+7 сила кто поставит"
        self.assertTrue(self.smithy.is_message(t))
