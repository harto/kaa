from pytest import mark, raises

from kaa.core import Symbol
from kaa.parser import Lambda, Params, parse_def, parse_lambda, parse_params, ParseError
from testing_utils import read


def test_parse_def():
    parsed = parse_def(read('(def foo 42)'))
    assert parsed.symbol == Symbol('foo')
    assert parsed.value == 42


def test_parse_invalid_def():
    with raises(ParseError):
        parse_def(read('(def foo 42 bar)'))


@mark.parametrize('s, expectations', (
    ('()', {'required': (), 'optional': (), 'rest': None}),
    ('(a b)', {'required': ('a', 'b'), 'optional': (), 'rest': None}),
    ('(&optional c)', {'required': (), 'optional': ('c',), 'rest': None}),
    ('(a b &optional c)', {'required': ('a', 'b'), 'optional': ('c',), 'rest': None}),
    ('(&rest args)', {'required': (), 'optional': (), 'rest': 'args'}),
    ('(a b &rest args)', {'required': ('a', 'b'), 'optional': (), 'rest': 'args'}),
    ('(a b &optional c &rest args)', {'required': ('a', 'b'), 'optional': ('c',), 'rest': 'args'}),
))
def test_parse_params(s, expectations):
    parsed = parse_params(read(s))
    assert parsed.required_names == expectations['required']
    assert parsed.optional_names == expectations['optional']
    assert parsed.rest_name == expectations['rest']


def test_parse_lambda():
    parsed = parse_lambda(read('(lambda (foo) bar)'))
    assert isinstance(parsed, Lambda)
    assert isinstance(parsed.params, Params)
    assert tuple(parsed.body) == ((Symbol('bar'),))


def test_parse_invalid_lambda():
    with raises(ParseError):
        parse_lambda(read('(lambda ((3)))'))
