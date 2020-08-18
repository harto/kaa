from kaa.evaluator import evaluate
from kaa.core import *
from unittest import TestCase


class ListTest(TestCase):
    def test_empty_list_evaluates_to_itself(self):
        l = List()
        self.assertEqual(l, evaluate(l, {}))

    def test_non_empty_list_evaluates_to_function_call(self):
        l = List([lambda x: 'Hello, %s' % x, 'world'])
        self.assertEqual('Hello, world', evaluate(l, {}))


class SymbolTest(TestCase):
    def test_symbol_evaluates_to_bound_value(self):
        s = Symbol('foo')
        self.assertEqual(42, evaluate(s, {'foo': 42}))

    def test_unbound_symbol_raises_error(self):
        s = Symbol('foo')
        self.assertRaises(UnboundSymbol, lambda: evaluate(s, {}))

    def test_equality(self):
        self.assertEqual(Symbol('foo'), Symbol('foo'))
        self.assertNotEqual(Symbol('bar'), Symbol('foo'))
