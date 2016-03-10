from kaa import formatter

class Namespace(object):

    def __init__(self, bindings = None, parent = None):
        self.bindings = bindings or {}
        self.parent = parent

    def __contains__(self, k):
        return k in self.bindings or \
            (self.parent and k in self.parent)

    def __getitem__(self, k):
        try:
            return self.bindings[k]
        except KeyError:
            if self.parent:
                return self.parent[k]
            else:
                raise

    def __setitem__(self, k, v):
        self.bindings[k] = v

    def flatten(self):
        if self.parent is None:
            return self.bindings
        bindings = self.bindings.copy()
        bindings.update(self.parent.bindings)
        return bindings

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

from kaa.evaluator import eval
