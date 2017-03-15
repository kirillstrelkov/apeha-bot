#!/usr/bin/env python
# encoding=utf8

import os
import sys
from threading import Thread


root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", '..', '..'))
if root not in os.sys.path:
    os.sys.path.append(root)
os.sys.path.append(os.path.abspath(os.curdir))

from wx._core import App, BoxSizer, VERTICAL, HORIZONTAL, ALL, EXPAND, \
    StaticBoxSizer, EVT_CHECKBOX, CB_READONLY, \
    CallAfter, EVT_BUTTON
from wx._windows import Frame
from wx._controls import StaticText, TextCtrl, StaticBox, CheckBox, TE_PASSWORD, \
    ComboBox, TE_READONLY, TE_MULTILINE, Button, TE_DONTWRAP

from src.web.utils.helper import safe_execute
from src.web.utils.webutils import quit_browser


from src.apeha.utils import unicode_str
from src.apeha.bot.bot import ApehaBot
from src.apeha.bot.settings import get_settings, Tactics, ClonePlacement


class RedirectText(object):
    def __init__(self, textctrl):
        self.out = textctrl

    def write(self, string):
        CallAfter(self.out.AppendText, string)


class ApehaBotUI(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.settings = get_settings()

        self.SetSizeWH(700, 500)
        self.SetTitle(u"АРЕНА бот")
        self.SetSizer(BoxSizer(VERTICAL))
        self.__create_ui()
        redir = RedirectText(self.output)
        sys.stdout = redir
        sys.stderr = redir
        self.apeha_bot = None
        self.running_thread = None

    def __create_ui(self):
        sizer = self.GetSizer()

        hbox = BoxSizer(HORIZONTAL)
        lname = StaticText(self)
        lname.SetLabel(u"Ник:")
        self.txt_nick = TextCtrl(self)
        hbox.Add(lname, 1, flag=ALL, border=4)
        hbox.Add(self.txt_nick, 2)
        sizer.Add(hbox, 0, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        lname = StaticText(self)
        lname.SetLabel(u"Пароль:")
        self.txt_pwd = TextCtrl(self, style=TE_PASSWORD)
        hbox.Add(lname, 1, flag=ALL, border=4)
        hbox.Add(self.txt_pwd, 2)
        sizer.Add(hbox, 0, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        label = StaticText(self)
        label.SetLabel(u"Уровень астрала:")
        self.cb_atral_level = ComboBox(self, style=CB_READONLY)
        for level in self.settings.fighting_settings.ASTRAL_LEVELS:
            self.cb_atral_level.Append(unicode_str(level))
        self.cb_atral_level.Select(
            self.settings.fighting_settings.ASTRAL_LEVELS.index(self.settings.default_astral_level))
        hbox.Add(label, 1, flag=ALL, border=4)
        hbox.Add(self.cb_atral_level, 2)
        sizer.Add(hbox, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        label = StaticText(self)
        label.SetLabel(u"Тактика клонов:")
        self.cb_tactics = ComboBox(self, style=CB_READONLY)
        for tactic in Tactics.ALL:
            self.cb_tactics.Append(tactic)
        # setting default tactics:
        self.cb_tactics.Select(Tactics.ALL.index(self.settings.default_tactics))
        hbox.Add(label, 1, flag=ALL, border=4)
        hbox.Add(self.cb_tactics, 2)
        sizer.Add(hbox, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        label = StaticText(self)
        label.SetLabel(u"Ставить клонов:")
        self.cb_placement = ComboBox(self, style=CB_READONLY)
        for value in ClonePlacement.ALL:
            self.cb_placement.Append(value)
        # setting default placement:
        self.cb_placement.Select(ClonePlacement.ALL.index(self.settings.clone_placement))
        hbox.Add(label, 1, flag=ALL, border=4)
        hbox.Add(self.cb_placement, 2)
        sizer.Add(hbox, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        lname = StaticText(self)
        lname.SetLabel(u"Не заходить в заявки с игроками:")
        self.txt_bad_players = TextCtrl(self)
        hbox.Add(lname, 1, flag=ALL, border=4)
        hbox.Add(self.txt_bad_players, 2)
        self.txt_bad_players.SetValue(u", ".join(self.settings.fighting_settings.UNWANTED_PLAYERS))
        sizer.Add(hbox, 0, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        self.cb_save_items = CheckBox(self)
        self.cb_save_items.SetLabel(u"Надеть сохраненные вещи")
        self.cb_save_items.SetValue(True)
        hbox.Add(self.cb_save_items)
        sizer.Add(hbox, 0, flag=EXPAND)

        hbox = BoxSizer(HORIZONTAL)
        self.cb_my_tactics = CheckBox(self)
        self.cb_my_tactics.SetLabel(u"Ставить блоки рэндомно")
        hbox.Add(self.cb_my_tactics)
        sizer.Add(hbox, 0, flag=EXPAND)
        self.Bind(EVT_CHECKBOX, self.__on_cb_tactics, self.cb_my_tactics)
        self.cb_my_tactics.SetValue(True)

        box = StaticBox(self)
        box.SetLabel(u"Блоки")
        sbs = StaticBoxSizer(box, VERTICAL)
        hbox = BoxSizer(HORIZONTAL)
        hbox.AddStretchSpacer()
        self.cb00 = CheckBox(self)
        hbox.Add(self.cb00)
        self.cb10 = CheckBox(self)
        hbox.Add(self.cb10)
        hbox.AddStretchSpacer()
        sbs.Add(hbox, flag=EXPAND)
        sbs.AddSpacer(10)

        hbox = BoxSizer(HORIZONTAL)
        self.cb01 = CheckBox(self)
        hbox.Add(self.cb01)
        self.cb11 = CheckBox(self)
        hbox.Add(self.cb11)
        hbox.AddSpacer(10)
        self.cb02 = CheckBox(self)
        hbox.Add(self.cb02)
        self.cb12 = CheckBox(self)
        hbox.Add(self.cb12)
        hbox.AddSpacer(10)
        self.cb03 = CheckBox(self)
        hbox.Add(self.cb03)
        self.cb13 = CheckBox(self)
        hbox.Add(self.cb13)
        sbs.Add(hbox, flag=EXPAND)
        sbs.AddSpacer(10)

        hbox = BoxSizer(HORIZONTAL)
        hbox.AddStretchSpacer()
        self.cb04 = CheckBox(self)
        hbox.Add(self.cb04)
        self.cb14 = CheckBox(self)
        hbox.Add(self.cb14)
        hbox.AddStretchSpacer()
        sbs.Add(hbox, flag=EXPAND)
        sizer.Add(sbs, 0)

        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb00)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb01)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb02)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb03)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb04)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb10)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb11)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb12)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb13)
        self.Bind(EVT_CHECKBOX, self.__on_cb, self.cb14)

        #         sizer.AddStretchSpacer()

        hbox = BoxSizer(HORIZONTAL)
        self.btn_stop_and_quit = Button(self)
        self.btn_stop_and_quit.SetLabel(u"Остановить бота и закрыть браузер")
        self.btn_stop_and_quit.Disable()
        self.Bind(EVT_BUTTON, self.__on_stop_and_quit, self.btn_stop_and_quit)
        hbox.Add(self.btn_stop_and_quit, 2)
        #         self.btn_stop = Button(self)
        #         self.btn_stop.SetLabel(u"Остановить бота")
        #         hbox.Add(self.btn_stop, 1)
        hbox.AddStretchSpacer()
        self.btn_start = Button(self)
        self.btn_start.SetLabel(u"Запустить бота")
        hbox.Add(self.btn_start, 2)
        self.Bind(EVT_BUTTON, self.__on_run_bot, self.btn_start)
        sizer.Add(hbox, flag=EXPAND)

        box = StaticBox(self)
        box.SetLabel(u"Информация")
        sbs = StaticBoxSizer(box, VERTICAL)
        self.output = TextCtrl(self, style=TE_READONLY | TE_MULTILINE | TE_DONTWRAP)
        sbs.Add(self.output, 1, flag=EXPAND)
        sizer.Add(sbs, 1, flag=EXPAND)

        self.__cb_disable()

    def __disable_fields(self):
        self.txt_nick.Disable()
        self.txt_pwd.Disable()
        self.cb_atral_level.Disable()
        self.cb_my_tactics.Disable()
        self.cb_tactics.Disable()
        self.cb_placement.Disable()
        self.__cb_disable()
        self.txt_bad_players.Disable()

    def __enable_fields(self):
        self.txt_nick.Enable()
        self.txt_pwd.Enable()
        self.cb_atral_level.Enable()
        self.cb_my_tactics.Enable()
        self.cb_tactics.Enable()
        self.cb_placement.Enable()
        self.txt_bad_players.Enable()
        if not self.cb_my_tactics.IsChecked():
            self.__cb_enable()

    def __on_run_bot(self, e):
        username = self.txt_nick.GetValue()
        password = self.txt_pwd.GetValue()
        astral_level = int(self.cb_atral_level.GetValue())
        block_ids = self.__get_block_ids()
        clone_tactics = self.cb_tactics.GetValue()
        clone_placement = self.cb_placement.GetValue()
        bad_players = [p.strip() for p in self.txt_bad_players.GetValue().split(u', ')]

        if self.__is_correct_values(username, password, astral_level, block_ids):
            self.settings.default_astral_level = astral_level
            self.settings.default_tactics = clone_tactics
            self.settings.clone_placement = clone_placement
            self.settings.fighting_settings.UNWANTED_PLAYERS = bad_players

            def cmd():
                self.apeha_bot = ApehaBot(self.settings, use_saved_ids_from_settings=self.cb_save_items.GetValue())
                self.apeha_bot.run(username, password, astral_level, block_ids)

                self.apeha_bot.stop_event.clear()

            self.running_thread = Thread(target=safe_execute, args=(cmd,))
            self.running_thread.setDaemon(True)
            self.running_thread.start()
            self.btn_start.Disable()
            self.btn_stop_and_quit.Enable()
            self.__disable_fields()
            self.output.Clear()

    def __get_block_ids(self):
        cbs_left = [self.cb00, self.cb01, self.cb02, self.cb03, self.cb04]
        cbs_right = [self.cb10, self.cb11, self.cb12, self.cb13, self.cb14]

        cbs_and_ids = {
            self.cb00: "00",
            self.cb01: "01",
            self.cb02: "02",
            self.cb03: "03",
            self.cb04: "04",
            self.cb10: "10",
            self.cb11: "11",
            self.cb12: "12",
            self.cb13: "13",
            self.cb14: "14"
        }
        ids = []
        for cb in cbs_left + cbs_right:
            if cb.IsChecked():
                ids.append(cbs_and_ids[cb])

        if len(ids) == 4:
            return ids
        else:
            return None

    def __is_correct_values(self, username, password, astral_level, block_ids):
        if not block_ids:
            ids_correct = self.cb_my_tactics.IsChecked() == True
        else:
            ids_correct = self.cb_my_tactics.IsChecked() == False

        return len(username) > 0 \
               and len(password) > 0 \
               and type(astral_level) == int \
               and ids_correct

    def __on_stop_and_quit(self, e):
        if self.apeha_bot.stop_event:
            self.apeha_bot.stop_event.set()

        def wait_for_thread_ends():
            while self.running_thread.is_alive():
                pass
            self.btn_start.Enable()
            self.__enable_fields()
            quit_browser()

        self.btn_stop_and_quit.Disable()
        wait_thread = Thread(target=wait_for_thread_ends)
        wait_thread.setDaemon(True)
        wait_thread.start()

    def __on_cb_tactics(self, e):
        if self.cb_my_tactics.IsChecked():
            self.__cb_disable()
        else:
            self.__cb_enable()

    def __cb_disable(self):
        cbs_left = [self.cb00, self.cb01, self.cb02, self.cb03, self.cb04]
        cbs_right = [self.cb10, self.cb11, self.cb12, self.cb13, self.cb14]

        for cb in cbs_left + cbs_right:
            cb.Disable()

    def __cb_enable(self):
        cbs_left = [self.cb00, self.cb01, self.cb02, self.cb03, self.cb04]
        cbs_right = [self.cb10, self.cb11, self.cb12, self.cb13, self.cb14]

        for cb in cbs_left + cbs_right:
            cb.Enable()

    def __on_cb(self, e):
        cbs_left = [self.cb00, self.cb01, self.cb02, self.cb03, self.cb04]
        cbs_right = [self.cb10, self.cb11, self.cb12, self.cb13, self.cb14]

        def reset(cbs):
            for cb in cbs:
                cb.SetValue(False)

        def get_checked(cbs):
            i = 0
            for cb in cbs:
                if cb.IsChecked():
                    i += 1
            return i

        obj = e.GetEventObject()
        is_left = obj in cbs_left

        if is_left:
            checked = get_checked(cbs_left)
        else:
            checked = get_checked(cbs_right)

        if obj.IsChecked() and checked > 2:
            if is_left:
                reset(cbs_left)
            else:
                reset(cbs_right)

            obj.SetValue(True)


if __name__ == '__main__':
    app = App(False)
    frame = ApehaBotUI(None)
    frame.Show()
    app.MainLoop()

    # увеличить скорость парсинга поля 8х8
    # выбор боя выбирать - на 1:00, 0:30 -для алмазных
    # сделать один																																											 exe файл
    # если на стули - встать
