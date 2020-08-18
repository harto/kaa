import pytest

from kaa.charbuf import CharBuffer, EmptyBuffer, LineIterCharBuffer


def test_charbuffer_eof():
    assert CharBuffer('').eof()
    buf = CharBuffer('x')
    assert not buf.eof()
    buf.pop()
    assert buf.eof()


def test_charbuffer_peek():
    buf = CharBuffer('a')
    assert buf.peek() == 'a'
    buf.pop()
    assert buf.peek() is None


def test_charbuffer_pop():
    buf = CharBuffer('a')
    assert buf.pop() == 'a'
    with pytest.raises(EmptyBuffer):
        buf.pop()


def test_lineitercharbuffer_eof():
    assert LineIterCharBuffer([]).eof()
    assert LineIterCharBuffer(['']).eof()
    buf = LineIterCharBuffer(['a', 'b'])
    assert not buf.eof()
    buf.pop()
    assert not buf.eof()
    buf.pop()
    assert buf.eof()


def test_lineitercharbuffer_peek():
    assert LineIterCharBuffer(['a']).peek() == 'a'
    assert LineIterCharBuffer(['']).peek() is None


def test_lineitercharbuffer_pop():
    buf = LineIterCharBuffer(['ab', 'c'])
    assert buf.pop() == 'a'
    assert buf.pop() == 'b'
    assert buf.pop() == 'c'
    with pytest.raises(EmptyBuffer):
        buf.pop()
