class Expr(object):

    def eval(self, env):
        return self

class Def(Expr):

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.__dict__ == self.__dict__

    def eval(self, env):
        return self.symbol.bind(self.value, env)

# todo: replace this with some kind of Python-lambda interop syntax
class Func(Expr):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        result = self.fn(*args)
        return result

class Lambda(Expr):

    # todo: capture lexical bindings
    def __init__(self, params, body = []):
        self.params = params
        self.body = body

    def __call__(self, env, *args):
        num_expected = len(self.params)
        num_received = len(args)
        if num_received != num_expected:
            raise ArityException('expected %d args, got %d' % (num_expected,
                                                               num_received))
        # todo: replace with generic binding mechanism, e.g. `let`
        param_names = [symbol.name for symbol in self.params]
        prev_bindings = dict((k, env[k]) for k in param_names if k in env)
        tmp_bindings = dict(zip(param_names, args))
        env.update(tmp_bindings)
        result = Nil
        try:
            for expr in self.body:
                result = expr.eval(env)
        finally:
            env.update(prev_bindings)
        return result

class ArityException(Exception): pass

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

    def eval(self, env):
        if not self.members:
            return self
        fn = self[0].eval(env)
        args = [expr.eval(env) for expr in self[1:]]
        # fixme: figure out consistent function call convention
        if isinstance(fn, Lambda):
            return fn(env, *args)
        else:
            return fn(*args)

class Symbol(Expr):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.name == self.name

    def bind(self, value, env):
        env[self.name] = value.eval(env)
        return self.eval(env)

    def eval(self, env):
        try:
            return env[self.name]
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
