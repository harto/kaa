import re
from ast import List, Symbol, Value

class Reader(object):

    EOLIST = object()

    ATOM = re.compile(r'[^\s\(\)]+')
    INTEGER = re.compile(r'[+-]?[0-9]+')

    def __init__(self):
        self.list_depth = 0

    def read(self, chars):
        while True:
            if chars.eof():
                if self.list_depth > 0:
                    raise UnexpectedEofException()
                break
            c = chars.pop()
            if c.isspace():
                while chars.peek() and chars.peek().isspace():
                    chars.pop()
                continue
            elif c == ';':
                while chars.peek():
                    chars.pop()
                continue
            elif c == '(':
                yield self._read_list(chars)
            elif c == ')':
                if self.list_depth == 0:
                    raise UnbalancedDelimiterException(c)
                else:
                    yield self.EOLIST
                    break
            else:
                yield self._read_atom(c, chars)

    def _read_list(self, chars):
        l = List()
        self.list_depth += 1
        for obj in self.read(chars):
            if obj == self.EOLIST:
                break
            l.append(obj)
        self.list_depth -= 1
        return l

    def _read_atom(self, first_char, chars):
        token = first_char
        while chars.peek() and self.ATOM.match(chars.peek()):
            token += chars.pop()
        if self.INTEGER.match(token):
            return Value(int(token))
        else:
            return Symbol(token)

class UnbalancedDelimiterException(Exception): pass
class UnexpectedEofException(Exception): pass
