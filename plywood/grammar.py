import string
import chomsky
from values import (
    PlywoodNumber,
    PlywoodString,
    PlywoodVariable,
    )


class PlywoodNumberGrammar(chomsky.Number):
    def __init__(self, parseme=None):
        self.location = self.buffer.position
        super(PlywoodNumberGrammar, self).__init__(parseme)

    def to_value(self):
        if isinstance(self.parsed, chomsky.Float):
            return PlywoodNumber(float(str(self)))

        base = 10
        if isinstance(self.parsed, chomsky.HexadecimalInteger):
            base = 16
        if isinstance(self.parsed, chomsky.OctalInteger):
            base = 8
        if isinstance(self.parsed, chomsky.BinaryInteger):
            base = 2
        return PlywoodNumber(int(str(self), base))


class PlywoodStringGrammar(chomsky.String):
    def __init__(self, parseme=None):
        self.location = self.buffer.position
        super(PlywoodStringGrammar, self).__init__(parseme)

    def to_value(self):
        parsed = self.parsed
        if isinstance(parsed, chomsky.TripleSingleQuotedString) or\
           isinstance(parsed, chomsky.TripleDoubleQuotedString):
            return PlywoodString(str(parsed), triple=True)
        return PlywoodString(str(parsed))


class PlywoodVariableGrammar(chomsky.Variable):
    __metaclass__ = chomsky.VariableGrammarType
    starts_with = chomsky.Char(string.ascii_letters + '_')
    ends_with = chomsky.Chars(string.ascii_letters + '_:-' + string.digits, min=0) + chomsky.PrevIsNot(chomsky.L('-') | chomsky.L(':'))

    def __init__(self, parseme=None):
        self.location = self.buffer.position
        super(PlywoodVariableGrammar, self).__init__(parseme)

    def to_value(self):
        return PlywoodVariable(str(self))


class PlywoodOperatorGrammar(chomsky.Grammar):
    def __init__(self, parseme=None):
        self.location = self.buffer.position
        super(PlywoodOperatorGrammar, self).__init__(parseme)

    __metaclass__ = chomsky.OperatorGrammarType
    operators = [
        '==', '!=', '<=', '>=', '<', '>',
        '**=', '//=', '+=', '-=', '/=', '*=', '%=', '.=', '=',
        'not', 'and', 'or', '&', '|', '~', '<<', '>>',
        '**',  '//',  '+',  '-',  '/',  '*',  '%',
        '.',  # getitem
        '@',  # id/name
        ',',  # auto arg
    ]
