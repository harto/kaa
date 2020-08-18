import pytest

from kaa.evaluator import evaluate
from kaa.core import List, Symbol, UnboundSymbol


def test_empty_list_evaluates_to_itself():
    l = List()
    assert evaluate(l, {}) == l


def test_non_empty_list_evaluates_to_function_call():
    l = List([lambda x: 'Hello, %s' % x, 'world'])
    assert evaluate(l, {}) == 'Hello, world'


def test_symbol_evaluates_to_bound_value():
    s = Symbol('foo')
    assert evaluate(s, {'foo': 42}) == 42


def test_unbound_symbol_raises_error():
    s = Symbol('foo')
    with pytest.raises(UnboundSymbol):
        evaluate(s, {})


def test_symbol_equality():
    assert Symbol('foo') == Symbol('foo')
    assert Symbol('foo') != Symbol('bar')
