from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from bootstrap.Token import *

class LexerError(Record):
    def __init__(self, message, span):
        super().__init__()
        self.message = message
        self.span = span

class LexerState(Record):
    def __init__(self, source, pos, line, column, tokens):
        super().__init__()
        self.source = source
        self.pos = pos
        self.line = line
        self.column = column
        self.tokens = tokens

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
    return LexerState(source, 0, 1, 1, [])

def atEnd(state):
    return state.pos >= String.length(state.source)

def peek(state):
    return '\x00' if atEnd(state) else String.unsafeAt(state.pos)(state.source)

def peekOffset(offset): return lambda state: (lambda pos: '\x00' if pos >= String.length(state.source) else String.unsafeAt(pos)(state.source))(state.pos + offset)

def advance(state):
    return ('\x00', state) if atEnd(state) else (lambda char: (lambda newState: (char, newState))(Record({**state, "pos": state.pos + 1, "line": state.line + 1, "column": 1}) if char == '\n' else Record({**state, "pos": state.pos + 1, "column": state.column + 1})))(String.unsafeAt(state.pos)(state.source))

def _match_(expected): return lambda state: (False, state) if atEnd(state) or String.unsafeAt(state.pos)(state.source) != expected else (lambda __let_val_0: (lambda newState: (True, newState))(__let_val_0[1]) if isinstance(__let_val_0, tuple) and len(__let_val_0) == 2 else None)(advance(state))

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

def scanNumber(startPos): return lambda startLine: lambda startCol: lambda firstChar: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda digits: lambda st: (lambda __let_val_1: (lambda c, st2: __cell[0](digits)(st2) if c == '_' else __cell[0]([c] + digits)(st2))(__let_val_1[0], __let_val_1[1]) if isinstance(__let_val_1, tuple) and len(__let_val_1) == 2 else None)(advance(st)) if isDigit(peek(st)) or peek(st) == '_' else (digits, st))) or (lambda __let_val_7: (lambda digits1, state1: (lambda __let_val_6: (lambda dot, state2: (lambda __let_val_5: (lambda digits2, state3: (lambda __let_val_4: (lambda e, state4: (lambda __let_val_3: (lambda sign, state5: (lambda digits3: (lambda __let_val_2: (lambda digits4, state6: (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(state6))(spanFrom(startPos)(startLine)(startCol)(state6)))(String.toFloat(str)))(String.fromList(reverse(digits4))))(__let_val_2[0], __let_val_2[1]) if isinstance(__let_val_2, tuple) and len(__let_val_2) == 2 else None)(__cell[0](digits3)(state5)))([e] + digits2 if sign == '\x00' else [sign] + [e] + digits2))(__let_val_3[0], __let_val_3[1]) if isinstance(__let_val_3, tuple) and len(__let_val_3) == 2 else None)(advance(state4) if peek(state4) == '+' or peek(state4) == '-' else ('\x00', state4)))(__let_val_4[0], __let_val_4[1]) if isinstance(__let_val_4, tuple) and len(__let_val_4) == 2 else None)(advance(state3)) if peek(state3) == 'e' or peek(state3) == 'E' else (lambda str: (lambda value: (lambda span: addToken(FLOAT)(FloatValue(value))(span)(state1))(spanFrom(startPos)(startLine)(startCol)(state1)))(String.toFloat(str)))(String.fromList(reverse(digits2))))(__let_val_5[0], __let_val_5[1]) if isinstance(__let_val_5, tuple) and len(__let_val_5) == 2 else None)(__cell[0]([dot] + digits1)(state2)))(__let_val_6[0], __let_val_6[1]) if isinstance(__let_val_6, tuple) and len(__let_val_6) == 2 else None)(advance(state1)) if peek(state1) == '.' and isDigit(peekOffset(1)(state1)) else (lambda str: (lambda value: (lambda span: addToken(INT)(IntValue(value))(span)(state1))(spanFrom(startPos)(startLine)(startCol)(state1)))(String.toInt(str)))(String.fromList(reverse(digits1))))(__let_val_7[0], __let_val_7[1]) if isinstance(__let_val_7, tuple) and len(__let_val_7) == 2 else None)(__cell[0]([firstChar])(state))))([None])

def escapeChar(c):
    return (lambda __match_val: ('\n' if __match_val == 'n' else ('\t' if __match_val == 't' else ('\r' if __match_val == 'r' else ('\\' if __match_val == '\\' else ('"' if __match_val == '"' else ("'" if __match_val == "'" else c)))))))(c)

def scanString(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: Error(LexerError('Unterminated string', spanFrom(startPos)(startLine)(startCol)(st))) if atEnd(st) else (lambda __let_val_8: (lambda st2: Ok(chars)(st2))(__let_val_8[1]) if isinstance(__let_val_8, tuple) and len(__let_val_8) == 2 else None)(advance(st)) if peek(st) == '"' else (lambda __let_val_10: (lambda st2: Error(LexerError('Unterminated escape sequence', spanFrom(startPos)(startLine)(startCol)(st2))) if atEnd(st2) else (lambda __let_val_9: (lambda c, st3: __cell[0]([escapeChar(c)] + chars)(st3))(__let_val_9[0], __let_val_9[1]) if isinstance(__let_val_9, tuple) and len(__let_val_9) == 2 else None)(advance(st2)))(__let_val_10[1]) if isinstance(__let_val_10, tuple) and len(__let_val_10) == 2 else None)(advance(st)) if peek(st) == '\\' else (lambda __let_val_11: (lambda c, st2: __cell[0]([c] + chars)(st2))(__let_val_11[0], __let_val_11[1]) if isinstance(__let_val_11, tuple) and len(__let_val_11) == 2 else None)(advance(st)))) or (lambda __match_val: ((lambda str: (lambda span: Ok(addToken(STRING)(StringValue(str))(span)(__match_val._field1)))(spanFrom(startPos)(startLine)(startCol)(__match_val._field1)))(String.fromList(reverse(__match_val._field0))) if isinstance(__match_val, Ok) else Error(__match_val._field0)))(__cell[0]([])(state))))([None])

def scanChar(startPos): return lambda startLine: lambda startCol: lambda state: Error(LexerError('Unterminated character literal', spanFrom(startPos)(startLine)(startCol)(state))) if atEnd(state) else Error(LexerError('Empty character literal', spanFrom(startPos)(startLine)(startCol)(state))) if peek(state) == "'" else (lambda __let_val_15: (lambda charValue, state2: Error(LexerError('Unterminated character literal', spanFrom(startPos)(startLine)(startCol)(state2))) if atEnd(state2) or peek(state2) != "'" else (lambda __let_val_14: (lambda state3: (lambda span: Ok(addToken(CHAR)(CharValue(charValue))(span)(state3)))(spanFrom(startPos)(startLine)(startCol)(state3)))(__let_val_14[1]) if isinstance(__let_val_14, tuple) and len(__let_val_14) == 2 else None)(advance(state2)))(__let_val_15[0], __let_val_15[1]) if isinstance(__let_val_15, tuple) and len(__let_val_15) == 2 else None)((lambda __let_val_13: (lambda s1: ('\x00', s1) if atEnd(s1) else (lambda __let_val_12: (lambda c, s2: (escapeChar(c), s2))(__let_val_12[0], __let_val_12[1]) if isinstance(__let_val_12, tuple) and len(__let_val_12) == 2 else None)(advance(s1)))(__let_val_13[1]) if isinstance(__let_val_13, tuple) and len(__let_val_13) == 2 else None)(advance(state)) if peek(state) == '\\' else advance(state))

def scanIdentifier(startPos): return lambda startLine: lambda startCol: lambda state: (lambda __cell: (__cell.__setitem__(0, (lambda chars: lambda st: (lambda __let_val_16: (lambda c, st2: __cell[0]([c] + chars)(st2))(__let_val_16[0], __let_val_16[1]) if isinstance(__let_val_16, tuple) and len(__let_val_16) == 2 else None)(advance(st)) if isAlnum(peek(st)) or peek(st) == '_' else (chars, st))) or (lambda __let_val_17: (lambda chars, state2: (lambda text: (lambda span: (lambda __match_val: (addStringToken(__match_val._field0)(text)(span)(state2) if isinstance(__match_val, Just) else addStringToken(IDENT)(text)(span)(state2)))(lookupKeyword(text)))(spanFrom(startPos)(startLine)(startCol)(state2)))(String.fromList(reverse(chars))))(__let_val_17[0], __let_val_17[1]) if isinstance(__let_val_17, tuple) and len(__let_val_17) == 2 else None)(__cell[0]([])(state))))([None])

def scanToken(state):
    return (lambda startPos: (lambda startLine: (lambda startCol: (lambda __let_val_18: (lambda char, state1: Ok(state1) if isWhitespace(char) else Ok(skipLineComment(state1)) if char == '-' and peek(state1) == '-' else Ok(scanNumber(startPos)(startLine)(startCol)(char)(state1)) if isDigit(char) else scanString(startPos)(startLine)(startCol)(state1) if char == '"' else scanChar(startPos)(startLine)(startCol)(state1) if char == "'" else Ok(addSimpleToken(UNDERSCORE)(spanFrom(startPos)(startLine)(startCol)(state1))(state1)) if char == '_' and _not_(isAlnum(peek(state1)) or peek(state1) == '_') else Ok(scanIdentifier(startPos)(startLine)(startCol)(state)) if isAlpha(char) or char == '_' else scanOperator(char)(startPos)(startLine)(startCol)(state1))(__let_val_18[0], __let_val_18[1]) if isinstance(__let_val_18, tuple) and len(__let_val_18) == 2 else None)(advance(state)))(state.column))(state.line))(state.pos)

def scanOperator(char): return lambda startPos: lambda startLine: lambda startCol: lambda state: (lambda span: (lambda addTok: (lambda __match_val: ((lambda __let_val_19: (lambda matched, state2: Ok(addSimpleToken(DOUBLE_PLUS)(span)(state2)) if matched else addTok(PLUS))(__let_val_19[0], __let_val_19[1]) if isinstance(__let_val_19, tuple) and len(__let_val_19) == 2 else None)(_match_('+')(state)) if __match_val == '+' else ((lambda __let_val_20: (lambda matched, state2: Ok(addSimpleToken(ARROW)(span)(state2)) if matched else addTok(MINUS))(__let_val_20[0], __let_val_20[1]) if isinstance(__let_val_20, tuple) and len(__let_val_20) == 2 else None)(_match_('>')(state)) if __match_val == '-' else (addTok(STAR) if __match_val == '*' else (addTok(SLASH) if __match_val == '/' else (addTok(PERCENT) if __match_val == '%' else ((lambda __let_val_21: (lambda matched, state2: Ok(addSimpleToken(DOUBLE_COLON)(span)(state2)) if matched else addTok(COLON))(__let_val_21[0], __let_val_21[1]) if isinstance(__let_val_21, tuple) and len(__let_val_21) == 2 else None)(_match_(':')(state)) if __match_val == ':' else ((lambda __let_val_23: (lambda matched1, state2: Ok(addSimpleToken(FAT_ARROW)(span)(state2)) if matched1 else (lambda __let_val_22: (lambda matched2, state3: Ok(addSimpleToken(EQ)(span)(state3)) if matched2 else addTok(EQUALS))(__let_val_22[0], __let_val_22[1]) if isinstance(__let_val_22, tuple) and len(__let_val_22) == 2 else None)(_match_('=')(state)))(__let_val_23[0], __let_val_23[1]) if isinstance(__let_val_23, tuple) and len(__let_val_23) == 2 else None)(_match_('>')(state)) if __match_val == '=' else ((lambda __let_val_24: (lambda matched, state2: Ok(addSimpleToken(NEQ)(span)(state2)) if matched else addTok(BANG))(__let_val_24[0], __let_val_24[1]) if isinstance(__let_val_24, tuple) and len(__let_val_24) == 2 else None)(_match_('=')(state)) if __match_val == '!' else (addTok(AT) if __match_val == '@' else ((lambda __let_val_26: (lambda matched1, state2: Ok(addSimpleToken(LE)(span)(state2)) if matched1 else (lambda __let_val_25: (lambda matched2, state3: Ok(addSimpleToken(LEFT_ARROW)(span)(state3)) if matched2 else addTok(LT))(__let_val_25[0], __let_val_25[1]) if isinstance(__let_val_25, tuple) and len(__let_val_25) == 2 else None)(_match_('-')(state2)))(__let_val_26[0], __let_val_26[1]) if isinstance(__let_val_26, tuple) and len(__let_val_26) == 2 else None)(_match_('=')(state)) if __match_val == '<' else ((lambda __let_val_27: (lambda matched, state2: Ok(addSimpleToken(GE)(span)(state2)) if matched else addTok(GT))(__let_val_27[0], __let_val_27[1]) if isinstance(__let_val_27, tuple) and len(__let_val_27) == 2 else None)(_match_('=')(state)) if __match_val == '>' else ((lambda __let_val_28: (lambda matched, state2: Ok(addSimpleToken(DOUBLE_PIPE)(span)(state2)) if matched else addTok(PIPE))(__let_val_28[0], __let_val_28[1]) if isinstance(__let_val_28, tuple) and len(__let_val_28) == 2 else None)(_match_('|')(state)) if __match_val == '|' else ((lambda __let_val_29: (lambda matched, state2: Ok(addSimpleToken(DOUBLE_AMP)(span)(state2)) if matched else addTok(AMP))(__let_val_29[0], __let_val_29[1]) if isinstance(__let_val_29, tuple) and len(__let_val_29) == 2 else None)(_match_('&')(state)) if __match_val == '&' else (addTok(LPAREN) if __match_val == '(' else (addTok(RPAREN) if __match_val == ')' else (addTok(LBRACKET) if __match_val == '[' else (addTok(RBRACKET) if __match_val == ']' else (addTok(LBRACE) if __match_val == '{' else (addTok(RBRACE) if __match_val == '}' else (addTok(COMMA) if __match_val == ',' else (addTok(DOT) if __match_val == '.' else (addTok(SEMICOLON) if __match_val == ';' else (addTok(BACKTICK) if __match_val == '`' else Error(LexerError('Unexpected character: ' + String.fromChar(char), span))))))))))))))))))))))))))(char))(lambda tt: Ok(addSimpleToken(tt)(span)(state))))(spanFrom(startPos)(startLine)(startCol)(state))

def tokenizeLoop(state):
    return (lambda __cell: (__cell.__setitem__(0, (lambda st: Ok(st) if atEnd(st) else (lambda __match_val: (__cell[0](__match_val._field0) if isinstance(__match_val, Ok) else Error(__match_val._field0)))(scanToken(st)))) or __cell[0](state)))([None])

def tokenize(source):
    return (lambda state: (lambda __match_val: ((lambda eofSpan: (lambda eofToken: Ok(__match_val._field0.tokens + [eofToken]))(Record({"tokenType": EOF, "value": NoValue, "span": eofSpan})))(currentSpan(__match_val._field0)) if isinstance(__match_val, Ok) else Error(__match_val._field0)))(tokenizeLoop(state)))(initLexer(source))

def tokenizeOrThrow(source):
    return (lambda __match_val: (__match_val._field0 if isinstance(__match_val, Ok) else error('Lexer error: ' + __match_val._field0.message + ' at ' + show(__match_val._field0.span))))(tokenize(source))