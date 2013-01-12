import sys
from plywood import plywood


def run():
    scope = {}
    for arg in sys.argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 2)
            scope[key] = value
    sys.stdout.write(plywood(sys.stdin.read(), scope, indent='  '))
