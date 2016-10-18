"""
Stores environment settings, e.g. options, and built-in functions.
"""
from plywood.values import PlywoodRuntime, PlywoodFunction, PlywoodHtmlPlugin
from plywood.scope import Scope


class PlywoodEnv(object):
    GLOBAL = {}
    STARTUP = []
    RUNTIME = {}
    FUNCTIONS = {}
    HTML_PLUGINS = {}

    def __init__(self, options={}):
        self.options = options
        self.scope = scope = Scope()
        scope.update(self.GLOBAL)

        scope['__runtime'] = self
        options.setdefault('separator', "\n")

        add_indent = options.get('indent', '    ')
        indent = ['']
        for startup in self.STARTUP:
            startup(self, scope)

        def indent_push(new_indent=add_indent):
            indent.append(new_indent)
            return indent

        def indent_pop():
            return indent.pop()

        def indent_apply(insides, push_indent=True):
            if not insides:
                return insides
            if push_indent:
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
            if push_indent:
                indent_pop()
            return retval

        self.indent = indent_apply
        scope['__indent'] = indent_apply

        include_defaults = options.get('defaults', True)
        if include_defaults:
            for key, runtime in self.RUNTIME.iteritems():
                fn, kwargs = runtime
                value = PlywoodRuntime(fn, **kwargs)
                scope[key] = value
            for key, function in self.FUNCTIONS.iteritems():
                fn, kwargs = function
                value = PlywoodFunction(fn, **kwargs)
                scope[key] = value
            for key, plugin in self.HTML_PLUGINS.iteritems():
                value = PlywoodHtmlPlugin(plugin)
                scope[key] = value

        more_globals = options.get('globals', {})
        scope.update(more_globals)

    @classmethod
    def register_global(cls, name, value):
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
    def register_fn(cls, name=None, **kwargs):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.FUNCTIONS[plugin_name] = (fn, kwargs)
            return fn
        return decorator

    @classmethod
    def register_html_plugin(cls, name):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.HTML_PLUGINS[plugin_name] = fn
            return fn
        return decorator
