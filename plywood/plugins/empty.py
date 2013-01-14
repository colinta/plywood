'''
A number of plugins (``for``, ``while``) support an ``empty`` clause, which is
only executed when the body of the loop was never executed.  It is up to those
plugins to include EmptyState() in the runtime states.
'''
from plywood.env import PlywoodEnv
from plywood.exceptions import ParseException
from plywood.runtime import Runtime, Continue


class EmptyState(Runtime):
    pass


@PlywoodEnv.register_runtime(accepts=EmptyState())
def empty(state, scope, arguments, block):
    if not len(block.lines):
        raise ParseException('A block is required in `empty`')
    if len(arguments.args) or len(arguments.kwargs):
        raise ParseException('`empty` does not accept any arguments')
    return [Continue()], block.get_value(scope)
