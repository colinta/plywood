'''
Implements ``if``, ``elif``, and ``else`` clauses.
'''
from plywood.runtime import Runtime, Continue
from plywood.values import PlywoodValue
from plywood import ParseException


class ElseState(Runtime):
    pass


@PlywoodValue.register_runtime('if')
def _if(states, scope, arguments, block):
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise ParseException('`if` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodValue.register_runtime('elif', accepts=ElseState())
def _elif(states, scope, arguments, block):
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise ParseException('`elif` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodValue.register_runtime('else', accepts=ElseState())
def _else(states, scope, arguments, block):
    if len(arguments.args) or len(arguments.kwargs):
        raise ParseException('`else` does not accept any arguments')
    return [Continue()], block.get_value(scope)
