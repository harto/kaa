from kaa.ast import Def, Lambda, List, Symbol, Value

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
        if not len(l):
            return l
        first = l[0]
        if first == Symbol('def'):
            return self._compile_def(l)
        elif first == Symbol('lambda'):
            return self._compile_lambda(l)
        else:
            # todo: decide on lists or generators everywhere
            return List(list(self.compile(l)))

    def _compile_def(self, l):
        try:
            sym, val = l[1:]
        except ValueError:
            sym = val = None
        if not isinstance(sym, Symbol):
            raise CompilationException('def expects symbol, value')
        return Def(sym, self._compile(val))

    def _compile_lambda(self, l):
        try:
            params = l[1]
        except IndexError:
            params = None
        if not isinstance(params, List):
            raise CompilationException('lambda expects list of params as first arg')
        if not all(isinstance(p, Symbol) for p in params):
            raise CompilationException('lambda params must be symbols')
        body = l[2:]
        return Lambda(params, self.compile(body))

class CompilationException(Exception): pass
