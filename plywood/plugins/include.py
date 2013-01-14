'''
Includes content from another template.  If you assign any keyword arguments,
those will be available in the scope of that template.
'''
import os

from plywood import Plywood
from plywood.exceptions import InvalidArguments
from plywood.env import PlywoodEnv


@PlywoodEnv.register_runtime()
def include(states, scope, arguments, block):
    if len(arguments.args) != 1:
        raise InvalidArguments('`include` only accepts one argument')
    if len(block.lines):
        raise InvalidArguments('`include` does not accept a block')
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
        input = f.read()
        old_input = scope['__input']
        scope['__input'] = input
        retval = Plywood(input).run(scope['__runtime'])
        scope['__input'] = old_input

    if len(arguments.kwargs):
        for key, value in restore_scope.iteritems():
            self_scope[key] = value
        for key in delete_scope:
            del self_scope[key]
    return states, retval


@PlywoodEnv.register_startup()
def startup(plywood, scope):
    scope['__path'] = plywood.options.get('path', os.getcwd())
