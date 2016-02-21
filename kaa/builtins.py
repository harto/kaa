from ast import Func, Value

# todo: should be a macro
def _assert(val):
    assert val.get()

# todo: clean up boilerplate
add = Func(lambda a, b: Value(a.get() + b.get()))
equals = Func(lambda a, b: Value(a.get() == b.get()))
multiply = Func(lambda a, b: Value(a.get() * b.get()))

def pr(*xs):
    print(' '.join(map(str, xs)))

# todo: build dynamically? using e.g. decorators
def env():
    return {'+': add,
            '=': equals,
            '*': multiply,
            'assert': _assert,
            'print': pr}
