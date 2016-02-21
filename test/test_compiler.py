from kaa.ast import Def, Func, Lambda, Let, List, Symbol, Value
from kaa.compiler import CompilationException, compile
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
        self.assertIsInstance(compiled, Def)
        self.assertEqual(Symbol('foo'), compiled.symbol)
        self.assertEqual(Value(42), compiled.value)

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

    def test_compile_let(self):
        expr = List([Symbol('let'),
                     List([Symbol('x'), Value(42)]),
                     List([Symbol('x')])])
        compiled = self._compile(expr)
        self.assertIsInstance(compiled, Let)
        self.assertEqual(List([Symbol('x'), Value(42)]), compiled.bindings)
        self.assertEqual([List([Symbol('x')])], list(compiled.body))

    def _compile(self, expr):
        return compile(expr)
