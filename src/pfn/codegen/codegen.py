from __future__ import annotations

from pfn.parser import ast


class CodeGenerator:
    def __init__(self):
        self._let_counter = 0
        self._helper_funcs = []
        self._helper_counter = 0
        self._zero_param_funcs: set = set()  # Track zero-param functions for proper calling
        self._current_module_decls: list = []  # Track current module declarations

    def _fresh_let_var(self) -> str:
        var = f"__let_val_{self._let_counter}"
        self._let_counter += 1
        return var

    def _fresh_helper_name(self) -> str:
        name = f"__helper_{self._helper_counter}"
        self._helper_counter += 1
        return name

    MODULE_LEVEL_NAMES = {
        "String", "List", "Dict", "Set", "Maybe", "Result", "Just", "Nothing", "Ok", "Err", "Record",
        "reverse", "_not_",
        "Ok", "Err", "Just", "Nothing", "UnitLit",
    }

    def _collect_free_vars(self, expr: ast.Expr, bound_vars: set = None) -> set:
        """Collect free variables from an expression."""
        if bound_vars is None:
            bound_vars = set()
        vars_found: set = set()

        def walk(e: ast.Expr):
            if isinstance(e, ast.Var):
                if e.name not in bound_vars and e.name not in self.PYTHON_KEYWORDS and e.name not in self.MODULE_LEVEL_NAMES:
                    vars_found.add(e.name)
            elif isinstance(e, (ast.IntLit, ast.FloatLit, ast.StringLit, ast.CharLit, ast.BoolLit, ast.UnitLit)):
                pass
            elif isinstance(e, ast.Lambda):
                old_bound = bound_vars.copy()
                for param in e.params:
                    bound_vars.add(param.name)
                walk(e.body)
                bound_vars.update(old_bound)
            elif isinstance(e, ast.Let):
                walk(e.value)
                old_bound = bound_vars.copy()
                bound_vars.add(e.name)
                walk(e.body)
                bound_vars.update(old_bound)
            elif isinstance(e, ast.LetPattern):
                walk(e.value)
                self._collect_pattern_vars(e.pattern, bound_vars)
                walk(e.body)
            elif isinstance(e, ast.LetFunc):
                walk(e.value)
                old_bound = bound_vars.copy()
                bound_vars.add(e.name)
                for param in e.params:
                    bound_vars.add(param.name)
                walk(e.body)
                bound_vars.update(old_bound)
            elif isinstance(e, ast.DoNotation):
                for binding in e.bindings:
                    walk(binding.value)
                    old_bound = bound_vars.copy()
                    bound_vars.add(binding.name)
                    walk(e.body)
                    bound_vars.update(old_bound)
            elif isinstance(e, ast.If):
                walk(e.cond)
                walk(e.then_branch)
                walk(e.else_branch)
            elif isinstance(e, ast.Match):
                walk(e.scrutinee)
                for case in e.cases:
                    self._collect_pattern_vars(case.pattern, bound_vars)
                    old_bound = bound_vars.copy()
                    walk(case.body)
                    bound_vars.update(old_bound)
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
                        old_bound = bound_vars.copy()
                        for p in case.params:
                            bound_vars.add(p.name)
                        walk(case.body)
                        bound_vars.update(old_bound)
            elif isinstance(e, ast.PerformExpr):
                for arg in e.args:
                    walk(arg)

        walk(expr)
        return vars_found

    def _collect_pattern_vars(self, pattern: ast.Pattern, vars_found: set):
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

    def _add_helper_func(self, name: str, params: list[str], body: str):
        self._helper_funcs.append((name, params, body))

    def _generate_helper_funcs(self) -> str:
        if not self._helper_funcs:
            return ""
        lines = ["", "# Helper functions to avoid deep nesting"]
        for name, params, body in self._helper_funcs:
            param_str = ", ".join(params)
            lines.append(f"def {name}({param_str}):")
            lines.append(f"    return {body}")
        return "\n".join(lines)

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

    def generate_module(self, module: ast.Module, source_file: str = None) -> str:
        # Reset tracking for each module
        self._zero_param_funcs.clear()
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_info = f" from {source_file}" if source_file else ""
        lines = [
            f"# ============================================================",
            f"# AUTO-GENERATED CODE - DO NOT EDIT",
            f"# Generated{source_info} by Pfn compiler",
            f"# Generated at: {timestamp}",
            f"# ============================================================",
            "",
            "from __future__ import annotations",
            "from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record",
            "from stdlib import reverse, _not_, fst, snd",
        ]
        for decl in module.declarations:
            lines.append(self._gen_decl(decl))
        # Insert helper functions AFTER imports but BEFORE declarations
        helper_funcs = self._generate_helper_funcs()
        if helper_funcs:
            # Find position after last import
            insert_pos = len(lines)
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_pos = i + 1
            lines.insert(insert_pos, helper_funcs)
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
            if decl.has_parens:
                # def foo() = expr - generate a function
                func_def = f"def {safe_name}():\n    return {body_code}"
            else:
                # def foo = expr - generate a value
                func_def = f"{safe_name} = {body_code}"
        elif len(decl.params) == 1:
            params_str = self._safe_name(decl.params[0].name)
            func_def = f"def {safe_name}({params_str}):\n    return {body_code}"
        else:
            # Generate curried Python function: def f(x): return lambda y: lambda z: body
            # This matches the curried calls generated by _gen_app
            inner_body = body_code
            for param in reversed(decl.params[1:]):
                inner_body = f"lambda {self._safe_name(param.name)}: {inner_body}"
            func_def = f"def {safe_name}({self._safe_name(decl.params[0].name)}):\n    return {inner_body}"

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
                # Use _instance suffix for singleton instances to avoid conflict with class name
                lines.append(f"_instance_{ctor.name.lower()} = {ctor.name}()")
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
        args = [self._gen_expr(arg) for arg in expr.args]
        
        # Flatten nested applications: App(App(f, [a]), [b]) -> f(a, b)
        # This handles constructor calls like LR_OK(chars)(st2) -> LR_OK(chars, st2)
        if isinstance(expr.func, ast.App):
            # This is a nested app like f(a)(b)
            # Flatten to f(a, b)
            inner_func = expr.func.func
            inner_args = expr.func.args
            all_args = inner_args + expr.args
            func_code = self._gen_expr(inner_func)
            args = [self._gen_expr(arg) for arg in all_args]
        
        # Check if this is a constructor call (uppercase name)
        # Constructors take a single tuple argument, not curried arguments
        is_constructor = False
        if isinstance(expr.func, ast.Var):
            is_constructor = expr.func.name[0].isupper()
        elif isinstance(expr.func, ast.App) and isinstance(expr.func.func, ast.Var):
            is_constructor = expr.func.func.name[0].isupper()
        
        # For constructors, wrap arguments in a tuple
        # Constructors take a single tuple argument, not curried arguments
        if is_constructor and len(args) > 1:
            args_str = ", ".join(args)
            return f"{func_code}(({args_str}))"
        
        # Generate curried calls: f(a)(b)(c) instead of f(a, b, c)
        # This matches the curried function definitions generated by _gen_def_decl
        if len(args) > 1:
            result = func_code
            for arg in args:
                result = f"({result})({arg})"
            return result
        elif len(args) == 1:
            return f"{func_code}({args[0]})"
        else:
            return f"{func_code}()"

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
        # Use IIL to avoid scope issues with nested lambdas
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
        # Use IIL instead of helper function to preserve scope
        return f"(lambda {let_var}: {body_code} if {pattern_check} else None)({value_code})"

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
            # Use cell pattern for recursion - this allows the function to reference itself
            value_code_with_cell = re.sub(pattern, "__cell[0]", curried_lambda)
            body_code_with_cell = re.sub(pattern, "__cell[0]", body_code)
            return f"(lambda __cell: (__cell.__setitem__(0, ({value_code_with_cell})) or {body_code_with_cell}))([None])"
        else:
            return f"(lambda {safe_name}: {body_code_with_safe_name})({curried_lambda})"

    def _gen_match(self, expr: ast.Match) -> str:
        scrutinee_code = self._gen_expr(expr.scrutinee)
        if not expr.cases:
            return "None"
        
        # For complex matches with multiple cases, use helper function to avoid deep nesting
        if len(expr.cases) > 2:
            # Generate unique helper function name
            helper_name = self._fresh_helper_name()
            
            # Build the cases as a series of if-else
            # Process cases in REVERSE order so the last case (wildcard) becomes the fallback
            chain = "None"
            for case in reversed(expr.cases):
                pattern_check, bindings = self._gen_pattern_check(
                    case.pattern, "__match_val"
                )
                body_code = self._gen_expr_with_bindings(case.body, bindings)
                # When pattern_check is "True" (wildcard), it should be the fallback
                # Wrap the current chain as the else branch
                if pattern_check == "True":
                    # Wildcard is the fallback - use its body directly
                    chain = body_code
                else:
                    chain = f"({body_code} if {pattern_check} else {chain})"
            
            # Collect free variables from the entire match expression
            closure_vars: set = set()
            closure_vars.update(self._collect_free_vars(expr))
            
            # Create helper function with closure parameters
            helper_params = ["__match_val"] + sorted(closure_vars)
            helper_body = f"(lambda __match_val: {chain})(__match_val)"
            self._add_helper_func(helper_name, helper_params, helper_body)
            
            # Call helper function with scrutinee and closure vars
            call_args = [scrutinee_code] + sorted([f"{v}" for v in closure_vars])
            return f"{helper_name}({', '.join(call_args)})"
            
            return f"{helper_name}({scrutinee_code})"
        
        # For simple matches, use inline approach
        cases_code = []
        for i, case in enumerate(expr.cases):
            pattern_check, bindings = self._gen_pattern_check(
                case.pattern, "__match_val"
            )
            body_code = self._gen_expr_with_bindings(case.body, bindings)
            if pattern_check == "True":
                cases_code.append(body_code)
            else:
                cases_code.append(f"({body_code} if {pattern_check} else None)")

        if len(cases_code) == 1:
            single_case = cases_code[0]
            # For single non-wildcard cases, return scrutinee instead of None when no match
            # This is critical for nested matches where scrutinee (like Nothing) should propagate
            if " if False else None)" not in single_case:
                chain = single_case.replace(" else None)", " else __match_val)")
            else:
                chain = single_case
        else:
            valid_cases = [c for c in cases_code if c != "None"]
            if not valid_cases:
                chain = "None"
            elif len(valid_cases) == 1:
                chain = valid_cases[0]
            else:
                chain = " or ".join(f"({c})" for c in valid_cases)

        return f"(lambda __match_val: {chain})({scrutinee_code})"

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
