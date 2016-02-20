from kaa.ast import List, Value, Symbol
from kaa.charbuf import CharBuffer
from kaa.reader import Reader, UnbalancedDelimiterException, UnexpectedEofException
from unittest import TestCase

class ReaderTest(TestCase):

    def test_read_int(self):
        self.assertEqual(Value(42), self._read_object('42'))

    def test_read_symbol(self):
        self.assertEqual(Symbol('foo-bar'), self._read_object('foo-bar'))

    def test_read_unclosed_list(self):
        self.assertRaises(UnexpectedEofException,
                          lambda: self._read_object("("))

    def test_read_unbalanced_delimiter(self):
        self.assertRaises(UnbalancedDelimiterException,
                          lambda: self._read_object(")"))

    def test_read_list(self):
        obj = self._read_object('(foo 42 bar)')
        self.assertIsInstance(obj, List)
        self.assertEqual(obj[0], Symbol('foo'))
        self.assertEqual(obj[1], Value(42))
        self.assertEqual(obj[2], Symbol('bar'))

    def _read_object(self, s):
        return next(self._read(s))

    def _read(self, s):
        return Reader().read(CharBuffer(s))