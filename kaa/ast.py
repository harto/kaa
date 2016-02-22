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

class Expr(object):

    def eval(self, ns):
        return self

class Body(Expr):

    def __init__(self, exprs = []):
        self.exprs = exprs

    def eval(self, ns):
        result = Nil
        for expr in self.exprs:
            result = expr.eval(ns)
        return result

class Def(Expr):

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        return self.symbol.bind(self.value, ns)

# todo: replace this with some kind of Python-lambda interop syntax
class Func(Expr):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        result = self.fn(*args)
        return result

class Lambda(Expr):

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
        return self.body.eval(ns)

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

class Let(Expr):

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, ns):
        return self.body.eval(self.bindings.overlay_onto(ns))

class LetBindings(object):

    def __init__(self, pairs):
        self.pairs = pairs

    def names(self):
        return [sym.name for sym, _ in self.pairs]

    def overlay_onto(self, ns):
        ns = Namespace(parent=ns)
        for sym, val in self.pairs:
            ns[sym.name] = val.eval(ns)
        return ns

class List(Expr):

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
        fn = self[0].eval(ns)
        args = [expr.eval(ns) for expr in self[1:]]
        # fixme: figure out consistent function call convention
        if isinstance(fn, Lambda):
            return fn(ns, *args)
        else:
            return fn(*args)

class Symbol(Expr):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.name == self.name

    def bind(self, value, ns):
        ns[self.name] = value.eval(ns)
        return self.eval(ns)

    def eval(self, ns):
        try:
            return ns[self.name]
        except KeyError:
            raise UnboundSymbolException(self.name)

class UnboundSymbolException(Exception): pass

class Value(Expr):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.value == self.value

    def __str__(self):
        return str(self.value)

    def get(self):
        return self.value

Nil = Value(None)

from kaa import analyzer
