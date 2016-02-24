def eval(expr, ns):
    try:
        return expr.eval(ns)
    except AttributeError:
        pass

    if is_valid_native_type(expr):
        return expr

    raise UnevaluatableTypeException(type(expr))

def eval_all(exprs, ns):
    result = None
    for e in exprs:
        result = eval(e, ns)
        return result

def is_valid_native_type(expr):
    return type(expr) in (int, str) \
        or callable(expr)

class UnevaluatableTypeException(Exception): pass
