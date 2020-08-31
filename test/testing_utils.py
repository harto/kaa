from kaa.ns import Namespace
from kaa.reader import Reader


def read(s):
    "Convenience method for reading a single object from a string."
    return next(Reader(Namespace('testing')).read_string(s))
