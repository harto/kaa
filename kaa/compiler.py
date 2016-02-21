from kaa.ast import Def, List, Symbol, Value

# AST-level transformations, e.g. parsing special forms

class Compiler(object):

    def compile(self, exprs):
        for expr in exprs:
            yield self._compile(expr)

    def _compile(self, expr):
        if isinstance(expr, List):
            return self._compile_list(expr)
        else:
            return expr

    def _compile_list(self, l):
        if l[0] == Symbol('def'):
            return self._compile_def(l[1:])
        else:
            # todo: decide on lists or generators everywhere
            return List(list(self._compile(expr for expr in l)))

    def _compile_def(self, binding):
        try:
            sym, val = binding
        except ValueError:
            sym = val = None
        if not isinstance(sym, Symbol):
            raise CompilationException('def accepts one symbol and one value')
        return Def(sym, val)

class CompilationException(Exception): pass
