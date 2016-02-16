import re
from ast import List, Symbol, Value

class CharStream(object):

    def __init__(self, s):
        self.s = s
        self.col = 0

    def eof(self):
        return self.col >= len(self.s)

    def peek(self):
        if self.eof():
            return None
        else:
            return self.s[self.col]

    def pop(self):
        c = self.peek()
        if not c:
            raise Exception('nothing left to pop')
        self.col += 1
        return c

    def unpop(self, _):
        self.col -= 1
        if self.col < 0:
            raise Exception('unpopped too hard')


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
                    raise Exception('unexpected end of input')
                break

            c = chars.pop()

            if c.isspace():
                while chars.peek() and chars.peek().isspace():
                    chars.pop()
                continue

            elif c == '(':
                yield self.read_list(chars)

            elif c == ')':
                if self.list_depth == 0:
                    raise Exception('unexpected closing parenthesis')
                else:
                    yield self.EOLIST
                    break

            else:
                chars.unpop(c)
                yield self.read_atom(chars)

    def read_list(self, chars):
        l = List()
        self.list_depth += 1
        for obj in self.read(chars):
            if obj == self.EOLIST:
                break
            l.append(obj)
        self.list_depth -= 1
        return l

    def read_atom(self, chars):
        token = ''
        while self.ATOM.match(chars.peek()):
            token += chars.pop()
        if self.INTEGER.match(token):
            return Value(int(token))
        else:
            return Symbol(token)


def read(s):
    chars = CharStream(s)
    reader = Reader()
    return reader.read(chars)
