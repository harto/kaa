from unittest import TestCase

from kaa.charbuf import CharBuffer
from kaa.string import InvalidEscapeSequence, read_str, UnterminatedString


class StringTest(TestCase):
    def test_read_string(self):
        self.assertEqual('hello', self._read_string('"hello"'))

    def test_read_unterminated_string(self):
        self.assertRaises(UnterminatedString,
                          lambda: self._read_string('"hello'))

    def test_read_string_with_escaped_quotes(self):
        self.assertEqual('"hello"', self._read_string('"\\"hello\\""'))

    def test_read_string_with_invalid_escape_sequence(self):
        self.assertRaises(InvalidEscapeSequence,
                          lambda: self._read_string('"h\\ello"'))

    def _read_string(self, s):
        return read_str(CharBuffer(s))
