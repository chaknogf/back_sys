import re


def trim_str(func):
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if value:
            value = re.sub(r'\s+', ' ', value.strip()).upper()
        return value
    return wrapper