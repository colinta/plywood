'''
Implements the ``for`` loop clause.  The syntax is the same as python, and it
supports the ``else`` clause in the same way.  However, it also supports an
``empty`` clause, which is only executed if the iterator was empty.  The
``empty`` clause must appear before the ``else`` clause.
'''
from plywood.env import PlywoodEnv
from plywood.values import PlywoodOperator, PlywoodVariable, PlywoodParens
from plywood.runtime import Continue
from plywood.exceptions import InvalidArguments
from _if import ElseState
from empty import EmptyState
from _break import BreakException, ContinueException


@PlywoodEnv.register_runtime('for')
def _for(states, scope, arguments, block):
    if not len(block.lines):
        raise InvalidArguments('A block is required in `for`')
    if len(arguments.args) != 1 \
        or len(arguments.kwargs) \
        or not isinstance(arguments.args[0], PlywoodOperator) \
        or arguments.args[0].operator != 'in':
        raise InvalidArguments('`for` only accepts an `in` operation')
    var = arguments.args[0].left
    if not isinstance(var, PlywoodVariable) and not isinstance(var, PlywoodParens):
        raise InvalidArguments('`for` expects a variable name or tuple of variable names')
    if isinstance(var, PlywoodParens):
        if var.kwargs:
            raise InvalidArguments('keyword arguments are not in appropriate in the list of  `for` variable names')
        for arg in var.arguments:
            if not isinstance(arg, PlywoodVariable):
                raise InvalidArguments('`for` expects a variable name or tuple of variable names')
    iterator = arguments.args[0].right.python_value(scope)

    retval = None
    if not iterator:
        return [Continue(), EmptyState(), ElseState()], ''
    for for_value in iterator:
        if retval is None:
            retval = ''
        if isinstance(var, PlywoodVariable):
            varname = var.get_name()
            scope[varname] = for_value
        elif isinstance(var, PlywoodParens):
            raise Exception('huh?')
            # for_values should be a PlywoodList, PlywoodDict,
            # if len(var.arguments) !=
            # scope[]
            pass
        try:
            retval += unicode(block.python_value(scope))
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
