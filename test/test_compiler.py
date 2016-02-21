from kaa.ast import Def, Func, Lambda, List, Symbol, Value
from kaa.compiler import CompilationException, Compiler
from unittest import TestCase

class CompilerTest(TestCase):

    def test_compile_untransformable_expr(self):
        sym = Symbol('foo')
        self.assertEqual(sym, self._compile(sym))

    def test_compile_list(self):
        l = List([Symbol('foo'), Value('bar')])
        self.assertEqual(l.members, self._compile(l).members)

    def test_compile_def(self):
        expr = List([Symbol('def'), Symbol('foo'), Value(42)])
        compiled = self._compile(expr)
        self.assertEqual(Def(Symbol('foo'), Value(42)), compiled)

    def test_compile_invalid_def(self):
        expr = List([Symbol('def'), Symbol('foo'), Value(42), Symbol('bar')])
        self.assertRaises(CompilationException,
                          lambda: self._compile(expr))

    def test_compile_lambda(self):
        expr = List([Symbol('lambda'), List([Symbol('foo')])])
        compiled = self._compile(expr)
        self.assertIsInstance(compiled, Lambda)
        self.assertEqual(List([Symbol('foo')]), compiled.params)

    def test_compile_invalid_lambda(self):
        expr = List([Symbol('lambda'), List([Value(3)])])
        self.assertRaises(CompilationException,
                          lambda: self._compile(expr))

    def _compile(self, expr):
        return next(Compiler().compile([expr]))
