from charbuf import EmptyBufferException, CharBuffer
from reader import Reader, UnexpectedEofException
import traceback

class Repl(object):

    PROMPT_1 = '=> '
    PROMPT_2 = ' > '

    def __init__(self, runtime):
        self.runtime = runtime

    def loop(self):
        # todo: install signal handlers for graceful exit
        while True:
            try:
                exprs = self._read_exprs()
                result = self.runtime.eval(exprs)
            except KeyboardInterrupt:
                # Ctrl-C; user wants to abandon current input
                print
                continue
            except EOFError:
                # Ctrl-D; user wants to quit
                print
                break
            except Exception:
                traceback.print_exc()
                continue
            if result:
                print(result)

    def _read_exprs(self):
        s = raw_input(self.PROMPT_1)
        while True:
            buf = CharBuffer(s)
            try:
                # eagerly evaluate the expression generator
                # to flush out unexpected EOF
                return list(Reader().read(buf))
            except UnexpectedEofException:
                s += raw_input(self.PROMPT_2)
