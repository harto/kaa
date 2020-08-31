from kaa.core import Symbol
from kaa.ns import Namespace


def test_define():
    ns = Namespace('testing', import_core=False)
    sym = Symbol('foo', 'testing')
    ns[sym] = 'bar'
    assert ns[sym] == 'bar'


def test_redefine():
    ns = Namespace('testing', import_core=False)
    sym = Symbol('foo', 'testing')
    ns[sym] = 'bar'
    ns[sym] = 'new-value'
    assert ns[sym] == 'new-value'


def test_resolve_unqualified_unknown():
    ns = Namespace('testing', import_core=False)
    sym = Symbol('foo')
    assert ns.resolve(sym) == sym.in_ns('testing')


def test_resolve_unqualified_def():
    ns = Namespace('testing', import_core=False)
    ns[Symbol('foo', 'testing')] = 'bar'
    sym = Symbol('foo')
    assert ns.resolve(sym) == sym.in_ns('testing')


def test_resolve_unqualified_import_ref():
    ns = Namespace('testing', import_core=True)
    sym = Symbol('defun')
    assert ns.resolve(sym) == sym.in_ns('kaa.core')


def test_resolve_qualified_import_ref():
    ns = Namespace('testing', import_core=True)
    sym = Symbol('defun', 'kaa.core')
    assert ns.resolve(sym) == sym


def test_resolve_qualified_with_alias():
    ns = Namespace('testing', import_core=False)
    core = ns.load_ns('kaa.core')
    ns.import_ns(core, (), 'core')
    sym = Symbol('asdfasdf', 'core')
    assert ns.resolve(sym) == sym.in_ns('kaa.core')


def test_resolve_qualified_with_unknown():
    ns = Namespace('testing', import_core=False)
    sym = Symbol('asfasdf', 'unknown')
    assert ns.resolve(sym) == sym


def test_lookup():
    ns = Namespace('testing')
    ns[Symbol('x', 'testing')] = 42
    assert ns[Symbol('x', 'testing')] == 42
    assert ns[Symbol('defun', 'kaa.core')] is not None
