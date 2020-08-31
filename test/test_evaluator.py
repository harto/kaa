from pytest import fixture, raises

from kaa.evaluator import Evaluator, UnboundSymbol, WrongArity
from kaa.ns import Namespace
from kaa.parser import Raise
from testing_utils import read


@fixture(name='evaluator')
def evaluator_fixture():
    return Evaluator(Namespace('test'))


def test_lambda_invocation_wrong_arity(evaluator):
    with raises(WrongArity):
        evaluator.evaluate(read('((lambda ()) 1)'))


def test_raises(evaluator):
    class SpecificException(Exception):
        pass
    with raises(SpecificException):
        evaluator.evaluate(Raise(SpecificException('oh no')))
    with raises(RuntimeError, match='oh no'):
        evaluator.evaluate(Raise('oh no'))


def test_unbound_symbol_raises_error(evaluator):
    with raises(UnboundSymbol):
        evaluator.evaluate(read('foo'))


def test_python_literal(evaluator):
    assert evaluator.evaluate(read('py/Exception')) == Exception
