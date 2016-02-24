from ast import Namespace

# todo: should be a macro
def assert_(val):
    assert val

def print_(*xs):
    print(' '.join(map(str, xs)))

add = lambda a, b: a + b
eql = lambda a, b: a == b
mul = lambda a, b: a * b

def namespace():
    return Namespace({'+': add,
                      '=': eql,
                      '*': mul,
                      'assert': assert_,
                      'print': print_})
