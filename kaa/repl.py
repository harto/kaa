from charbuf import EmptyBufferException, InteractiveCharBuffer
from reader import Reader

class Repl(object):

    PROMPT_1 = '=> '
    PROMPT_2 = ' > '

    def __init__(self, runtime):
        self.runtime = runtime

    def loop(self):
        # todo: install signal handlers for graceful exit
        while True:
            buf = InteractiveCharBuffer(self.PROMPT_1, self.PROMPT_2)
            try:
                exprs = Reader().read(buf)
            except EmptyBufferException:
                # user aborted input
                # todo: better exception
                continue
            result = self.runtime.eval(exprs)
            print(result)
