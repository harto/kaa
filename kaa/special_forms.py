from kaa.evaluator import eval, eval_all
from kaa.types import Namespace

class Def(object):

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        result = ns[self.symbol.name] = eval(self.value, ns)
        return result

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
        num_expected = len(self.param_names)
        num_received = len(args)
        if num_received != num_expected:
            raise ArityException('expected %d args, got %d' % (num_expected,
                                                               num_received))

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

class ArityException(Exception): pass