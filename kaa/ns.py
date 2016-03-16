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

    def define_global(self, k, v):
        if self.parent:
            return self.parent.define_global(k, v)
        else:
            self.bindings[k] = v
            return v

    def push(self, bindings = None):
        return Namespace(bindings=bindings, parent=self)
