from kaa.special_forms import *
from kaa.types import List, Namespace, Symbol
from unittest import TestCase

class DefTest(TestCase):

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), 42)
        ns = Namespace()
        result = d.eval(ns)
        self.assertEqual(result, 42)
        self.assertEqual(result, ns['x'])

class LambdaTest(TestCase):

    def test_call_produces_expected_result(self):
        lam = Lambda(['x', 'y'],
                     [List([lambda a, b: a + b,
                            Symbol('x'),
                            Symbol('y')])])
        self.assertEqual(3, lam(Namespace(), 1, 2))

    def test_call_with_invalid_arity(self):
        lam = Lambda([], [])
        self.assertRaises(ArityException, lambda: lam(Namespace(), 'foo'))

class LetTest(TestCase):

    def test_body_evaluates_with_bindings(self):
        let = Let([('x', 42)],
                  [Symbol('x')])
        ns = Namespace({'x': 5})
        self.assertEqual(42, let.eval(ns))

class RaiseTest(TestCase):

    def test_raises_exception(self):
        class ExampleException(Exception): pass
        r = Raise(ExampleException('oh no'))
        self.assertRaises(ExampleException, lambda: r.eval(Namespace()))
        r = Raise('oh no')
        self.assertRaises(Exception, lambda: r.eval(Namespace()))

class QuoteTest(TestCase):

    def test_quoted_form_not_evaluated(self):
        expr = List([Symbol('foo')])
        quote = Quote(expr)
        self.assertEqual(expr, quote.eval(Namespace()))
