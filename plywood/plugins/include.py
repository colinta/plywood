'''
Implements the ``for`` loop clause.  The syntax is the same as python, and it
supports the ``else`` clause in the same way.  However, it also supports an
``empty`` clause, which is only executed if the iterator was empty.  The
``empty`` clause must appear before the ``else`` clause.
'''
import os

from plywood.values import PlywoodValue
from plywood import Plywood, ParseException


@PlywoodValue.register_runtime('include')
def include(states, scope, arguments, block):
    if len(arguments.args) != 1:
        raise ParseException('`include` only accepts one argument')
    restore_scope = {}
    delete_scope = []
    self_scope = scope['self']
    if len(arguments.kwargs):
        kwargs = dict(
            (item.key.get_name(), item.value)
                for item in arguments.kwargs
                )
        for key, value in kwargs.iteritems():
            if key in self_scope:
                restore_scope[key] = self_scope[key]
            else:
                delete_scope.append(key)
            self_scope[key] = value

    template_name = arguments.args[0].python_value(scope)
    template_path = os.path.join(scope['__path'], template_name) + '.ply'
    retval = ''
    with open(template_path) as f:
        retval = Plywood(f.read()).run(scope['__runtime'])

    if len(arguments.kwargs):
        for key, value in restore_scope.iteritems():
            self_scope[key] = value
        for key in delete_scope:
            del self_scope[key]
    return states, retval


@PlywoodValue.register_startup()
def startup(plywood, scope):
    scope['__path'] = plywood.options.get('indent', os.getcwd())
