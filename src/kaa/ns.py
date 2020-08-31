from importlib import import_module
import os
import sys

from kaa.core import Symbol
from kaa.env import Environment
from kaa.evaluator import Evaluator
from kaa.reader import Reader


class Namespace:
    def __init__(self, name, import_core=True):
        self.name = name
        self.defs = Environment()
        self.imported_namespaces = {}  # ns name -> Namespace
        self.imported_modules = {}     # module name -> module
        self.imported_symbol_refs = {} # local name -> imported name
        self.imported_symbols = set()  # imported names
        self.ns_aliases = {}           #
        if name != 'kaa.core' and import_core:
            self.import_ns(self.load_ns('kaa.core'), '*')

    def load_ns(self, name):  # pylint: disable=no-self-use
        if name.startswith('.'):
            # To implement relative imports we need to track the current
            # namespace and where it is in the filesystem.
            raise NotImplementedError('relative imports not yet implemented')
        filename = f'{name.replace(".", "/")}.lisp'
        candidates = (os.path.join(dirname, filename) for dirname in sys.path)
        try:
            path = next(path for path in candidates if os.path.exists(path))
        except StopIteration:
            raise ImportError(f'"{filename}" not found for namespace {name}', name=name) from None
        ns = Namespace(name)
        with open(path) as f:
            Evaluator(ns).evaluate_all(Reader(ns).read_file(f))
        return ns

    def import_ns(self, ns, symbol_names, alias=None):
        self.imported_namespaces[ns.name] = ns
        if symbol_names == '*' or symbol_names:
            importables = ns.exportables()
            imported_symbols = importables if symbol_names == '*' \
                else tuple(Symbol(name, ns.name) for name in symbol_names)
            for sym in imported_symbols:
                self.import_symbol(sym)
        if alias:
            self.ns_aliases[alias] = ns.name

    def load_module(self, mod_name):  # pylint: disable=no-self-use
        if mod_name.startswith('.'):
            # To implement relative imports we need to track the current
            # namespace and where it is in the filesystem.
            raise NotImplementedError('relative imports not yet implemented')
        return import_module(mod_name)

    def import_module(self, mod, attrs=None, alias=None):
        self.imported_modules[mod.__name__] = mod
        if attrs == '*':
            raise NotImplementedError('`import *` not yet implemented for modules')
        if attrs:
            for attr in attrs:
                self.import_symbol(Symbol(attr, mod.__name__))
        if alias:
            self.ns_aliases[alias] = mod.__name__

    def import_symbol(self, sym):
        # TODO: handle name not found in module
        # TODO: warn if symbol collision with self.defs
        self.imported_symbol_refs[Symbol(sym.name, self.name)] = sym
        self.imported_symbols.add(sym)

    def resolve(self, sym):
        if sym.ns is None:
            sym = sym.in_ns(self.name)
        if sym in self.imported_symbol_refs:
            return self.imported_symbol_refs[sym]
        if sym.ns in self.ns_aliases:
            return sym.in_ns(self.ns_aliases[sym.ns])
        return sym

    def __eq__(self, other):
        return isinstance(other, Namespace) and other.name == self.name

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name)  # TODO: is this sufficient?

    def __contains__(self, sym):
        try:
            self[sym]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, sym):
        try:
            return self.defs[sym]
        except KeyError:
            pass
        try:
            return self.imported_namespaces[sym.ns][sym]
        except KeyError:
            pass
        mod = self.imported_modules[sym.ns]
        try:
            return getattr(mod, sym.name)
        except AttributeError as ex:
            raise KeyError from ex

    def __setitem__(self, sym, value):
        assert isinstance(sym, Symbol), f'{sym} is not a Symbol'
        if sym.ns is None:
            sym = Symbol(sym.name, self.name, sym.meta)
        assert sym.ns == self.name, f'cannot define {sym} via namespace {self.name}'
        self.defs[sym] = value

    def exportables(self):
        return (sym for sym in self.defs if sym.ns == self.name)
