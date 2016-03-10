from kaa import string

def format(obj):
    if isinstance(obj, str):
        return string.format(obj)
    return str(obj)
