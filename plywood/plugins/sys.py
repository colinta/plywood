import sys
from plywood.values import PlywoodValue


@PlywoodValue.register_fn('print')
def print_(scope, arguments, block):
    args = arguments.args
    kwargs = arguments.kwargs
    sys.stderr.write(repr(args), repr(kwargs))
    sys.stderr.write("\n")
    return block.get_value(scope)
