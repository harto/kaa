from kaa.reader import Reader


def read(s):
    "Convenience method for reading a single object from a string."
    return next(Reader().read_string(s))
