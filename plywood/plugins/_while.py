'''
Implements the ``while`` loop.  Supports ``break`` and ``continue`` statements
'''
from plywood.env import PlywoodEnv
from plywood.values import PlywoodParens
from plywood.runtime import Continue
from plywood.exceptions import InvalidArguments
from _if import ElseState
from empty import EmptyState
from _break import BreakException, ContinueException


@PlywoodEnv.register_runtime('while')
def _while(states, scope, arguments, block):
    if not len(block.lines):
        raise InvalidArguments('A block is required in `while`')
    if len(arguments.args) != 1 \
        or len(arguments.kwargs):
        raise InvalidArguments('`while` only accepts one conditional argument')
    var = arguments.args[0]

    retval = None
    while var.python_value(scope):
        if retval is None:
            retval = ''
        try:
            retval += str(block.python_value(scope))
        except BreakException as e:
            retval += e.retval
            break
        except ContinueException as e:
            retval += e.retval
            continue
    else:
        if retval is None:
            return [Continue(), EmptyState(), ElseState()], ''
        return [Continue(), ElseState()], retval
    return [Continue()], retval
