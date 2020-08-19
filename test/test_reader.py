from pytest import raises

from kaa.core import List, Symbol
from kaa.reader import EOF, InvalidEscapeSequence, read, Reader, UnbalancedDelimiter
from kaa.stream import MultilineStream


def test_read_int():
    assert read('42') == 42


def test_read_string():
    assert read('"hello"') == 'hello'


def test_read_unterminated_string():
    with raises(EOF):
        read('"hello')


def test_read_string_with_escaped_quotes():
    assert read('"\\"hello\\""') == '"hello"'


def test_read_string_with_invalid_escape_sequence():
    with raises(InvalidEscapeSequence):
        read('"h\\ello"')


def test_read_symbol():
    assert read('foo-bar') == Symbol('foo-bar')


def test_read_unclosed_list():
    with raises(EOF):
        read("(")


def test_read_unbalanced_delimiter():
    with raises(UnbalancedDelimiter):
        read(")")


def test_read_empty_list():
    obj = read('()')
    assert isinstance(obj, List)


def test_read_list():
    obj = read('(foo 42 bar)')
    assert isinstance(obj, List)
    assert obj[0] == Symbol('foo')
    assert obj[1] == 42
    assert obj[2] == Symbol('bar')


def test_read_python_builtin():
    obj = read('py/Exception')
    assert obj == Exception


def test_source_meta():
    lines = MultilineStream(('(foo', '  (bar))'))
    obj = Reader().read_next(lines)
    assert obj.meta['source'].line == 1
    assert obj.meta['source'].col == 0
    obj = obj[1]
    assert obj.meta['source'].line == 2
    assert obj.meta['source'].col == 2
