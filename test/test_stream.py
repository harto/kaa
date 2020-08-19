import pytest

from kaa.stream import CharStream, MultilineStream, StreamEmpty


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


def test_multiline_stream_peek_empty():
    assert MultilineStream(['']).peek_char() is None


def test_multiline_stream_peek():
    assert MultilineStream(['a']).peek_char() == 'a'


def test_multiline_stream_pop():
    stream = MultilineStream(['ab', 'c'])
    assert stream.pop_char() == 'a'
    assert stream.pop_char() == 'b'
    assert stream.pop_char() == 'c'
    with pytest.raises(StreamEmpty):
        stream.pop_char()
