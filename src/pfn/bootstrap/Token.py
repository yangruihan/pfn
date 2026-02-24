from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from dataclasses import dataclass
from typing import Union

class INT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class FLOAT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class STRING:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class CHAR:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class IDENT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_DEF:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_LET:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_IN:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_IF:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_THEN:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_ELSE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_MATCH:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_WITH:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_TYPE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_INTERFACE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_IMPL:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_IMPORT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_EXPORT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_MODULE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_AS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_EFFECT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_HANDLER:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_HANDLE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_DO:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_FORALL:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_EXISTS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_DATA:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_FAMILY:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_WHERE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_FN:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class KW_GADT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TRUE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class FALSE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class PLUS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class MINUS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class STAR:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class SLASH:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class PERCENT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class ARROW:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class FAT_ARROW:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class DOUBLE_COLON:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class EQUALS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class EQ:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class NEQ:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class GT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class GE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class PIPE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class DOUBLE_PIPE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class AMP:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class DOUBLE_AMP:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LEFT_ARROW:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class DOUBLE_PLUS:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class BANG:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class AT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LPAREN:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class RPAREN:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LBRACKET:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class RBRACKET:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class LBRACE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class RBRACE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class COMMA:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class COLON:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class DOT:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class UNDERSCORE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class SEMICOLON:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class BACKTICK:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class NEWLINE:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class EOF:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

TokenType = Union[INT, FLOAT, STRING, CHAR, IDENT, KW_DEF, KW_LET, KW_IN, KW_IF, KW_THEN, KW_ELSE, KW_MATCH, KW_WITH, KW_TYPE, KW_INTERFACE, KW_IMPL, KW_IMPORT, KW_EXPORT, KW_MODULE, KW_AS, KW_EFFECT, KW_HANDLER, KW_HANDLE, KW_DO, KW_FORALL, KW_EXISTS, KW_DATA, KW_FAMILY, KW_WHERE, KW_FN, KW_GADT, TRUE, FALSE, PLUS, MINUS, STAR, SLASH, PERCENT, ARROW, FAT_ARROW, DOUBLE_COLON, EQUALS, EQ, NEQ, LT, LE, GT, GE, PIPE, DOUBLE_PIPE, AMP, DOUBLE_AMP, LEFT_ARROW, DOUBLE_PLUS, BANG, AT, LPAREN, RPAREN, LBRACKET, RBRACKET, LBRACE, RBRACE, COMMA, COLON, DOT, UNDERSCORE, SEMICOLON, BACKTICK, NEWLINE, EOF]
INT = INT()
FLOAT = FLOAT()
STRING = STRING()
CHAR = CHAR()
IDENT = IDENT()
KW_DEF = KW_DEF()
KW_LET = KW_LET()
KW_IN = KW_IN()
KW_IF = KW_IF()
KW_THEN = KW_THEN()
KW_ELSE = KW_ELSE()
KW_MATCH = KW_MATCH()
KW_WITH = KW_WITH()
KW_TYPE = KW_TYPE()
KW_INTERFACE = KW_INTERFACE()
KW_IMPL = KW_IMPL()
KW_IMPORT = KW_IMPORT()
KW_EXPORT = KW_EXPORT()
KW_MODULE = KW_MODULE()
KW_AS = KW_AS()
KW_EFFECT = KW_EFFECT()
KW_HANDLER = KW_HANDLER()
KW_HANDLE = KW_HANDLE()
KW_DO = KW_DO()
KW_FORALL = KW_FORALL()
KW_EXISTS = KW_EXISTS()
KW_DATA = KW_DATA()
KW_FAMILY = KW_FAMILY()
KW_WHERE = KW_WHERE()
KW_FN = KW_FN()
KW_GADT = KW_GADT()
TRUE = TRUE()
FALSE = FALSE()
PLUS = PLUS()
MINUS = MINUS()
STAR = STAR()
SLASH = SLASH()
PERCENT = PERCENT()
ARROW = ARROW()
FAT_ARROW = FAT_ARROW()
DOUBLE_COLON = DOUBLE_COLON()
EQUALS = EQUALS()
EQ = EQ()
NEQ = NEQ()
LT = LT()
LE = LE()
GT = GT()
GE = GE()
PIPE = PIPE()
DOUBLE_PIPE = DOUBLE_PIPE()
AMP = AMP()
DOUBLE_AMP = DOUBLE_AMP()
LEFT_ARROW = LEFT_ARROW()
DOUBLE_PLUS = DOUBLE_PLUS()
BANG = BANG()
AT = AT()
LPAREN = LPAREN()
RPAREN = RPAREN()
LBRACKET = LBRACKET()
RBRACKET = RBRACKET()
LBRACE = LBRACE()
RBRACE = RBRACE()
COMMA = COMMA()
COLON = COLON()
DOT = DOT()
UNDERSCORE = UNDERSCORE()
SEMICOLON = SEMICOLON()
BACKTICK = BACKTICK()
NEWLINE = NEWLINE()
EOF = EOF()

class Span(Record):
    def __init__(self, start, end, line, column):
        super().__init__()
        self.start = start
        self.end = end
        self.line = line
        self.column = column

class Token(Record):
    def __init__(self, tokenType, value, span):
        super().__init__()
        self.tokenType = tokenType
        self.value = value
        self.span = span

from dataclasses import dataclass
from typing import Union

@dataclass
class IntValue:
    _field0: int

@dataclass
class FloatValue:
    _field0: float

@dataclass
class StringValue:
    _field0: str

@dataclass
class CharValue:
    _field0: Char

class NoValue:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

TokenValue = Union[IntValue, FloatValue, StringValue, CharValue, NoValue]
NoValue = NoValue()

keywords = Dict.fromList([('def', KW_DEF), ('let', KW_LET), ('in', KW_IN), ('if', KW_IF), ('then', KW_THEN), ('else', KW_ELSE), ('match', KW_MATCH), ('with', KW_WITH), ('type', KW_TYPE), ('gadt', KW_GADT), ('interface', KW_INTERFACE), ('impl', KW_IMPL), ('import', KW_IMPORT), ('export', KW_EXPORT), ('module', KW_MODULE), ('as', KW_AS), ('effect', KW_EFFECT), ('handler', KW_HANDLER), ('handle', KW_HANDLE), ('do', KW_DO), ('forall', KW_FORALL), ('exists', KW_EXISTS), ('data', KW_DATA), ('family', KW_FAMILY), ('where', KW_WHERE), ('fn', KW_FN), ('True', TRUE), ('False', FALSE)])

def lookupKeyword(name):
    return Dict.lookup(name)(keywords)

def makeSpan(start): return lambda end: lambda line: lambda column: Span(start, end, line, column)

def token(tt): return lambda span: Token(tt, NoValue, span)

def stringToken(tt): return lambda value: lambda span: Token(tt, StringValue(value), span)

def intToken(value): return lambda span: Token(INT, IntValue(value), span)

def floatToken(value): return lambda span: Token(FLOAT, FloatValue(value), span)

def charToken(value): return lambda span: Token(CHAR, CharValue(value), span)

def tokenTypeName(tt):
    return (lambda __match_val: ('INT' if __match_val is INT else ('FLOAT' if __match_val is FLOAT else ('STRING' if __match_val is STRING else ('CHAR' if __match_val is CHAR else ('IDENT' if __match_val is IDENT else ('KW_DEF' if __match_val is KW_DEF else ('KW_LET' if __match_val is KW_LET else ('KW_IN' if __match_val is KW_IN else ('KW_IF' if __match_val is KW_IF else ('KW_THEN' if __match_val is KW_THEN else ('KW_ELSE' if __match_val is KW_ELSE else ('KW_MATCH' if __match_val is KW_MATCH else ('KW_WITH' if __match_val is KW_WITH else ('KW_TYPE' if __match_val is KW_TYPE else ('KW_INTERFACE' if __match_val is KW_INTERFACE else ('KW_IMPL' if __match_val is KW_IMPL else ('KW_IMPORT' if __match_val is KW_IMPORT else ('KW_EXPORT' if __match_val is KW_EXPORT else ('KW_MODULE' if __match_val is KW_MODULE else ('KW_AS' if __match_val is KW_AS else ('KW_EFFECT' if __match_val is KW_EFFECT else ('KW_HANDLER' if __match_val is KW_HANDLER else ('KW_HANDLE' if __match_val is KW_HANDLE else ('KW_DO' if __match_val is KW_DO else ('KW_FORALL' if __match_val is KW_FORALL else ('KW_EXISTS' if __match_val is KW_EXISTS else ('KW_DATA' if __match_val is KW_DATA else ('KW_FAMILY' if __match_val is KW_FAMILY else ('KW_WHERE' if __match_val is KW_WHERE else ('KW_FN' if __match_val is KW_FN else ('KW_GADT' if __match_val is KW_GADT else ('TRUE' if __match_val is TRUE else ('FALSE' if __match_val is FALSE else ('PLUS' if __match_val is PLUS else ('MINUS' if __match_val is MINUS else ('STAR' if __match_val is STAR else ('SLASH' if __match_val is SLASH else ('PERCENT' if __match_val is PERCENT else ('ARROW' if __match_val is ARROW else ('FAT_ARROW' if __match_val is FAT_ARROW else ('DOUBLE_COLON' if __match_val is DOUBLE_COLON else ('EQUALS' if __match_val is EQUALS else ('EQ' if __match_val is EQ else ('NEQ' if __match_val is NEQ else ('LT' if __match_val is LT else ('LE' if __match_val is LE else ('GT' if __match_val is GT else ('GE' if __match_val is GE else ('PIPE' if __match_val is PIPE else ('DOUBLE_PIPE' if __match_val is DOUBLE_PIPE else ('AMP' if __match_val is AMP else ('DOUBLE_AMP' if __match_val is DOUBLE_AMP else ('LEFT_ARROW' if __match_val is LEFT_ARROW else ('DOUBLE_PLUS' if __match_val is DOUBLE_PLUS else ('BANG' if __match_val is BANG else ('AT' if __match_val is AT else ('LPAREN' if __match_val is LPAREN else ('RPAREN' if __match_val is RPAREN else ('LBRACKET' if __match_val is LBRACKET else ('RBRACKET' if __match_val is RBRACKET else ('LBRACE' if __match_val is LBRACE else ('RBRACE' if __match_val is RBRACE else ('COMMA' if __match_val is COMMA else ('COLON' if __match_val is COLON else ('DOT' if __match_val is DOT else ('UNDERSCORE' if __match_val is UNDERSCORE else ('SEMICOLON' if __match_val is SEMICOLON else ('BACKTICK' if __match_val is BACKTICK else ('NEWLINE' if __match_val is NEWLINE else 'EOF'))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))(tt)