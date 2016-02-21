import builtins
from charbuf import CharBuffer, LineIterCharBuffer
from compiler import Compiler
from reader import Reader

class Runtime(object):

    LAST_RESULT = '^'

    def __init__(self):
        self.env = builtins.env()

    def eval_lines(self, lines):
        return self.eval(Reader().read(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval(Reader().read(CharBuffer(s)))

    def eval(self, expressions):
        result = None
        for expr in Compiler().compile(expressions):
            result = expr.eval(self.env)
        self.env[self.LAST_RESULT] = result
        return result
