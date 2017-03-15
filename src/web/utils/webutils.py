from easyselenium.browser import Browser

TIMEOUT = 7
__BROWSER = None


def get_browser():
    global __BROWSER

    if not __BROWSER:
        try:
            # NOTE: LOGGER increases exec time
            __BROWSER = Browser('gc')
        except Exception as e:
            print(e)
            __BROWSER = Browser()

    return __BROWSER


def quit_browser():
    global __BROWSER

    if __BROWSER:
        __BROWSER.quit()
        __BROWSER = None


'''
TODO: remove
def find_element(element):
    browser = get_browser()
    by = element[0]
    value = element[1]
    return browser.find_element((by, value))

def find_elements(element):
    browser = get_browser()
    by = element[0]
    value = element[1]
    return browser.find_elements((by, value))

def __fix_element(element):
    if type(element) == tuple:
        element = find_element(element)
    
    return element

def execute_js(js_script):
    browser = get_browser()
    return browser.execute_js(js_script)

def wait_for_visible(element, msg=None, timeout=None):
    if not timeout:
        timeout = TIMEOUT
    
    if not msg:
        msg = u"Element '%s' is not visible for %s seconds" % (element, timeout)
    
    webbrowser_wait(lambda browser: is_visible(element), msg, timeout)

def wait_for_not_visible(element, timeout=None):
    if not timeout:
        timeout = TIMEOUT
    
    if type(element) == tuple:
        message = u"Element '%s' is visible for %s seconds" % (get_text(element), timeout)
    
    webbrowser_wait(lambda browser: not is_visible(element), message, timeout)

def wait_for_present(element, timeout=None):
    if not timeout:
        timeout = TIMEOUT
    
    message = u"Element {By: '%s', value: '%s'} is not presented for %s seconds" % (element[0], element[1], timeout)
    webbrowser_wait(lambda browser: is_present(element), message, timeout)

def wait_for_not_present(element, timeout=None):
    if not timeout:
        timeout = TIMEOUT
    
    message = u"Element {By: '%s', value: '%s'} is presented for %s seconds" % (element[0], element[1], timeout)
    webbrowser_wait(lambda browser: not is_present(element), message, timeout)

def is_visible(element):
    try:
        if type(element) == tuple:
            elements = find_elements(element)
            return elements and len(elements) > 0 and elements[0].is_displayed()
        else:
            return element.is_displayed()
    except WebDriverException:
        return False
        
def is_present(element):
    elements = find_elements(element)
    return len(elements) > 0

def save_screenshot(saving_dir=None, action=''):
    if not saving_dir:
        saving_dir = os.getenv('Temp') + u"/"
    
    path_to_file = os.path.abspath(saving_dir + get_timestamp() + action + u".png")
    
    print u"* Saving screenshot to '%s'" % path_to_file
    
    get_browser().save_screenshot(path_to_file)

def get_elements_count(element):
    return len(find_elements(element))
    
def get_random_value(_list, *val_to_skip):
    _tmp = list(_list)
    
    for skipped in val_to_skip:
        _tmp.remove(skipped)
    
    value = choice(_tmp)
    
    print u"* Random value is '%s'" % value
        
    return value

def get_timestamp():
    t = datetime.now().timetuple()
    timestamp = u"%d%02d%02d%02d%02d%02d" % (t[0], t[1], t[2], t[3], t[4], t[5])
    return timestamp

def switch_to_frame(element, to_print=True):
    browser = get_browser()
    
    if type(element) in [str, unicode]:
        msg =  u"* Switching to '%s' frame" % element
    else:
        element = __fix_element(element)
        
        attr = get_attribute(element, "name")
        if len(attr) > 0:
            msg = u"* Switching to '%s' frame" % attr
        else:
            msg = u"* Switching to '%s' frame" % get_text(element)
    
    if to_print:
        print msg
    
    browser.switch_to_frame(element)

def get_frame_elements():
    frames = find_elements((By.TAG_NAME, "frame"))
    frames += find_elements((By.TAG_NAME, "iframe"))
    
    return frames

def get_frame_names():
    names = [get_attribute(f, "name") for f in get_frame_elements()]
    
    return names

def switch_to_new_window(function, *args):
    browser = get_browser()
    initial_handles = browser._driver.window_handles
    function(*args)
    WebDriverWait(browser, 20).until(lambda browser: len(initial_handles) < len(browser._driver.window_handles))
    new_handles = [wh for wh in browser._driver.window_handles if wh not in initial_handles]
    browser._driver.switch_to_window(new_handles[0])
    try:
        print u"* Switching to '%s' window" % browser._driver.title
    except:
        print u"* Switching window"

def switch_to_default_content(to_print=True):
    if to_print:
        print u"* Switching to default content"
    get_browser().switch_to_default_content()
    
def close_current_window_and_focus_to_previous_one():
    browser = get_browser()
    handles = browser._driver.window_handles
    browser.close()
    browser._driver.switch_to_window(handles[-2])
    try:
        print u"* Switching to '%s' window" % browser._driver.title
    except:
        print u"* Switching window"

def wait_for_text_is_not_equal(element, text):
    wait_for_visible(element)
    element = __fix_element(element)
    
    msg = u"Text has not changed from '%s'" % text
    webbrowser_wait(lambda browser: get_text(element) != text, msg)

def wait_for_text_is_equal(element, text):
    wait_for_visible(element)
    element = __fix_element(element)
    msg = u"Text has not changed to '%s'" % text
    webbrowser_wait(lambda browser: get_text(element) == text, msg)

def wait_for_attribute_value_contains(element, attr, expected_value):
    wait_for_visible(element)
    element = __fix_element(element)
    
    msg = u"Webelement's attribute '%s'='%s' doesn't have '%s'" % (attr, element.get_attribute(attr), expected_value)
    webbrowser_wait(lambda browser: expected_value in element.get_attribute(attr), msg)

def get_number_from_string(pattern, text):
    first_text = search(pattern, text).group()
    return  search("\\d+", first_text).group()

def wait_for_value(js_script, value, msg=None):
    if not msg:
        msg = u"'%s' not equal to '%s'" % (js_script, value)
    
    webbrowser_wait(lambda browser: browser.execute_script(js_script) == value, msg)

def delete_all_cookies():
    get_browser().delete_all_cookies()

def accept_alert():
    get_browser().alert_accept()
    print u"* Click Accept/OK in alert box"

def dismiss_alert():
    get_browser().alert_dismiss()
    print u"* Click Dismiss/Cancel in alert box"
    
def refresh_page():
    get_browser().refresh_page()
        
def webbrowser_wait(function, msg='', timeout=None):
    if not timeout:
        timeout = TIMEOUT
    
    WebDriverWait(get_browser(), timeout).until(function, msg)

def get_text(element):
    wait_for_visible(element)
    element = __fix_element(element)
    return element.text

def click(element, to_print=True):
    wait_for_visible(element)
    if to_print:
        try:
            if get_text(element) != u"":
                print u"* Clicking at '%s'" % get_text(element)
            elif get_value(element)!= u"":
                print u"* Clicking at '%s'" % get_value(element)
            else:
                try:
                    webelement = find_element(element)
                    element_information = repr(element)
                    element_loc = webelement.location
                    print u"* Clicking at '%s'" % str(element_information) + str(element_loc)
                except:
                    print u"* Clicking at UNKNOWN BUTTON"
        except:
            try:
                webelement = find_element(element)
                element_information = repr(element)
                element_loc = webelement.location
                print u"* Clicking at '%s'" % str(element_information) + str(element_loc)
            except:
                print u"* Clicking at UNKNOWN BUTTON"
                
    element = __fix_element(element)
    element.click()

def get_attribute(element, attr):
    wait_for_visible(element)
    element = __fix_element(element)
    return element.get_attribute(attr)

def get_value(element):
    return get_attribute(element, u"value")

def send_keys(element, value, to_print=True):
    wait_for_visible(element)
    
    if to_print:
        print u"* Typing '%s'" % value
    
    element = __fix_element(element)
    
    element.clear()
    element.send_keys(value)
        
def get_selected_value_of_dropdown_list(element):
    element = __fix_element(element)
    
    return Select(element).first_selected_option.text

def select_value_from_dropdown_list(element, value):
    wait_for_visible(element)
    element = Select(__fix_element(element))
    
    print u"* Selecting '%s' from dropdown list" % value
    
    element.select_by_value(value)

def select_text_from_dropdown_list(element, text):
    wait_for_visible(element)
    element = Select(__fix_element(element))
    
    print u"* Selecting '%s' from dropdown list" % text
    
    element.select_by_visible_text(text)

def select_random_option_from_dropdownmenu(element, *val_to_skip):
    wait_for_visible(element)
    options = get_texts_from_dropdown_list(element)
    option_to_select = get_random_value(options, *val_to_skip)
    select_text_from_dropdown_list(element, option_to_select)

def set_checkbox(element, status):
    if get_attribute(element, u"type") == u"checkbox":
        if status == u"checked":
            if get_attribute(element, u"checked") == None:
                print u"* Checking the checkbox"
                click(element)
            else:
                print u"* Checkbox is already checked"
        elif status == u"unchecked":
            if get_attribute(element, u"checked") == u"true" or get_attribute(element, u"checked") == u"checked":
                print u"* Unchecking the checkbox"
                click(element)
            else:
                print u"* Checkbox is already unchecked"    
    else:
        print u"Element might be not a checkbox" 

def get_texts_from_dropdown_list(element):
    wait_for_visible(element)
    values = []
    element = __fix_element(element)
    
    for value in Select(element).options:
        values.append(get_text(value))
    return values

def get_values_from_dropdown_list(element):
    wait_for_visible(element)
    values = []
    element = __fix_element(element)
    
    for value in Select(element).options:
        values.append(get_value(value))
    return values


# MouseActions

    
def _get_actions():
    return ActionChains(get_browser())
        
def mouse_click_by_offset(element, xoffset, yoffset):
    actions = _get_actions()
    wait_for_visible(element)
    
    element = __fix_element(element)
        
    print u"* Click at '%s' by offset(%s,%s)" % (get_text(element), xoffset, yoffset)
    actions.move_to_element(element).move_by_offset(xoffset, yoffset).click().perform()
    
def mouse_over(element):
    mouse_over_by_offset(element, 0, 0)
    
def mouse_over_by_offset(element, xoffset, yoffset):
    actions = _get_actions()
    wait_for_visible(element)
    
    element = __fix_element(element)
    
    print u"* Mouse over '%s' by offset(%s,%s)" % (get_text(element), xoffset, yoffset)
    actions.move_to_element(element).move_by_offset(xoffset, yoffset).perform()
    
def mouse_right_click(element):
    actions = _get_actions()
    wait_for_visible(element)
    element = __fix_element(element)
    
    print u"* Right click at '%s'" % get_text(element)
    
    actions.context_click(element).perform()
    
def mouse_right_click_by_offset(element, xoffset, yoffset):
    actions = _get_actions()
    wait_for_visible(element)
    element = __fix_element(element)
    
    print u"* Right click at '%s' by offset(%s,%s)" % (get_text(element), xoffset, yoffset)
    
    actions.move_to_element(element).move_by_offset(xoffset, yoffset).context_click().perform()

def drag_and_drop(draggable, droppable):
    actions = _get_actions()
    wait_for_visible(draggable)
    
    if type(draggable) == tuple:
        draggable = find_element(draggable)
    if type(droppable) == tuple:
        droppable = find_element(droppable)    
        
    actions.drag_and_drop(draggable, droppable).perform()
'''
