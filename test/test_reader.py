from pytest import raises

from kaa.core import List, Symbol
from kaa.ns import Namespace
from kaa.reader import EOF, InvalidEscapeSequence, Reader, UnbalancedDelimiter
from kaa.stream import IterStream
from testing_utils import read


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


def test_read_unqualified_symbol():
    assert read('foo-bar') == Symbol('foo-bar', 'testing')


def test_read_qualified_symbol():
    assert read('foo/bar') == Symbol('bar', 'foo')


def test_read_special_form():
    assert read('def') == Symbol('def')


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
    assert obj[0] == Symbol('foo', 'testing')
    assert obj[1] == 42
    assert obj[2] == Symbol('bar', 'testing')


def test_source_meta():
    reader = Reader(Namespace('testing'))
    lines = IterStream(('(foo', '  (bar))'), filename='yadda')
    obj = reader.read_next(lines)
    assert obj.meta['source'].filename == 'yadda'
    assert obj.meta['source'].line == 1
    assert obj.meta['source'].col == 0
    obj = obj[1]
    assert obj.meta['source'].filename == 'yadda'
    assert obj.meta['source'].line == 2
    assert obj.meta['source'].col == 2
