# todo: fix source meta in repl
# todo: consolidate different buffer types, including repl

class CharBuffer(object):

    def __init__(self, s):
        self.s = s
        self.line_num = 1
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

    def unpop(self):
        if self.col == 0:
            raise Exception('unpopped too far')
        self.col -= 1
        return self

    def source_meta(self):
        return SourceMeta(self.col - 1, self.line_num)

class LineIterCharBuffer(object):

    def __init__(self, lines):
        self.lines = iter(lines)
        self.line_num = 1
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

    def unpop(self):
        self.line.unpop()
        return self

    def _pop_line(self):
        try:
            line = next(self.lines)
        except StopIteration:
            return None
        return CharBuffer(line)

    def source_meta(self):
        line_meta = self.line.source_meta()
        return SourceMeta(line_meta.col, self.line_num)

class FileCharBuffer(LineIterCharBuffer):

    def __init__(self, f):
        LineIterCharBuffer.__init__(self, f)
        self.path = f.name

    def source_meta(self):
        meta = LineIterCharBuffer.source_meta(self)
        meta.filename = self.path
        return meta

class EmptyBufferException(Exception): pass

class SourceMeta(object):

    def __init__(self, col, line = None, filename = '<none>'):
        self.line = line
        self.col = col
        self.filename = filename

    def __str__(self):
        return '%s:%s:%s' % (self.filename, self.line, self.col)
