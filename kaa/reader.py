import re

from kaa.core import empty, first, is_list, rest, List, Symbol
from kaa.string import read_str, UnterminatedString


EOLIST = object()
ATOM = re.compile(r'[^\s\(\)]+')
INTEGER = re.compile(r'[+-]?[0-9]+')


class Reader:
    def __init__(self):
        self.list_depth = 0

    def read_all(self, chars):
        while True:
            obj = self.read(chars)
            if obj is None:
                break
            yield obj

    def read(self, chars):  # pylint: disable=too-many-branches,too-many-return-statements
        if chars.eof():
            if self.list_depth > 0:
                raise EOF()
            return None
        c = chars.pop()
        if c.isspace():
            while chars.peek() and chars.peek().isspace():
                chars.pop()
            return self.read(chars)
        if c == ';':
            while chars.peek():
                chars.pop()
            return self.read(chars)
        if c == "'":
            return self._read_quote(chars)
        if c == '`':
            return self._read_quasiquote(chars)
        if c == '~':
            return self._read_unquote(chars)
        if c == '(':
            return self._read_list(chars)
        if c == ')':
            if self.list_depth == 0:
                raise UnbalancedDelimiter(
                    'unbalanced delimiter %s at %s' % (c, chars.source_meta()))
            return EOLIST
        if c == '"':
            return _read_string(chars)
        return _read_atom(c, chars)

    def _read_quote(self, chars):
        return List([Symbol('quote', {'source': chars.source_meta()}),
                     self.read(chars)])

    def _read_quasiquote(self, chars):
        return _process_quasiquote(self.read(chars))

    def _read_unquote(self, chars):
        if chars.peek() == '@':
            chars.pop()
            return List([Symbol('unquote-splice', {'source': chars.source_meta()}),
                         self.read(chars)])

        return List([Symbol('unquote', {'source': chars.source_meta()}),
                     self.read(chars)])

    def _read_list(self, chars):
        l = List(meta={'source': chars.source_meta()})
        self.list_depth += 1
        for obj in self.read_all(chars):
            if obj == EOLIST:
                break
            l.append(obj)
        self.list_depth -= 1
        return l


def _read_string(chars):
    try:
        return read_str(chars.unpop())
    except UnterminatedString as ex:
        raise EOF(ex)


def _read_atom(first_char, chars):
    meta = {'source': chars.source_meta()}
    token = first_char
    while chars.peek() and ATOM.match(chars.peek()):
        token += chars.pop()
    if INTEGER.match(token):
        return int(token)
    if token.startswith('py/'):
        return eval(token[3:]) # pylint: disable=eval-used
    return Symbol(token, meta)


class UnbalancedDelimiter(Exception):
    pass


class EOF(Exception):
    pass


# References:
#  - http://axisofeval.blogspot.com/2013/04/a-quasiquote-i-can-understand.html
#  - Clojure


def _process_quasiquote(obj):
    # `a -> 'a
    if not is_list(obj) or empty(obj):
        return List([Symbol('quote'), obj])
    # `~a -> a
    if first(obj) == Symbol('unquote'):
        return obj
    # `(a ~b ~@c) -> (concat (list 'a) (list b) c)
    return List([Symbol('concat')] +
                [_process_quasiquote_list_item(o) for o in obj])


def _process_quasiquote_list_item(obj):
    if first(obj) == Symbol('unquote'):
        return List([Symbol('list'), first(rest(obj))])
    if first(obj) == Symbol('unquote-splice'):
        return first(rest(obj))
    return List([Symbol('list'), _process_quasiquote(obj)])
