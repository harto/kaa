def eval(expr, ns):
    try:
        return expr.eval(ns)
    except AttributeError:
        if is_evaluatable(expr):
            return expr
        else:
            raise UnevaluatableTypeException(type(expr))

def is_evaluatable(expr):
    return type(expr) in (int, str) \
        or callable(expr)

class UnevaluatableTypeException(Exception): pass
