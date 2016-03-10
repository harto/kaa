from kaa import builtins, evaluator
from kaa.charbuf import CharBuffer, LineIterCharBuffer
from kaa.reader import Reader
from os import path

class Runtime(object):

    LAST_RESULT = '^'

    def __init__(self):
        self.ns = builtins.namespace()
        self._load_stdlib()

    def _load_stdlib(self):
        with open(path.join(path.dirname(__file__), 'lib', 'core.lisp')) as f:
            return self.eval_lines(f)

    def eval_lines(self, lines):
        return self.eval_all(Reader().read_all(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval_all(Reader().read_all(CharBuffer(s)))

    def eval_all(self, exprs):
        result = None
        for expr in exprs:
            result = self.eval(expr)
        return result

    def eval(self, expr):
        self.ns[self.LAST_RESULT] = result = evaluator.eval(expr, self.ns)
        return result
