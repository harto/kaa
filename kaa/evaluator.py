# fixme: figure out where to put this
def eval(expr, ns):
    if isinstance(expr, List) and len(expr):
        return _invoke(expr, ns)
    try:
        return expr.eval(ns)
    except AttributeError:
        return expr

def _invoke(L, ns):
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

from kaa.special_forms import Lambda, Macro
from kaa.types import List
