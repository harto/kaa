from pytest import raises

from kaa.env import Environment


def test_define_global():
    root = Environment()
    assert 'foo' not in root
    root['foo'] = 'bar'
    assert 'foo' in root
    assert root['foo'] == 'bar'

    scope = root.push_bindings({'foo': 'local-bar'})
    assert scope['foo'] == 'local-bar'
    assert root['foo'] == 'bar'
    with raises(AssertionError):
        scope['foo'] = 'something-else'


def test_lookup():
    root = Environment({'foo': 'bar'})
    assert root['foo'] == 'bar'
    scope = root.push_bindings({'baz': 'bla'})
    assert 'baz' not in root
    assert scope['foo'] == 'bar'
    assert scope['baz'] == 'bla'
