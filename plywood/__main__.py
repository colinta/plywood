import sys
from plywood import plywood


def run():
    scope = {}
    for arg in sys.argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 2)
            scope[key] = eval(value)
    out = plywood(sys.stdin.read(), scope, indent='  ')
    sys.stdout.write(out.encode('utf-8'))
