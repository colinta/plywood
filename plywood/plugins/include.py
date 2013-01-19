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

    scope.push()
    restore_scope = {}
    delete_scope = []
    context = scope['self']
    if len(arguments.kwargs):
        kwargs = dict(
            (item.key.get_name(), item.value)
                for item in arguments.kwargs
                )
        for key, value in kwargs.iteritems():
            if key in context:
                restore_scope[key] = context[key]
            else:
                delete_scope.append(key)
            context[key] = value

    template_name = arguments.args[0].python_value(scope)
    found = False
    for path in scope['__paths']:
        template_path = os.path.join(path, template_name) + '.ply'
        if os.path.exists(template_path):
            found = True
            retval = ''
            with open(template_path) as f:
                input = f.read()
                scope.push()
                scope['__input'] = input
                retval = Plywood(input).run(context, scope['__runtime'])
                scope.pop()
            break
    if not found:
        raise Exception('Could not find template: {0!r}'.format(template_name))

    if len(arguments.kwargs):
        for key, value in restore_scope.iteritems():
            context[key] = value
        for key in delete_scope:
            del context[key]
    return states, retval


@PlywoodEnv.register_startup()
def startup(plywood, scope):
    if plywood.options.get('paths'):
        scope['__paths'] = plywood.options.get('paths')
    elif plywood.options.get('path'):
        scope['__paths'] = [plywood.options.get('path')]
    else:
        scope['__paths'] = [os.getcwd()]
