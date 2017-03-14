# encoding=utf8

import pynotify
import time
from random import randint
from threading import Thread, Event
from wx._controls import TextCtrl, TE_MULTILINE, TE_READONLY, Button, \
    StaticBox, TE_DONTWRAP, CheckBox
from wx._core import BoxSizer, VERTICAL, HORIZONTAL, \
    EXPAND, StaticBoxSizer, EVT_BUTTON, EVT_CLOSE, \
    CallAfter, EVT_CHECKBOX
from wx._windows import Frame

from src.apeha.bot.settings import BotSettings
from src.web.utils.webutils import get_browser
from src.web.views.frames import ApehaMain, FrameAction
from src.web.views.market import MarketChat
from src.web.views.smithy import SmithyChat


class Notifier(Frame):
    __TITLE = u"Обзор собщений в чате"
    __SIZE = (700, 400)

    def __init__(self, parent, username, password):
        Frame.__init__(self, parent, size=self.__SIZE, title=self.__TITLE)

        bozer = BoxSizer(VERTICAL)
        self.SetSizer(bozer)
        self.event = Event()

        self.create_ui()
        self.Bind(EVT_CLOSE, self.__on_quit)
        self.settings = BotSettings()

        self.username = username
        self.password = password

    def create_ui(self):
        main_sizer = self.GetSizer()

        sizer = BoxSizer(HORIZONTAL)

        self.check_market = CheckBox(self, label=u"Поиск по рыноку")
        self.check_market.SetValue(True)
        self.Bind(EVT_CHECKBOX, self.__on_checkbox, self.check_market)
        sizer.Add(self.check_market, 0, EXPAND)

        self.check_smithy = CheckBox(self, label=u"Поиск по кузнице")
        self.check_smithy.SetValue(True)
        self.Bind(EVT_CHECKBOX, self.__on_checkbox, self.check_smithy)
        sizer.Add(self.check_smithy, 0, EXPAND)

        sizer.AddStretchSpacer(1)

        self.btn_stop = Button(self, label=u"Остановить поиск")
        self.btn_stop.Disable()
        self.Bind(EVT_BUTTON, self.__on_btn, self.btn_stop)
        sizer.Add(self.btn_stop, 0, EXPAND)

        self.btn_search = Button(self, label=u"Начать поиск")
        self.Bind(EVT_BUTTON, self.__on_btn, self.btn_search)
        sizer.Add(self.btn_search, 0, EXPAND)

        sizer.AddStretchSpacer(1)
        self.btn_quit = Button(self, label=u"Выйти")
        self.Bind(EVT_BUTTON, self.__on_btn, self.btn_quit)
        sizer.Add(self.btn_quit, 0, EXPAND)

        main_sizer.Add(sizer, 0, EXPAND)

        sbox = StaticBox(self, label=u"Сообщения чата:")
        sizer = StaticBoxSizer(sbox)
        self.text_area = TextCtrl(self, style=TE_MULTILINE | TE_READONLY | TE_DONTWRAP)
        sizer.Add(self.text_area, 1, EXPAND)

        main_sizer.Add(sizer, 1, EXPAND)

    def notify(self, text):
        CallAfter(self.text_area.AppendText, text)
        m_text = text[:6]
        message = text
        pynotify.init("My app")
        n = pynotify.Notification(m_text.encode("utf8"), message.encode("utf8"))
        n.set_timeout(5000)
        n.show()

    def __on_checkbox(self, e):
        if not self.check_market.IsChecked() and not self.check_smithy.IsChecked():
            self.btn_search.Disable()
        else:
            self.btn_search.Enable()

    def __on_btn(self, e):
        obj = e.GetEventObject()

        if obj == self.btn_search:
            self.check_market.Disable()
            self.check_smithy.Disable()
            self.text_area.Clear()
            self.btn_search.Disable()
            self.btn_stop.Enable()
            self.event.clear()
            get_browser()

            main = ApehaMain(self.settings)
            main.login(self.username, self.password)

            thread = Thread(target=self.search_and_notify)
            thread.setDaemon(True)
            thread.start()
        elif obj == self.btn_stop:
            self.check_market.Enable()
            self.check_smithy.Enable()
            self.btn_stop.Disable()
            self.event.set()
        elif obj == self.btn_quit:
            self.__on_quit(None)

    def search_and_notify(self):
        action = FrameAction(self.settings)
        mchat = MarketChat(self.settings)
        smithychat = SmithyChat(self.settings)

        timeout = 20  # in secs

        chats = []
        if self.check_market.IsChecked():
            chats.append(mchat)
        if self.check_smithy.IsChecked():
            chats.append(smithychat)

        def go_to(is_market):
            action._click_main_square()
            if is_market:
                action._click_market()
            else:
                action._click_smithy()

        if len(chats) == 1:
            go_to(chats[0] == mchat)

        while (not self.event.is_set()):
            for chat in chats:
                if len(chats) > 1:
                    action._click_main_square()
                    go_to(chat == mchat)

                messages = chat.get_messages()
                if messages:
                    for message in messages:
                        self.notify(message + "\n")

                t = randint(timeout / 2, timeout)
                for _ in range(0, t):
                    if self.event.is_set():
                        break
                    time.sleep(1)

        self.btn_search.Enable()
        self.btn_stop.Disable()

    def __on_quit(self, e):
        try:
            browser = get_browser()()
            if browser:
                browser.quit()
        except:
            pass
        finally:
            self.Destroy()
