from kaa.ast import Def, Lambda, Let, List, Symbol, Value

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
        elif first == Symbol('let'):
            return self._compile_let(l)
        else:
            # todo: decide on lists or generators everywhere
            return List(list(self.compile(l)))

    def _compile_def(self, l):
        try:
            sym, val = l[1:]
        except ValueError:
            sym = val = None
        if not isinstance(sym, Symbol):
            self._err('def expects symbol, value')
        return Def(sym, self._compile(val))

    def _compile_lambda(self, l):
        try:
            params = l[1]
        except IndexError:
            params = None
        if not isinstance(params, List):
            self._err('lambda expects list of params as first arg')
        if not all(isinstance(p, Symbol) for p in params):
            self._err('lambda params must be symbols')
        body = l[2:]
        return Lambda(params, self.compile(body))

    def _compile_let(self, l):
        try:
            bindings = l[1]
        except IndexError:
            bindings = None
        if not isinstance(bindings, List):
            self._err('let requires list of bindings as first arg')
        if len(bindings) % 2:
            self._err('let requires matching pairs of key-value bindings')
        binding_pairs = zip(*(iter(bindings),) * 2)
        compiled_bindings = List()
        for sym, val in binding_pairs:
            if not isinstance(sym, Symbol):
                self._err('binding LHS must be a symbol')
            compiled_bindings.append(sym)
            compiled_bindings.append(self._compile(val))
        body = l[2:]
        return Let(compiled_bindings, self.compile(body))

    def _err(self, msg = None):
        raise CompilationException(msg)

class CompilationException(Exception): pass