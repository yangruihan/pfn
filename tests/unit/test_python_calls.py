from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser


class TestPythonCallSupport:
    def test_call_python_function(self):
        """Call a Python function"""
        source = """
import python math

def test() = math.sqrt(16.0)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "from math import *" in code
        assert "math.sqrt(16.0)" in code

    def test_call_python_with_args(self):
        """Call Python function with multiple args"""
        source = """
import python math

def test() = math.pow(2.0, 10.0)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "math.pow" in code

    def test_chain_python_calls(self):
        """Chain Python method calls"""
        source = """
import python os.path

def test() = os.path.join("a", "b")
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "from os.path import *" in code
        assert "os.path.join" in code

    def test_python_in_expression(self):
        """Use Python function in expression"""
        source = """
import python math

def hypot(a, b) = math.sqrt(a * a + b * b)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "from math import *" in code
        assert "math.sqrt(a * a + b * b)" in code

    def test_nested_python_calls(self):
        """Nested Python function calls"""
        source = """
import python math

def test() = math.abs(math.sin(1.0))
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "math.abs(math.sin(1.0))" in code

    def test_python_builtin(self):
        """Use Python builtins"""
        source = """
import python builtins

def len(x) = builtins.len(x)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "from builtins import *" in code
        assert "builtins.len" in code
