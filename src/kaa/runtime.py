from kaa.evaluator import Evaluator
from kaa.ns import Namespace
from kaa.reader import Reader


class Runtime:
    def __init__(self):
        self.ns = Namespace('main')

    def eval_file(self, f):
        return self.eval_all(Reader(self.ns).read_file(f))

    def eval_string(self, s):
        return self.eval_all(Reader(self.ns).read_string(s))

    def eval_all(self, exprs):
        return Evaluator(self.ns).evaluate_all(exprs)
