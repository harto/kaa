from kaa import string
from kaa.core import empty, first, is_list, rest, List, Symbol
import re

class Reader(object):

    EOLIST = object()

    ATOM = re.compile(r'[^\s\(\)]+')
    INTEGER = re.compile(r'[+-]?[0-9]+')

    def __init__(self):
        self.list_depth = 0

    def read_all(self, chars):
        while True:
            obj = self.read(chars)
            if obj is None:
                raise StopIteration
            yield obj

    def read(self, chars):
        if chars.eof():
            if self.list_depth > 0:
                raise EOF()
            return None
        c = chars.pop()
        if c.isspace():
            while chars.peek() and chars.peek().isspace(): chars.pop()
            return self.read(chars)
        elif c == ';':
            while chars.peek(): chars.pop()
            return self.read(chars)
        elif c == "'":
            return self._read_quote(chars)
        elif c == '`':
            return self._read_quasiquote(chars)
        elif c == '~':
            return self._read_unquote(chars)
        elif c == '(':
            return self._read_list(chars)
        elif c == ')':
            if self.list_depth == 0:
                raise UnbalancedDelimiter(
                    'unbalanced delimiter %s at %s' % (c, chars.source_meta()))
            else:
                return self.EOLIST
        elif c == '"':
            return self._read_string(chars)
        else:
            return self._read_atom(c, chars)

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
        else:
            return List([Symbol('unquote', {'source': chars.source_meta()}),
                         self.read(chars)])

    def _read_list(self, chars):
        L = List()
        L.meta = {'source': chars.source_meta()}
        self.list_depth += 1
        for obj in self.read_all(chars):
            if obj == self.EOLIST:
                break
            L.append(obj)
        self.list_depth -= 1
        return L

    def _read_string(self, chars):
        try:
            return string.read(chars.unpop())
        except string.UnterminatedStringException as e:
            raise EOF(e)

    def _read_atom(self, first_char, chars):
        meta = {'source': chars.source_meta()}
        token = first_char
        while chars.peek() and self.ATOM.match(chars.peek()):
            token += chars.pop()
        if self.INTEGER.match(token):
            return int(token)
        elif token.startswith('py/'):
            return eval(token[3:])
        else:
            return Symbol(token, meta)

class UnbalancedDelimiter(Exception): pass
class EOF(Exception): pass

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
    elif first(obj) == Symbol('unquote-splice'):
        return first(rest(obj))
    else:
        return List([Symbol('list'), _process_quasiquote(obj)])
