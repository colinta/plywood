'''
A number of plugins (``for``, ``while``) support an ``empty`` clause, which is
only executed when the body of the loop was never executed.  It is up to those
plugins to include EmptyState() in the runtime states.
'''
from plywood.values import PlywoodValue
from plywood.runtime import Runtime, Continue
from plywood import ParseException


class EmptyState(Runtime):
    pass


@PlywoodValue.register_runtime(accepts=EmptyState())
def empty(state, scope, arguments, block):
    if len(arguments.args) or len(arguments.kwargs):
        raise ParseException('`empty` does not accept any arguments')
    return [Continue()], block.get_value(scope)
