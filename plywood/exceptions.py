from chomsky import ParseException


class CompilationError(Exception):
    def __init__(self, buffer, message):
        self.buffer = buffer
        super(CompilationError, self).__init__(message)


class IndentError(CompilationError):
    pass


class IndentBreak(Exception):
    pass


class PlywoodKeyError(Exception):
    pass


class InvalidArguments(Exception):
    pass


class BreakException(Exception):
    def __init__(self, retval=''):
        self.retval = retval


class ContinueException(Exception):
    def __init__(self, retval=''):
        self.retval = retval


def this_line(input, location):
    newline_start = min(location, len(input))
    newline_end = min(location, len(input))
    while newline_start >= 0:
        newline_start -= 1
        if input[newline_start] == "\n":
            newline_start += 1
            break
    while newline_end < len(input):
        newline_end += 1
        try:
            if input[newline_end] == "\n":
                break
        except IndexError:
            break
    line_no = input[:newline_start].count("\n")
    return line_no, input[newline_start:newline_end]
