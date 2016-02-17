from kaa import ast
from unittest import TestCase

class FuncTest(TestCase):

    def test_call_proxies_to_python_function(self):
        add = ast.Func(lambda x, y: x + y)
        self.assertEqual(5, add(2, 3))

class ListTest(TestCase):

    def test_empty_list_evaluates_to_itself(self):
        l = ast.List()
        self.assertEqual(l, l.eval({}))

    def test_non_empty_list_evaluates_to_function_call(self):
        l = ast.List([ast.Func(lambda x: "Hello, %s" % x), ast.Value("world")])
        self.assertEqual("Hello, world", l.eval({}))

class SymbolTest(TestCase):

    def test_symbol_evaluates_to_bound_value(self):
        s = ast.Symbol('foo')
        self.assertEqual(42, s.eval({'foo': 42}))

    def test_unbound_symbol_raises_error(self):
        s = ast.Symbol('foo')
        self.assertRaises(ast.UnboundSymbolException,
                          lambda: s.eval({}))

    def test_equality(self):
        self.assertEqual(ast.Symbol('foo'), ast.Symbol('foo'))
        self.assertNotEqual(ast.Symbol('bar'), ast.Symbol('foo'))

class ValueTest(TestCase):

    def test_equality(self):
        self.assertEqual(ast.Value(42), ast.Value(42))
        self.assertNotEqual(ast.Value(42.0), ast.Value(42))
