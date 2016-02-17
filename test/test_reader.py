from kaa import ast, reader
from unittest import TestCase

class CharStreamTest(TestCase):

    def test_eof(self):
        self.assertTrue(reader.CharStream('').eof())
        r = reader.CharStream('x')
        self.assertFalse(r.eof())
        r.pop()
        self.assertTrue(r.eof())

    def test_peek(self):
        r = reader.CharStream('a')
        self.assertEqual('a', r.peek())
        r.pop()
        self.assertIsNone(r.peek())

    def test_pop(self):
        r = reader.CharStream('a')
        self.assertEqual('a', r.pop())
        self.assertRaises(Exception, lambda: r.pop())

    def test_unpop(self):
        r = reader.CharStream('a')
        self.assertRaises(Exception, lambda: r.unpop('x'))
        r.pop()
        r.unpop('a')
        self.assertEqual('a', r.pop())


class ReaderTest(TestCase):

    def test_read_int(self):
        self.assertEqual(ast.Value(42), self._read_object('42'))

    def test_read_symbol(self):
        self.assertEqual(ast.Symbol('foo-bar'), self._read_object('foo-bar'))

    def test_read_unclosed_list(self):
        self.assertRaises(reader.UnexpectedEofException, lambda: self._read_object("("))

    def test_read_unbalanced_delimiter(self):
        self.assertRaises(reader.UnbalancedDelimiterException,
                          lambda: self._read_object(")"))

    def test_read_list(self):
        obj = self._read_object('(foo 42 bar)')
        self.assertIsInstance(obj, ast.List)
        self.assertEqual(obj[0], ast.Symbol('foo'))
        self.assertEqual(obj[1], ast.Value(42))
        self.assertEqual(obj[2], ast.Symbol('bar'))

    def _read_object(self, s):
        return next(self._read(s))

    def _read(self, s):
        return reader.Reader().read(reader.CharStream(s))
