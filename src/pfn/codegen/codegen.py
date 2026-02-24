from __future__ import annotations

from pfn.parser import ast


class CodeGenerator:
    def __init__(self):
        self._let_counter = 0

    def _fresh_let_var(self) -> str:
        var = f"__let_val_{self._let_counter}"
        self._let_counter += 1
        return var

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
            "from stdlib import reverse, _not_",
        ]
        for decl in module.declarations:
            lines.append(self._gen_decl(decl))
        code = "\n\n".join(lines)
        # Note: Formatting disabled - original code has syntax errors that need fixing in codegen
        return code

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
        body_code = self._gen_expr(decl.body)

        if len(decl.params) == 0:
            func_def = f"{safe_name} = {body_code}"
        elif len(decl.params) > 1:
            inner_body = body_code
            for param in reversed(decl.params[1:]):
                inner_body = f"lambda {self._safe_name(param.name)}: {inner_body}"
            func_def = f"def {safe_name}({self._safe_name(decl.params[0].name)}): return {inner_body}"
        else:
            params_str = ", ".join(self._safe_name(p.name) for p in decl.params)
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
            if ctor.fields:
                lines.append("@dataclass")
                lines.append(f"class {ctor.name}:")
                for i, field_type in enumerate(ctor.fields):
                    type_str = self._gen_type_ref(field_type)
                    lines.append(f"    _field{i}: {type_str}")
                lines.append("")
            else:
                lines.append(f"class {ctor.name}:")
                lines.append("    _instance = None")
                lines.append("    def __new__(cls):")
                lines.append("        if cls._instance is None:")
                lines.append("            cls._instance = super().__new__(cls)")
                lines.append("        return cls._instance")
                lines.append("")
        ctor_names = [c.name for c in decl.constructors]
        lines.append(f"{decl.name} = Union[{', '.join(ctor_names)}]")
        for ctor in decl.constructors:
            if not ctor.fields:
                lines.append(f"{ctor.name} = {ctor.name}()")
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
        return f"from {module} import *"

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

    def _gen_expr(self, expr: ast.Expr, bindings: dict = None) -> str:
        if bindings is None:
            bindings = {}
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
        let_var = self._fresh_let_var()
        pattern_check, bindings = self._gen_pattern_check(expr.pattern, let_var)
        if pattern_check == "True" and not bindings:
            return body_code
        if bindings:
            import re
            valid_identifier = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
            param_names = list(bindings.keys())
            if all(valid_identifier.match(name) for name in param_names):
                var_paths = list(bindings.values())
                inner_lambda = f"(lambda {', '.join(param_names)}: {body_code})"
                call_args = ", ".join(var_paths)
                body_code = f"{inner_lambda}({call_args})"
            else:
                for name, var_path in bindings.items():
                    pattern = r"\b" + re.escape(name) + r"\b"
                    body_code = re.sub(pattern, var_path, body_code)
        # Wrap in extra parens to fix precedence issue with immediately-called lambdas
        return f"(lambda {let_var}: ({body_code} if {pattern_check} else None))({value_code})"

    def _gen_let_func(self, expr: ast.LetFunc) -> str:
        import re

        safe_name = self._safe_name(expr.name)
        value_code = self._gen_expr(expr.value)
        body_code = self._gen_expr(expr.body)

        pattern = r"\b" + re.escape(expr.name) + r"\b"
        is_recursive = bool(re.search(pattern, value_code))

        curried_lambda = value_code
        for param in reversed(expr.params):
            curried_lambda = f"lambda {self._safe_name(param.name)}: {curried_lambda}"

        # Replace function name references in body_code with safe_name
        body_code_with_safe_name = re.sub(pattern, safe_name, body_code)

        if is_recursive:
            value_code_with_cell = re.sub(pattern, "__cell[0]", curried_lambda)
            body_code_with_cell = re.sub(pattern, "__cell[0]", body_code)
            return f"(lambda __cell: (__cell.__setitem__(0, ({value_code_with_cell})) or {body_code_with_cell}))([None])"
        else:
            return f"(lambda {safe_name}: {body_code_with_safe_name})({curried_lambda})"

    def _gen_match(self, expr: ast.Match) -> str:
        scrutinee_code = self._gen_expr(expr.scrutinee)
        if not expr.cases:
            return "None"
        
        # Generate each case with proper formatting
        cases_code = []
        for i, case in enumerate(expr.cases):
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, "__match_val"
            )
            body_code = self._gen_expr_with_bindings(case.body, bindings)
            if pattern_check == "True":
                cases_code.append(body_code)
            else:
                # Wrap ternary in extra parens to avoid precedence issues with immediately-called lambdas
                cases_code.append(f"(({body_code} if {pattern_check} else None))")

        # Use 'or' chain for simpler code - avoids deeply nested 'if True else'
        if len(cases_code) == 1:
            chain = cases_code[0]
        else:
            # Filter out None cases and chain with 'or'
            valid_cases = [c for c in cases_code if c != "None"]
            if not valid_cases:
                chain = "None"
            elif len(valid_cases) == 1:
                chain = valid_cases[0]
            else:
                # Use 'or' chain - returns first truthy result
                chain = " or ".join(f"({c})" for c in valid_cases)

        # Wrap entire lambda body in parens to fix precedence issue
        return f"(lambda __match_val: ({chain}))({scrutinee_code})"

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
            check = f"isinstance({var}, list) and len({var}) == {len(pattern.elements)}"
            for i, elem in enumerate(pattern.elements):
                elem_var = f"{var}[{i}]"
                elem_check, elem_bindings = self._gen_pattern_check(elem, elem_var)
                if elem_check != "True":
                    check = f"{check} and {elem_check}"
                bindings.update(elem_bindings)
            return check, bindings
        if isinstance(pattern, ast.ConsPattern):
            check = f"isinstance({var}, list) and len({var}) > 0"
            head_check, head_bindings = self._gen_pattern_check(pattern.head, f"{var}[0]")
            tail_check, tail_bindings = self._gen_pattern_check(pattern.tail, f"{var}[1:]")
            if head_check != "True":
                check = f"{check} and {head_check}"
            if tail_check != "True":
                check = f"{check} and {tail_check}"
            bindings.update(head_bindings)
            bindings.update(tail_bindings)
            return check, bindings
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
            # For constructors without args, use 'is' for singleton comparison
            # For constructors with args, use 'isinstance' for type checking
            if not pattern.args:
                check = f"{var} is {pattern.name}"
            else:
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

        # Apply bindings via regex substitution, but be careful not to replace
        # inside Record field names (which are inside quotes)
        # We do this by replacing field names with placeholders first
        for name, var_path in bindings.items():
            # Skip if this binding name could be confused with a field name
            # (simple heuristic: field names are usually shorter)
            if len(name) < 3:
                # For short names, use word boundary to avoid replacing inside words
                pattern = r"\b" + re.escape(name) + r"\b"
            else:
                pattern = r"\b" + re.escape(name) + r"\b"
            code = re.sub(pattern, var_path, code)
        return code

    def _gen_list(self, expr: ast.ListLit) -> str:
        elems_str = ", ".join(self._gen_expr(e) for e in expr.elements)
        return f"[{elems_str}]"

    def _gen_tuple(self, expr: ast.TupleLit) -> str:
        elems_str = ", ".join(self._gen_expr(e) for e in expr.elements)
        return f"({elems_str})"

    def _gen_record(self, expr: ast.RecordLit, bindings: dict = None) -> str:
        # Don't pass bindings here - let _gen_expr_with_bindings handle all binding substitution
        # via regex to avoid double-substitution issues
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


    def _format_code(self, code: str, max_line_length: int = 200) -> str:
        """Format code by breaking long lines at safe points."""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Only process lines that are too long
            if len(line) <= max_line_length:
                formatted_lines.append(line)
                continue
            
            # Try to break at good points
            broken = self._break_line(line, max_line_length)
            formatted_lines.extend(broken)
        
        return '\n'.join(formatted_lines)
    
    def _break_line(self, line: str, max_length: int) -> list[str]:
        """Break a long line at safe points."""
        if len(line) <= max_length:
            return [line]
        
        # Find a good break point
        # Look for ),  or ,  at around max_length
        search_start = max(0, max_length - 50)
        search_end = min(len(line), max_length + 50)
        
        # Try to find a safe break point
        break_point = -1
        depth = 0
        
        for i in range(search_end - 1, search_start - 1, -1):
            c = line[i]
            
            # Track parenthesis depth
            if c == ')':
                depth += 1
            elif c == '(':
                depth -= 1
            
            # Only break at depth 0 (outside parentheses)
            # and after a comma or closing paren
            if depth == 0 and i + 1 < len(line):
                next_char = line[i + 1]
                if c in ',)' and next_char not in ' 	':
                    break_point = i + 1
                    break
                # Also break after )=  or ),
                if c == ')' and next_char == '=':
                    break_point = i + 1
                    break
        
        if break_point == -1:
            # No good break point found, just truncate
            break_point = max_length
        
        first_line = line[:break_point].rstrip()
        rest = line[break_point:].lstrip()
        
        # Add proper continuation - wrap rest in parens if it starts with binary operator
        if rest.startswith('or ') or rest.startswith('and '):
            rest = '(' + rest + ')'
        
        # Recursively break remaining lines
        remaining = self._break_line(rest, max_length)
        return [first_line] + remaining
