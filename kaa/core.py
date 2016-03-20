from kaa import formatter
from kaa.evaluator import eval

class List(object):

    def __init__(self, members = None, meta = None):
        self.members = members or []
        self.meta = meta or {}

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

    def __init__(self, name, meta = None):
        self.name = name
        self.meta = meta or {}

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
            raise UnboundSymbolException(self)

class UnboundSymbolException(Exception):

    def __init__(self, sym):
        try:
            msg = '%s at %s' % (sym.name, sym.meta['source'])
        except KeyError:
            msg = sym.name
        Exception.__init__(self, msg)

def concat(*Ls):
    return reduce(lambda x, y: List((x and list(x.members) or []) +
                                    (y and list(y.members) or [])),
                  Ls)

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
    return ''.join(map(str, xs))

def symbol(name):
    return Symbol(str(name))

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
            'count': len,
            'first': first,
            'list': list_,
            'list?': is_list,
            'not': not_,
            'print': print_,
            'rest': rest,
            'str': str_,
            'symbol': symbol,
            'symbol?': is_symbol}
