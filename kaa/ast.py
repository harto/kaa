import builtins


class Expr(object):

    def eval(self, env):
        return self


class Func(Expr):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        result = self.fn(*args)
        return result


class List(Expr):

    def __init__(self, members = None):
        self.members = members or []

    def append(self, x):
        self.members.append(x)

    def eval(self, env):
        if not self.members:
            return []
        fn = self.members[0].eval(env)
        args = [expr.eval(env) for expr in self.members[1:]]
        return fn(*args)


class Symbol(Expr):

    def __init__(self, name):
        self.name = name

    def eval(self, env):
        try:
            return env[self.name]
        except KeyError:
            raise Exception('undefined symbol: %s' % self.name)


class Value(Expr):

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def __str__(self):
        return str(self.value)
