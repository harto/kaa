from pytest import fixture, mark, raises

from kaa.core import Symbol
from kaa.env import Environment
from kaa.evaluator import (
    CompilationError,
    Evaluator,
    Lambda,
    Params,
    parse_def,
    parse_lambda,
    parse_params,
    Raise,
    UnboundSymbol,
    WrongArity,
)
from testing_utils import read


def test_parse_def():
    parsed = parse_def(read('(def foo 42)'))
    assert parsed.symbol == Symbol('foo')
    assert parsed.value == 42


def test_parse_invalid_def():
    with raises(CompilationError):
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
    with raises(CompilationError):
        parse_lambda(read('(lambda ((3)))'))


# TODO: move to system test


@fixture(name='evaluator')
def evaluator_fixture():
    return Evaluator(Environment())


def test_lambda_invocation_wrong_arity(evaluator):
    with raises(WrongArity):
        evaluator.evaluate(read('((lambda ()) 1)'))


def test_raises(evaluator):
    class SpecificException(Exception):
        pass
    with raises(SpecificException):
        evaluator.evaluate(Raise(SpecificException('oh no')))
    with raises(RuntimeError, match='oh no'):
        evaluator.evaluate(Raise('oh no'))


def test_unbound_symbol_raises_error(evaluator):
    with raises(UnboundSymbol):
        evaluator.evaluate(read('foo'))
