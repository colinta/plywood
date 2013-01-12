class PlywoodKeyError(Exception):
    pass


class UnindentException(Exception):
    pass


class InvalidArguments(Exception):
    pass


def this_line(input, location):
    newline_start = location
    newline_end = location
    while newline_start:
        newline_start -= 1
        if input[newline_start] == "\n":
            newline_start += 1
            break
    while newline_end < len(input):
        newline_end += 1
        if input[newline_end] == "\n":
            newline_end -= 1
            break
    line_no = input[:newline_start].count("\n")
    return line_no, input[newline_start:newline_end]
