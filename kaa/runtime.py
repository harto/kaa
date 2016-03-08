from kaa import builtins, evaluator
from kaa.charbuf import CharBuffer, LineIterCharBuffer
from kaa.reader import Reader

class Runtime(object):

    LAST_RESULT = '^'

    def __init__(self):
        self.ns = builtins.namespace()

    def eval_lines(self, lines):
        return self.eval_all(Reader().read(LineIterCharBuffer(lines)))

    def eval_string(self, s):
        return self.eval_all(Reader().read(CharBuffer(s)))

    def eval_all(self, exprs):
        result = None
        for expr in exprs:
            result = self.eval(expr)
        return result

    def eval(self, expr):
        self.ns[self.LAST_RESULT] = result = eval(expr, self.ns)
        return result

def eval(expr, ns):
    return evaluator.eval(expr, ns)
