import builtins
from kaa.charbuf import CharBuffer, LineIterCharBuffer
from kaa.compiler import compile
from kaa.evaluator import eval
from kaa.reader import Reader

class Runtime(object):

    LAST_RESULT = '^'

    def __init__(self):
        self.ns = builtins.namespace()

    def eval_lines(self, lines):
        return self.eval(Reader().read(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval(Reader().read(CharBuffer(s)))

    def eval(self, expressions):
        result = None
        for expr in expressions:
            result = eval(compile(expr), self.ns)
        self.ns[self.LAST_RESULT] = result
        return result
