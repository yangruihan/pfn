from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser


class TestCodeGeneratorLiterals:
    def test_integer(self):
        tokens = Lexer("42").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "42"

    def test_float(self):
        tokens = Lexer("3.14").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "3.14"

    def test_string(self):
        tokens = Lexer('"hello"').tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "'hello'"

    def test_true(self):
        tokens = Lexer("True").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "True"

    def test_false(self):
        tokens = Lexer("False").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "False"

    def test_empty_list(self):
        tokens = Lexer("[]").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "[]"


class TestCodeGeneratorExpressions:
    def test_variable(self):
        tokens = Lexer("foo").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "foo"

    def test_addition(self):
        tokens = Lexer("1 + 2").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "1 + 2"

    def test_subtraction(self):
        tokens = Lexer("3 - 1").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "3 - 1"

    def test_multiplication(self):
        tokens = Lexer("2 * 3").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "2 * 3"

    def test_parenthesized_expr(self):
        tokens = Lexer("(1 + 2) * 3").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert "1 + 2" in code and "* 3" in code


class TestCodeGeneratorFunctions:
    def test_lambda(self):
        tokens = Lexer("fn x => x + 1").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert "lambda" in code
        assert "x" in code

    def test_function_call(self):
        tokens = Lexer("f(x)").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "f(x)"

    def test_def(self):
        tokens = Lexer("def add(x, y) = x + y").tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "def add(x):" in code
        assert "lambda y:" in code
        assert "x + y" in code


class TestCodeGeneratorIf:
    def test_if_expr(self):
        tokens = Lexer("if x then 1 else 0").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert "1 if x else 0" in code


class TestCodeGeneratorLet:
    def test_let_expr(self):
        tokens = Lexer("let x = 5 in x").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert ":=" in code and "5" in code


class TestCodeGeneratorList:
    def test_list(self):
        tokens = Lexer("[1, 2, 3]").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "[1, 2, 3]"


class TestCodeGeneratorTuple:
    def test_tuple(self):
        tokens = Lexer("(1, 2)").tokenize()
        ast = Parser(tokens).parse_expr()
        code = CodeGenerator().generate(ast)
        assert code == "(1, 2)"
