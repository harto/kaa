from kaa.runtime import Runtime


def test_initialization():
    runtime = Runtime()
    assert runtime.eval_string('(+ 1 2)') == 3
