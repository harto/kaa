from kaa.core import List, Symbol


def test_list_python_interop():
    l = List((1, 2))
    assert l[1] == 2
    assert isinstance(l[1:], List)


def test_symbol_equality():
    assert Symbol('foo') == Symbol('foo')
    assert Symbol('foo') != Symbol('bar')
    assert Symbol('foo') != Symbol('foo', 'ns')
    assert Symbol('foo', 'ns1') != Symbol('foo', 'ns2')
    assert Symbol('foo', 'ns') == Symbol('foo', 'ns')
