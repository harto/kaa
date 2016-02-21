import builtins
from charbuf import CharBuffer, LineIterCharBuffer
from compiler import compile
from reader import Reader

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
            result = compile(expr).eval(self.ns)
        self.ns[self.LAST_RESULT] = result
        return result
