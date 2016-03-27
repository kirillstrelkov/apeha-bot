import re
import traceback

def get_number_from_text(text):
    m = re.search("\d+", text)
    if m:
        return int(m.group())
    else:
        return None

def print_exception():
    print traceback.format_exc()