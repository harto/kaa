from collections import OrderedDict
import json


def read_str(chars):
    s = []
    assert chars.peek() == '"'
    chars.pop()
    while chars.peek():
        c = chars.pop()
        if c == '"':
            #raise Exception('finishing with %s' % ''.join(s))
            return ''.join(s)
        if c == '\\':
            if not chars.peek():
                # EOF
                break
            escape_sequence = c + chars.pop()
            try:
                s.append(STRING_ESCAPE_SEQUENCES[escape_sequence])
            except KeyError:
                raise InvalidEscapeSequence(escape_sequence)
        else:
            s.append(c)
    raise UnterminatedString()


def format_str(s):
    # We don't use repr(s), because that sometimes results in single-quoted
    # strings. We always want double-quoted strings.
    return json.dumps(s)


STRING_ESCAPE_SEQUENCES = OrderedDict((
    # Order is important for formatting strings (e.g. in REPL); backslashes
    # must be escaped first to avoid double escaping.
    ('\\\\', '\\'),
    ('\\"', '"'),
    ('\\n', '\n'),
    ('\\t', '\t'),
))


class InvalidEscapeSequence(Exception):
    pass


class UnterminatedString(Exception):
    pass
