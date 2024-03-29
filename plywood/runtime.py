"""
These classes control the state and control flow of a block.  They are what
allow an if, elif, try, or for function to pass control to an else function, or
a raise exception to get passed to an except or finally block.

Basically, these allow plywood to implement all language features as plugins,
instead of built-in, hard-coded constructs.
"""


class RuntimeMetaclass(type):
    def __init__(cls, classname, bases, cls_dict):
        super().__init__(classname, bases, cls_dict)
        cls.singleton = None


class Runtime(object, metaclass=RuntimeMetaclass):
    def __new__(cls):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton


class Continue(Runtime):
    """
    The most basic of all states, the Continue state indicates "all good!".
    """


class Skip(Runtime):
    """
    Like Continue, but does not append the current line's output
    """


class SuppressNewline(Runtime):
    """
    Suppresses newlines for the entire block
    """


class SuppressOneNewline(SuppressNewline):
    """
    Suppresses newline for the current command
    """
