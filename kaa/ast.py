from evaluator import eval

class Namespace(object):

    def __init__(self, bindings = None, parent = None):
        self.bindings = bindings or {}
        self.parent = parent

    def __contains__(self, k):
        return k in self.bindings or \
            (self.parent and k in self.parent)

    def __getitem__(self, k):
        try:
            return self.bindings[k]
        except KeyError:
            if self.parent:
                return self.parent[k]
            else:
                raise

    def __setitem__(self, k, v):
        self.bindings[k] = v

    def flatten(self):
        if self.parent is None:
            return self.bindings
        bindings = self.bindings.copy()
        bindings.update(self.parent.bindings)
        return bindings

class Body(object):

    def __init__(self, exprs = []):
        self.exprs = exprs

    def eval(self, ns):
        result = None
        for expr in self.exprs:
            result = eval(expr, ns)
        return result

class Def(object):

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        return self.symbol.bind(self.value, ns)

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
        return eval(self.body, ns)

    def _check_arity(self, args):
        num_expected = len(self.param_names)
        num_received = len(args)
        if num_received != num_expected:
            raise ArityException('expected %d args, got %d' % (num_expected,
                                                               num_received))

    def eval(self, ns):
        self.capture_lexical_bindings(ns)
        return self

    def capture_lexical_bindings(self, ns):
        if self.lexical_bindings is not None:
            return
        self.lexical_bindings = {}
        free_vars = analyzer.free_vars(self)
        for name in free_vars:
            if name in ns:
                self.lexical_bindings[name] = ns[name]

class ArityException(Exception): pass

class Let(object):

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, ns):
        return eval(self.body, self.with_bindings(ns))

    def with_bindings(self, ns):
        ns = Namespace(parent=ns)
        for name, expr in self.bindings:
            ns[name] = eval(expr, ns)
        return ns

class List(object):

    def __init__(self, members = None):
        self.members = members or []

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.members == self.members

    def __getitem__(self, i):
        return self.members[i]

    def __len__(self):
        return len(self.members)

    def append(self, x):
        self.members.append(x)

    def eval(self, ns):
        if not self.members:
            return self
        fn = eval(self[0], ns)
        args = [eval(expr, ns) for expr in self[1:]]
        if isinstance(fn, Lambda):
            return fn(ns, *args)
        else:
            return fn(*args)

class Symbol(object):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.name == self.name

    def bind(self, value, ns):
        ns[self.name] = eval(value, ns)
        return self.eval(ns)

    def eval(self, ns):
        try:
            return ns[self.name]
        except KeyError:
            raise UnboundSymbolException(self.name)

class UnboundSymbolException(Exception): pass

from kaa import analyzer
