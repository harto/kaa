from kaa.ast import *

class Scope(object):

    def __init__(self, declared = None, parent = None):
        self.declared = declared or set()
        self.parent = parent

    def __contains__(self, name):
        return name in self.declared or \
            (self.parent and name in self.parent)

    def declare(self, x):
        self.declared.add(x)

def free_vars(expr, scope = Scope()):
    if isinstance(expr, Symbol):
        if expr.name in scope:
            return set()
        else:
            return set([expr.name])
    elif isinstance(expr, Lambda):
        scope = Scope(declared=set(expr.param_names), parent=scope)
        return free_vars(expr.body, scope)
    elif isinstance(expr, Let):
        return free_vars_in_let(expr, scope)
    try: # iterable
        return reduce(set.union,
                      (free_vars(e, scope) for e in expr),
                      set())
    except TypeError:
        return set()

def free_vars_in_let(let, scope):
    scope = Scope(parent=scope)
    result = set()
    for k, expr in let.bindings:
        scope.declare(k)
        result.update(free_vars(expr, scope))
    result.update(free_vars(let.body, scope))
    return result
