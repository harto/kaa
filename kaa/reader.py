from kaa.types import List, Symbol
from collections import OrderedDict
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
                raise UnexpectedEofException()
            return None
        c = chars.pop()
        if c.isspace():
            while chars.peek() and chars.peek().isspace():
                chars.pop()
            return self.read(chars)
        elif c == ';':
            while chars.peek():
                chars.pop()
            return self.read(chars)
        elif c == '(':
            return self._read_list(chars)
        elif c == ')':
            if self.list_depth == 0:
                raise UnbalancedDelimiterException(
                    'unbalanced delimiter %s at %s' % (c, chars.source_meta()))
            else:
                return self.EOLIST
        elif c == '"':
            return self._read_string(chars)
        else:
            return self._read_atom(c, chars)

    def _read_list(self, chars):
        L = List()
        L.source_meta = chars.source_meta()
        self.list_depth += 1
        for obj in self.read_all(chars):
            if obj == self.EOLIST:
                break
            L.append(obj)
        self.list_depth -= 1
        return L

    def _read_string(self, chars):
        s = []
        while chars.peek():
            c = chars.pop()
            if c == '"':
                return ''.join(s)
            elif c == '\\':
                if not chars.peek():
                    # EOF
                    break
                escape_sequence = c + chars.pop()
                try:
                    s.append(self.STRING_ESCAPE_SEQUENCES[escape_sequence])
                except KeyError:
                    raise InvalidEscapeSequence(escape_sequence)
            else:
                s.append(c)
        raise UnexpectedEofException()

    STRING_ESCAPE_SEQUENCES = OrderedDict((
        # Order is important for formatting strings (e.g. in REPL); backslashes
        # must be escaped first to avoid double escaping.
        ('\\\\', '\\'),
        ('\\"', '"'),
        ('\\n', '\n'),
        ('\\t', '\t'),
    ))

    def _read_atom(self, first_char, chars):
        source_meta = chars.source_meta()
        token = first_char
        while chars.peek() and self.ATOM.match(chars.peek()):
            token += chars.pop()
        if self.INTEGER.match(token):
            return int(token)
        elif token.startswith('py/'):
            return eval(token[3:])
        else:
            return Symbol(token, source_meta)

class InvalidEscapeSequence(Exception): pass
class UnbalancedDelimiterException(Exception): pass
class UnexpectedEofException(Exception): pass
