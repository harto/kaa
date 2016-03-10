from collections import OrderedDict

def read(chars):
    s = []
    assert chars.peek() == '"'
    chars.pop()
    while chars.peek():
        c = chars.pop()
        if c == '"':
            #raise Exception('finishing with %s' % ''.join(s))
            return ''.join(s)
        elif c == '\\':
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
    raise UnterminatedStringException()

def format(s):
    for k, v in STRING_ESCAPE_SEQUENCES.items():
        s = s.replace(v, k)
    return '"%s"' % s

STRING_ESCAPE_SEQUENCES = OrderedDict((
    # Order is important for formatting strings (e.g. in REPL); backslashes
    # must be escaped first to avoid double escaping.
    ('\\\\', '\\'),
    ('\\"', '"'),
    ('\\n', '\n'),
    ('\\t', '\t'),
))

class InvalidEscapeSequence(Exception): pass
class UnterminatedStringException(Exception): pass
