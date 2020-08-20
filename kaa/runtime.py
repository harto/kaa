import os.path

from kaa.core import builtins
from kaa.env import Environment
from kaa.evaluator import evaluate_all
from kaa.reader import Reader
from kaa.stream import CharStream, FileStream, MultilineStream


class Runtime:
    def __init__(self):
        self.env = Environment()
        self.bootstrap()

    def bootstrap(self):
        for name, value in builtins().items():
            self.env.define_global(name, value)
        self.eval_file(os.path.join(os.path.dirname(__file__), 'core.lisp'))

    def eval_file(self, path):
        with open(path) as f:
            return self.eval_all(Reader().read_all(FileStream(f)))

    def eval_lines(self, lines):
        return self.eval_all(Reader().read_all(MultilineStream(lines)))

    def eval_string(self, s):
        return self.eval_all(Reader().read_all(CharStream(s)))

    def eval_all(self, exprs):
        return evaluate_all(exprs, self.env)
