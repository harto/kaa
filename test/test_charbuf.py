from kaa.charbuf import CharBuffer, EmptyBuffer, LineIterCharBuffer
from unittest import TestCase


class CharBufferTest(TestCase):

    def test_eof(self):
        self.assertTrue(CharBuffer('').eof())
        buf = CharBuffer('x')
        self.assertFalse(buf.eof())
        buf.pop()
        self.assertTrue(buf.eof())

    def test_peek(self):
        buf = CharBuffer('a')
        self.assertEqual('a', buf.peek())
        buf.pop()
        self.assertIsNone(buf.peek())

    def test_pop(self):
        buf = CharBuffer('a')
        self.assertEqual('a', buf.pop())
        self.assertRaises(EmptyBuffer, lambda: buf.pop())


class LineIterCharBufferTest(TestCase):

    def test_eof(self):
        self.assertTrue(LineIterCharBuffer([]).eof())
        self.assertTrue(LineIterCharBuffer(['']).eof())
        buf = LineIterCharBuffer(['a', 'b'])
        self.assertFalse(buf.eof())
        buf.pop()
        self.assertFalse(buf.eof())
        buf.pop()
        self.assertTrue(buf.eof())

    def test_peek(self):
        self.assertEqual('a', LineIterCharBuffer(['a']).peek())
        self.assertIsNone(LineIterCharBuffer(['']).peek())

    def test_pop(self):
        buf = LineIterCharBuffer(['ab', 'c'])
        self.assertEqual('a', buf.pop())
        self.assertEqual('b', buf.pop())
        self.assertEqual('c', buf.pop())
        self.assertRaises(EmptyBuffer, lambda: buf.pop())
