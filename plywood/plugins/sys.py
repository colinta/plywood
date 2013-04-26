from __future__ import absolute_import
import sys
from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn('print')
def print_(*args, **kwargs):
    out = kwargs.pop('out', sys.stdout)
    if kwargs:
        raise TypeError("print() got unexpected keyword arguments '{args}'", "', '".join(kwargs.keys()))
    out.write(' '.join(str(arg) for arg in args))
    out.write("\n")
    return None
