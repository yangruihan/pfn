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

from dataclasses import dataclass

@dataclass
class Span:
    start: int
    end: int
    line: int
    column: int

from dataclasses import dataclass

@dataclass
class Token:
    tokenType: TokenType
    value: TokenValue
    span: Span

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

def makeSpan(start): return lambda end: lambda line: lambda column: Record({"start": start, "end": end, "line": line, "column": column})

def token(tt): return lambda span: Record({"tokenType": tt, "value": NoValue, "span": span})

def stringToken(tt): return lambda value: lambda span: Record({"tokenType": tt, "value": StringValue(value), "span": span})

def intToken(value): return lambda span: Record({"tokenType": INT, "value": IntValue(value), "span": span})

def floatToken(value): return lambda span: Record({"tokenType": FLOAT, "value": FloatValue(value), "span": span})

def charToken(value): return lambda span: Record({"tokenType": CHAR, "value": CharValue(value), "span": span})

def tokenTypeName(tt):
    return (lambda __match_val: ('INT' if isinstance(__match_val, INT) else ('FLOAT' if isinstance(__match_val, FLOAT) else ('STRING' if isinstance(__match_val, STRING) else ('CHAR' if isinstance(__match_val, CHAR) else ('IDENT' if isinstance(__match_val, IDENT) else ('KW_DEF' if isinstance(__match_val, KW_DEF) else ('KW_LET' if isinstance(__match_val, KW_LET) else ('KW_IN' if isinstance(__match_val, KW_IN) else ('KW_IF' if isinstance(__match_val, KW_IF) else ('KW_THEN' if isinstance(__match_val, KW_THEN) else ('KW_ELSE' if isinstance(__match_val, KW_ELSE) else ('KW_MATCH' if isinstance(__match_val, KW_MATCH) else ('KW_WITH' if isinstance(__match_val, KW_WITH) else ('KW_TYPE' if isinstance(__match_val, KW_TYPE) else ('KW_INTERFACE' if isinstance(__match_val, KW_INTERFACE) else ('KW_IMPL' if isinstance(__match_val, KW_IMPL) else ('KW_IMPORT' if isinstance(__match_val, KW_IMPORT) else ('KW_EXPORT' if isinstance(__match_val, KW_EXPORT) else ('KW_MODULE' if isinstance(__match_val, KW_MODULE) else ('KW_AS' if isinstance(__match_val, KW_AS) else ('KW_EFFECT' if isinstance(__match_val, KW_EFFECT) else ('KW_HANDLER' if isinstance(__match_val, KW_HANDLER) else ('KW_HANDLE' if isinstance(__match_val, KW_HANDLE) else ('KW_DO' if isinstance(__match_val, KW_DO) else ('KW_FORALL' if isinstance(__match_val, KW_FORALL) else ('KW_EXISTS' if isinstance(__match_val, KW_EXISTS) else ('KW_DATA' if isinstance(__match_val, KW_DATA) else ('KW_FAMILY' if isinstance(__match_val, KW_FAMILY) else ('KW_WHERE' if isinstance(__match_val, KW_WHERE) else ('KW_FN' if isinstance(__match_val, KW_FN) else ('KW_GADT' if isinstance(__match_val, KW_GADT) else ('TRUE' if isinstance(__match_val, TRUE) else ('FALSE' if isinstance(__match_val, FALSE) else ('PLUS' if isinstance(__match_val, PLUS) else ('MINUS' if isinstance(__match_val, MINUS) else ('STAR' if isinstance(__match_val, STAR) else ('SLASH' if isinstance(__match_val, SLASH) else ('PERCENT' if isinstance(__match_val, PERCENT) else ('ARROW' if isinstance(__match_val, ARROW) else ('FAT_ARROW' if isinstance(__match_val, FAT_ARROW) else ('DOUBLE_COLON' if isinstance(__match_val, DOUBLE_COLON) else ('EQUALS' if isinstance(__match_val, EQUALS) else ('EQ' if isinstance(__match_val, EQ) else ('NEQ' if isinstance(__match_val, NEQ) else ('LT' if isinstance(__match_val, LT) else ('LE' if isinstance(__match_val, LE) else ('GT' if isinstance(__match_val, GT) else ('GE' if isinstance(__match_val, GE) else ('PIPE' if isinstance(__match_val, PIPE) else ('DOUBLE_PIPE' if isinstance(__match_val, DOUBLE_PIPE) else ('AMP' if isinstance(__match_val, AMP) else ('DOUBLE_AMP' if isinstance(__match_val, DOUBLE_AMP) else ('LEFT_ARROW' if isinstance(__match_val, LEFT_ARROW) else ('DOUBLE_PLUS' if isinstance(__match_val, DOUBLE_PLUS) else ('BANG' if isinstance(__match_val, BANG) else ('AT' if isinstance(__match_val, AT) else ('LPAREN' if isinstance(__match_val, LPAREN) else ('RPAREN' if isinstance(__match_val, RPAREN) else ('LBRACKET' if isinstance(__match_val, LBRACKET) else ('RBRACKET' if isinstance(__match_val, RBRACKET) else ('LBRACE' if isinstance(__match_val, LBRACE) else ('RBRACE' if isinstance(__match_val, RBRACE) else ('COMMA' if isinstance(__match_val, COMMA) else ('COLON' if isinstance(__match_val, COLON) else ('DOT' if isinstance(__match_val, DOT) else ('UNDERSCORE' if isinstance(__match_val, UNDERSCORE) else ('SEMICOLON' if isinstance(__match_val, SEMICOLON) else ('BACKTICK' if isinstance(__match_val, BACKTICK) else ('NEWLINE' if isinstance(__match_val, NEWLINE) else 'EOF'))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))(tt)