from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser
from pfn.python import (
    python_type_to_pfn,
    pfn_type_to_python,
    infer_python_function_type,
    export,
    is_exported,
    get_export_name,
    get_export_registry,
    inspect_python_module,
    py_import,
)
from pfn.types import TInt, TFloat, TString, TBool, TList, TTuple, TFun


class TestPythonImport:
    def test_import_python_module(self):
        tokens = Lexer("import python math").tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "import math" in code

    def test_import_python_module_with_alias(self):
        tokens = Lexer("import python numpy as np").tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "import numpy as np" in code

    def test_import_python_submodule(self):
        source = """
import python os.path

def main() = "test"
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "import os.path" in code


class TestPythonCall:
    def test_call_python_function(self):
        source = """
import python math

def main() = math.sqrt(16.0)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "import math" in code
        assert "math.sqrt(16.0)" in code

    def test_call_python_method(self):
        source = """
import python math

def main() = math.pow(2.0, 3.0)
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()
        code = CodeGenerator().generate_module(module)
        assert "math.pow" in code


class TestPythonInteropIntegration:
    def test_full_program_with_python(self):
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

        assert "import math" in code
        assert "def distance(x1):" in code
        assert "math.sqrt" in code
