from kaa import formatter, string
from kaa.charbuf import CharBuffer
from kaa.reader import Reader, UnexpectedEofException
import re
import traceback

class Repl(object):

    PROMPT_1 = '=> '
    PROMPT_2 = ' > '

    def __init__(self, runtime):
        self.runtime = runtime

    def loop(self):
        while True:
            try:
                exprs = self._read_exprs()
                result = self.runtime.eval_all(exprs)
            except KeyboardInterrupt:
                # Ctrl-C; user wants to abandon current input
                print
                continue
            except EOFError:
                # Ctrl-D; user wants to quit
                print
                break
            except Exception:
                traceback.print_exc(1)
                continue
            if result is not None:
                print(formatter.format(result))

    def _read_exprs(self):
        s = raw_input(self.PROMPT_1)
        while True:
            buf = CharBuffer(s)
            try:
                # eagerly evaluate the expression generator
                # to flush out unexpected EOF
                return list(Reader().read_all(buf))
            except UnexpectedEofException:
                s += '\n' + raw_input(self.PROMPT_2)
