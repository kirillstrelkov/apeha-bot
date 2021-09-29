from unittest.case import TestCase

from src.web.utils.webutils import get_browser, quit_browser


class BrowserTest(TestCase):
    def setUp(self):
        self.browser = get_browser(headless=False)

    def tearDown(self):
        try:
            quit_browser()
        finally:
            pass
