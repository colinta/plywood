import sys
from plywood import plywood


def run():
    sys.stdout.write(plywood(sys.stdin.read()))
