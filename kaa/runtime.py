from kaa import builtins, evaluator
from kaa.charbuf import CharBuffer, FileCharBuffer, LineIterCharBuffer
from kaa.reader import Reader
from os import path

class Runtime(object):

    def __init__(self):
        self.ns = builtins.namespace()
        self._load_stdlib()

    def _load_stdlib(self):
        self.eval_file(path.join(path.dirname(__file__), 'lib', 'core.lisp'))

    def eval_file(self, path):
        with open(path) as f:
            return self.eval_all(Reader().read_all(FileCharBuffer(f)))

    def eval_lines(self, lines):
        return self.eval_all(Reader().read_all(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval_all(Reader().read_all(CharBuffer(s)))

    def eval_all(self, exprs):
        result = None
        for expr in exprs:
            result = evaluator.eval(expr, self.ns)
        return result
