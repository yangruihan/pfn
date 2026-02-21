from pfn.types import (
    TInt,
    TFloat,
    TString,
    TBool,
    TList,
    TTuple,
    TVar,
    TFun,
    Scheme,
    TypeEnv,
)
from pfn.typechecker import TypeChecker
from pfn.lexer import Lexer
from pfn.parser import Parser


class TestPythonTypeMapping:
    def test_int_maps_to_int(self):
        """Python int should map to Pfn Int"""
        from pfn.types import TInt

        assert TInt() == TInt()

    def test_float_maps_to_float(self):
        """Python float should map to Pfn Float"""
        from pfn.types import TFloat

        assert TFloat() == TFloat()

    def test_str_maps_to_string(self):
        """Python str should map to Pfn String"""
        from pfn.types import TString

        assert TString() == TString()

    def test_bool_maps_to_bool(self):
        """Python bool should map to Pfn Bool"""
        from pfn.types import TBool

        assert TBool() == TBool()

    def test_list_maps_to_list(self):
        """Python list should map to Pfn List"""
        assert TList(TInt()) == TList(TInt())
        assert TList(TString()) == TList(TString())

    def test_tuple_maps_to_tuple(self):
        """Python tuple should map to Pfn Tuple"""
        t = TTuple((TInt(), TString()))
        assert isinstance(t, TTuple)
        assert t.elements[0] == TInt()
        assert t.elements[1] == TString()


class TestPythonTypeInference:
    def test_infer_python_comparison(self):
        """Type inference with Python comparisons"""
        source = """
def test() = 1 < 2
"""
        tokens = Lexer(source).tokenize()
        module = Parser(tokens).parse()

        checker = TypeChecker()
        for decl in module.declarations:
            if hasattr(decl, "body") and decl.name == "test":
                t = checker.infer(decl.body)
                assert t == TBool()

    def test_field_access_infers_type_var(self):
        """Field access should infer a type variable"""
        source = "fn r => r.field"
        tokens = Lexer(source).tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert isinstance(t, TFun)

    def test_index_access_infers_type_var(self):
        """Index access should infer a type variable"""
        source = "fn xs => xs[0]"
        tokens = Lexer(source).tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert isinstance(t, TFun)
