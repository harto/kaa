from charbuf import CharBuffer
from reader import Reader, UnexpectedEofException
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
                # todo: filter internal stack frames
                traceback.print_exc()
                continue
            if result:
                print(self._format(result))

    def _read_exprs(self):
        s = raw_input(self.PROMPT_1)
        while True:
            buf = CharBuffer(s)
            try:
                # eagerly evaluate the expression generator
                # to flush out unexpected EOF
                return list(Reader().read(buf))
            except UnexpectedEofException:
                s += '\n' + raw_input(self.PROMPT_2)

    def _format(self, value):
        if isinstance(value, str):
            return format_str(value)
        else:
            return value

def format_str(s):
    for k, v in Reader.STRING_ESCAPE_SEQUENCES.items():
        s = s.replace(v, k)
    return '"%s"' % s
