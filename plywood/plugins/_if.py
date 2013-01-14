'''
Implements ``if``, ``elif``, and ``else`` clauses.
'''
from plywood.env import PlywoodEnv
from plywood.runtime import Runtime, Continue
from plywood.exceptions import ParseException


class ElseState(Runtime):
    pass


@PlywoodEnv.register_runtime('if')
def _if(states, scope, arguments, block):
    if not len(block.lines):
        raise ParseException('A block is required in `if`')
    if not len(arguments.args):
        raise ParseException('A condition is required in `if`')
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise ParseException('`if` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodEnv.register_runtime('elif', accepts=ElseState())
def _elif(states, scope, arguments, block):
    if not len(block.lines):
        raise ParseException('A block is required in `elif`')
    if not len(arguments.args):
        raise ParseException('A condition is required in `elif`')
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise ParseException('`elif` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodEnv.register_runtime('else', accepts=ElseState())
def _else(states, scope, arguments, block):
    if not len(block.lines):
        raise ParseException('A block is required in `else`')
    if len(arguments.args) or len(arguments.kwargs):
        raise ParseException('`else` does not accept any arguments')
    return [Continue()], block.get_value(scope)
