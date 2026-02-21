import pytest

from pfn.lexer import Lexer, LexerError, Token, TokenType


class TestLexerInteger:
    def test_single_digit(self):
        tokens = Lexer("5").tokenize()
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == 5
        assert tokens[1].type == TokenType.EOF

    def test_multiple_digits(self):
        tokens = Lexer("12345").tokenize()
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == 12345

    def test_zero(self):
        tokens = Lexer("0").tokenize()
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == 0

    def test_negative_not_in_lexer(self):
        tokens = Lexer("-5").tokenize()
        assert tokens[0].type == TokenType.MINUS
        assert tokens[1].type == TokenType.INT
        assert tokens[1].value == 5

    def test_underscores(self):
        tokens = Lexer("1_000_000").tokenize()
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == 1000000


class TestLexerFloat:
    def test_simple_float(self):
        tokens = Lexer("3.14").tokenize()
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 3.14

    def test_float_with_exponent(self):
        tokens = Lexer("1.5e10").tokenize()
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 1.5e10

    def test_float_negative_exponent(self):
        tokens = Lexer("1.0e-5").tokenize()
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 1.0e-5


class TestLexerString:
    def test_simple_string(self):
        tokens = Lexer('"hello"').tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_empty_string(self):
        tokens = Lexer('""').tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""

    def test_string_with_escape(self):
        tokens = Lexer(r'"hello\nworld"').tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello\nworld"

    def test_unclosed_string_raises_error(self):
        with pytest.raises(LexerError):
            Lexer('"unclosed').tokenize()


class TestLexerChar:
    def test_simple_char(self):
        tokens = Lexer("'a'").tokenize()
        assert tokens[0].type == TokenType.CHAR
        assert tokens[0].value == "a"

    def test_escape_char(self):
        tokens = Lexer(r"'\n'").tokenize()
        assert tokens[0].type == TokenType.CHAR
        assert tokens[0].value == "\n"


class TestLexerIdentifiers:
    def test_simple_identifier(self):
        tokens = Lexer("foo").tokenize()
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "foo"

    def test_underscore_prefix(self):
        tokens = Lexer("_private").tokenize()
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "_private"

    def test_qualified_name(self):
        tokens = Lexer("List.map").tokenize()
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "List"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENT
        assert tokens[2].value == "map"


class TestLexerKeywords:
    def test_def_keyword(self):
        tokens = Lexer("def").tokenize()
        assert tokens[0].type == TokenType.KW_DEF

    def test_let_keyword(self):
        tokens = Lexer("let").tokenize()
        assert tokens[0].type == TokenType.KW_LET

    def test_if_keyword(self):
        tokens = Lexer("if").tokenize()
        assert tokens[0].type == TokenType.KW_IF

    def test_then_keyword(self):
        tokens = Lexer("then").tokenize()
        assert tokens[0].type == TokenType.KW_THEN

    def test_else_keyword(self):
        tokens = Lexer("else").tokenize()
        assert tokens[0].type == TokenType.KW_ELSE

    def test_match_keyword(self):
        tokens = Lexer("match").tokenize()
        assert tokens[0].type == TokenType.KW_MATCH

    def test_with_keyword(self):
        tokens = Lexer("with").tokenize()
        assert tokens[0].type == TokenType.KW_WITH

    def test_type_keyword(self):
        tokens = Lexer("type").tokenize()
        assert tokens[0].type == TokenType.KW_TYPE

    def test_true_keyword(self):
        tokens = Lexer("True").tokenize()
        assert tokens[0].type == TokenType.TRUE

    def test_false_keyword(self):
        tokens = Lexer("False").tokenize()
        assert tokens[0].type == TokenType.FALSE


class TestLexerOperators:
    def test_plus(self):
        tokens = Lexer("+").tokenize()
        assert tokens[0].type == TokenType.PLUS

    def test_minus(self):
        tokens = Lexer("-").tokenize()
        assert tokens[0].type == TokenType.MINUS

    def test_star(self):
        tokens = Lexer("*").tokenize()
        assert tokens[0].type == TokenType.STAR

    def test_slash(self):
        tokens = Lexer("/").tokenize()
        assert tokens[0].type == TokenType.SLASH

    def test_arrow(self):
        tokens = Lexer("->").tokenize()
        assert tokens[0].type == TokenType.ARROW

    def test_double_colon(self):
        tokens = Lexer("::").tokenize()
        assert tokens[0].type == TokenType.DOUBLE_COLON

    def test_equals(self):
        tokens = Lexer("=").tokenize()
        assert tokens[0].type == TokenType.EQUALS

    def test_double_equals(self):
        tokens = Lexer("==").tokenize()
        assert tokens[0].type == TokenType.EQ

    def test_not_equals(self):
        tokens = Lexer("!=").tokenize()
        assert tokens[0].type == TokenType.NEQ

    def test_less_than(self):
        tokens = Lexer("<").tokenize()
        assert tokens[0].type == TokenType.LT

    def test_less_equal(self):
        tokens = Lexer("<=").tokenize()
        assert tokens[0].type == TokenType.LE

    def test_greater_than(self):
        tokens = Lexer(">").tokenize()
        assert tokens[0].type == TokenType.GT

    def test_greater_equal(self):
        tokens = Lexer(">=").tokenize()
        assert tokens[0].type == TokenType.GE

    def test_pipe(self):
        tokens = Lexer("|").tokenize()
        assert tokens[0].type == TokenType.PIPE

    def test_double_pipe(self):
        tokens = Lexer("||").tokenize()
        assert tokens[0].type == TokenType.DOUBLE_PIPE

    def test_double_ampersand(self):
        tokens = Lexer("&&").tokenize()
        assert tokens[0].type == TokenType.DOUBLE_AMP

    def test_left_arrow(self):
        tokens = Lexer("<-").tokenize()
        assert tokens[0].type == TokenType.LEFT_ARROW

    def test_right_arrow_long(self):
        tokens = Lexer("=>").tokenize()
        assert tokens[0].type == TokenType.FAT_ARROW

    def test_double_plus(self):
        tokens = Lexer("++").tokenize()
        assert tokens[0].type == TokenType.DOUBLE_PLUS

    def test_cons_right(self):
        tokens = Lexer("::").tokenize()
        assert tokens[0].type == TokenType.DOUBLE_COLON


class TestLexerPunctuation:
    def test_left_paren(self):
        tokens = Lexer("(").tokenize()
        assert tokens[0].type == TokenType.LPAREN

    def test_right_paren(self):
        tokens = Lexer(")").tokenize()
        assert tokens[0].type == TokenType.RPAREN

    def test_left_bracket(self):
        tokens = Lexer("[").tokenize()
        assert tokens[0].type == TokenType.LBRACKET

    def test_right_bracket(self):
        tokens = Lexer("]").tokenize()
        assert tokens[0].type == TokenType.RBRACKET

    def test_left_brace(self):
        tokens = Lexer("{").tokenize()
        assert tokens[0].type == TokenType.LBRACE

    def test_right_brace(self):
        tokens = Lexer("}").tokenize()
        assert tokens[0].type == TokenType.RBRACE

    def test_comma(self):
        tokens = Lexer(",").tokenize()
        assert tokens[0].type == TokenType.COMMA

    def test_colon(self):
        tokens = Lexer(":").tokenize()
        assert tokens[0].type == TokenType.COLON

    def test_dot(self):
        tokens = Lexer(".").tokenize()
        assert tokens[0].type == TokenType.DOT

    def test_underscore_wildcard(self):
        tokens = Lexer("_").tokenize()
        assert tokens[0].type == TokenType.UNDERSCORE


class TestLexerWhitespace:
    def test_spaces_ignored(self):
        tokens = Lexer("1  +  2").tokenize()
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.INT
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.INT
        assert tokens[3].type == TokenType.EOF

    def test_tabs_ignored(self):
        tokens = Lexer("1\t+\t2").tokenize()
        assert len(tokens) == 4


class TestLexerComments:
    def test_line_comment(self):
        tokens = Lexer("1 -- comment\n2").tokenize()
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == 1
        assert tokens[1].type == TokenType.INT
        assert tokens[1].value == 2


class TestLexerComplex:
    def test_function_definition(self):
        code = "def add(x: Int, y: Int) -> Int = x + y"
        tokens = Lexer(code).tokenize()
        assert tokens[0].type == TokenType.KW_DEF
        assert tokens[1].type == TokenType.IDENT
        assert tokens[1].value == "add"
        assert tokens[2].type == TokenType.LPAREN
        assert tokens[3].type == TokenType.IDENT
        assert tokens[3].value == "x"
        assert tokens[4].type == TokenType.COLON
        assert tokens[5].type == TokenType.IDENT
        assert tokens[5].value == "Int"

    def test_lambda_expression(self):
        code = "fn x => x + 1"
        tokens = Lexer(code).tokenize()
        assert tokens[0].type == TokenType.KW_FN
        assert tokens[1].type == TokenType.IDENT
        assert tokens[2].type == TokenType.FAT_ARROW
        assert tokens[3].type == TokenType.IDENT
        assert tokens[4].type == TokenType.PLUS
        assert tokens[5].type == TokenType.INT

    def test_list_literal(self):
        code = "[1, 2, 3]"
        tokens = Lexer(code).tokenize()
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.INT
        assert tokens[2].type == TokenType.COMMA
        assert tokens[3].type == TokenType.INT

    def test_match_expression(self):
        code = 'match x with\n| 0 -> "zero"\n| _ -> "other"'
        tokens = Lexer(code).tokenize()
        assert tokens[0].type == TokenType.KW_MATCH
        assert tokens[1].type == TokenType.IDENT
        assert tokens[2].type == TokenType.KW_WITH
        assert tokens[3].type == TokenType.PIPE


class TestLexerSpan:
    def test_token_has_span(self):
        tokens = Lexer("foo").tokenize()
        assert tokens[0].span is not None
        assert tokens[0].span.start == 0
        assert tokens[0].span.end == 3

    def test_token_span_multiline(self):
        tokens = Lexer("1\n2").tokenize()
        assert tokens[0].span.line == 1
        assert tokens[1].span.line == 2
