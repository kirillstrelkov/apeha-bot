from unittest.case import TestCase
from src.apeha.bot.settings import BotSettings, save_settings, get_settings
import pickle
import tempfile
import os


class SettingsTest(TestCase):
    def __assert_setting_objs(self, obj1, obj2):
        self.assertEqual(obj1.default_tactics, obj2.default_tactics)
        # self.assertEqual(obj1.fighting_settings, obj2.fighting_settings)
        # self.assertEqual(obj1.timeouts, obj2.timeouts)
        self.assertEqual(obj1.rating, obj2.rating)
        self.assertEqual(obj1.item_ids, obj2.item_ids)

    def test_pickle_unpickle_settings(self):
        obj1 = BotSettings()
        pickled_string = pickle.dumps(obj1)
        obj2 = pickle.loads(pickled_string)
        self.__assert_setting_objs(obj1, obj2)

    def test_save_get_settings_from_local(self):
        path = os.path.join(tempfile.gettempdir(), '.settingsapehapy')
        settings = BotSettings()
        save_settings(settings, path)
        settings2 = get_settings(path)
        self.__assert_setting_objs(settings, settings2)

    def test_save_get_settings_from_local_default_path(self):
        settings = BotSettings()
        save_settings(settings)
        settings2 = get_settings()
        self.__assert_setting_objs(settings, settings2)
