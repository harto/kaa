from kaa.evaluator import eval
from kaa.ast import List, Namespace, Symbol
from kaa.special_forms import *
from unittest import TestCase

class DefTest(TestCase):

    def test_def_sets_value_in_env(self):
        d = Def(Symbol('x'), 42)
        ns = Namespace()
        result = eval(d, ns)
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
        self.assertEqual(42, eval(let, ns))
