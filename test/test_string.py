from kaa import string
from kaa.charbuf import CharBuffer
from unittest import TestCase

class StringTest(TestCase):

    def test_read_string(self):
        self.assertEqual('hello', self._read_string('"hello"'))

    def test_read_unterminated_string(self):
        self.assertRaises(string.UnterminatedStringException,
                          lambda: self._read_string('"hello'))

    def test_read_string_with_escaped_quotes(self):
        self.assertEqual('"hello"', self._read_string('"\\"hello\\""'))

    def test_read_string_with_invalid_escape_sequence(self):
        self.assertRaises(string.InvalidEscapeSequence,
                          lambda: self._read_string('"h\\ello"'))

    def _read_string(self, s):
        return string.read(CharBuffer(s))
