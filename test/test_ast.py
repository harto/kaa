from kaa.ast import *
from unittest import TestCase

class DefTest(TestCase):

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), Value(42))
        ns = Namespace()
        result = d.eval(ns)
        self.assertEqual(result, Value(42))
        self.assertEqual(result, ns['x'])

class FuncTest(TestCase):

    def test_call_proxies_to_python_function(self):
        add = Func(lambda x, y: x + y)
        self.assertEqual(5, add(2, 3))

class LambdaTest(TestCase):

    def test_call_produces_expected_result(self):
        lam = Lambda(List([Symbol('x'),
                           Symbol('y')]),
                     Body([List([Func(lambda a, b: a + b),
                            Symbol('x'),
                            Symbol('y')])]))
        self.assertEqual(3, lam({}, 1, 2))

    def test_call_with_invalid_arity(self):
        lam = Lambda(List(), Body())
        self.assertRaises(ArityException, lambda: lam({}, 'foo'))

class LetTest(TestCase):

    def test_body_evaluates_with_bindings(self):
        let = Let(List([Symbol('x'), Value(42)]),
                  Body([Symbol('x')]))
        ns = Namespace({'x': Value(5)})
        self.assertEqual(Value(42), let.eval(ns))

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
