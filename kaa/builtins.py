from kaa.types import List, Namespace

def list_(*xs):
    return List(xs)

def not_(val):
    return not val

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
                      'list': list_,
                      'not': not_,
                      'print': print_,
                      'str': str_})
