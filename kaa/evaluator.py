def eval(expr, ns):
    try:
        return expr.eval(ns)
    except AttributeError:
        return expr

def eval_all(exprs, ns):
    result = None
    for e in exprs:
        result = eval(e, ns)
        return result
