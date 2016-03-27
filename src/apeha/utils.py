import re
import traceback


def get_number_from_text(text):
    m = re.search("\d+", text)
    if m:
        return int(m.group())
    else:
        return None


def get_float_from_text(text):
    m = re.search("\d+\.\d+", text)
    if m:
        return float(m.group())
    else:
        return None


def print_exception():
    print traceback.format_exc()


def unicode_str(string):
    return u"%s" % string