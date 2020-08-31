import traceback

from kaa.core import serialize, Symbol
from kaa.evaluator import Evaluator
from kaa.ns import Namespace
from kaa.reader import Reader, EOF
from kaa.stream import CharStream


PROMPT_1 = '=> '
PROMPT_2 = ' > '

LAST_RESULT = '^'


class Repl:
    def __init__(self):
        self.ns = Namespace('repl')
        self.last_result_symbol = self.ns.resolve(Symbol('^'))

    def loop(self):
        self.ns[self.last_result_symbol] = None
        while True:
            try:
                exprs = self.read_exprs()
                result = Evaluator(self.ns).evaluate_all(exprs)
            except KeyboardInterrupt:
                # Ctrl-C; user wants to abandon current input
                print()
                continue
            except EOFError:
                # Ctrl-D; user wants to quit
                print()
                break
            except Exception:  # pylint: disable=broad-except
                traceback.print_exc(1)
                continue
            if result is not None:
                self.ns[self.last_result_symbol] = result
                print(serialize(result))

    # TODO: proper readline support, etc.
    # TODO: tab completion
    def read_exprs(self):
        s = input(PROMPT_1)
        while True:
            line = CharStream(s)
            try:
                # eagerly evaluate the expression generator
                # to flush out unexpected EOF
                return list(Reader(self.ns).read_all(line))
            except EOF:
                s += '\n' + input(PROMPT_2)
