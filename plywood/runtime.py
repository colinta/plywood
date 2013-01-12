"""
These classes control the state and control flow of a block.  They are what
allow an if, elif, try, or for function to pass control to an else function, or
a raise exception to get passed to an except or finally block.

Basically, these allow plywood to implement all language features as plugins,
instead of built-in, hard-coded constructs.
"""


class Continue(object):
    """
    The most basic of all states, the Continue state indicates "all good!".
    """
    singleton = None

    def __new__(cls):
        if not cls.singleton:
            cls.singleton = super(Continue, cls).__new__(cls)
        return cls.singleton
