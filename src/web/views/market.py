# encoding=utf8

from src.web.views.frames import FrameAction, FrameChat


class MarketAction(FrameAction):
    def __init__(self, settings):
        FrameAction.__init__(self, settings)


class MarketChat(FrameChat):
    def __init__(self, settings):
        FrameChat.__init__(self, settings)

    def is_message(self, msg):
        msg = msg.lower()
        sell0 = u"(мод" in msg
        sell1 = u"продам" in msg and u"мод" in msg
        sell2 = u"подкладка" not in msg
        if (sell0 or sell1) and sell2:
            return True
        else:
            return False

    def get_messages(self):
        return FrameChat.get_messages(self, self.is_message)
