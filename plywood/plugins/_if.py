from plywood.runtime import Runtime, Continue
from plywood.values import PlywoodValue


class ElseState(Runtime):
    pass


@PlywoodValue.register_runtime('if')
def _if(state, scope, arguments, block):
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise Exception('`if` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodValue.register_runtime('elif', accepts=ElseState())
def _elif(state, scope, arguments, block):
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise Exception('`if` only accepts one argument')
    arg = arguments.args[0].python_value(scope)
    if arg:
        return [Continue()], block.get_value(scope)
    return [Continue(), ElseState()], ''


@PlywoodValue.register_runtime('else', accepts=ElseState())
def _else(state, scope, arguments, block):
    if len(arguments.args) or len(arguments.kwargs):
        raise Exception('`if` only accepts one argument')
    return [Continue()], block.get_value(scope)
