from kaa.ast import *
from kaa.evaluator import eval
from unittest import TestCase

class DefTest(TestCase):

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), 42)
        ns = Namespace()
        result = eval(d, ns)
        self.assertEqual(result, 42)
        self.assertEqual(result, ns['x'])

class FuncTest(TestCase):

    def test_call_proxies_to_python_function(self):
        add = lambda x, y: x + y
        self.assertEqual(5, add(2, 3))

class LambdaTest(TestCase):

    def test_call_produces_expected_result(self):
        lam = Lambda(['x', 'y'],
                     Body([List([lambda a, b: a + b,
                                 Symbol('x'),
                                 Symbol('y')])]))
        self.assertEqual(3, lam(Namespace(), 1, 2))

    def test_call_with_invalid_arity(self):
        lam = Lambda([], Body())
        self.assertRaises(ArityException, lambda: lam(Namespace(), 'foo'))

class LetTest(TestCase):

    def test_body_evaluates_with_bindings(self):
        let = Let(LetBindings([(Symbol('x'), 42)]),
                  Body([Symbol('x')]))
        ns = Namespace({'x': 5})
        self.assertEqual(42, eval(let, ns))

class ListTest(TestCase):

    def test_empty_list_evaluates_to_itself(self):
        l = List()
        self.assertEqual(l, eval(l, {}))

    def test_non_empty_list_evaluates_to_function_call(self):
        l = List([lambda x: 'Hello, %s' % x, 'world'])
        self.assertEqual('Hello, world', eval(l, {}))

class SymbolTest(TestCase):

    def test_symbol_evaluates_to_bound_value(self):
        s = Symbol('foo')
        self.assertEqual(42, eval(s, {'foo': 42}))

    def test_unbound_symbol_raises_error(self):
        s = Symbol('foo')
        self.assertRaises(UnboundSymbolException,
                          lambda: eval(s, {}))

    def test_equality(self):
        self.assertEqual(Symbol('foo'), Symbol('foo'))
        self.assertNotEqual(Symbol('bar'), Symbol('foo'))
