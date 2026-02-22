from __future__ import annotations

from pfn.parser import ast


class CodeGenerator:
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

    def _safe_name(self, name: str) -> str:
        if name in self.PYTHON_KEYWORDS:
            return f"_{name}_"
        return name

    def generate(self, node: ast.Expr) -> str:
        return self._gen_expr(node)

    def generate_module(self, module: ast.Module) -> str:
        lines = [
            "from __future__ import annotations",
            "from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record",
        ]
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
        safe_name = self._safe_name(decl.name)
        params_str = ", ".join(self._safe_name(p.name) for p in decl.params)
        body_code = self._gen_expr(decl.body)

        if len(decl.params) > 1:
            inner_body = body_code
            for param in reversed(decl.params[1:]):
                inner_body = f"lambda {self._safe_name(param.name)}: {inner_body}"
            func_def = f"def {safe_name}({self._safe_name(decl.params[0].name)}): return {inner_body}"
        else:
            func_def = f"def {safe_name}({params_str}):\n    return {body_code}"

        if decl.is_exported:
            export_name = decl.export_name or decl.name
            return f"{func_def}\n\n{export_name} = {safe_name}"

        return func_def

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
        module = decl.module.replace("Bootstrap.", "bootstrap.")
        if decl.alias:
            return f"import {module} as {decl.alias}"
        if decl.exposing:
            if decl.exposing == [".."]:
                return f"from {module} import *"
            names = []
            for name in decl.exposing:
                if name.endswith("(..)"):
                    names.append(name[:-4])
                else:
                    names.append(name)
            return f"from {module} import {', '.join(names)}"
        return f"import {module}"

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
            return self._safe_name(expr.name)
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
        if isinstance(expr, ast.LetPattern):
            return self._gen_let_pattern(expr)
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
        if isinstance(expr, ast.RecordUpdate):
            return self._gen_record_update(expr)
        if isinstance(expr, ast.FieldAccess):
            return self._gen_field_access(expr)
        if isinstance(expr, ast.IndexAccess):
            return self._gen_index_access(expr)
        if isinstance(expr, ast.DoNotation):
            return self._gen_do(expr)
        return ""

    def _gen_lambda(self, expr: ast.Lambda) -> str:
        body_code = self._gen_expr(expr.body)
        result = body_code
        for param in reversed(expr.params):
            safe_name = self._safe_name(param.name)
            result = f"lambda {safe_name}: {result}"
        return result

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
        if op == "||":
            return f"{left_code} or {right_code}"
        if op == "&&":
            return f"{left_code} and {right_code}"
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
        safe_name = self._safe_name(expr.name)
        return f"(lambda {safe_name}: {body_code})({value_code})"

    def _gen_let_pattern(self, expr: ast.LetPattern) -> str:
        value_code = self._gen_expr(expr.value)
        body_code = self._gen_expr(expr.body)
        pattern_check, bindings = self._gen_pattern_check(expr.pattern, "__let_val")
        if pattern_check == "True" and not bindings:
            return body_code
        if bindings:
            import re

            for name, var_path in bindings.items():
                pattern = r"\b" + re.escape(name) + r"\b"
                body_code = re.sub(pattern, var_path, body_code)
        return f"(lambda __let_val: {body_code} if {pattern_check} else None)({value_code})"

    def _gen_let_func(self, expr: ast.LetFunc) -> str:
        safe_name = self._safe_name(expr.name)
        value_code = self._gen_expr(expr.value)
        body_code = self._gen_expr(expr.body)

        import re

        pattern = r"\b" + re.escape(expr.name) + r"\b"
        is_recursive = bool(re.search(pattern, value_code))

        curried_lambda = value_code
        for param in reversed(expr.params):
            curried_lambda = f"lambda {self._safe_name(param.name)}: {curried_lambda}"

        if is_recursive:
            value_code_with_cell = re.sub(pattern, "__cell[0]", curried_lambda)
            body_code_with_cell = re.sub(pattern, "__cell[0]", body_code)
            return f"(lambda __cell: (__cell.__setitem__(0, ({value_code_with_cell})) or {body_code_with_cell}))([None])"
        else:
            return f"(lambda {safe_name}: {body_code})({curried_lambda})"

    def _gen_match(self, expr: ast.Match) -> str:
        scrutinee_code = self._gen_expr(expr.scrutinee)
        if not expr.cases:
            return "None"

        result = "(lambda __match_val: "
        parts = []
        for case in expr.cases:
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, "__match_val"
            )
            body_code = self._gen_expr_with_bindings(case.body, bindings)
            parts.append((pattern_check, body_code))

        chain = parts[-1][1]
        for pattern_check, body_code in reversed(parts[:-1]):
            if pattern_check == "True":
                chain = body_code
            else:
                chain = f"({body_code} if {pattern_check} else {chain})"

        result += chain + ")({})".format(scrutinee_code)
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
        if isinstance(pattern, ast.TuplePattern):
            check = (
                f"isinstance({var}, tuple) and len({var}) == {len(pattern.elements)}"
            )
            for i, elem in enumerate(pattern.elements):
                elem_var = f"{var}[{i}]"
                elem_check, elem_bindings = self._gen_pattern_check(elem, elem_var)
                if elem_check != "True":
                    check = f"{check} and {elem_check}"
                bindings.update(elem_bindings)
            return check, bindings
        if isinstance(pattern, ast.ConstructorPattern):
            check = f"isinstance({var}, {pattern.name})"
            for i, arg in enumerate(pattern.args):
                arg_var = f"{var}._field{i}"
                arg_check, arg_bindings = self._gen_pattern_check(arg, arg_var)
                if arg_check != "True":
                    check = f"{check} and {arg_check}"
                bindings.update(arg_bindings)
            return check, bindings
        return "True", bindings

    def _gen_expr_with_bindings(self, expr: ast.Expr, bindings: dict[str, str]) -> str:
        if not bindings:
            return self._gen_expr(expr)
        code = self._gen_expr(expr)
        import re

        for name, var_path in bindings.items():
            pattern = r"\b" + re.escape(name) + r"\b"
            code = re.sub(pattern, var_path, code)
        return code

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
        return f"Record({{{fields_str}}})"

    def _gen_record_update(self, expr: ast.RecordUpdate) -> str:
        record_code = self._gen_expr(expr.record)
        updates_str = ", ".join(
            f'"{f.name}": {self._gen_expr(f.value)}' for f in expr.updates
        )
        return f"Record({{**{record_code}, {updates_str}}})"

    def _gen_field_access(self, expr: ast.FieldAccess) -> str:
        expr_code = self._gen_expr(expr.expr)
        return f"{expr_code}.{expr.field}"

    def _gen_index_access(self, expr: ast.IndexAccess) -> str:
        expr_code = self._gen_expr(expr.expr)
        index_code = self._gen_expr(expr.index)
        return f"{expr_code}[{index_code}]"

    def _gen_do(self, expr: ast.DoNotation) -> str:
        result = self._gen_expr(expr.body)
        for binding in reversed(expr.bindings):
            value_code = self._gen_expr(binding.value)
            result = f"(lambda {binding.name}: {result})({value_code})"
        return result
