from functools import reduce

from kaa.string import format_str


def serialize(val):
    return format_str(val) if isinstance(val, str) else repr(val)


class List:
    def __init__(self, members=None, meta=None):
        self.members = members or []
        self.meta = meta or {}

    def __eq__(self, other):
        return isinstance(other, List) \
            and list(other.members) == list(self.members)

    def __getitem__(self, i):
        return self.members[i]

    def __len__(self):
        return len(self.members)

    def __str__(self):
        return '(%s)' % ' '.join(map(str, self.members))

    def __repr__(self):
        return '(%s)' % ' '.join(map(serialize, self.members))

    def append(self, item):
        self.members.append(item)

    def empty(self):
        return not self.members

    def eval(self, _ns):
        return self

    def first(self):
        return None if self.empty() else self.members[0]

    def rest(self):
        return List(self.members[1:]) if len(self) > 1 else None


class Symbol:
    def __init__(self, name, meta=None):
        self.name = name
        self.meta = meta or {}

    def __eq__(self, other):
        return isinstance(other, Symbol) \
            and other.name == self.name

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def eval(self, ns):
        try:
            return ns[self.name]
        except KeyError:
            raise UnboundSymbol(self)


class UnboundSymbol(Exception):
    def __init__(self, sym):
        try:
            msg = '%s at %s' % (sym.name, sym.meta['source'])
        except KeyError:
            msg = sym.name
        Exception.__init__(self, msg)


def concat(*Ls):
    # return List(reduce(lambda x, y: (x and x.members or []) + (y and y.members or []),
    #                    colls))
    return reduce(lambda x, y: List((x and list(x.members) or []) +
                                    (y and list(y.members) or [])),
                  Ls)



def empty(coll):
    return coll.empty()


def is_list(val):
    return isinstance(val, List)


def is_symbol(val):
    return isinstance(val, Symbol)


def list_(*items):
    return List(items)


def first(coll):
    try:
        return coll.first()
    except AttributeError:
        return None


def not_(val):
    return not val


def print_(*vals):
    print(*(str(v) for v in vals), sep=' ', end='')


def println(*vals):
    print(*(str(v) for v in vals), sep=' ')


def rest(coll):
    try:
        return coll.rest()
    except AttributeError:
        return None


def str_(*vals):
    return ''.join(map(str, vals))


def symbol(name):
    return Symbol(str(name))


def add(*xs):
    return reduce(lambda acc, x: acc + x, xs, 0)


def eql(*xs):
    return all(x == xs[0] for x in xs)


def mul(*xs):
    return reduce(lambda acc, x: acc * x, xs, 1)


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
            'println': println,
            'rest': rest,
            'str': str_,
            'symbol': symbol,
            'symbol?': is_symbol}
