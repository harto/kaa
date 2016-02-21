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

class Func(Expr):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        result = self.fn(*args)
        return result

class List(Expr):

    def __init__(self, members = None):
        self.members = members or []

    def __getitem__(self, i):
        return self.members[i]

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.members == self.members

    def append(self, x):
        self.members.append(x)

    def eval(self, env):
        if not self.members:
            return self
        fn = self[0].eval(env)
        args = [expr.eval(env) for expr in self[1:]]
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
