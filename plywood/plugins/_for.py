from plywood.values import PlywoodValue, PlywoodOperator, PlywoodVariable, PlywoodParens
from plywood.runtime import Continue
from plywood import ParseException
from _if import ElseState


class ForLoop(object):
    pass


@PlywoodValue.register_runtime('for')
def _for(state, scope, arguments, block):
    if len(arguments.args) != 1 \
        or len(arguments.kwargs) \
        or not isinstance(arguments.args[0], PlywoodOperator) \
        or arguments.args[0].operator != 'in':
        raise ParseException('`for` only accepts an "in" operation')
    var = arguments.args[0].left
    if not isinstance(var, PlywoodVariable) and not isinstance(var, PlywoodParens):
        raise ParseException('`for` expects a variable name or tuple of variable names')
    if isinstance(var, PlywoodParens):
        if var.kwargs:
            raise ParseException('keyword arguments are not in appropriate in the list of  `for` variable names')
        for arg in var.arguments:
            if not isinstance(arg, PlywoodVariable):
                raise ParseException('`for` expects a variable name or tuple of variable names')
    iterator = arguments.args[0].right.python_value(scope)

    retval = ''
    for for_value in iterator:
        if isinstance(var, PlywoodVariable):
            varname = var.get_name()
            scope[varname] = for_value
        elif isinstance(var, PlywoodParens):
            # for_values should be a PlywoodList, PlywoodDict,
            # if len(var.arguments) !=
            # scope[]
            pass
        retval += str(block.python_value(scope))
    else:
        return [Continue(), ElseState()], retval
    return [Continue()], retval
