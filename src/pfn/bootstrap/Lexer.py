from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_, snd

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
    return '\x00' if atEnd(state) else String.unsafeAt(state.pos)(state.source)

def peekOffset(offset): return lambda state: (lambda pos: '\x00' if pos >= String.length(state.source) else String.unsafeAt(pos)(state.source))(state.pos + offset)

def advance(state):
    return ('\x00', state) if atEnd(state) else (lambda char: (lambda newState: (char, newState))(Record({**state, "pos": state.pos + 1, "line": state.line + 1, "column": 1}) if char == '\n' else Record({**state, "pos": state.pos + 1, "column": state.column + 1})))(String.unsafeAt(state.pos)(state.source))

def _match_(expected): return lambda state: (False, state) if atEnd(state) or String.unsafeAt(state.pos)(state.source) != expected else (lambda __let_val_0: (True, __let_val_0[1]) if isinstance(__let_val_0, tuple) and len(__let_val_0) == 2 else None)(advance(state))

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

def scanNumber(startPos): return lambda startLine: lambda startCol: lambda firstChar: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda digits: lambda st: (lambda __let_val_1: __cell[0](digits)(__let_val_1[1]) if __let_val_1[0] == '_' else __cell[0]([__let_val_1[0]] + digits)(__let_val_1[1]) if isinstance(__let_val_1, tuple) and len(__let_val_1) == 2 else None)(advance(st)) if isDigit(peek(st)) or peek(st) == '_' else (digits, st))) or (lambda __let_val_7: (lambda __let_val_6: (lambda __let_val_5: (lambda __let_val_4: (lambda __let_val_3: (lambda digits3: (lambda __let_val_2: (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(__let_val_2[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val_2[1])))(String.toFloat(str)))(String.fromList(reverse(__let_val_2[0]))) if isinstance(__let_val_2, tuple) and len(__let_val_2) == 2 else None)(__cell[0](digits3)(__let_val_3[1])))([__let_val_4[0]] + __let_val_5[0] if __let_val_3[0] == '\x00' else [__let_val_3[0]] + [__let_val_4[0]] + __let_val_5[0]) if isinstance(__let_val_3, tuple) and len(__let_val_3) == 2 else None)(advance(__let_val_4[1]) if peek(__let_val_4[1]) == '+' or peek(__let_val_4[1]) == '-' else ('\x00', __let_val_4[1])) if isinstance(__let_val_4, tuple) and len(__let_val_4) == 2 else None)(advance(__let_val_5[1])) if peek(__let_val_5[1]) == 'e' or peek(__let_val_5[1]) == 'E' else (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(__let_val_7[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val_7[1])))(String.toFloat(str)))(String.fromList(reverse(__let_val_5[0]))) if isinstance(__let_val_5, tuple) and len(__let_val_5) == 2 else None)(__cell[0]([__let_val_6[0]] + __let_val_7[0])(__let_val_6[1])) if isinstance(__let_val_6, tuple) and len(__let_val_6) == 2 else None)(advance(__let_val_7[1])) if peek(__let_val_7[1]) == '.' and isDigit(peekOffset(1)(__let_val_7[1])) else (lambda str: (lambda value: (lambda span: addToken(INT)(IntValue(value))(span)(__let_val_7[1]))(spanFrom(startPos)(startLine)(startCol)(__let_val_7[1])))(String.toInt(str)))(String.fromList(reverse(__let_val_7[0]))) if isinstance(__let_val_7, tuple) and len(__let_val_7) == 2 else None)(__cell[0]([firstChar])(state))))([None])

def escapeChar(c):
    return (lambda __match_val: ('\n' if __match_val == 'n' else ('\t' if __match_val == 't' else ('\r' if __match_val == 'r' else ('\\' if __match_val == '\\' else ('"' if __match_val == '"' else ("'" if __match_val == "'" else c)))))))(c)

def scanString(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: Error(Record({"message": 'Unterminated string', "span": spanFrom(startPos)(startLine)(startCol)(st)})) if atEnd(st) else (lambda __let_val_8: Ok((chars, __let_val_8[1])) if isinstance(__let_val_8, tuple) and len(__let_val_8) == 2 else None)(advance(st)) if peek(st) == '"' else (lambda __let_val_10: Error(Record({"message": 'Unterminated escape sequence', "span": spanFrom(startPos)(startLine)(startCol)(__let_val_10[1])})) if atEnd(__let_val_10[1]) else (lambda __let_val_9: __cell[0]([escapeChar(__let_val_9[0])] + chars)(__let_val_9[1]) if isinstance(__let_val_9, tuple) and len(__let_val_9) == 2 else None)(advance(__let_val_10[1])) if isinstance(__let_val_10, tuple) and len(__let_val_10) == 2 else None)(advance(st)) if peek(st) == '\\' else (lambda __let_val_11: __cell[0]([__let_val_11[0]] + chars)(__let_val_11[1]) if isinstance(__let_val_11, tuple) and len(__let_val_11) == 2 else None)(advance(st)))) or (lambda __match_val: ((lambda str: (lambda span: Ok(addToken(STRING)(StringValue(str))(span)(__match_val._field0[1])))(spanFrom(startPos)(startLine)(startCol)(__match_val._field0[1])))(String.fromList(reverse(__match_val._field0[0]))) if isinstance(__match_val, Ok) else Error(__match_val._field0)))(__cell[0]([])(state))))([None])

def scanChar(startPos): return lambda startLine: lambda startCol: lambda state: Error(Record({"message": 'Unterminated character literal', "span": spanFrom(startPos)(startLine)(startCol)(state)})) if atEnd(state) else Error(Record({"message": 'Empty character literal', "span": spanFrom(startPos)(startLine)(startCol)(state)})) if peek(state) == "'" else (lambda __let_val_15: Error(Record({"message": 'Unterminated character literal', "span": spanFrom(startPos)(startLine)(startCol)(__let_val_15[1])})) if atEnd(__let_val_15[1]) or peek(__let_val_15[1]) != "'" else (lambda __let_val_14: (lambda span: Ok(addToken(CHAR)(CharValue(__let_val_15[0]))(span)(__let_val_14[1])))(spanFrom(startPos)(startLine)(startCol)(__let_val_14[1])) if isinstance(__let_val_14, tuple) and len(__let_val_14) == 2 else None)(advance(__let_val_15[1])) if isinstance(__let_val_15, tuple) and len(__let_val_15) == 2 else None)((lambda __let_val_13: ('\x00', __let_val_13[1]) if atEnd(__let_val_13[1]) else (lambda __let_val_12: (escapeChar(__let_val_12[0]), __let_val_12[1]) if isinstance(__let_val_12, tuple) and len(__let_val_12) == 2 else None)(advance(__let_val_13[1])) if isinstance(__let_val_13, tuple) and len(__let_val_13) == 2 else None)(advance(state)) if peek(state) == '\\' else advance(state))

def scanIdentifier(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: (lambda __let_val_16: __cell[0]([__let_val_16[0]] + chars)(__let_val_16[1]) if isinstance(__let_val_16, tuple) and len(__let_val_16) == 2 else None)(advance(st)) if isAlnum(peek(st)) or peek(st) == '_' else (chars, st))) or (lambda __let_val_17: (lambda text: (lambda span: (lambda __match_val: (addStringToken(__match_val._field0)(text)(span)(__let_val_17[1]) if isinstance(__match_val, Just) else addStringToken(IDENT)(text)(span)(__let_val_17[1])))(lookupKeyword(text)))(spanFrom(startPos)(startLine)(startCol)(__let_val_17[1])))(String.fromList(reverse(__let_val_17[0]))) if isinstance(__let_val_17, tuple) and len(__let_val_17) == 2 else None)(__cell[0]([])(state))))([None])

def scanToken(state):
    return (lambda startPos: (lambda startLine: (lambda startCol: (lambda __let_val_18: Ok(__let_val_18[1]) if isWhitespace(__let_val_18[0]) else Ok(skipLineComment(__let_val_18[1])) if __let_val_18[0] == '-' and peek(__let_val_18[1]) == '-' else Ok(scanNumber(startPos)(startLine)(startCol)(__let_val_18[0])(__let_val_18[1])) if isDigit(__let_val_18[0]) else scanString(startPos)(startLine)(startCol)(__let_val_18[1]) if __let_val_18[0] == '"' else scanChar(startPos)(startLine)(startCol)(__let_val_18[1]) if __let_val_18[0] == "'" else Ok(addSimpleToken(UNDERSCORE)(spanFrom(startPos)(startLine)(startCol)(__let_val_18[1]))(__let_val_18[1])) if __let_val_18[0] == '_' and _not_(isAlnum(peek(__let_val_18[1])) or peek(__let_val_18[1]) == '_') else Ok(scanIdentifier(startPos)(startLine)(startCol)(state)) if isAlpha(__let_val_18[0]) or __let_val_18[0] == '_' else scanOperator(__let_val_18[0])(startPos)(startLine)(startCol)(__let_val_18[1]) if isinstance(__let_val_18, tuple) and len(__let_val_18) == 2 else None)(advance(state)))(state.column))(state.line))(state.pos)

def scanOperator(char): return lambda startPos: lambda startLine: lambda startCol: lambda state: (lambda span: (lambda addTok: (lambda __match_val: ((lambda __let_val_19: Ok(addSimpleToken(DOUBLE_PLUS)(span)(__let_val_19[1])) if __let_val_19[0] else addTok(PLUS) if isinstance(__let_val_19, tuple) and len(__let_val_19) == 2 else None)(_match_('+')(state)) if __match_val == '+' else ((lambda __let_val_20: Ok(addSimpleToken(ARROW)(span)(__let_val_20[1])) if __let_val_20[0] else addTok(MINUS) if isinstance(__let_val_20, tuple) and len(__let_val_20) == 2 else None)(_match_('>')(state)) if __match_val == '-' else (addTok(STAR) if __match_val == '*' else (addTok(SLASH) if __match_val == '/' else (addTok(PERCENT) if __match_val == '%' else ((lambda __let_val_21: Ok(addSimpleToken(DOUBLE_COLON)(span)(__let_val_21[1])) if __let_val_21[0] else addTok(COLON) if isinstance(__let_val_21, tuple) and len(__let_val_21) == 2 else None)(_match_(':')(state)) if __match_val == ':' else ((lambda __let_val_23: Ok(addSimpleToken(FAT_ARROW)(span)(__let_val_23[1])) if __let_val_23[0] else (lambda __let_val_22: Ok(addSimpleToken(EQ)(span)(__let_val_22[1])) if __let_val_22[0] else addTok(EQUALS) if isinstance(__let_val_22, tuple) and len(__let_val_22) == 2 else None)(_match_('=')(state)) if isinstance(__let_val_23, tuple) and len(__let_val_23) == 2 else None)(_match_('>')(state)) if __match_val == '=' else ((lambda __let_val_24: Ok(addSimpleToken(NEQ)(span)(__let_val_24[1])) if __let_val_24[0] else addTok(BANG) if isinstance(__let_val_24, tuple) and len(__let_val_24) == 2 else None)(_match_('=')(state)) if __match_val == '!' else (addTok(AT) if __match_val == '@' else ((lambda __let_val_26: Ok(addSimpleToken(LE)(span)(__let_val_26[1])) if __let_val_26[0] else (lambda __let_val_25: Ok(addSimpleToken(LEFT_ARROW)(span)(__let_val_25[1])) if __let_val_25[0] else addTok(LT) if isinstance(__let_val_25, tuple) and len(__let_val_25) == 2 else None)(_match_('-')(__let_val_26[1])) if isinstance(__let_val_26, tuple) and len(__let_val_26) == 2 else None)(_match_('=')(state)) if __match_val == '<' else ((lambda __let_val_27: Ok(addSimpleToken(GE)(span)(__let_val_27[1])) if __let_val_27[0] else addTok(GT) if isinstance(__let_val_27, tuple) and len(__let_val_27) == 2 else None)(_match_('=')(state)) if __match_val == '>' else ((lambda __let_val_28: Ok(addSimpleToken(DOUBLE_PIPE)(span)(__let_val_28[1])) if __let_val_28[0] else addTok(PIPE) if isinstance(__let_val_28, tuple) and len(__let_val_28) == 2 else None)(_match_('|')(state)) if __match_val == '|' else ((lambda __let_val_29: Ok(addSimpleToken(DOUBLE_AMP)(span)(__let_val_29[1])) if __let_val_29[0] else addTok(AMP) if isinstance(__let_val_29, tuple) and len(__let_val_29) == 2 else None)(_match_('&')(state)) if __match_val == '&' else (addTok(LPAREN) if __match_val == '(' else (addTok(RPAREN) if __match_val == ')' else (addTok(LBRACKET) if __match_val == '[' else (addTok(RBRACKET) if __match_val == ']' else (addTok(LBRACE) if __match_val == '{' else (addTok(RBRACE) if __match_val == '}' else (addTok(COMMA) if __match_val == ',' else (addTok(DOT) if __match_val == '.' else (addTok(SEMICOLON) if __match_val == ';' else (addTok(BACKTICK) if __match_val == '`' else Error(Record({"message": 'Unexpected character: ' + String.fromChar(char), "span": span}))))))))))))))))))))))))))(char))(lambda tt: Ok(addSimpleToken(tt)(span)(state))))(spanFrom(startPos)(startLine)(startCol)(state))

def tokenizeLoop(state):
    while not atEnd(state):
        result = scanToken(state)
        if isinstance(result, Ok):
            state = result._field0
        else:
            return result
    return Ok(state)


def tokenize(source):
    return (lambda state: (lambda __match_val: ((lambda eofSpan: (lambda eofToken: Ok(__match_val._field0.tokens + [eofToken]))(Record({"tokenType": EOF, "value": NoValue, "span": eofSpan})))(currentSpan(__match_val._field0)) if isinstance(__match_val, Ok) else Error(__match_val._field0)))(tokenizeLoop(state)))(initLexer(source))

def tokenizeOrThrow(source):
    return (lambda __match_val: (__match_val._field0 if isinstance(__match_val, Ok) else error('Lexer error: ' + __match_val._field0.message + ' at ' + show(__match_val._field0.span))))(tokenize(source))
