from kaa.types import List, Symbol
from kaa.special_forms import Def, If, Lambda, Let, Macro, Raise, Quote

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
    if not _is_symbol(sym):
        _err('invalid def form', L.source_meta)
    return Def(sym, compile(val))

def _compile_defmacro(L):
    try:
        name = L[1]
        params = L[2]
    except IndexError:
        name = params = None
    if not _is_symbol(name):
        _err('invalid macro name', L.source_meta)
    if not _is_valid_param_list(params):
        _err('invalid macro params', L.source_meta)
    body = [compile(expr) for expr in L[3:]]
    return Def(name, Macro(params, body))

def _compile_if(L):
    if len(L) not in (3, 4):
        _err('invalid if form', L.source_meta)
    cond = L[1]
    then = L[2]
    try:
        else_ = L[3]
    except IndexError:
        else_ = None
    return If(cond, then, else_)

def _compile_lambda(L):
    try:
        params = L[1]
    except IndexError:
        params = None
    if not _is_valid_param_list(params):
        _err('invalid lambda params', L.source_meta)
    body = [compile(expr) for expr in L[2:]]
    return Lambda([p.name for p in params], body)

def _is_symbol(x):
    return isinstance(x, Symbol)

def _is_valid_param_list(params):
    return isinstance(params, List) and all(_is_symbol(p) for p in params)

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
        if not _is_symbol(sym):
            _err('value must be bound to symbol', bindings.source_meta)
        compiled.append((sym.name, compile(val)))
    return compiled

def _compile_raise(L):
    try:
        exception = L[1]
    except IndexError:
        _err('raise takes one arg', L.source_meta)
    return Raise(exception)

def _compile_quote(L):
    # Short-circuit compilation
    if len(L) != 2:
        _err('quote takes one argument', L.source_meta)
    return Quote(L[1])

special_form_compilers = {
    Symbol('def'): _compile_def,
    Symbol('defmacro'): _compile_defmacro,
    Symbol('if'): _compile_if,
    Symbol('lambda'): _compile_lambda,
    Symbol('let'): _compile_let,
    Symbol('raise'): _compile_raise,
    Symbol('quote'): _compile_quote,
}

def _err(msg, source_meta):
    if source_meta:
        msg += ' (%s)' % source_meta
    raise CompilationException(msg)

class CompilationException(Exception): pass
