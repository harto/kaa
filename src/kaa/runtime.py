import os.path

from kaa.core import builtins
from kaa.env import Environment
from kaa.evaluator import Evaluator
from kaa.reader import Reader


class Runtime:
    def __init__(self):
        self.env = Environment()
        self.bootstrap()

    def bootstrap(self):
        for name, value in builtins().items():
            self.env.define_global(name, value)
        with open(os.path.join(os.path.dirname(__file__), 'core.lisp')) as f:
            self.eval_file(f)

    def eval_file(self, f):
        return self.eval_all(Reader.read_file(f))

    def eval_string(self, s):
        return self.eval_all(Reader.read_string(s))

    def eval_all(self, exprs):
        return Evaluator(self.env).evaluate_all(exprs)
