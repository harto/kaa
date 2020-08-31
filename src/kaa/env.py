class Environment:
    def __init__(self, bindings=None, parent=None):
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
            raise

    def __setitem__(self, k, val):
        assert self.parent is None, 'attempted to set value in non-root environment'
        self.bindings[k] = val

    def __iter__(self):
        return iter(self.bindings)

    def push_bindings(self, bindings=None):
        return Environment(bindings=bindings, parent=self)
