from chomsky import ParseException


class CompilationError(Exception):
    def __init__(self, buffer, message):
        self.buffer = buffer
        super(CompilationError, self).__init__(message)


class IndentError(CompilationError):
    pass


class IndentBreak(Exception):
    pass


class RuntimeError(Exception):
    def __init__(self, location, scope, message):
        self.location = location
        self.scope = scope
        self.message = message
        super(RuntimeError, self).__init__()

    def __str__(self):
        input = self.scope['__input']
        line_no, prev, line, next = runtime_context(input, self.location)
        print("""=============== exceptions.py at line {0} ===============
line_no: {1!r}
prev: {2!r}
line: {3!r}
next: {4!r}
""".format(__import__('sys')._getframe().f_lineno - 5, line_no, prev, line, next, ))

        output = "{}\n".format(self.message)
        output += "At line {!r}:\n".format(line_no)
        if prev:
            output += "    {}\n".format(prev)
        output += ">>> {}\n".format(line)
        if next:
            output += "    {}\n".format(next)
        return output


class KeyError(RuntimeError):
    def __init__(self, location, scope, name):
        self.name = name
        super(KeyError, self).__init__(location, scope, 'No value for {!r}'.format(name))

class InvalidArguments(Exception):
    pass


class BreakException(Exception):
    def __init__(self, retval=''):
        self.retval = retval


class ContinueException(Exception):
    def __init__(self, retval=''):
        self.retval = retval


def runtime_context(input, location):
    line_no, line_start, line_end = runtime_line(input, location)
    line = input[line_start:line_end]
    if line_start > 0:
        _, prevline_start, prevline_end = runtime_line(input, line_start - 1)
        prev = input[prevline_start:prevline_end]
    else:
        prev = None
    if line_end < len(input) - 1:
        _, nextline_start, nextline_end = runtime_line(input, line_end + 1)
        next = input[nextline_start:nextline_end]
    else:
        next = None
    return line_no, prev, line, next

def runtime_line(input, location):
    line_start = location
    line_end = location
    while line_start >= 0:
        line_start -= 1
        if input[line_start] == "\n" or line_start == -1:
            line_start += 1
            break
    while line_end < len(input):
        try:
            if input[line_end] == "\n":
                break
        except IndexError:
            break
        line_end += 1
    line_no = 1 + input[:line_start].count("\n")
    return line_no, line_start, line_end
