from kaa import formatter, string
from kaa.charbuf import CharBuffer
from kaa.reader import Reader, EOF
import re
import traceback

# TODO: proper line-editing support, etc.
class Repl(object):

    PROMPT_1 = '=> '
    PROMPT_2 = ' > '

    LAST_RESULT = '^'

    def __init__(self, runtime):
        self.runtime = runtime

    def loop(self):
        self._store_last_result(None)
        while True:
            try:
                exprs = self._read_exprs()
                result = self.runtime.eval_all(exprs)
            except KeyboardInterrupt:
                # Ctrl-C; user wants to abandon current input
                print()
                continue
            except EOFError:
                # Ctrl-D; user wants to quit
                print()
                break
            except Exception:
                traceback.print_exc(1)
                continue
            if result is not None:
                self._store_last_result(result)
                print(formatter.format(result))

    def _store_last_result(self, value):
        self.runtime.ns.define_global(self.LAST_RESULT, value)

    def _read_exprs(self):
        s = input(self.PROMPT_1)
        while True:
            buf = CharBuffer(s)
            try:
                # eagerly evaluate the expression generator
                # to flush out unexpected EOF
                return list(Reader().read_all(buf))
            except EOF:
                s += '\n' + input(self.PROMPT_2)
