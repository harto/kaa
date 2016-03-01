from kaa.charbuf import CharBuffer, LineIterCharBuffer
from kaa.reader import *
from kaa.types import List, Symbol
from unittest import TestCase

class ReaderTest(TestCase):

    def test_read_int(self):
        self.assertEqual(42, self._read_object('42'))

    def test_read_string(self):
        self.assertEqual("hello", self._read_object('"hello"'))

    def test_read_unterminated_string(self):
        self.assertRaises(UnexpectedEofException,
                          lambda: self._read_object('"hello'))

    def test_read_string_with_escaped_quotes(self):
        self.assertEqual('"hello"', self._read_object('"\\"hello\\""'))

    def test_read_string_with_invalid_escape_sequence(self):
        self.assertRaises(InvalidEscapeSequence,
                          lambda: self._read_object('"h\\ello"'))

    def test_read_symbol(self):
        self.assertEqual(Symbol('foo-bar'), self._read_object('foo-bar'))

    def test_read_unclosed_list(self):
        self.assertRaises(UnexpectedEofException,
                          lambda: self._read_object("("))

    def test_read_unbalanced_delimiter(self):
        self.assertRaises(UnbalancedDelimiterException,
                          lambda: self._read_object(")"))

    def test_read_empty_list(self):
        obj = self._read_object('()')
        self.assertIsInstance(obj, List)

    def test_read_list(self):
        obj = self._read_object('(foo 42 bar)')
        self.assertIsInstance(obj, List)
        self.assertEqual(obj[0], Symbol('foo'))
        self.assertEqual(obj[1], 42)
        self.assertEqual(obj[2], Symbol('bar'))

    def test_read_python_builtin(self):
        obj = self._read_object('py/Exception')
        self.assertEqual(Exception, obj)

    def test_source_meta(self):
        lines = LineIterCharBuffer(('(foo', '  (bar))'))
        obj = next(Reader().read(lines))
        self.assertEqual(1, obj.source_meta.line)
        self.assertEqual(0, obj.source_meta.col)
        obj = obj[1]
        self.assertEqual(2, obj.source_meta.line)
        self.assertEqual(2, obj.source_meta.col)

    def _read_object(self, s):
        return next(self._read(s))

    def _read(self, s):
        return Reader().read(CharBuffer(s))
