from charbuf import EmptyBufferException, CharBuffer
from reader import Reader, UnexpectedEofException

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
            except EOFError:
                # user aborted input
                # fixme: better exception needed
                print
                continue
            result = self.runtime.eval(exprs)
            print(result)

    def _read_exprs(self):
        input = raw_input(self.PROMPT_1)
        while True:
            buf = CharBuffer(input)
            try:
                # list() coercion flushes out UnexpectedEofException before
                # evaluation
                return list(Reader().read(buf))
            except UnexpectedEofException:
                # fixme: should be e.g. BufferExhausted? or something else
                input += raw_input(self.PROMPT_2)
