# fixme: figure out where to put this
def eval(expr, ns):
    expr = eval_special_form(expr)

    if isinstance(expr, List) and len(expr):
        return invoke(expr, ns)
    elif hasattr(expr, 'eval'):
        return expr.eval(ns)
    else:
        # native Python type
        return expr

def invoke(L, ns):
    first = eval(L[0], ns)
    rest = L[1:]

    if isinstance(first, Macro):
        expansion = first(ns, *rest)
        return eval(expansion, ns)

    args = [eval(expr, ns) for expr in rest]
    if isinstance(first, Lambda):
        return first(ns, *args)
    else:
        # assume Python callable
        return first(*args)

def eval_special_form(expr):
    if not isinstance(expr, List):
        return expr
    try:
        sym = expr[0]
        handler = special_form_handler(sym)
    except (IndexError, KeyError):
        return expr
    return handler(expr)

# lazy-load to avoid circular import issue
_special_form_handlers = None
def special_form_handler(sym):
    global _special_form_handlers
    if not _special_form_handlers:
        _special_form_handlers = {
            Symbol('def'): Def.create,
            Symbol('defmacro'): Macro.define,
            Symbol('if'): If.create,
            Symbol('lambda'): Lambda.create,
            Symbol('let'): Let.create,
            Symbol('raise'): Raise.create,
            Symbol('quasiquote'): Quasiquote.create,
            Symbol('quote'): Quote.create,
        }
    return _special_form_handlers[sym]

from kaa.special_forms import *
from kaa.types import List, Symbol
