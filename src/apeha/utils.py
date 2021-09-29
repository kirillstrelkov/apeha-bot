import re
import traceback


class ApehaRegExp(object):
    NICKNAME_HP_ENDING = re.compile(r"\s*\[\d+/?\d*\]$")
    NICKNAME_RACE_START = re.compile(r"^[\w]{2}\s+")
    FLOAT = re.compile(r"\d+\.\d+")
    NUMBER = re.compile(r"\d+")


def get_number_from_text(text):
    m = re.search(ApehaRegExp.NUMBER, text)
    if m:
        return int(m.group())
    else:
        return None


def get_float_from_text(text):
    m = re.search(ApehaRegExp.FLOAT, text)
    if m:
        return float(m.group())
    else:
        return None


def print_exception():
    print(traceback.format_exc())


