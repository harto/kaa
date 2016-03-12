from kaa import formatter
from kaa.evaluator import eval

class List(object):

    def __init__(self, members = None, source_meta = None):
        self.members = members or []
        self.source_meta = source_meta

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.members == self.members

    def __getitem__(self, i):
        return self.members[i]

    def __len__(self):
        return len(self.members)

    def __str__(self):
        return '(%s)' % ' '.join(map(formatter.format, self.members))

    def append(self, x):
        self.members.append(x)

    def eval(self, ns):
        return self

class Symbol(object):

    def __init__(self, name, source_meta = None):
        self.name = name
        self.source_meta = source_meta

    def __eq__(self, other):
        return type(other) == type(self) \
            and other.name == self.name

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def eval(self, ns):
        try:
            return ns[self.name]
        except KeyError:
            raise UnboundSymbolException(
                '%s at %s' % (self.name, self.source_meta))

class UnboundSymbolException(Exception): pass

def is_list(x):
    return isinstance(x, List)

def is_symbol(x):
    return isinstance(x, Symbol)

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

def builtins():
    return {'True': True,
            'False': False,
            'None': None,
            '+': add,
            '=': eql,
            '*': mul,
            'list': list_,
            'list?': is_list,
            'not': not_,
            'print': print_,
            'str': str_,
            'symbol?': is_symbol}
