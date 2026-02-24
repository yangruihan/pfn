from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser
from pfn.typechecker import TypeChecker


class TestPythonInterop:
    def test_full_program(self):
        """Full program with Python interop"""
        source = """
import python math

def distance(x1, y1, x2, y2) =
  let dx = x2 - x1 in
  let dy = y2 - y1 in
  math.sqrt(dx * dx + dy * dy)

def main() = distance(0.0, 0.0, 3.0, 4.0)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)

        assert "from math import *" in code
        assert "def distance(x1, y1, x2, y2):" in code
        assert "math.sqrt" in code

    def test_multiple_imports(self):
        """Multiple Python imports"""
        source = """
import python math
import python json

def test() = "ok"
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)

        assert "from math import *" in code
        assert "from json import *" in code

    def test_import_with_alias(self):
        """Python import with alias"""
        source = """
import python numpy as np

def test() = "ok"
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)

        assert "import numpy as np" in code

    def test_python_in_let(self):
        """Python function in let binding"""
        source = """
import python math

def test() =
  let pi = math.pi in
  math.sin(pi)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)

        assert "from math import *" in code
        assert "math.pi" in code
        assert "math.sin" in code

    def test_python_in_if(self):
        """Python function in if expression"""
        source = """
import python math

def isNearZero(x) =
  if math.abs(x) < 0.0001
    then True
    else False
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)

        assert "from math import *" in code
        assert "math.abs" in code
