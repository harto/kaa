from pytest import mark, raises

from kaa.core import Symbol
from kaa.parser import Lambda, Params, parse_def, parse_lambda, parse_params, ParseError
from testing_utils import read


def test_parse_def():
    parsed = parse_def(read('(def foo 42)'))
    assert parsed.symbol.name == 'foo'
    assert parsed.value == 42


def test_parse_invalid_def():
    with raises(ParseError):
        parse_def(read('(def foo 42 bar)'))


@mark.parametrize('s, expectations', (
    ('()', {
        'required': (),
        'optional': (),
        'rest': None,
    }),
    ('(a b)', {
        'required': ('a', 'b'),
        'optional': (),
        'rest': None,
    }),
    ('(&optional c)', {
        'required': (),
        'optional': ('c',),
        'rest': None,
    }),
    ('(a b &optional c)', {
        'required': ('a', 'b'),
        'optional': ('c',),
        'rest': None,
    }),
    ('(&rest args)', {
        'required': (),
        'optional': (),
        'rest': 'args',
    }),
    ('(a b &rest args)', {
        'required': ('a', 'b'),
        'optional': (),
        'rest': 'args',
    }),
    ('(a b &optional c &rest args)', {
        'required': ('a', 'b'),
        'optional': ('c',),
        'rest': 'args',
    }),
))
def test_parse_params(s, expectations):
    parsed = parse_params(read(s))
    assert tuple(sym.name for sym in parsed.required) == expectations['required']
    assert tuple(sym.name for sym in parsed.optional) == expectations['optional']
    if expectations['rest'] is None:
        assert parsed.rest is None
    else:
        assert parsed.rest.name == expectations['rest']


def test_parse_lambda():
    parsed = parse_lambda(read('(lambda (foo) bar)'))
    assert isinstance(parsed, Lambda)
    assert isinstance(parsed.params, Params)
    assert tuple(parsed.body) == ((Symbol('bar', 'testing'),))


def test_parse_invalid_lambda():
    with raises(ParseError):
        parse_lambda(read('(lambda ((3)))'))
