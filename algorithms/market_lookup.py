#!/usr/bin/env python
import os

from algorithms import credentials
from src.web.utils.helper import safe_execute

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in os.sys.path:
    os.sys.path.append(root)

from src.ui.market_notifier import Notifier
from wx._core import App


def run():
    app = App(False)
    frame = Notifier(None, credentials.USERNAME, credentials.PASSWORD)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    safe_execute(run)
