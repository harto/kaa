from kaa.ast import Def, Lambda, Let, List, Symbol
from kaa.compiler import CompilationException, compile
from unittest import TestCase

class CompilerTest(TestCase):

    def test_compile_untransformable_expr(self):
        sym = Symbol('foo')
        self.assertEqual(sym, self._compile(sym))

    def test_compile_list(self):
        L = List([Symbol('foo'), 'bar'])
        self.assertEqual(L.members, self._compile(L).members)

    def test_compile_def(self):
        expr = List([Symbol('def'), Symbol('foo'), 42])
        compiled = self._compile(expr)
        self.assertIsInstance(compiled, Def)
        self.assertEqual(Symbol('foo'), compiled.symbol)
        self.assertEqual(42, compiled.value)

    def test_compile_invalid_def(self):
        expr = List([Symbol('def'), Symbol('foo'), 42, Symbol('bar')])
        self.assertRaises(CompilationException,
                          lambda: self._compile(expr))

    def test_compile_lambda(self):
        expr = List([Symbol('lambda'), List([Symbol('foo')])])
        compiled = self._compile(expr)
        self.assertIsInstance(compiled, Lambda)
        self.assertEqual(['foo'], compiled.param_names)

    def test_compile_invalid_lambda(self):
        expr = List([Symbol('lambda'), List([3])])
        self.assertRaises(CompilationException,
                          lambda: self._compile(expr))

    def test_compile_let(self):
        expr = List([Symbol('let'),
                     List([Symbol('x'), 42]),
                     List([Symbol('x')])])
        compiled = self._compile(expr)
        self.assertIsInstance(compiled, Let)
        self.assertEqual([('x', 42)], compiled.bindings)
        self.assertEqual([List([Symbol('x')])], compiled.body)

    def _compile(self, expr):
        return compile(expr)
