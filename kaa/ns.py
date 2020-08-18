class Namespace:
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

    def define_global(self, name, val):
        if self.parent:
            return self.parent.define_global(name, val)
        self.bindings[name] = val
        return val

    def push(self, bindings=None):
        return Namespace(bindings=bindings, parent=self)
