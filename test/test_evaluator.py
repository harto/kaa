from pytest import mark, raises

from kaa.core import List, Symbol, UnboundSymbol
from kaa.env import Environment
from kaa.evaluator import (
    CompilationError,
    Def,
    evaluate,
    Lambda,
    parse_def,
    parse_lambda,
    parse_params,
    Quote,
    Raise,
    WrongArity,
)
from kaa.reader import read


def test_parse_def():
    parsed = parse_def(read('(def foo 42)'))
    assert parsed.symbol == Symbol('foo')
    assert parsed.value == 42


def test_parse_invalid_def():
    with raises(CompilationError):
        parse_def(read('(def foo 42 bar)'))


def test_def_sets_value_in_env():
    form = Def(Symbol('x'), 42)
    env = Environment()
    result = form.eval(env)
    assert result == 42
    assert result == env['x']


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
    assert tuple(parsed.required_names) == expectations['required']
    assert tuple(parsed.optional_names) == expectations['optional']
    assert parsed.rest_name == expectations['rest']


def test_parse_lambda():
    parsed = parse_lambda(read('(lambda (foo))'))
    assert isinstance(parsed, Lambda)


def test_parse_invalid_lambda():
    with raises(CompilationError):
        parse_lambda(read('(lambda ((3)))'))


def test_lambda_invocation():
    env = Environment({'+': int.__add__})
    f = parse_lambda(read('(lambda (x y) (+ x y))'))
    assert f.invoke((1, 2), env) == 3


def test_lambda_invocation_wrong_arity():
    f = parse_lambda(read('(lambda ())'))
    with raises(WrongArity):
        f.invoke(('foo',), Environment())


def test_raises():
    class ExampleException(Exception):
        pass
    form = Raise(ExampleException('oh no'))
    with raises(ExampleException):
        form.eval(Environment())
    form = Raise('oh no')
    with raises(Exception):
        form.eval(Environment())


def test_quoted_form_evaluates_to_self():
    expr = List([Symbol('foo')])
    quote = Quote(expr)
    assert quote.eval(Environment()) == expr


def test_empty_list_evaluates_to_self():
    l = List()
    assert evaluate(l, {}) == l


def test_non_empty_list_evaluates_to_function_call():
    l = List((lambda x: 'Hello, %s' % x, 'world'))
    assert evaluate(l, {}) == 'Hello, world'


def test_symbol_evaluates_to_bound_value():
    s = Symbol('foo')
    assert evaluate(s, {'foo': 42}) == 42


def test_unbound_symbol_raises_error():
    s = Symbol('foo')
    with raises(UnboundSymbol):
        evaluate(s, {})
