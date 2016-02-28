from kaa.ast import List, Symbol
from kaa.special_forms import Def, Lambda, Let

# AST-level transformations, e.g. parsing special forms

def compile(expr):
    if isinstance(expr, List):
        return _compile_list(expr)
    else:
        return expr

def _compile_list(L):
    if not len(L):
        return L
    try:
        _compile_special_form = special_form_compilers[L[0]]
    except KeyError:
        # not a special form
        return List([compile(expr) for expr in L], L.source_meta)
    return _compile_special_form(L)

def _compile_def(L):
    try:
        sym, val = L[1:]
    except ValueError:
        sym = val = None
    if not isinstance(sym, Symbol):
        _err('def expects symbol, value', L.source_meta)
    return Def(sym, compile(val))

def _compile_lambda(L):
    try:
        params = L[1]
    except IndexError:
        params = None
    if not isinstance(params, List):
        _err('lambda expects list of params as first arg', L.source_meta)
    if not all(isinstance(p, Symbol) for p in params):
        _err('lambda params must be symbols', params.source_meta)
    body = [compile(expr) for expr in L[2:]]
    return Lambda([p.name for p in params], body)

def _compile_let(L):
    try:
        first = L[1]
    except IndexError:
        first = None
    rest = L[2:]
    bindings = _compile_let_bindings(first)
    body = [compile(expr) for expr in rest]
    return Let(bindings, body)

def _compile_let_bindings(bindings):
    if not isinstance(bindings, List):
        _err('let expects list of bindings as first arg', bindings.source_meta)
    if len(bindings) % 2:
        _err('let expects matching pairs of key-value bindings', bindings.source_meta)
    pairs = zip(*(iter(bindings),) * 2)
    compiled = []
    for sym, val in pairs:
        if not isinstance(sym, Symbol):
            _err('value must be bound to symbol', bindings.source_meta)
        compiled.append((sym.name, compile(val)))
    return compiled

special_form_compilers = {
    Symbol('def'): _compile_def,
    Symbol('lambda'): _compile_lambda,
    Symbol('let'): _compile_let,
}

def _err(msg, source_meta):
    if source_meta:
        msg += ' (%s)' % source_meta
    raise CompilationException(msg)

class CompilationException(Exception): pass
