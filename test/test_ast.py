from kaa.ast import Func, List, Symbol, UnboundSymbolException, Value
from unittest import TestCase

class FuncTest(TestCase):

    def test_call_proxies_to_python_function(self):
        add = Func(lambda x, y: x + y)
        self.assertEqual(5, add(2, 3))

class ListTest(TestCase):

    def test_empty_list_evaluates_to_itself(self):
        l = List()
        self.assertEqual(l, l.eval({}))

    def test_non_empty_list_evaluates_to_function_call(self):
        l = List([Func(lambda x: "Hello, %s" % x), Value("world")])
        self.assertEqual("Hello, world", l.eval({}))

class SymbolTest(TestCase):

    def test_symbol_evaluates_to_bound_value(self):
        s = Symbol('foo')
        self.assertEqual(42, s.eval({'foo': 42}))

    def test_unbound_symbol_raises_error(self):
        s = Symbol('foo')
        self.assertRaises(UnboundSymbolException,
                          lambda: s.eval({}))

    def test_equality(self):
        self.assertEqual(Symbol('foo'), Symbol('foo'))
        self.assertNotEqual(Symbol('bar'), Symbol('foo'))

class ValueTest(TestCase):

    def test_equality(self):
        self.assertEqual(Value(42), Value(42))
        self.assertNotEqual(Value(42.0), Value(42))
