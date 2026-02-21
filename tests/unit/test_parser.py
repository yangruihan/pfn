import pytest

from pfn.lexer import Lexer
from pfn.parser import Parser, ParseError
from pfn.parser import ast


class TestParserLiterals:
    def test_integer(self):
        tokens = Lexer("42").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.IntLit)
        assert expr.value == 42

    def test_float(self):
        tokens = Lexer("3.14").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.FloatLit)
        assert expr.value == 3.14

    def test_string(self):
        tokens = Lexer('"hello"').tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.StringLit)
        assert expr.value == "hello"

    def test_char(self):
        tokens = Lexer("'a'").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.CharLit)
        assert expr.value == "a"

    def test_true(self):
        tokens = Lexer("True").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BoolLit)
        assert expr.value is True

    def test_false(self):
        tokens = Lexer("False").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BoolLit)
        assert expr.value is False


class TestParserIdentifier:
    def test_simple_identifier(self):
        tokens = Lexer("foo").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Var)
        assert expr.name == "foo"

    def test_qualified_identifier(self):
        tokens = Lexer("List.map").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.FieldAccess)
        assert expr.field == "map"
        assert isinstance(expr.expr, ast.Var)
        assert expr.expr.name == "List"


class TestParserLambda:
    def test_single_param_lambda(self):
        tokens = Lexer("fn x => x + 1").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Lambda)
        assert len(expr.params) == 1
        assert expr.params[0].name == "x"
        assert isinstance(expr.body, ast.BinOp)

    def test_multi_param_lambda(self):
        tokens = Lexer("fn x y => x + y").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Lambda)
        assert len(expr.params) == 2

    def test_typed_param_lambda(self):
        tokens = Lexer("fn (x: Int) => x").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Lambda)
        assert expr.params[0].type_annotation is not None


class TestParserFunctionApplication:
    def test_simple_application(self):
        tokens = Lexer("f(x)").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.App)
        assert isinstance(expr.func, ast.Var)
        assert expr.func.name == "f"

    def test_curried_application(self):
        tokens = Lexer("f(x)(y)").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.App)
        assert isinstance(expr.func, ast.App)

    def test_multi_arg_application(self):
        tokens = Lexer("f(x, y)").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.App)


class TestParserBinaryOps:
    def test_addition(self):
        tokens = Lexer("1 + 2").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "+"
        assert isinstance(expr.left, ast.IntLit)
        assert isinstance(expr.right, ast.IntLit)

    def test_subtraction(self):
        tokens = Lexer("3 - 1").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "-"

    def test_multiplication(self):
        tokens = Lexer("2 * 3").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "*"

    def test_division(self):
        tokens = Lexer("6 / 2").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "/"

    def test_operator_precedence(self):
        tokens = Lexer("1 + 2 * 3").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "+"
        assert isinstance(expr.right, ast.BinOp)
        assert expr.right.op == "*"

    def test_comparison(self):
        tokens = Lexer("x < y").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "<"

    def test_equality(self):
        tokens = Lexer("x == y").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.BinOp)
        assert expr.op == "=="


class TestParserIf:
    def test_simple_if(self):
        tokens = Lexer("if x then 1 else 0").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.If)
        assert isinstance(expr.cond, ast.Var)
        assert isinstance(expr.then_branch, ast.IntLit)
        assert isinstance(expr.else_branch, ast.IntLit)

    def test_nested_if(self):
        tokens = Lexer("if a then if b then 1 else 2 else 3").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.If)
        assert isinstance(expr.then_branch, ast.If)


class TestParserLet:
    def test_simple_let(self):
        tokens = Lexer("let x = 5 in x").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Let)
        assert expr.name == "x"
        assert isinstance(expr.value, ast.IntLit)
        assert isinstance(expr.body, ast.Var)

    def test_nested_let(self):
        tokens = Lexer("let x = 1 in let y = 2 in x + y").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Let)
        assert isinstance(expr.body, ast.Let)


class TestParserList:
    def test_empty_list(self):
        tokens = Lexer("[]").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.ListLit)
        assert len(expr.elements) == 0

    def test_single_element_list(self):
        tokens = Lexer("[1]").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.ListLit)
        assert len(expr.elements) == 1

    def test_multi_element_list(self):
        tokens = Lexer("[1, 2, 3]").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.ListLit)
        assert len(expr.elements) == 3


class TestParserTuple:
    def test_pair(self):
        tokens = Lexer("(1, 2)").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.TupleLit)
        assert len(expr.elements) == 2

    def test_triple(self):
        tokens = Lexer("(1, 2, 3)").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.TupleLit)
        assert len(expr.elements) == 3


class TestParserRecord:
    def test_simple_record(self):
        tokens = Lexer("{ x: 1, y: 2 }").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.RecordLit)
        assert len(expr.fields) == 2
        assert expr.fields[0].name == "x"
        assert expr.fields[1].name == "y"

    def test_record_access(self):
        tokens = Lexer("person.name").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.FieldAccess)
        assert expr.field == "name"


class TestParserPattern:
    def test_int_pattern(self):
        tokens = Lexer('match x with | 0 -> "zero" | _ -> "other"').tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr, ast.Match)
        assert len(expr.cases) == 2
        assert isinstance(expr.cases[0].pattern, ast.IntPattern)

    def test_var_pattern(self):
        tokens = Lexer("match x with | n -> n").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr.cases[0].pattern, ast.VarPattern)

    def test_cons_pattern(self):
        tokens = Lexer("match xs with | x :: xs -> x").tokenize()
        expr = Parser(tokens).parse_expr()
        assert isinstance(expr.cases[0].pattern, ast.ConsPattern)


class TestParserDef:
    def test_simple_def(self):
        tokens = Lexer("def add(x, y) = x + y").tokenize()
        module = Parser(tokens).parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert isinstance(decl, ast.DefDecl)
        assert decl.name == "add"
        assert len(decl.params) == 2

    def test_def_with_type(self):
        tokens = Lexer("def add(x: Int, y: Int) -> Int = x + y").tokenize()
        module = Parser(tokens).parse()
        decl = module.declarations[0]
        assert decl.return_type is not None
        assert decl.params[0].type_annotation is not None


class TestParserType:
    def test_simple_type(self):
        tokens = Lexer("type Point = { x: Float, y: Float }").tokenize()
        module = Parser(tokens).parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert isinstance(decl, ast.TypeDecl)
        assert decl.name == "Point"

    def test_sum_type(self):
        tokens = Lexer("type Option a | Some a | None").tokenize()
        module = Parser(tokens).parse()
        decl = module.declarations[0]
        assert isinstance(decl, ast.TypeDecl)
        assert len(decl.constructors) == 2
