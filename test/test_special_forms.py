from kaa.core import List, Symbol
from kaa.ns import Namespace
from kaa.special_forms import *
from unittest import TestCase

class DefTest(TestCase):

    def test_parse(self):
        expr = List([Symbol('def'), Symbol('foo'), 42])
        obj = Def.parse(expr)
        self.assertIsInstance(obj, Def)
        self.assertEqual(Symbol('foo'), obj.symbol)
        self.assertEqual(42, obj.value)

    def test_parse_invalid(self):
        expr = List([Symbol('def'), Symbol('foo'), 42, Symbol('bar')])
        self.assertRaises(CompilationException,
                          lambda: Def.parse(expr))

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), 42)
        ns = Namespace()
        result = d.eval(ns)
        self.assertEqual(result, 42)
        self.assertEqual(result, ns['x'])

class LambdaTest(TestCase):

    def test_parse(self):
        expr = List([Symbol('lambda'), List([Symbol('foo')])])
        obj = Lambda.parse(expr)
        self.assertIsInstance(obj, Lambda)

    def test_parse_invalid(self):
        expr = List([Symbol('lambda'), List([3])])
        self.assertRaises(CompilationException,
                          lambda: Lambda.parse(expr))

    def test_call_produces_expected_result(self):
        lam = Lambda.parse(List([Symbol('lambda'),
                                  List([Symbol('x'), Symbol('y')]),
                                  List([lambda a, b: a + b,
                                        Symbol('x'),
                                        Symbol('y')])]))
        self.assertEqual(3, lam(Namespace(), 1, 2))

    def test_call_with_invalid_arity(self):
        lam = Lambda.parse(List([Symbol('lambda'), List([])]))
        self.assertRaises(ArityException, lambda: lam(Namespace(), 'foo'))

class LetTest(TestCase):

    def test_parse(self):
        expr = List([Symbol('let'),
                     List([Symbol('x'), 42]),
                     List([Symbol('x')])])
        obj = Let.parse(expr)
        self.assertIsInstance(obj, Let)
        self.assertEqual([('x', 42)], obj.bindings)
        self.assertEqual([List([Symbol('x')])], obj.body)

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
