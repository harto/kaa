class CharStream:
    def __init__(self, source):
        self.source = source
        self.col = 0

    def peek_char(self):
        try:
            return self.source[self.col]
        except IndexError:
            return None

    def pop_char(self):
        c = self.peek_char()
        if not c:
            raise StreamEmpty()
        self.col += 1
        return c

    def source_meta(self):
        return SourceMeta(self.col - 1)


class IterStream:
    def __init__(self, lines, filename=None):
        self.lines = (CharStream(line) for line in lines)
        self.filename = filename
        self.line_num = 0
        self.peeked_line = None
        self.line = self.pop_line()

    def peek_char(self):
        c = self.line.peek_char()
        if not c:
            line = self.peek_line()
            if line:
                c = line.peek_char()
        return c

    def pop_char(self):
        try:
            return self.line.pop_char()
        except StreamEmpty:
            return self.pop_line().pop_char()

    def peek_line(self):
        if not self.peeked_line:
            try:
                self.peeked_line = next(self.lines)
            except StopIteration:
                pass
        return self.peeked_line

    def pop_line(self):
        line = self.peek_line()
        if not line:
            raise StreamEmpty()
        self.line = line
        self.line_num += 1
        self.peeked_line = None
        return line

    def source_meta(self):
        line_meta = self.line.source_meta()
        return SourceMeta(line_meta.col, self.line_num, self.filename)


class StreamEmpty(Exception):
    pass


class SourceMeta:
    def __init__(self, col, line=1, filename='<none>'):
        self.line = line
        self.col = col
        self.filename = filename

    def __str__(self):
        return '%s:%s:%s' % (self.filename, self.line, self.col)
