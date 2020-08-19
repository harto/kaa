import re

from kaa.core import empty, first, is_list, rest, List, Symbol
from kaa.stream import CharStream, StreamEmpty


EOLIST = object()


def read(s):
    "Convenience method for reading a single object from a string."
    return Reader().read_next(CharStream(s))


class Reader:
    def __init__(self):
        self.list_depth = 0

    def read_all(self, stream):
        while True:
            obj = self.read_next(stream)
            if obj is None:
                break
            yield obj

    def read_next(self, stream):  # pylint: disable=too-many-return-statements
        "Reads next form from given char buffer."
        while (stream.peek_char() or '').isspace():
            stream.pop_char()

        try:
            c = stream.pop_char()
        except StreamEmpty:
            if self.list_depth > 0:
                raise EOF()  # TODO: should this return UnbalancedDelimiter?
            return None

        if c == ';':
            while c != '\n':
                c = stream.pop_char()
            return self.read_next(stream)
        if c == "'":
            return self._read_quote(stream)
        if c == '`':
            return self._read_quasiquote(stream)
        if c == '~':
            return self._read_unquote(stream)
        if c == '(':
            return self._read_list(stream)
        if c == ')':
            if self.list_depth == 0:
                raise UnbalancedDelimiter(
                    'unbalanced delimiter %s at %s' % (c, stream.source_meta()))
            return EOLIST
        if c == '"':
            return _read_string(stream)
        return _read_atom(c, stream)

    def _read_quote(self, stream):
        return List([Symbol('quote', {'source': stream.source_meta()}),
                     self.read_next(stream)])

    def _read_quasiquote(self, stream):
        return _process_quasiquote(self.read_next(stream))

    def _read_unquote(self, stream):
        if stream.peek_char() == '@':
            stream.pop_char()
            return List([Symbol('unquote-splice', {'source': stream.source_meta()}),
                         self.read_next(stream)])

        return List([Symbol('unquote', {'source': stream.source_meta()}),
                     self.read_next(stream)])

    def _read_list(self, stream):
        l = List(meta={'source': stream.source_meta()})
        self.list_depth += 1
        while True:
            form = self.read_next(stream)
            if form == EOLIST:
                break
            l.append(form)
        self.list_depth -= 1
        return l


def _read_string(stream):
    try:
        return read_str(stream)
    except StreamEmpty as ex:
        raise EOF(ex)


STRING_ESCAPE_SEQUENCES = {
    '\\\\': r'\\',
    '\\"': '"',
    '\\n': '\n',
    '\\t': '\t',
}


def read_str(stream):
    s = []
    while True:
        c = stream.pop_char()
        if c == '"':
            return ''.join(s)
        if c == '\\':
            escape_sequence = c + stream.pop_char()
            try:
                s.append(STRING_ESCAPE_SEQUENCES[escape_sequence])
            except KeyError:
                raise InvalidEscapeSequence(escape_sequence)
        else:
            s.append(c)


class InvalidEscapeSequence(Exception):
    pass


class UnterminatedString(Exception):
    pass


ATOM = re.compile(r'[^\s\(\)]+')
INTEGER = re.compile(r'[+-]?[0-9]+')


def _read_atom(first_char, stream):
    meta = {'source': stream.source_meta()}
    token = first_char
    # TODO: is this weird? (regexp match against a single char)
    while ATOM.match(stream.peek_char() or ''):
        token += stream.pop_char()
    if INTEGER.match(token):
        return int(token)
    if token.startswith('py/'):
        # TODO: should this be evaled later?
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
