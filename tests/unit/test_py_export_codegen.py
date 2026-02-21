from pfn.lexer import Lexer
from pfn.parser import Parser
from pfn.codegen import CodeGenerator


class TestPythonExportCodegen:
    def test_regular_function_generates_python(self):
        source = "def add(x, y) = x + y"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()

        gen = CodeGenerator()
        code = gen.generate_module(module)

        assert "lambda y:" in code
        assert "x + y" in code

    def test_single_param_function(self):
        source = "def double(x) = x * 2"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()

        gen = CodeGenerator()
        code = gen.generate_module(module)

        assert "def double(x):" in code
        assert "return x * 2" in code
