from kaa.ast import Body, Def, Lambda, Let, List, Symbol

# AST-level transformations, e.g. parsing special forms

def compile(expr):
    if isinstance(expr, List):
        return _compile_list(expr)
    else:
        return expr

def _compile_list(l):
    if not len(l):
        return l
    first = l[0]
    if first == Symbol('def'):
        return _compile_def(l)
    elif first == Symbol('lambda'):
        return _compile_lambda(l)
    elif first == Symbol('let'):
        return _compile_let(l)
    else:
        return List([compile(expr) for expr in l])

def _compile_def(l):
    try:
        sym, val = l[1:]
    except ValueError:
        sym = val = None
    if not isinstance(sym, Symbol):
        _err('def expects symbol, value')
    return Def(sym, compile(val))

def _compile_lambda(l):
    try:
        params = l[1]
    except IndexError:
        params = None
    if not isinstance(params, List):
        _err('lambda expects list of params as first arg')
    if not all(isinstance(p, Symbol) for p in params):
        _err('lambda params must be symbols')
    body = Body([compile(expr) for expr in l[2:]])
    return Lambda([p.name for p in params], body)

def _compile_let(l):
    try:
        first = l[1]
    except IndexError:
        first = None
    rest = l[2:]
    bindings = _compile_let_bindings(first)
    body = Body([compile(expr) for expr in rest])
    return Let(bindings, body)

def _compile_let_bindings(bindings):
    if not isinstance(bindings, List):
        _err('let expects list of bindings as first arg')
    if len(bindings) % 2:
        _err('let expects matching pairs of key-value bindings')
    pairs = zip(*(iter(bindings),) * 2)
    compiled = []
    for sym, val in pairs:
        if not isinstance(sym, Symbol):
            _err('value must be bound to symbol')
        compiled.append((sym.name, compile(val)))
    return compiled

def _err(msg = None):
        raise CompilationException(msg)

class CompilationException(Exception): pass
