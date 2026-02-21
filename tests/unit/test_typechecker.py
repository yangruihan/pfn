from pfn.types import (
    Type,
    TInt,
    TFloat,
    TString,
    TBool,
    TVar,
    TFun,
    TList,
    TTuple,
    Scheme,
    TypeEnv,
    Subst,
)
from pfn.lexer import Lexer
from pfn.parser import Parser


class TestTypeRepresentation:
    def test_int_type(self):
        t = TInt()
        assert isinstance(t, Type)
        assert str(t) == "Int"

    def test_float_type(self):
        t = TFloat()
        assert str(t) == "Float"

    def test_string_type(self):
        t = TString()
        assert str(t) == "String"

    def test_bool_type(self):
        t = TBool()
        assert str(t) == "Bool"

    def test_type_variable(self):
        t = TVar("a")
        assert str(t) == "a"
        assert t.name == "a"

    def test_function_type(self):
        t = TFun(TInt(), TInt())
        assert str(t) == "Int -> Int"

    def test_function_type_curried(self):
        t = TFun(TInt(), TFun(TInt(), TInt()))
        assert "Int -> Int -> Int" in str(t)

    def test_list_type(self):
        t = TList(TInt())
        assert str(t) == "[Int]"

    def test_tuple_type(self):
        t = TTuple([TInt(), TString()])
        assert str(t) == "(Int, String)"

    def test_type_scheme(self):
        t = Scheme(["a"], TFun(TVar("a"), TVar("a")))
        assert "forall a." in str(t) or "a" in str(t)


class TestSubstitution:
    def test_empty_subst(self):
        s = Subst()
        assert s.apply(TInt()) == TInt()

    def test_single_subst(self):
        s = Subst({"a": TInt()})
        t = TVar("a")
        result = s.apply(t)
        assert result == TInt()

    def test_subst_function_type(self):
        s = Subst({"a": TInt()})
        t = TFun(TVar("a"), TVar("a"))
        result = s.apply(t)
        assert result == TFun(TInt(), TInt())

    def test_subst_composition(self):
        s1 = Subst({"a": TInt()})
        s2 = Subst({"b": TVar("a")})
        s = s2.compose(s1)
        result = s.apply(TVar("b"))
        assert result == TInt()


class TestTypeEnv:
    def test_empty_env(self):
        env = TypeEnv()
        assert env.lookup("x") is None

    def test_extend_env(self):
        env = TypeEnv()
        env = env.extend("x", Scheme([], TInt()))
        result = env.lookup("x")
        assert result is not None
        assert result.type == TInt()

    def test_multiple_extensions(self):
        env = TypeEnv()
        env = env.extend("x", Scheme([], TInt()))
        env = env.extend("y", Scheme([], TString()))
        assert env.lookup("x").type == TInt()
        assert env.lookup("y").type == TString()


class TestUnification:
    def test_unify_same_type(self):
        s = Subst()
        result = s.unify(TInt(), TInt())
        assert result is not None

    def test_unify_var_with_int(self):
        s = Subst()
        result = s.unify(TVar("a"), TInt())
        assert result is not None
        assert result.apply(TVar("a")) == TInt()

    def test_unify_int_with_var(self):
        s = Subst()
        result = s.unify(TInt(), TVar("a"))
        assert result is not None
        assert result.apply(TVar("a")) == TInt()

    def test_unify_two_vars(self):
        s = Subst()
        result = s.unify(TVar("a"), TVar("b"))
        assert result is not None

    def test_unify_function_types(self):
        s = Subst()
        result = s.unify(TFun(TVar("a"), TInt()), TFun(TString(), TVar("b")))
        assert result is not None
        assert result.apply(TVar("a")) == TString()
        assert result.apply(TVar("b")) == TInt()

    def test_unify_different_types_fails(self):
        s = Subst()
        result = s.unify(TInt(), TString())
        assert result is None

    def test_occurs_check(self):
        s = Subst()
        result = s.unify(TVar("a"), TFun(TInt(), TVar("a")))
        assert result is None


class TestTypeInference:
    def test_infer_int_literal(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("42").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TInt()

    def test_infer_float_literal(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("3.14").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TFloat()

    def test_infer_string_literal(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer('"hello"').tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TString()

    def test_infer_bool_literal(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("True").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TBool()

    def test_infer_addition(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("1 + 2").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TInt()

    def test_infer_variable(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("x").tokenize()
        expr = Parser(tokens).parse_expr()
        env = TypeEnv().extend("x", Scheme([], TInt()))
        checker = TypeChecker(env)
        t = checker.infer(expr)
        assert t == TInt()

    def test_infer_lambda(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("fn x => x").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert isinstance(t, TFun)

    def test_infer_application(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("(fn x => x)(1)").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TInt()

    def test_infer_let(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("let x = 1 in x").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TInt()

    def test_infer_if(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("if True then 1 else 2").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert t == TInt()

    def test_let_polymorphism(self):
        from pfn.typechecker import TypeChecker

        tokens = Lexer("let id = fn x => x in (id(1), id(True))").tokenize()
        expr = Parser(tokens).parse_expr()
        checker = TypeChecker()
        t = checker.infer(expr)
        assert isinstance(t, TTuple)
