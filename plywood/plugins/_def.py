'''
Implements a ``def`` keyword.
'''
from plywood.env import PlywoodEnv
from plywood.values import PlywoodCallOperator, PlywoodVariable, PlywoodOperator, PlywoodRuntime
from plywood.runtime import Continue
from plywood.exceptions import InvalidArguments


@PlywoodEnv.register_runtime('def')
def _def(states, scope, arguments, block):
    '''
    Example:
        def foo(bar, baz, quux='value')
    foo => name of function
    [bar, baz] => arguments, no default values.  These must be variable names.

    Sorry, no support for *args and **kwargs just yet.
    '''
    if not len(block.lines):
        raise InvalidArguments('A block is required in `def`')
    if len(arguments.args) != 1 \
        or len(arguments.kwargs) \
        or not isinstance(arguments.args[0], PlywoodCallOperator) \
        or arguments.args[0].operator != '()':
        raise InvalidArguments('`def` should be followed by a function definition')
    function_name = arguments.args[0].left.get_name()
    arglist = arguments.args[0].right.args
    kwarglist = arguments.args[0].right.kwargs
    final_arglist = []
    defaults = {}
    # all arglist.args should be a varname
    for var_name in arglist:
        if not isinstance(var_name, PlywoodVariable):
            raise InvalidArguments('`def` should be given a list of variable names.  '
                                   '{0!r} is invalid'.format(var_name.python_value(scope)))
        final_arglist.append(var_name.get_name())

    for kwarg in kwarglist:
        var_name = kwarg.key.python_value(scope)
        final_arglist.append(var_name)
        value = kwarg.value.python_value(scope)
        defaults[var_name] = value

    # Now we have to re-produce python's way of accepting arguments, but I'm
    # gonna get away with being sloppy about it...
    # First, any kwargs can be assigned, and removed from the final_arglist.
    # Then, args is scanned and values are assigned to corresponding names in
    # final_arglist.  If any values are left over in final_arglist, args, or
    # kwargs, something went wrong.
    #
    # The sloppy part comes because unlike python, you can specify args and
    # kwargs in pretty much any order.  All kwargs are assigned first, then
    # the args are assigned to whatever is left in the local_arglist, then
    # defaults.  Only after all that is local_arglist checked to make sure it is
    # empty.
    def the_function(states, called_scope, called_arguments, called_block):
        args = called_arguments.args
        kwargs = called_arguments.kwargs
        local_arglist = [] + final_arglist
        called_scope.push()
        for plywood_kwarg in kwargs:
            local_value = plywood_kwarg.value.python_value(scope)
            local_var_name = plywood_kwarg.key.python_value(scope)
            if local_var_name in local_arglist:
                local_arglist.remove(local_var_name)
            else:
                raise InvalidArguments('Unknown keyword argument {0!r}'.format(local_var_name))
            called_scope[local_var_name] = local_value

        for plywood_value in args:
            local_value = plywood_value.python_value(called_scope)
            if not local_arglist:
                raise InvalidArguments('Too many arguments passed to {0}'.format(function_name))
            local_var_name = local_arglist.pop(0)
            called_scope[local_var_name] = local_value

        for local_var_name, local_value in defaults.iteritems():
            if local_var_name in local_arglist:
                local_arglist.remove(local_var_name)
                called_scope[local_var_name] = local_value

        if local_arglist:
            raise InvalidArguments('Unassigned values: {0}'.format(', '.join(local_arglist)))
        retval = block.get_value(called_scope)
        called_scope.pop()
        return [Continue()], retval
    the_function.__name__ = function_name

    scope[function_name] = PlywoodRuntime(the_function)
    return [Continue()], ''
