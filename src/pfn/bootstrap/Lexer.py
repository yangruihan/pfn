from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from bootstrap.Token import *

from dataclasses import dataclass

@dataclass
class LexerError:
    message: str
    span: Span

from dataclasses import dataclass

@dataclass
class LexerState:
    source: str
    pos: int
    line: int
    column: int
    tokens: list[Token]

from dataclasses import dataclass
from typing import Union

@dataclass
class Ok:
    _field0: a

@dataclass
class Error:
    _field0: LexerError

LexerResult = Union[Ok, Error]

def initLexer(source):
    return Record({"source": source, "pos": 0, "line": 1, "column": 1, "tokens": []})

def atEnd(state):
    return state.pos >= String.length(state.source)

def peek(state):
    return '0' if atEnd(state) else String.unsafeAt(state.pos)(state.source)

def peekOffset(offset): return lambda state: (lambda pos: '0' if pos >= String.length(state.source) else String.unsafeAt(pos)(state.source))(state.pos + offset)

def advance(state):
    return (lambda char: (lambda newState: (char, newState))(Record({**state, "pos": state.pos + 1, "line": state.line + 1, "column": 1}) if char == '\n' else Record({**state, "pos": state.pos + 1, "column": state.column + 1})))(String.unsafeAt(state.pos)(state.source))

def _match_(expected): return lambda state: (False, state) if atEnd(state) or String.unsafeAt(state.pos)(state.source) != expected else (lambda __let_val: (True, __let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(state))

def currentSpan(state):
    return makeSpan(state.pos)(state.pos)(state.line)(state.column)

def spanFrom(startPos): return lambda startLine: lambda startCol: lambda state: makeSpan(startPos)(state.pos)(startLine)(startCol)

def addToken(tt): return lambda value: lambda span: lambda state: (lambda newToken: Record({**state, "tokens": state.tokens + [newToken]}))(Record({"tokenType": tt, "value": value, "span": span}))

def addSimpleToken(tt): return lambda span: lambda state: addToken(tt)(NoValue)(span)(state)

def addStringToken(tt): return lambda value: lambda span: lambda state: addToken(tt)(StringValue(value))(span)(state)

def isWhitespace(c):
    return c == ' ' or c == '\t' or c == '\n' or c == '\r'

def isDigit(c):
    return c >= '0' and c <= '9'

def isAlpha(c):
    return c >= 'a' and c <= 'z' or c >= 'A' and c <= 'Z'

def isAlnum(c):
    return isAlpha(c) or isDigit(c)

def skipLineComment(state):
    return state if atEnd(state) or peek(state) == '\n' else skipLineComment(snd(advance(state)))

def scanNumber(startPos): return lambda startLine: lambda startCol: lambda firstChar: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda digits: lambda st: (lambda __let_val: __cell[0](digits)(__let_val[1]) if __let_val[0] == '_' else __cell[0]([__let_val[0]] + digits)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(st)) if isDigit(peek(st)) or peek(st) == '_' else (digits, st))) or (lambda __let_val: (lambda __let_val: (lambda __let_val: (lambda __let_val: (lambda __let_val: (lambda digits3: (lambda __let_val: (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(__let_val[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val[1])))(String.toFloat(str)))(String.fromList(reverse(__let_val[0]))) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(__cell[0](digits3)(__let_val[1])))([__let_val[0]] + __let_val[0] if __let_val[0] == '0' else [__let_val[0]] + [__let_val[0]] + __let_val[0]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1]) if peek(__let_val[1]) == '+' or peek(__let_val[1]) == '-' else ('0', __let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1])) if peek(__let_val[1]) == 'e' or peek(__let_val[1]) == 'E' else (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(__let_val[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val[1])))(String.toFloat(str)))(String.fromList(reverse(__let_val[0]))) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(__cell[0]([__let_val[0]] + __let_val[0])(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1])) if peek(__let_val[1]) == '.' and isDigit(peekOffset(1)(__let_val[1])) else (lambda str: (lambda value: (lambda span: addToken(INT)(IntValue(value))(span)(__let_val[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val[1])))(String.toInt(str)))(String.fromList(reverse(__let_val[0]))) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(__cell[0]([firstChar])(state))))([None])

def escapeChar(c):
    return (lambda __match_val: ('\n' if __match_val == 'n' else ('\t' if __match_val == 't' else ('\r' if __match_val == 'r' else ('\\' if __match_val == '\\' else ('"' if __match_val == '"' else ("'" if __match_val == "'" else c)))))))(c)

def scanString(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: Error(Record({"message": 'Unterminated string', "span": spanFrom(startPos)(startLine)(startCol)(st)})) if atEnd(st) else (lambda __let_val: Ok(chars)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(st)) if peek(st) == '"' else (lambda __let_val: Error(Record({"message": 'Unterminated escape sequence', "span": spanFrom(startPos)(startLine)(startCol)(__let_val[1])})) if atEnd(__let_val[1]) else (lambda __let_val: __cell[0]([escapeChar(__let_val[0])] + chars)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(st)) if peek(st) == '\\' else (lambda __let_val: __cell[0]([__let_val[0]] + chars)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(st)))) or (lambda __match_val: ((lambda str: (lambda span: Ok(addToken(STRING)(StringValue(str))(span)(__match_val._field1))(Error))(spanFrom(startPos)(startLine)(startCol)(__match_val._field1)))(String.fromList(reverse(__match_val._field0))) if isinstance(__match_val, Ok) else Error(__match_val)))(__cell[0]([])(state))))([None])

def scanChar(startPos): return lambda startLine: lambda startCol: lambda state: Error(Record({"message": 'Unterminated character literal', "span": spanFrom(startPos)(startLine)(startCol)(state)})) if atEnd(state) else Error(Record({"message": 'Empty character literal', "span": spanFrom(startPos)(startLine)(startCol)(state)})) if peek(state) == "'" else (lambda __let_val: Error(Record({"message": 'Unterminated character literal', "span": spanFrom(startPos)(startLine)(startCol)(__let_val[1])})) if atEnd(__let_val[1]) or peek(__let_val[1]) != "'" else (lambda __let_val: (lambda span: Ok(addToken(CHAR)(CharValue(__let_val[0]))(span)(__let_val[1])))(spanFrom(startPos)(startLine)(startCol)(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)((lambda __let_val: ('0', __let_val[1]) if atEnd(__let_val[1]) else (lambda __let_val: (escapeChar(__let_val[0]), __let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(state)) if peek(state) == '\\' else advance(state))

def scanIdentifier(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: (lambda __let_val: __cell[0]([__let_val[0]] + chars)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(st)) if isAlnum(peek(st)) or peek(st) == '_' else (chars, st))) or (lambda __let_val: (lambda text: (lambda span: (lambda __match_val: (addStringToken(__match_val._field0)(text)(span)(__let_val[1]) if isinstance(__match_val, Just) else addStringToken(IDENT)(text)(span)(__let_val[1])))(lookupKeyword(text)))(spanFrom(startPos)(startLine)(startCol)(__let_val[1])))(String.fromList(reverse(__let_val[0]))) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(__cell[0]([])(state))))([None])

def scanToken(state):
    return (lambda startPos: (lambda startLine: (lambda startCol: (lambda __let_val: Ok(__let_val[1]) if isWhitespace(__let_val[0]) else Ok(skipLineComment(__let_val[1])) if __let_val[0] == '-' and peek(__let_val[1]) == '-' else Ok(scanNumber(startPos)(startLine)(startCol)(__let_val[0])(__let_val[1])) if isDigit(__let_val[0]) else scanString(startPos)(startLine)(startCol)(__let_val[1]) if __let_val[0] == '"' else scanChar(startPos)(startLine)(startCol)(__let_val[1]) if __let_val[0] == "'" else Ok(addSimpleToken(UNDERSCORE)(spanFrom(startPos)(startLine)(startCol)(__let_val[1]))(__let_val[1])) if __let_val[0] == '_' and _not_(isAlnum(peek(__let_val[1])) or peek(__let_val[1]) == '_') else Ok(scanIdentifier(startPos)(startLine)(startCol)(__let_val[1])) if isAlpha(__let_val[0]) or __let_val[0] == '_' else scanOperator(__let_val[0])(startPos)(startLine)(startCol)(__let_val[1]) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(advance(state)))(state.column))(state.line))(state.pos)

def scanOperator(char): return lambda startPos: lambda startLine: lambda startCol: lambda state: (lambda span: (lambda addTok: (lambda __match_val: ((lambda __let_val: Ok(addSimpleToken(DOUBLE_PLUS)(span)(__let_val[1])) if __let_val[0] else addTok(PLUS) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('+')(state)) if __match_val == '+' else ((lambda __let_val: Ok(addSimpleToken(ARROW)(span)(__let_val[1])) if __let_val[0] else addTok(MINUS) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('>')(state)) if __match_val == '-' else (addTok(STAR) if __match_val == '*' else (addTok(SLASH) if __match_val == '/' else (addTok(PERCENT) if __match_val == '%' else ((lambda __let_val: Ok(addSimpleToken(DOUBLE_COLON)(span)(__let_val[1])) if __let_val[0] else addTok(COLON) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_(':')(state)) if __match_val == ':' else ((lambda __let_val: Ok(addSimpleToken(FAT_ARROW)(span)(__let_val[1])) if __let_val[0] else (lambda __let_val: Ok(addSimpleToken(EQ)(span)(__let_val[1])) if __let_val[0] else addTok(EQUALS) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('=')(state)) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('>')(state)) if __match_val == '=' else ((lambda __let_val: Ok(addSimpleToken(NEQ)(span)(__let_val[1])) if __let_val[0] else addTok(BANG) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('=')(state)) if __match_val == '!' else (addTok(AT) if __match_val == '@' else ((lambda __let_val: Ok(addSimpleToken(LE)(span)(__let_val[1])) if __let_val[0] else (lambda __let_val: Ok(addSimpleToken(LEFT_ARROW)(span)(__let_val[1])) if __let_val[0] else addTok(LT) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('-')(__let_val[1])) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('=')(state)) if __match_val == '<' else ((lambda __let_val: Ok(addSimpleToken(GE)(span)(__let_val[1])) if __let_val[0] else addTok(GT) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('=')(state)) if __match_val == '>' else ((lambda __let_val: Ok(addSimpleToken(DOUBLE_PIPE)(span)(__let_val[1])) if __let_val[0] else addTok(PIPE) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('|')(state)) if __match_val == '|' else ((lambda __let_val: Ok(addSimpleToken(DOUBLE_AMP)(span)(__let_val[1])) if __let_val[0] else addTok(AMP) if isinstance(__let_val, tuple) and len(__let_val) == 2 else None)(_match_('&')(state)) if __match_val == '&' else (addTok(LPAREN) if __match_val == '(' else (addTok(RPAREN) if __match_val == ')' else (addTok(LBRACKET) if __match_val == '[' else (addTok(RBRACKET) if __match_val == ']' else (addTok(LBRACE) if __match_val == '{' else (addTok(RBRACE) if __match_val == '}' else (addTok(COMMA) if __match_val == ',' else (addTok(DOT) if __match_val == '.' else (addTok(SEMICOLON) if __match_val == ';' else (addTok(BACKTICK) if __match_val == '`' else Error(Record({"message": 'Unexpected character: ' + String.fromChar(char), "span": span}))))))))))))))))))))))))))(char))(lambda tt: Ok(addSimpleToken(tt)(span)(state))))(spanFrom(startPos)(startLine)(startCol)(state))

def tokenizeLoop(state):
    return Ok(state) if atEnd(state) else (lambda __match_val: (tokenizeLoop(__match_val._field0)(Error) if isinstance(__match_val, Ok) else Error(__match_val)))(scanToken(state))

def tokenize(source):
    return (lambda state: (lambda __match_val: ((lambda eofSpan: (lambda eofToken: Ok(__match_val._field0.tokens + [eofToken])(Error))(Record({"tokenType": EOF, "value": NoValue, "span": eofSpan})))(currentSpan(__match_val._field0)) if isinstance(__match_val, Ok) else Error(__match_val)))(tokenizeLoop(state)))(initLexer(source))

def tokenizeOrThrow(source):
    return (lambda __match_val: (__match_val._field0(Error) if isinstance(__match_val, Ok) else error('Lexer error: ' + __match_val.message + ' at ' + show(__match_val.span))))(tokenize(source))