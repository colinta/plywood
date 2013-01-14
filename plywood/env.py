"""
Stores environment settings, e.g. options, and built-in functions.
"""
from plywood.values import PlywoodRuntime, PlywoodFunction, PlywoodHtmlPlugin


class PlywoodEnv(object):
    GLOBAL = {}
    STARTUP = []
    RUNTIME = {}
    FUNCTIONS = {}
    HTML_PLUGINS = {}

    def __init__(self, input, options, self_scope):
        self.input = input
        self.options = options
        scope = {}
        scope['__runtime'] = self
        options = self.options
        add_indent = options.get('indent', '    ')
        scope['self'] = self_scope  # TODO: PlywoodWrapper
        indent = ['']
        for startup in self.STARTUP:
            startup(self, scope)

        def indent_push(new_indent=add_indent):
            indent.append(new_indent)
            return indent

        def indent_pop():
            return indent.pop()

        def indent_apply(insides):
            if not insides:
                return insides
            indent_push()
            current = indent[-1]
            retval = None
            for line in insides.splitlines():
                if retval is None:
                    retval = ''
                else:
                    retval += "\n"
                if line:
                    retval += current + line
            indent_pop()
            return retval

        scope['__indent'] = indent_apply
        scope.update(self.GLOBAL)
        for key, runtime in self.RUNTIME.iteritems():
            fn, kwargs = runtime
            value = PlywoodRuntime(fn, **kwargs)
            scope[key] = value
        for key, fn in self.FUNCTIONS.iteritems():
            value = PlywoodFunction(fn)
            scope[key] = value
        for key, fn in self.HTML_PLUGINS.iteritems():
            value = PlywoodHtmlPlugin(fn)
            scope[key] = value
        self.scope = scope

    @classmethod
    def register(cls, name, value):
        cls.GLOBAL[name] = value

    @classmethod
    def register_startup(cls, arg=None):
        def decorator(fn):
            cls.STARTUP.append(fn)
        if arg:
            return decorator(arg)
        return decorator

    @classmethod
    def register_runtime(cls, name=None, **kwargs):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.RUNTIME[plugin_name] = (fn, kwargs)
            return fn
        return decorator

    @classmethod
    def register_fn(cls, name=None):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.FUNCTIONS[plugin_name] = fn
            return fn
        return decorator

    @classmethod
    def register_html_plugin(cls, name=None):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.HTML_PLUGINS[plugin_name] = fn
            return fn
        return decorator
