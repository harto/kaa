import pytest

from kaa.stream import CharStream, IterStream, StreamEmpty


def test_char_stream_peek_empty():
    assert CharStream('').peek_char() is None


def test_char_stream_peek():
    stream = CharStream('a')
    assert stream.peek_char() == 'a'
    stream.pop_char()
    assert stream.peek_char() is None


def test_char_stream_pop():
    stream = CharStream('a')
    assert stream.pop_char() == 'a'
    with pytest.raises(StreamEmpty):
        stream.pop_char()


def test_iter_stream_peek_empty():
    assert IterStream(['']).peek_char() is None


def test_iter_stream_peek():
    assert IterStream(['a']).peek_char() == 'a'


def test_iter_stream_pop():
    stream = IterStream(['ab', 'c'])
    assert stream.pop_char() == 'a'
    assert stream.pop_char() == 'b'
    assert stream.pop_char() == 'c'
    with pytest.raises(StreamEmpty):
        stream.pop_char()
