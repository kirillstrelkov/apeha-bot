from easelenium.browser import Browser

TIMEOUT = 7
__BROWSER = None


def get_browser(name="gc", headless=False):
    global __BROWSER

    if not __BROWSER:
        try:
            # NOTE: LOGGER increases exec time
            __BROWSER = Browser(name, headless=headless)
        except Exception as e:
            print(e)
            __BROWSER = Browser()

    return __BROWSER


def quit_browser():
    global __BROWSER

    if __BROWSER:
        __BROWSER.quit()
        __BROWSER = None
