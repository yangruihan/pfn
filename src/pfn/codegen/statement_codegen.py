"""Statement-level code generator for pfn compiler.

This module provides StatementCodeGenerator which converts pfn expressions
to flat Python statements, avoiding deep nesting issues that cause SyntaxError
and properly handling closure variable capture.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union

from pfn.parser import ast
from pfn.codegen.statement import (
    Statement,
    Assign,
    Return,
    IfStatement,
    PassStatement,
    statements_to_python,
)


class StatementCodeGenerator:
    """Generate flat Python statements from pfn expressions.

    This avoids the deep nesting issues caused by IIL (Immediately Invoked Lambdas)
    and properly handles closure variable capture by:
    1. Converting expressions to statement sequences
    2. Using intermediate variables for let bindings
    3. Generating if/else statements for match expressions
    4. Properly tracking and passing closure variables to helper functions
    """

    def __init__(self):
        self._let_counter = 0
        self._helper_funcs = []
        self._helper_counter = 0
        self._current_closure_vars: set[str] = set()

    def _fresh_let_var(self) -> str:
        """Generate a fresh variable name for let bindings."""
        var = f"__let_val_{self._let_counter}"
        self._let_counter += 1
        return var

    def _fresh_helper_name(self) -> str:
        """Generate a unique helper function name."""
        name = f"__helper_{self._helper_counter}"
        self._helper_counter += 1
        return name

    def _collect_vars(self, expr: ast.Expr) -> set[str]:
        """Collect all free variables in an expression."""
        vars_found: set[str] = set()

        def walk(e: ast.Expr):
            if isinstance(e, ast.Var):
                vars_found.add(e.name)
            elif isinstance(e, ast.IntLit):
                pass
            elif isinstance(e, ast.FloatLit):
                pass
            elif isinstance(e, ast.StringLit):
                pass
            elif isinstance(e, ast.CharLit):
                pass
            elif isinstance(e, ast.BoolLit):
                pass
            elif isinstance(e, ast.UnitLit):
                pass
            elif isinstance(e, ast.Lambda):
                # Lambda params are bound, not free
                for param in e.params:
                    vars_found.discard(param.name)
                walk(e.body)
            elif isinstance(e, ast.Let):
                walk(e.value)
                vars_found.discard(e.name)  # Let binding shadows
                walk(e.body)
            elif isinstance(e, ast.LetPattern):
                walk(e.value)
                self._collect_pattern_vars(e.pattern, vars_found)
                vars_found.discard(e.name)  # Pattern binding shadows
                walk(e.body)
            elif isinstance(e, ast.LetFunc):
                walk(e.value)
                vars_found.discard(e.name)  # Function name is bound
                for param in e.params:
                    vars_found.discard(param.name)
                walk(e.body)
            elif isinstance(e, ast.DoNotation):
                for binding in e.bindings:
                    walk(binding.value)
                    vars_found.discard(binding.name)
                walk(e.body)
            elif isinstance(e, ast.If):
                walk(e.cond)
                walk(e.then_branch)
                walk(e.else_branch)
            elif isinstance(e, ast.Match):
                walk(e.scrutinee)
                for case in e.cases:
                    self._collect_pattern_vars(case.pattern, vars_found)
                    walk(case.body)
            elif isinstance(e, ast.App):
                walk(e.func)
                for arg in e.args:
                    walk(arg)
            elif isinstance(e, ast.BinOp):
                walk(e.left)
                walk(e.right)
            elif isinstance(e, ast.UnaryOp):
                walk(e.operand)
            elif isinstance(e, ast.FieldAccess):
                walk(e.expr)
            elif isinstance(e, ast.RecordUpdate):
                walk(e.record)
                for field in e.updates:
                    walk(field.value)
            elif isinstance(e, ast.IndexAccess):
                walk(e.expr)
                walk(e.index)
            elif isinstance(e, ast.Slice):
                walk(e.expr)
                if e.start:
                    walk(e.start)
                if e.end:
                    walk(e.end)
                if e.step:
                    walk(e.step)
            elif isinstance(e, ast.ListLit):
                for elem in e.elements:
                    walk(elem)
            elif isinstance(e, ast.TupleLit):
                for elem in e.elements:
                    walk(elem)
            elif isinstance(e, ast.RecordLit):
                for field in e.fields:
                    walk(field.value)
            elif isinstance(e, ast.HandleExpr):
                walk(e.expr)
                for case in e.handler_cases:
                    if case.params:
                        for p in case.params:
                            vars_found.discard(p.name)
                    walk(case.body)
            elif isinstance(e, ast.PerformExpr):
                for arg in e.args:
                    walk(arg)

        walk(expr)
        return vars_found

    def _collect_pattern_vars(self, pattern: ast.Pattern, vars_found: set[str]):
        """Collect variables bound by a pattern."""
        if isinstance(pattern, ast.VarPattern):
            vars_found.add(pattern.name)
        elif isinstance(pattern, ast.ConsPattern):
            self._collect_pattern_vars(pattern.head, vars_found)
            self._collect_pattern_vars(pattern.tail, vars_found)
        elif isinstance(pattern, ast.ListPattern):
            for elem in pattern.elements:
                self._collect_pattern_vars(elem, vars_found)
            if pattern.rest:
                self._collect_pattern_vars(pattern.rest, vars_found)
        elif isinstance(pattern, ast.TuplePattern):
            for elem in pattern.elements:
                self._collect_pattern_vars(elem, vars_found)
        elif isinstance(pattern, ast.RecordPattern):
            for _, p in pattern.fields:
                self._collect_pattern_vars(p, vars_found)
        elif isinstance(pattern, ast.ConstructorPattern):
            for arg in pattern.args:
                self._collect_pattern_vars(arg, vars_found)

    def _gen_expr(self, expr: ast.Expr) -> str:
        """Generate Python expression code."""
        if isinstance(expr, ast.IntLit):
            return str(expr.value)
        elif isinstance(expr, ast.FloatLit):
            return str(expr.value)
        elif isinstance(expr, ast.StringLit):
            return repr(expr.value)
        elif isinstance(expr, ast.CharLit):
            return repr(expr.value)
        elif isinstance(expr, ast.BoolLit):
            return "True" if expr.value else "False"
        elif isinstance(expr, ast.UnitLit):
            return "None"
        elif isinstance(expr, ast.Var):
            return self._safe_name(expr.name)
        elif isinstance(expr, ast.Lambda):
            params = ", ".join(self._safe_name(p.name) for p in expr.params)
            body = self._gen_expr(expr.body)
            return f"lambda {params}: {body}"
        elif isinstance(expr, ast.Let):
            value = self._gen_expr(expr.value)
            body = self._gen_expr(expr.body)
            safe_name = self._safe_name(expr.name)
            return f"({safe_name} := {value}, {body})[1]"
        elif isinstance(expr, ast.LetPattern):
            value = self._gen_expr(expr.value)
            let_var = self._fresh_let_var()
            pattern_check, bindings = self._gen_pattern_check(expr.pattern, let_var)
            if pattern_check == "True" and not bindings:
                body = self._gen_expr(expr.body)
                return body
            body = self._gen_expr(expr.body)
            if bindings:
                import re

                valid_identifier = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
                param_names = list(bindings.keys())
                if all(valid_identifier.match(name) for name in param_names):
                    var_paths = list(bindings.values())
                    inner_lambda = f"(lambda {', '.join(param_names)}: {body})"
                    call_args = ", ".join(var_paths)
                    body = f"{inner_lambda}({call_args})"
                else:
                    for name, var_path in bindings.items():
                        pattern = r"\b" + re.escape(name) + r"\b"
                        body = re.sub(pattern, var_path, body)
            return f"({let_var} := {value}, {body} if {pattern_check} else None)[1]"
        elif isinstance(expr, ast.LetFunc):
            import re

            safe_name = self._safe_name(expr.name)
            value = self._gen_expr(expr.value)
            body = self._gen_expr(expr.body)
            pattern = r"\b" + re.escape(expr.name) + r"\b"
            is_recursive = bool(re.search(pattern, value))
            curried_lambda = value
            for param in reversed(expr.params):
                curried_lambda = (
                    f"lambda {self._safe_name(param.name)}: {curried_lambda}"
                )
            body_code_with_safe_name = re.sub(pattern, safe_name, body)
            if is_recursive:
                value_code_with_cell = re.sub(pattern, "__cell[0]", curried_lambda)
                body_code_with_cell = re.sub(pattern, "__cell[0]", body)
                return f"(lambda __cell: (__cell.__setitem__(0, ({value_code_with_cell})) or {body_code_with_cell}))([None])"
            else:
                return (
                    f"({safe_name} := {curried_lambda}, {body_code_with_safe_name})[1]"
                )
        elif isinstance(expr, ast.DoNotation):
            result = self._gen_expr(expr.body)
            for binding in reversed(expr.bindings):
                value_code = self._gen_expr(binding.value)
                result = f"({binding.name} := {value_code}, {result})[1]"
            return result
        elif isinstance(expr, ast.If):
            cond = self._gen_expr(expr.cond)
            then_branch = self._gen_expr(expr.then_branch)
            else_branch = self._gen_expr(expr.else_branch)
            return f"({then_branch} if {cond} else {else_branch})"
        elif isinstance(expr, ast.Match):
            return self._gen_match_expr(expr)
        VN|        elif isinstance(expr, ast.App):
MK|            func = self._gen_expr(expr.func)
VJ|            args = []
SH|            for arg in expr.args:
ZW|                arg_code = self._gen_expr(arg)
ZM|                if arg_code is not None:
KN|                    args.append(arg_code)
ZR|                else:
SS|                    args.append('None')
YP|            # Generate curried calls: f(a)(b)(c) instead of f(a, b, c)
BK|            # This matches the curried function definitions
HB|            if len(args) > 1:
NY|                result = func
MK|                for arg in args:
NW|                    result = f"({result})({arg})"
HM|                return result
HB|            elif len(args) == 1:
MK|                return f"{func}({args[0]})"
HN|            else:
BK|                return f"{func}()"
        elif isinstance(expr, ast.BinOp):
            left = self._gen_expr(expr.left)
            right = self._gen_expr(expr.right)
            return f"({left} {expr.op} {right})"
        elif isinstance(expr, ast.UnaryOp):
            operand = self._gen_expr(expr.operand)
            return f"({expr.op}{operand})"
        elif isinstance(expr, ast.ListLit):
            elements = ", ".join(self._gen_expr(e) for e in expr.elements)
            return f"[{elements}]"
        elif isinstance(expr, ast.TupleLit):
            elements = ", ".join(self._gen_expr(e) for e in expr.elements)
            return f"({elements},)" if len(elements) == 1 else f"({elements})"
        elif isinstance(expr, ast.RecordLit):
            fields = ", ".join(
                f'"{f.name}": {self._gen_expr(f.value)}' for f in expr.fields
            )
            return f"Record({{{fields}}})"
        elif isinstance(expr, ast.FieldAccess):
            record = self._gen_expr(expr.expr)
            return f"{record}.{expr.field}"
        elif isinstance(expr, ast.RecordUpdate):
            record = self._gen_expr(expr.record)
            updates = ", ".join(
                f'"{f.name}": {self._gen_expr(f.value)}' for f in expr.updates
            )
            return f"Record({{**{record}, {updates}}})"
        elif isinstance(expr, ast.IndexAccess):
            expr_code = self._gen_expr(expr.expr)
            index = self._gen_expr(expr.index)
            return f"{expr_code}[{index}]"
        elif isinstance(expr, ast.Slice):
            expr_code = self._gen_expr(expr.expr)
            start = self._gen_expr(expr.start) if expr.start else ""
            end = self._gen_expr(expr.end) if expr.end else ""
            step = self._gen_expr(expr.step) if expr.step else ""
            return f"{expr_code}[{start}:{end}:{step}]"
        elif isinstance(expr, ast.HandleExpr):
            return self._gen_expr(expr.expr)  # Simplified for now
        elif isinstance(expr, ast.PerformExpr):
            args = [self._gen_expr(a) for a in expr.args]
            return f"{expr.effect_name}_{expr.op_name}({', '.join(args)})"
        else:
            return "None"

    def _gen_pattern_check(
        self, pattern: ast.Pattern, var: str
    ) -> tuple[str, dict[str, str]]:
        """Generate pattern check code and bindings."""
        bindings: dict[str, str] = {}

        if isinstance(pattern, ast.IntPattern):
            return f"{var} == {pattern.value}", bindings
        elif isinstance(pattern, ast.FloatPattern):
            return f"{var} == {pattern.value}", bindings
        elif isinstance(pattern, ast.StringPattern):
            return f"{var} == {repr(pattern.value)}", bindings
        elif isinstance(pattern, ast.CharPattern):
            return f"{var} == {repr(pattern.value)}", bindings
        elif isinstance(pattern, ast.BoolPattern):
            return f"{var} == {pattern.value}", bindings
        elif isinstance(pattern, ast.WildcardPattern):
            return "True", bindings
        elif isinstance(pattern, ast.VarPattern):
            bindings[pattern.name] = var
            return "True", bindings
        elif isinstance(pattern, ast.ConsPattern):
            head_var = f"{var}._field0"
            tail_var = f"{var}._field1"
            head_check, head_bindings = self._gen_pattern_check(pattern.head, head_var)
            tail_check, tail_bindings = self._gen_pattern_check(pattern.tail, tail_var)
            bindings.update(head_bindings)
            bindings.update(tail_bindings)
            return (
                f"isinstance({var}, tuple) and len({var}) == 2 and {head_check} and {tail_check}",
                bindings,
            )
        elif isinstance(pattern, ast.ListPattern):
            if not pattern.elements and pattern.rest is None:
                return f"isinstance({var}, list) and len({var}) == 0", bindings
            # Simplified - just check if it's a list
            return f"isinstance({var}, list)", bindings
        elif isinstance(pattern, ast.TuplePattern):
            checks = []
            for i, elem in enumerate(pattern.elements):
                elem_var = f"{var}[{i}]"
                elem_check, elem_bindings = self._gen_pattern_check(elem, elem_var)
                checks.append(elem_check)
                bindings.update(elem_bindings)
            return (
                f"isinstance({var}, tuple) and len({var}) == {len(pattern.elements)} and {' and '.join(checks)}",
                bindings,
            )
        elif isinstance(pattern, ast.RecordPattern):
            checks = []
            for fname, fp in pattern.fields:
                field_var = f"{var}.{fname}"
                field_check, field_bindings = self._gen_pattern_check(fp, field_var)
                checks.append(f"hasattr({var}, '{fname}') and {field_check}")
                bindings.update(field_bindings)
            return " and ".join(checks), bindings
        elif isinstance(pattern, ast.ConstructorPattern):
            if pattern.args:
                checks = [
                    f"isinstance({var}, tuple) and len({var}) == {len(pattern.args)}"
                ]
                for i, arg in enumerate(pattern.args):
                    arg_var = f"{var}[{i}]"
                    arg_check, arg_bindings = self._gen_pattern_check(arg, arg_var)
                    checks.append(arg_check)
                    bindings.update(arg_bindings)
                return " and ".join(checks), bindings
            else:
                return "True", bindings
        else:
            return "True", bindings

    def _gen_match_expr(self, expr: ast.Match) -> str:
        """Generate match expression as Python code."""
        scrutinee_code = self._gen_expr(expr.scrutinee)

        if not expr.cases:
            return "None"

        # For simple cases, use inline approach
        if len(expr.cases) <= 2:
            cases_code = []
            for case in expr.cases:
                pattern_check, bindings = self._gen_pattern_check(
                    case.pattern, "__match_val"
                )
                body_code = self._gen_expr(case.body)
                if pattern_check == "True":
                    cases_code.append(body_code)
                else:
                    cases_code.append(f"({body_code} if {pattern_check} else None)")

            valid_cases = [c for c in cases_code if c != "None"]
            if not valid_cases:
                return "None"
            elif len(valid_cases) == 1:
                chain = valid_cases[0]
            else:
                chain = " or ".join(f"({c})" for c in valid_cases)

            return f"(lambda __match_val: {chain})({scrutinee_code})"

        # For complex matches, use helper function with proper closure
        return self._gen_match_with_helper(expr, scrutinee_code)

    def _gen_match_with_helper(self, expr: ast.Match, scrutinee_code: str) -> str:
        """Generate match using helper function with proper closure variables."""
        helper_name = self._fresh_helper_name()

        # Collect closure variables from all case bodies
        closure_vars: set[str] = set()
        scrutinee_vars = self._collect_vars(expr.scrutinee)
        closure_vars.update(scrutinee_vars)

        for case in expr.cases:
            body_vars = self._collect_vars(case.body)
            closure_vars.update(body_vars)

        # Build match cases as if/else chain in statements
        match_var = self._fresh_let_var()
        stmts = [Assign(match_var, "None")]

        for case in reversed(expr.cases):
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, scrutinee_code
            )
            body_code = self._gen_expr(case.body)

            # Create bindings as assignments
            binding_stmts = []
            for name, path in bindings.items():
                binding_stmts.append(Assign(self._safe_name(name), path))

            then_stmts = binding_stmts + [Assign(match_var, body_code)]

            if_stmt = IfStatement(
                cond=pattern_check, then_stmts=then_stmts, else_stmts=[]
            )
            stmts.append(if_stmt)

        stmts.append(Return(match_var))

        # Generate helper function with closure vars
        helper_params = list(closure_vars) + ["__match_val"]
        helper_body = statements_to_python(stmts)
        self._helper_funcs.append((helper_name, helper_params, helper_body))

        # Build call with closure vars
        call_args = [scrutinee_code]  # scrutinee is the first closure var
        return f"{helper_name}({', '.join(call_args)})"

    def _safe_name(self, name: str) -> str:
        """Make a name safe for Python."""
        PYTHON_KEYWORDS = {
            "lambda",
            "def",
            "class",
            "if",
            "else",
            "elif",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "as",
            "import",
            "from",
            "return",
            "yield",
            "raise",
            "break",
            "continue",
            "pass",
            "True",
            "False",
            "None",
            "and",
            "or",
            "not",
            "in",
            "is",
            "global",
            "nonlocal",
            "assert",
            "del",
            "match",
            "case",
        }
        if name in PYTHON_KEYWORDS:
            return f"_{name}_"
        return name

    def _generate_helper_funcs(self) -> str:
        """Generate helper functions as Python code."""
        if not self._helper_funcs:
            return ""

        lines = ["", "# Helper functions"]
        for name, params, body in self._helper_funcs:
            param_str = ", ".join(params)
            lines.append(f"def {name}({param_str}):")
            lines.append(body)

        return "\n".join(lines)

    def generate(self, expr: ast.Expr) -> str:
        """Generate complete Python code from an expression."""
        self._let_counter = 0
        self._helper_funcs = []
        self._helper_counter = 0

        expr_code = self._gen_expr(expr)
        helper_funcs = self._generate_helper_funcs()

        if helper_funcs:
            return f"{helper_funcs}\n{expr_code}"
        return expr_code

    def to_statements(self, expr: ast.Expr) -> list[Statement]:
        """Convert expression to statement list."""
        return self._expr_to_statements(expr)

    def _expr_to_statements(self, expr: ast.Expr) -> list[Statement]:
        """Convert expression to statements."""
        if isinstance(expr, ast.Let):
            value_code = self._gen_expr(expr.value)
            var_name = self._safe_name(expr.name)
            stmts = [Assign(var_name, value_code)]
            stmts.extend(self._expr_to_statements(expr.body))
            return stmts
        elif isinstance(expr, ast.LetPattern):
            value_code = self._gen_expr(expr.value)
            let_var = self._fresh_let_var()
            pattern_check, bindings = self._gen_pattern_check(expr.pattern, let_var)

            stmts = [Assign(let_var, value_code)]

            if bindings:
                for name, path in bindings.items():
                    stmts.append(Assign(self._safe_name(name), path))

            then_stmts = self._expr_to_statements(expr.body)

            if pattern_check == "True":
                return stmts + then_stmts

            return [
                IfStatement(
                    cond=pattern_check,
                    then_stmts=then_stmts,
                    else_stmts=[Return("None")],
                )
            ]
        elif isinstance(expr, ast.If):
            cond = self._gen_expr(expr.cond)
            then_stmts = self._expr_to_statements(expr.then_branch)
            else_stmts = self._expr_to_statements(expr.else_branch)
            return [
                IfStatement(cond=cond, then_stmts=then_stmts, else_stmts=else_stmts)
            ]
        elif isinstance(expr, ast.Match):
            return self._match_to_statements(expr)
        else:
            return [Return(self._gen_expr(expr))]

    def _match_to_statements(self, expr: ast.Match) -> list[Statement]:
        """Convert match expression to statements."""
        scrutinee_code = self._gen_expr(expr.scrutinee)
        match_var = self._fresh_let_var()

        stmts = [Assign(match_var, "None")]

        for case in reversed(expr.cases):
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, scrutinee_code
            )

            then_stmts = []
            for name, path in bindings.items():
                then_stmts.append(Assign(self._safe_name(name), path))
            then_stmts.extend(self._expr_to_statements(case.body))

            stmts.append(
                IfStatement(cond=pattern_check, then_stmts=then_stmts, else_stmts=[])
            )

        stmts.append(Return(match_var))
        return stmts
