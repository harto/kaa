import os.path

from kaa import evaluator, core
from kaa.ns import Namespace
from kaa.reader import Reader
from kaa.stream import CharStream, FileStream, MultilineStream


class Runtime:
    def __init__(self):
        self.ns = Namespace()
        self._load_core()

    def _load_core(self):
        for name, value in core.builtins().items():
            self.ns.define_global(name, value)
        self.eval_file(os.path.join(os.path.dirname(__file__), 'core.lisp'))

    def eval_file(self, path):
        with open(path) as f:
            return self.eval_all(Reader().read_all(FileStream(f)))

    def eval_lines(self, lines):
        return self.eval_all(Reader().read_all(MultilineStream(lines)))

    def eval_string(self, s):
        return self.eval_all(Reader().read_all(CharStream(s)))

    def eval_all(self, exprs):
        result = None
        for expr in exprs:
            result = evaluator.evaluate(expr, self.ns)
        return result
