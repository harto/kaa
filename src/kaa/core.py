from functools import reduce
import json


def serialize(val):
    # We don't use repr to serialize strings, because that sometimes results in
    # single quotes. We always want double-quoted strings.
    return json.dumps(val) if isinstance(val, str) else repr(val)


class List(list):
    def __init__(self, items=(), meta=None):
        super().__init__(items)
        self.meta = meta or {}

    def __str__(self):
        return '(%s)' % ' '.join(map(str, self))

    def __repr__(self):
        return '(%s)' % ' '.join(map(serialize, self))

    # Ensure slicing returns new List instance
    def __getitem__(self, k):
        val = super().__getitem__(k)
        return List(super().__getitem__(k)) if isinstance(k, slice) else val


class Symbol:
    def __init__(self, name, ns=None, meta=None):
        assert isinstance(name, str)
        assert ns is None or isinstance(ns, str)
        self.name = name
        self.ns = ns
        self.meta = meta or {}

    def in_ns(self, ns):
        return Symbol(self.name, ns, self.meta)

    def __eq__(self, other):
        return isinstance(other, Symbol) \
            and other.name == self.name \
            and other.ns == self.ns

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.name, self.ns))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f'{self.ns}/{self.name}' if self.ns else self.name


def concat(*lists):
    return reduce(lambda x, y: List((x or []) + (y or [])), lists)


def empty(val):
    try:
        next(iter(val))
    except StopIteration:
        return True
    except TypeError:
        return False
    return False


def is_list(val):
    return isinstance(val, List)


def is_symbol(val):
    return isinstance(val, Symbol)


def list_(*items):
    return List(items)


def first(val):
    if val is None:
        return None
    try:
        return next(iter(val))
    except StopIteration:
        return None


def not_(val):
    return not val


def print_(*vals):
    print(*(str(v) for v in vals), sep=' ', end='')


def println(*vals):
    print(*(str(v) for v in vals), sep=' ')


def rest(val):
    if val is None:
        return None
    if is_list(val):
        return val[1:]
    raise ValueError(f"can't get rest of {type(val)}")


def str_(*vals):
    return ''.join(map(str, vals))


# TODO: does this need to know the current namespace?
def symbol(name):
    return Symbol(str(name))


def add(*xs):
    return reduce(lambda acc, x: acc + x, xs, 0)


def eql(*xs):
    return all(x == xs[0] for x in xs)


def mul(*xs):
    return reduce(lambda acc, x: acc * x, xs, 1)


def div(*xs):
    return reduce(lambda acc, x: acc / x, xs, 1)
