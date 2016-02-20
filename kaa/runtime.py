import builtins
from charbuf import CharBuffer, LineIterCharBuffer
from reader import Reader

class Runtime(object):

    def __init__(self):
        self.env = builtins.env()

    def eval_lines(self, lines):
        return self.eval(Reader().read(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval(Reader().read(CharBuffer(s)))

    def eval(self, expressions):
        result = None
        for expr in expressions:
            result = expr.eval(self.env)
        return result
