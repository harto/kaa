import traceback

from kaa.charbuf import CharBuffer
from kaa.core import serialize
from kaa.reader import Reader, EOF


PROMPT_1 = '=> '
PROMPT_2 = ' > '

LAST_RESULT = '^'


class Repl:
    def __init__(self, runtime):
        self.runtime = runtime

    def loop(self):
        self._store_last_result(None)
        while True:
            try:
                exprs = _read_exprs()
                result = self.runtime.eval_all(exprs)
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
                self._store_last_result(result)
                print(serialize(result))

    def _store_last_result(self, value):
        self.runtime.ns.define_global(LAST_RESULT, value)


# TODO: proper readline support, etc.
def _read_exprs():
    s = input(PROMPT_1)
    while True:
        line = CharBuffer(s)
        try:
            # eagerly evaluate the expression generator
            # to flush out unexpected EOF
            return list(Reader().read_all(line))
        except EOF:
            s += '\n' + input(PROMPT_2)
