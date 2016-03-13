from kaa import formatter
from kaa.evaluator import eval

class List(object):

    def __init__(self, members = None, source_meta = None):
        self.members = members or []
        self.source_meta = source_meta

    def __eq__(self, other):
        return type(other) == type(self) \
            and list(other.members) == list(self.members)

    def __getitem__(self, i):
        return self.members[i]

    def __len__(self):
        return len(self.members)

    def __str__(self):
        return '(%s)' % ' '.join(map(formatter.format, self.members))

    def append(self, x):
        self.members.append(x)

    def concat(self, other):
        return List(self.members + other.members)

    def empty(self):
        return len(self) == 0

    def eval(self, ns):
        return self

    def first(self):
        if not self.empty():
            return self.members[0]

    def rest(self):
        if len(self.members) > 1:
            return List(self.members[1:])

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

def concat(*Ls):
    return reduce(List.concat, Ls)

def empty(L):
    return L.empty()

def is_list(x):
    return isinstance(x, List)

def is_symbol(x):
    return isinstance(x, Symbol)

def list_(*xs):
    return List(xs)

def first(L):
    return is_list(L) and L.first() or None

def not_(val):
    return not val

def print_(*xs):
    print(str_(*xs))

def rest(L):
    return is_list(L) and L.rest() or None

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
            'concat': concat,
            'first': first,
            'list': list_,
            'list?': is_list,
            'not': not_,
            'print': print_,
            'rest': rest,
            'str': str_,
            'symbol?': is_symbol}
