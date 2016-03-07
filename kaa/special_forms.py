from kaa.evaluator import eval
from kaa.types import Namespace

def eval_all(exprs, ns):
    result = None
    for e in exprs:
        result = eval(e, ns)
        return result

class Def(object):

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        result = ns[self.symbol.name] = eval(self.value, ns)
        return result

class If(object):

    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def eval(self, ns):
        if eval(self.cond, ns):
            return eval(self.then, ns)
        elif self.else_:
            return eval(self.else_, ns)
        else:
            return None

class Lambda(object):

    def __init__(self, param_names, body):
        self.param_names = param_names
        self.body = body
        self.lexical_bindings = None

    def __call__(self, ns, *args):
        self._check_arity(args)
        if self.lexical_bindings:
            ns = Namespace(bindings=self.lexical_bindings,
                           parent=ns)
        ns = Namespace(bindings=dict(zip(self.param_names, args)),
                       parent=ns)
        return eval_all(self.body, ns)

    def _check_arity(self, args):
        _check_arity(self.param_names, args)

    def eval(self, ns):
        if self.lexical_bindings is None:
            # could optimise this, e.g. don't capture if no free vars
            self.lexical_bindings = ns
        return self

class Let(object):

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, ns):
        return eval_all(self.body, self.with_bindings(ns))

    def with_bindings(self, ns):
        ns = Namespace(parent=ns)
        for name, expr in self.bindings:
            ns[name] = eval(expr, ns)
        return ns

class Macro(object):

    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __call__(self, ns, *args):
        _check_arity(self.params, args)
        ns = Namespace(bindings=self._locals(args), parent=ns)
        return eval_all(self.body, ns)

    def _locals(self, args):
        return dict(zip([sym.name for sym in self.params], args))

class Raise(object):

    def __init__(self, exception):
        self.exception = exception

    def eval(self, ns):
        if isinstance(self.exception, str):
            raise Exception(self.exception)
        else:
            raise eval(self.exception, ns)

class Quote(object):

    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, _):
        return self.quoted

def _check_arity(params, args):
    num_expected = len(params)
    num_received = len(args)
    if num_received != num_expected:
        raise ArityException('expected %d args, got %d' % (num_expected,
                                                           num_received))


class ArityException(Exception): pass
