'''
Implements the ``for`` loop clause.  The syntax is the same as python, and it
supports the ``else`` clause in the same way.  However, it also supports an
``empty`` clause, which is only executed if the iterator was empty.  The
``empty`` clause must appear before the ``else`` clause.
'''
from plywood.values import PlywoodValue, PlywoodOperator, PlywoodVariable, PlywoodParens
from plywood.runtime import Continue
from plywood import ParseException
from _if import ElseState
from empty import EmptyState
from _break import BreakException, ContinueException


class ForLoop(object):
    pass


@PlywoodValue.register_runtime('for')
def _for(states, scope, arguments, block):
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

    retval = None
    for for_value in iterator:
        if retval is None:
            retval = ''
        if isinstance(var, PlywoodVariable):
            varname = var.get_name()
            scope[varname] = for_value
        elif isinstance(var, PlywoodParens):
            # for_values should be a PlywoodList, PlywoodDict,
            # if len(var.arguments) !=
            # scope[]
            pass
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
