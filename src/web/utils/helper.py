import traceback

from src.web.utils.webutils import get_browser, quit_browser


def safe_execute(function):
    value = None
    browser = get_browser()

    try:
        if not browser:
            browser = get_browser()

        function()
        value = True
    except:
        if browser:
            browser.save_screenshot()
        print traceback.format_exc()
        value = False
    finally:
        if browser:
            quit_browser()

    return value
