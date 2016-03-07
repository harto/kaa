from kaa.types import List, Namespace

# todo: should be a macro
def assert_(val):
    assert val

def list_(*xs):
    return List(xs)

def print_(*xs):
    print(str_(*xs))

def str_(*xs):
    return ' '.join(map(str, xs))

add = lambda a, b: a + b
eql = lambda a, b: a == b
mul = lambda a, b: a * b

def namespace():
    return Namespace({'True': True,
                      'False': False,
                      'None': None,
                      '+': add,
                      '=': eql,
                      '*': mul,
                      'assert': assert_,
                      'list': list_,
                      'print': print_,
                      'str': str_})
