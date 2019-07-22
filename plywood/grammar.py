import string
import chomsky
from .values import (
    PlywoodNumber,
    PlywoodString,
    PlywoodVariable,
    )


class PlywoodNumberGrammar(chomsky.Number):
    def __init__(self, parseme=None):
        super(PlywoodNumberGrammar, self).__init__(parseme)
        self.location = self.buffer.position

    def plywood_value(self):
        if isinstance(self.parsed, chomsky.Float):
            return PlywoodNumber(self.location - len(str(self)), float(str(self)))

        base = 10
        if isinstance(self.parsed, chomsky.HexadecimalInteger):
            base = 16
        if isinstance(self.parsed, chomsky.OctalInteger):
            base = 8
        if isinstance(self.parsed, chomsky.BinaryInteger):
            base = 2
        return PlywoodNumber(self.location - len(str(self)), int(str(self), base))


class PlywoodStringGrammar(chomsky.String):
    def __init__(self, parseme=None):
        super(PlywoodStringGrammar, self).__init__(parseme)
        self.location = self.buffer.position

    def plywood_value(self):
        parsed = self.parsed
        if isinstance(parsed, chomsky.TripleSingleQuotedString) or\
           isinstance(parsed, chomsky.TripleDoubleQuotedString):
            return PlywoodString(self.location - len(str(parsed)), str(parsed), triple=True)
        return PlywoodString(self.location - len(str(parsed)), str(parsed))


class PlywoodVariableGrammar(chomsky.Variable, metaclass=chomsky.VariableGrammarType):
    starts_with = chomsky.Char(string.ascii_letters + '_')
    ends_with = chomsky.Chars(string.ascii_letters + '_:-' + string.digits, min=0) + chomsky.PrevIsNot(chomsky.L('-') | chomsky.L(':'))

    def __init__(self, parseme=None):
        super(PlywoodVariableGrammar, self).__init__(parseme)
        self.location = self.buffer.position

    def plywood_value(self):
        return PlywoodVariable(self.location - len(str(self)), str(self))


class PlywoodOperatorGrammar(chomsky.Grammar):
    def __init__(self, parseme=None):
        if parseme == '[]':
            self.parsed = '[]'
        else:
            super(PlywoodOperatorGrammar, self).__init__(parseme)
            self.location = self.buffer.position

    grammar = chomsky.Any(
        '==', '!=', '<=', '>=', '<', '>',
        '**=', '//=', '+=', '-=', '/=', '*=', '%=', '.=', '=',
        'and=', 'or=',
        '**',  '//',  '+',  '-',  '/',  '*',  '%',
        '|',  # pipe
        '.',  # get_attr
        ',',  # auto arg
        (chomsky.WordStart(string.ascii_letters + '_') + chomsky.Any('is', 'in', 'not', 'and', 'or') + chomsky.WordEnd(string.ascii_letters + '_')),
    )
