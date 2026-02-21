from __future__ import annotations

from pfn.lexer.tokens import KEYWORDS, Span, Token, TokenType


class LexerError(Exception):
    def __init__(self, message: str, span: Span):
        self.message = message
        self.span = span
        super().__init__(f"{message} at {span}")


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        self.tokens = []
        while not self._at_end():
            self._scan_token()
        self._add_token(TokenType.EOF, None)
        return self.tokens

    def _at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.source):
            return "\0"
        return self.source[pos]

    def _advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._at_end() or self.source[self.pos] != expected:
            return False
        self._advance()
        return True

    def _current_span(self) -> Span:
        return Span(
            start=self.pos,
            end=self.pos,
            line=self.line,
            column=self.column,
        )

    def _span_from(self, start_pos: int, start_line: int, start_col: int) -> Span:
        return Span(
            start=start_pos,
            end=self.pos,
            line=start_line,
            column=start_col,
        )

    def _add_token(
        self,
        token_type: TokenType,
        value: str | int | float | None,
        span: Span | None = None,
    ) -> None:
        if span is None:
            span = self._current_span()
        self.tokens.append(Token(token_type, value, span))

    def _scan_token(self) -> None:
        start_pos = self.pos
        start_line = self.line
        start_col = self.column

        char = self._advance()

        if char.isspace():
            return

        if char == "-" and self._peek() == "-":
            self._line_comment()
            return

        if char.isdigit():
            self._number(start_pos, start_line, start_col, char)
            return

        if char == '"':
            self._string(start_pos, start_line, start_col)
            return

        if char == "'":
            self._char(start_pos, start_line, start_col)
            return

        if char.isalpha() or char == "_":
            if char == "_" and not (self._peek().isalnum() or self._peek() == "_"):
                self._add_token(
                    TokenType.UNDERSCORE,
                    "_",
                    self._span_from(start_pos, start_line, start_col),
                )
                return
            self._identifier(start_pos, start_line, start_col)
            return

        if char == "+":
            if self._match("+"):
                self._add_token(
                    TokenType.DOUBLE_PLUS,
                    "++",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.PLUS,
                    "+",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "-":
            if self._match(">"):
                self._add_token(
                    TokenType.ARROW,
                    "->",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.MINUS,
                    "-",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "*":
            self._add_token(
                TokenType.STAR, "*", self._span_from(start_pos, start_line, start_col)
            )
        elif char == "/":
            self._add_token(
                TokenType.SLASH, "/", self._span_from(start_pos, start_line, start_col)
            )
        elif char == "%":
            self._add_token(
                TokenType.PERCENT,
                "%",
                self._span_from(start_pos, start_line, start_col),
            )
        elif char == ":":
            if self._match(":"):
                self._add_token(
                    TokenType.DOUBLE_COLON,
                    "::",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.COLON,
                    ":",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "=":
            if self._match(">"):
                self._add_token(
                    TokenType.FAT_ARROW,
                    "=>",
                    self._span_from(start_pos, start_line, start_col),
                )
            elif self._match("="):
                self._add_token(
                    TokenType.EQ,
                    "==",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.EQUALS,
                    "=",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "!":
            if self._match("="):
                self._add_token(
                    TokenType.NEQ,
                    "!=",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.BANG,
                    "!",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "<":
            if self._match("="):
                self._add_token(
                    TokenType.LE,
                    "<=",
                    self._span_from(start_pos, start_line, start_col),
                )
            elif self._match("-"):
                self._add_token(
                    TokenType.LEFT_ARROW,
                    "<-",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.LT,
                    "<",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == ">":
            if self._match("="):
                self._add_token(
                    TokenType.GE,
                    ">=",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.GT,
                    ">",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "|":
            if self._match("|"):
                self._add_token(
                    TokenType.DOUBLE_PIPE,
                    "||",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.PIPE,
                    "|",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "&":
            if self._match("&"):
                self._add_token(
                    TokenType.DOUBLE_AMP,
                    "&&",
                    self._span_from(start_pos, start_line, start_col),
                )
            else:
                self._add_token(
                    TokenType.AMP,
                    "&",
                    self._span_from(start_pos, start_line, start_col),
                )
        elif char == "(":
            self._add_token(
                TokenType.LPAREN, "(", self._span_from(start_pos, start_line, start_col)
            )
        elif char == ")":
            self._add_token(
                TokenType.RPAREN, ")", self._span_from(start_pos, start_line, start_col)
            )
        elif char == "[":
            self._add_token(
                TokenType.LBRACKET,
                "[",
                self._span_from(start_pos, start_line, start_col),
            )
        elif char == "]":
            self._add_token(
                TokenType.RBRACKET,
                "]",
                self._span_from(start_pos, start_line, start_col),
            )
        elif char == "{":
            self._add_token(
                TokenType.LBRACE, "{", self._span_from(start_pos, start_line, start_col)
            )
        elif char == "}":
            self._add_token(
                TokenType.RBRACE, "}", self._span_from(start_pos, start_line, start_col)
            )
        elif char == ",":
            self._add_token(
                TokenType.COMMA, ",", self._span_from(start_pos, start_line, start_col)
            )
        elif char == ".":
            self._add_token(
                TokenType.DOT, ".", self._span_from(start_pos, start_line, start_col)
            )
        elif char == ";":
            self._add_token(
                TokenType.SEMICOLON,
                ";",
                self._span_from(start_pos, start_line, start_col),
            )
        elif char == "`":
            self._add_token(
                TokenType.BACKTICK,
                "`",
                self._span_from(start_pos, start_line, start_col),
            )
        else:
            raise LexerError(
                f"Unexpected character: {char!r}",
                self._span_from(start_pos, start_line, start_col),
            )

    def _line_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _number(
        self, start_pos: int, start_line: int, start_col: int, first_char: str
    ) -> None:
        digits = [first_char]

        while self._peek().isdigit() or self._peek() == "_":
            char = self._advance()
            if char != "_":
                digits.append(char)

        if self._peek() == "." and self._peek(1).isdigit():
            digits.append(self._advance())
            while self._peek().isdigit() or self._peek() == "_":
                char = self._advance()
                if char != "_":
                    digits.append(char)

            if self._peek() in "eE":
                digits.append(self._advance())
                if self._peek() in "+-":
                    digits.append(self._advance())
                while self._peek().isdigit():
                    digits.append(self._advance())

            value = float("".join(digits))
            self._add_token(
                TokenType.FLOAT,
                value,
                self._span_from(start_pos, start_line, start_col),
            )
        else:
            value = int("".join(digits))
            self._add_token(
                TokenType.INT, value, self._span_from(start_pos, start_line, start_col)
            )

    def _string(self, start_pos: int, start_line: int, start_col: int) -> None:
        chars: list[str] = []

        while not self._at_end() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexerError(
                    "Unterminated string",
                    self._span_from(start_pos, start_line, start_col),
                )
            if self._peek() == "\\":
                self._advance()
                if self._at_end():
                    raise LexerError(
                        "Unterminated escape sequence",
                        self._span_from(start_pos, start_line, start_col),
                    )
                escaped = self._advance()
                if escaped == "n":
                    chars.append("\n")
                elif escaped == "t":
                    chars.append("\t")
                elif escaped == "r":
                    chars.append("\r")
                elif escaped == "\\":
                    chars.append("\\")
                elif escaped == '"':
                    chars.append('"')
                else:
                    chars.append(escaped)
            else:
                chars.append(self._advance())

        if self._at_end():
            raise LexerError(
                "Unterminated string",
                self._span_from(start_pos, start_line, start_col),
            )

        self._advance()
        self._add_token(
            TokenType.STRING,
            "".join(chars),
            self._span_from(start_pos, start_line, start_col),
        )

    def _char(self, start_pos: int, start_line: int, start_col: int) -> None:
        if self._at_end():
            raise LexerError(
                "Unterminated character literal",
                self._span_from(start_pos, start_line, start_col),
            )

        if self._peek() == "'":
            raise LexerError(
                "Empty character literal",
                self._span_from(start_pos, start_line, start_col),
            )

        char_value: str
        if self._peek() == "\\":
            self._advance()
            if self._at_end():
                raise LexerError(
                    "Unterminated escape sequence",
                    self._span_from(start_pos, start_line, start_col),
                )
            escaped = self._advance()
            if escaped == "n":
                char_value = "\n"
            elif escaped == "t":
                char_value = "\t"
            elif escaped == "r":
                char_value = "\r"
            elif escaped == "\\":
                char_value = "\\"
            elif escaped == "'":
                char_value = "'"
            else:
                char_value = escaped
        else:
            char_value = self._advance()

        if self._at_end() or self._peek() != "'":
            raise LexerError(
                "Unterminated character literal",
                self._span_from(start_pos, start_line, start_col),
            )

        self._advance()
        self._add_token(
            TokenType.CHAR,
            char_value,
            self._span_from(start_pos, start_line, start_col),
        )

    def _identifier(self, start_pos: int, start_line: int, start_col: int) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[start_pos : self.pos]
        token_type = KEYWORDS.get(text, TokenType.IDENT)
        self._add_token(
            token_type, text, self._span_from(start_pos, start_line, start_col)
        )
