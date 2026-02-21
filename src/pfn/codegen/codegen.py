from __future__ import annotations

from pfn.parser import ast


class CodeGenerator:
    def generate(self, node: ast.Expr) -> str:
        return self._gen_expr(node)

    def generate_module(self, module: ast.Module) -> str:
        lines = []
        for decl in module.declarations:
            lines.append(self._gen_decl(decl))
        return "\n\n".join(lines)

    def _gen_decl(self, decl: ast.Decl) -> str:
        if isinstance(decl, ast.DefDecl):
            return self._gen_def_decl(decl)
        if isinstance(decl, ast.TypeDecl):
            return self._gen_type_decl(decl)
        if isinstance(decl, ast.ImportDecl):
            return self._gen_import_decl(decl)
        return ""

    def _gen_def_decl(self, decl: ast.DefDecl) -> str:
        params_str = ", ".join(p.name for p in decl.params)
        body_code = self._gen_expr(decl.body)

        if len(decl.params) > 1:
            inner_body = body_code
            for param in reversed(decl.params[1:]):
                inner_body = f"lambda {param.name}: {inner_body}"
            return f"def {decl.name}({decl.params[0].name}): return {inner_body}"

        return f"def {decl.name}({params_str}):\n    return {body_code}"

    def _gen_type_decl(self, decl: ast.TypeDecl) -> str:
        if decl.is_record:
            return self._gen_record_type(decl)
        return self._gen_sum_type(decl)

    def _gen_record_type(self, decl: ast.TypeDecl) -> str:
        lines = ["from dataclasses import dataclass", ""]
        lines.append("@dataclass")
        lines.append(f"class {decl.name}:")
        for field_name, field_type in decl.record_fields:
            type_str = self._gen_type_ref(field_type)
            lines.append(f"    {field_name}: {type_str}")
        return "\n".join(lines)

    def _gen_sum_type(self, decl: ast.TypeDecl) -> str:
        lines = ["from dataclasses import dataclass", "from typing import Union", ""]
        for ctor in decl.constructors:
            lines.append("@dataclass")
            if ctor.fields:
                fields_str = ", ".join(self._gen_type_ref(f) for f in ctor.fields)
                lines.append(f"class {ctor.name}:")
                for i, field_type in enumerate(ctor.fields):
                    type_str = self._gen_type_ref(field_type)
                    lines.append(f"    _field{i}: {type_str}")
            else:
                lines.append(f"class {ctor.name}:")
                lines.append("    pass")
            lines.append("")
        ctor_names = [c.name for c in decl.constructors]
        lines.append(f"{decl.name} = Union[{', '.join(ctor_names)}]")
        return "\n".join(lines)

    def _gen_import_decl(self, decl: ast.ImportDecl) -> str:
        if decl.alias:
            return f"import {decl.module} as {decl.alias}"
        return f"import {decl.module}"

    def _gen_type_ref(self, type_ref: ast.TypeRef) -> str:
        if isinstance(type_ref, ast.SimpleTypeRef):
            name = type_ref.name
            if name == "Int":
                name = "int"
            elif name == "Float":
                name = "float"
            elif name == "String":
                name = "str"
            elif name == "Bool":
                name = "bool"
            elif name == "List":
                name = "list"
            if type_ref.args:
                args_str = ", ".join(self._gen_type_ref(a) for a in type_ref.args)
                return f"{name}[{args_str}]"
            return name
        if isinstance(type_ref, ast.FunTypeRef):
            return "Callable[[...], ...]"
        if isinstance(type_ref, ast.TupleTypeRef):
            elems = ", ".join(self._gen_type_ref(e) for e in type_ref.elements)
            return f"tuple[{elems}]"
        if isinstance(type_ref, ast.RecordTypeRef):
            return "dict"
        return "Any"

    def _gen_expr(self, expr: ast.Expr) -> str:
        if isinstance(expr, ast.IntLit):
            return str(expr.value)
        if isinstance(expr, ast.FloatLit):
            return str(expr.value)
        if isinstance(expr, ast.StringLit):
            return repr(expr.value)
        if isinstance(expr, ast.CharLit):
            return repr(expr.value)
        if isinstance(expr, ast.BoolLit):
            return "True" if expr.value else "False"
        if isinstance(expr, ast.UnitLit):
            return "None"
        if isinstance(expr, ast.Var):
            return expr.name
        if isinstance(expr, ast.Lambda):
            return self._gen_lambda(expr)
        if isinstance(expr, ast.App):
            return self._gen_app(expr)
        if isinstance(expr, ast.BinOp):
            return self._gen_binop(expr)
        if isinstance(expr, ast.UnaryOp):
            return self._gen_unaryop(expr)
        if isinstance(expr, ast.If):
            return self._gen_if(expr)
        if isinstance(expr, ast.Let):
            return self._gen_let(expr)
        if isinstance(expr, ast.LetFunc):
            return self._gen_let_func(expr)
        if isinstance(expr, ast.Match):
            return self._gen_match(expr)
        if isinstance(expr, ast.ListLit):
            return self._gen_list(expr)
        if isinstance(expr, ast.TupleLit):
            return self._gen_tuple(expr)
        if isinstance(expr, ast.RecordLit):
            return self._gen_record(expr)
        if isinstance(expr, ast.FieldAccess):
            return self._gen_field_access(expr)
        if isinstance(expr, ast.IndexAccess):
            return self._gen_index_access(expr)
        return ""

    def _gen_lambda(self, expr: ast.Lambda) -> str:
        params_str = ", ".join(p.name for p in expr.params)
        body_code = self._gen_expr(expr.body)
        if len(expr.params) == 1:
            return f"lambda {params_str}: {body_code}"
        return f"lambda {params_str}: {body_code}"

    def _gen_app(self, expr: ast.App) -> str:
        func_code = self._gen_expr(expr.func)
        args_str = ", ".join(self._gen_expr(arg) for arg in expr.args)
        return f"{func_code}({args_str})"

    def _gen_binop(self, expr: ast.BinOp) -> str:
        left_code = self._gen_expr(expr.left)
        right_code = self._gen_expr(expr.right)
        op = expr.op
        if op == "::":
            return f"[{left_code}] + {right_code}"
        if op == "++":
            return f"{left_code} + {right_code}"
        return f"{left_code} {op} {right_code}"

    def _gen_unaryop(self, expr: ast.UnaryOp) -> str:
        operand_code = self._gen_expr(expr.operand)
        return f"{expr.op}{operand_code}"

    def _gen_if(self, expr: ast.If) -> str:
        cond_code = self._gen_expr(expr.cond)
        then_code = self._gen_expr(expr.then_branch)
        else_code = self._gen_expr(expr.else_branch)
        return f"{then_code} if {cond_code} else {else_code}"

    def _gen_let(self, expr: ast.Let) -> str:
        value_code = self._gen_expr(expr.value)
        body_code = self._gen_expr(expr.body)
        return f"({body_code} if ({expr.name} := {value_code}) is not None else None)"

    def _gen_let_func(self, expr: ast.LetFunc) -> str:
        params_str = ", ".join(p.name for p in expr.params)
        value_code = self._gen_expr(expr.value)
        body_code = self._gen_expr(expr.body)
        return f"(lambda {params_str}: {body_code})({value_code})"

    def _gen_match(self, expr: ast.Match) -> str:
        scrutinee_code = self._gen_expr(expr.scrutinee)
        if not expr.cases:
            return "None"

        result = "(lambda __match_val: "
        conds = []
        for case in expr.cases:
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, "__match_val"
            )
            body_code = self._gen_expr_with_bindings(case.body, bindings)
            if pattern_check == "True":
                conds.append(f"({body_code})")
            else:
                conds.append(f"({body_code} if {pattern_check} else None)")

        result += " else ".join(conds) + ")({})".format(scrutinee_code)
        return result

    def _gen_pattern_check(
        self, pattern: ast.Pattern, var: str
    ) -> tuple[str, dict[str, str]]:
        bindings: dict[str, str] = {}

        if isinstance(pattern, ast.IntPattern):
            return f"{var} == {pattern.value}", bindings
        if isinstance(pattern, ast.FloatPattern):
            return f"{var} == {pattern.value}", bindings
        if isinstance(pattern, ast.StringPattern):
            return f"{var} == {repr(pattern.value)}", bindings
        if isinstance(pattern, ast.CharPattern):
            return f"{var} == {repr(pattern.value)}", bindings
        if isinstance(pattern, ast.BoolPattern):
            return f"{var} is {pattern.value}", bindings
        if isinstance(pattern, ast.VarPattern):
            bindings[pattern.name] = var
            return "True", bindings
        if isinstance(pattern, ast.WildcardPattern):
            return "True", bindings
        if isinstance(pattern, ast.ListPattern):
            if not pattern.elements:
                return f"{var} == []", bindings
            return "isinstance({}, list)".format(var), bindings
        if isinstance(pattern, ast.ConsPattern):
            return "isinstance({}, list) and len({}) > 0".format(var, var), bindings
        return "True", bindings

    def _gen_expr_with_bindings(self, expr: ast.Expr, bindings: dict[str, str]) -> str:
        return self._gen_expr(expr)

    def _gen_list(self, expr: ast.ListLit) -> str:
        elems_str = ", ".join(self._gen_expr(e) for e in expr.elements)
        return f"[{elems_str}]"

    def _gen_tuple(self, expr: ast.TupleLit) -> str:
        elems_str = ", ".join(self._gen_expr(e) for e in expr.elements)
        return f"({elems_str})"

    def _gen_record(self, expr: ast.RecordLit) -> str:
        fields_str = ", ".join(
            f'"{f.name}": {self._gen_expr(f.value)}' for f in expr.fields
        )
        return f"{{{fields_str}}}"

    def _gen_field_access(self, expr: ast.FieldAccess) -> str:
        expr_code = self._gen_expr(expr.expr)
        return f"{expr_code}.{expr.field}"

    def _gen_index_access(self, expr: ast.IndexAccess) -> str:
        expr_code = self._gen_expr(expr.expr)
        index_code = self._gen_expr(expr.index)
        return f"{expr_code}[{index_code}]"
