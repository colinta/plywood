import sys
from plywood.values import PlywoodValue


@PlywoodValue.register_fn('print')
def print_(*args):
    sys.stderr.write(repr(args))
    sys.stderr.write("\n")
    return ''
