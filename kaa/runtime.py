import builtins
from evaluator import Evaluator
import reader

class Runtime(object):

    def __init__(self):
        self.evaluator = Evaluator()
        self.env = builtins.env()

    def eval_file(self, f):
        # todo: don't slurp entire file
        return self.eval_string(f.read())

    def eval_string(self, s):
        result = None
        for form in reader.read(s):
            result = self.eval(form)
        return result

    def eval(self, form):
        self.env = self.evaluator.eval(form, self.env)
        return self.env[Evaluator.LAST_RESULT]
