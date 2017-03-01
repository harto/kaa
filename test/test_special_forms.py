from kaa.core import List, Symbol
from kaa.ns import Namespace
from kaa.special_forms import *
from unittest import TestCase

class DefTest(TestCase):

    def test_parse(self):
        obj = Def.parse(read('(def foo 42)'))
        self.assertIsInstance(obj, Def)
        self.assertEqual(Symbol('foo'), obj.symbol)
        self.assertEqual(42, obj.value)

    def test_parse_invalid(self):
        self.assertRaises(CompilationException,
                          lambda: Def.parse(read('(def foo 42 bar)')))

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), 42)
        ns = Namespace()
        result = d.eval(ns)
        self.assertEqual(result, 42)
        self.assertEqual(result, ns['x'])

class LambdaTest(TestCase):

    def test_parse(self):
        obj = Lambda.parse(read('(lambda (foo))'))
        self.assertIsInstance(obj, Lambda)

    def test_parse_invalid(self):
        self.assertRaises(CompilationException,
                          lambda: Lambda.parse(read('(lambda ((3)))')))

    def test_call_produces_expected_result(self):
        lam = Lambda.parse(List([Symbol('lambda'),
                                  List([Symbol('x'), Symbol('y')]),
                                  List([lambda a, b: a + b,
                                        Symbol('x'),
                                        Symbol('y')])]))
        self.assertEqual(3, lam(Namespace(), 1, 2))

    def test_call_with_invalid_arity(self):
        lam = Lambda.parse(read('(lambda ())'))
        self.assertRaises(ArityException, lambda: lam(Namespace(), 'foo'))

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

from kaa.charbuf import CharBuffer
from kaa.reader import Reader

def read(s):
    return Reader().read(CharBuffer(s))
