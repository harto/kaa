# fixme: figure out where to put this
def eval(expr, ns):
    try:
        return expr.eval(ns)
    except AttributeError:
        return expr
