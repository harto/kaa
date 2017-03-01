# fixme: figure out where to put this
def eval(expr, ns):
    expr = maybe_eval_special_form(expr)

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

def maybe_eval_special_form(expr):
    if not (isinstance(expr, List) and len(expr) and isinstance(expr[0], Symbol)):
        return expr

    handlers = {Symbol('def'): Def.parse,
                Symbol('defmacro'): Macro.define,
                Symbol('if'): If.parse,
                Symbol('lambda'): Lambda.parse,
                Symbol('raise'): Raise.parse,
                Symbol('quote'): Quote.parse,
                Symbol('try'): Try.parse}
    try:
        handler = handlers[expr[0]]
    except KeyError:
        return expr
    return handler(expr)

from kaa.special_forms import *
from kaa.core import List, Symbol
