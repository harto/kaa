from kaa.ast import *

class Scope(object):

    def __init__(self, declared = None, parent = None):
        self.declared = declared or set()
        self.parent = parent

    def __contains__(self, name):
        return name in self.declared or \
            (self.parent and name in self.parent)

def free_vars(expr, scope = Scope()):
    if isinstance(expr, Symbol):
        if expr.name in scope:
            return set()
        else:
            return set([expr.name])
    elif isinstance(expr, List):
        return collect_free_vars(expr, scope)
    elif isinstance(expr, Body):
        return collect_free_vars(expr.exprs, scope)
    elif isinstance(expr, Lambda):
        scope = Scope(declared=set(expr.param_names), parent=scope)
        return free_vars(expr.body, scope)
    elif isinstance(expr, Let):
        # fixme: let bindings RHS may have free vars
        scope = Scope(declared=set(k for k, _ in let.bindings), parent=scope)
        return free_vars(expr.body, scope)
    else:
        return set()

def collect_free_vars(iterable, scope):
    return reduce(set.union,
                  (free_vars(expr, scope) for expr in iterable),
                  set())
