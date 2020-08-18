from pytest import raises

from kaa.core import List, Symbol
from kaa.ns import Namespace
from kaa.reader import read
from kaa.special_forms import ArityException, CompilationException, Def, Lambda, Quote, Raise


def test_parse_def():
    parsed = Def.parse(read('(def foo 42)'))
    assert isinstance(parsed, Def)
    assert parsed.symbol == Symbol('foo')
    assert parsed.value == 42


def test_parse_invalid_def():
    with raises(CompilationException):
        Def.parse(read('(def foo 42 bar)'))


def test_def_sets_value_in_env():
    form = Def(Symbol('x'), 42)
    ns = Namespace()
    result = form.eval(ns)
    assert result == 42
    assert result == ns['x']


def test_parse_lambda():
    parsed = Lambda.parse(read('(lambda (foo))'))
    assert isinstance(parsed, Lambda)


def test_parse_invalid_lambda():
    with raises(CompilationException):
        Lambda.parse(read('(lambda ((3)))'))


def test_call_lambda_produces_expected_result():
    ns = Namespace({'+': int.__add__})
    fn = Lambda.parse(read('(lambda (x y) (+ x y))'))
    # TODO: could this be callable in Python without needing a namespace passed in?
    assert fn(ns, 1, 2) == 3


def test_call_lambda_with_invalid_arity():
    fn = Lambda.parse(read('(lambda ())'))
    with raises(ArityException):
        fn(Namespace(), 'foo')


def test_raises():
    class ExampleException(Exception):
        pass
    form = Raise(ExampleException('oh no'))
    with raises(ExampleException):
        form.eval(Namespace())
    form = Raise('oh no')
    with raises(Exception):
        form.eval(Namespace())


def test_quoted_form_evaluates_to_self():
    expr = List([Symbol('foo')])
    quote = Quote(expr)
    assert quote.eval(Namespace()) == expr
