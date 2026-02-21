from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class TokenType(Enum):
    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()

    # Identifiers and keywords
    IDENT = auto()
    KW_DEF = auto()
    KW_LET = auto()
    KW_IN = auto()
    KW_IF = auto()
    KW_THEN = auto()
    KW_ELSE = auto()
    KW_MATCH = auto()
    KW_WITH = auto()
    KW_TYPE = auto()
    KW_INTERFACE = auto()
    KW_IMPL = auto()
    KW_IMPORT = auto()
    KW_EXPORT = auto()
    KW_MODULE = auto()
    KW_AS = auto()
    KW_EFFECT = auto()
    KW_DO = auto()
    KW_FORALL = auto()
    KW_EXISTS = auto()
    KW_DATA = auto()
    KW_FAMILY = auto()
    KW_WHERE = auto()
    KW_FN = auto()
    KW_GADT = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    DOUBLE_COLON = auto()
    EQUALS = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    PIPE = auto()
    DOUBLE_PIPE = auto()
    AMP = auto()
    DOUBLE_AMP = auto()
    LEFT_ARROW = auto()
    DOUBLE_PLUS = auto()
    BANG = auto()
    AT = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    UNDERSCORE = auto()
    SEMICOLON = auto()
    BACKTICK = auto()

    # Special
    NEWLINE = auto()
    EOF = auto()


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    line: int
    column: int

    def __repr__(self):
        return f"Span({self.line}:{self.column})"


@dataclass
class Token:
    type: TokenType
    value: str | int | float | None
    span: Span

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.span})"


KEYWORDS: dict[str, TokenType] = {
    "def": TokenType.KW_DEF,
    "let": TokenType.KW_LET,
    "in": TokenType.KW_IN,
    "if": TokenType.KW_IF,
    "then": TokenType.KW_THEN,
    "else": TokenType.KW_ELSE,
    "match": TokenType.KW_MATCH,
    "with": TokenType.KW_WITH,
    "type": TokenType.KW_TYPE,
    "gadt": TokenType.KW_GADT,
    "interface": TokenType.KW_INTERFACE,
    "impl": TokenType.KW_IMPL,
    "import": TokenType.KW_IMPORT,
    "export": TokenType.KW_EXPORT,
    "module": TokenType.KW_MODULE,
    "as": TokenType.KW_AS,
    "effect": TokenType.KW_EFFECT,
    "do": TokenType.KW_DO,
    "forall": TokenType.KW_FORALL,
    "exists": TokenType.KW_EXISTS,
    "data": TokenType.KW_DATA,
    "family": TokenType.KW_FAMILY,
    "where": TokenType.KW_WHERE,
    "fn": TokenType.KW_FN,
    "True": TokenType.TRUE,
    "False": TokenType.FALSE,
}
