#!/usr/bin/env python
# encoding=utf8
import os

from algorithms import credentials
from src.apeha.bot.settings import BotSettings

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in os.sys.path:
    os.sys.path.append(root)

from src.web.views.frames import ApehaMain
from src.web.views.smithy import Smithy
from src.web.utils.helper import safe_execute
from src.apeha.market.ui.stone_viewer import show_stones


def get_stones():
    settings = BotSettings()
    main = ApehaMain(settings)
    main.login(credentials.USERNAME, credentials.PASSWORD)
    
    smithy = Smithy(settings)
    stones = smithy.get_stones(30, True)
    smithy.print_stones(stones)
    show_stones(stones)


if __name__ == '__main__':
    safe_execute(get_stones)
