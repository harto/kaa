class CharBuffer(object):

    def __init__(self, s):
        self.s = s
        self.col = 0

    def eof(self):
        return self.col >= len(self.s)

    def peek(self):
        if self.eof():
            return None
        else:
            return self.s[self.col]

    def pop(self):
        c = self.peek()
        if not c:
            raise EmptyBufferException()
        self.col += 1
        return c

class LineIterCharBuffer(object):

    def __init__(self, lines):
        self.lines = iter(lines)
        self.line_num = 0
        self.line = self._pop_line()
        self.next_line = self._pop_line()

    def eof(self):
        return (not self.line or self.line.eof()) \
            and not self.next_line

    def peek(self):
        if self.eof():
            return None
        elif self.line:
            return self.line.peek()
        else:
            return self.next_line.peek()

    def pop(self):
        if self.eof():
            raise EmptyBufferException()
        c = self.line.peek()
        if c:
            return self.line.pop()
        else:
            self.line = self.next_line
            self.next_line = self._pop_line()
            self.line_num += 1
            return self.pop()

    def _pop_line(self):
        try:
            line = next(self.lines)
        except StopIteration:
            return None
        return CharBuffer(line)

class InteractiveCharBuffer(object):

    def __init__(self, prompt_1, prompt_2):
        self.prompt_1 = prompt_1
        self.prompt_2 = prompt_2
        self.line = None
        self.aborted = False

    def eof(self):
        return self.aborted

    def peek(self):
        if not self.line or self.line.eof():
            self.line = self._read_line()
        return self.line.peek()

    def pop(self):
        c = self.peek()
        if not c: raise EmptyBufferException()
        self.line.pop()
        return c

    def _read_line(self):
        try:
            s = raw_input(self.line and self.prompt_2 or self.prompt_1)
        except EOFError:
            s = ''
            self.aborted = True
        return CharBuffer(s)

class EmptyBufferException(Exception): pass
