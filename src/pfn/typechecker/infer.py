from __future__ import annotations

from pfn.parser import ast
from pfn.types import (
    Scheme,
    Subst,
    TBool,
    TChar,
    TCon,
    TConstraint,
    TExists,
    TFloat,
    TForall,
    TFun,
    TInt,
    TIO,
    TList,
    TQualified,
    TString,
    TTuple,
    TUnit,
    TVar,
    Type,
    TypeEnv,
)
from pfn.typechecker.classes import (
    ClassContext,
    get_default_context,
    resolve_instance,
)
from pfn.effects import EffectSet, IOEffect, StateEffect, ThrowEffect, PURE
from pfn.effects.infer import EffectInferer, EffectEnv, infer_effects


class TypeError(Exception):
    pass


class TypeChecker:
    def __init__(
        self, env: TypeEnv | None = None, class_ctx: ClassContext | None = None
    ):
        self.env = env or TypeEnv()
        self.var_counter = 0
        self.class_ctx = class_ctx or get_default_context()

    def fresh_var(self) -> TVar:
        self.var_counter += 1
        return TVar(f"t{self.var_counter}")

    def instantiate(self, scheme: Scheme) -> Type:
        if not scheme.vars:
            return scheme.type
        subst = Subst()
        for var in scheme.vars:
            subst.mapping[var] = self.fresh_var()
        return subst.apply(scheme.type)

    def generalize(self, env: TypeEnv, t: Type) -> Scheme:
        subst = Subst()
        env_vars = subst.free_vars_env(env)
        type_vars = subst.free_vars(t)
        gen_vars = tuple(sorted(type_vars - env_vars))
        return Scheme(gen_vars, t)

    def infer(self, expr: ast.Expr) -> Type:
        subst, t = self._infer(expr, Subst())
        return subst.apply(t)

    def _infer(self, expr: ast.Expr, subst: Subst) -> tuple[Subst, Type]:
        if isinstance(expr, ast.IntLit):
            return subst, TInt()

        if isinstance(expr, ast.FloatLit):
            return subst, TFloat()

        if isinstance(expr, ast.StringLit):
            return subst, TString()

        if isinstance(expr, ast.CharLit):
            return subst, TChar()

        if isinstance(expr, ast.BoolLit):
            return subst, TBool()

        if isinstance(expr, ast.UnitLit):
            return subst, TUnit()

        if isinstance(expr, ast.Var):
            scheme = self.env.lookup(expr.name)
            if scheme is None:
                raise TypeError(f"Unbound variable: {expr.name}")
            return subst, self.instantiate(scheme)

        if isinstance(expr, ast.Lambda):
            param_types = []
            new_env = self.env
            for param in expr.params:
                tv = self.fresh_var()
                param_types.append(tv)
                new_env = new_env.extend(param.name, Scheme((), tv))

            old_env = self.env
            self.env = new_env
            subst, body_type = self._infer(expr.body, subst)
            self.env = old_env

            result_type = body_type
            for pt in reversed(param_types):
                result_type = TFun(pt, result_type)

            return subst, result_type

        if isinstance(expr, ast.App):
            subst, func_type = self._infer(expr.func, subst)
            for arg in expr.args:
                subst, arg_type = self._infer(arg, subst)
                result_type = self.fresh_var()
                new_subst = subst.unify(func_type, TFun(arg_type, result_type))
                if new_subst is None:
                    raise TypeError(f"Cannot apply {func_type} to {arg_type}")
                subst = new_subst.compose(subst)
                func_type = subst.apply(result_type)
            return subst, func_type

        if isinstance(expr, ast.BinOp):
            subst, left_type = self._infer(expr.left, subst)
            subst, right_type = self._infer(expr.right, subst)

            op = expr.op
            if op in ["+", "-", "*", "/", "%"]:
                new_subst = subst.unify(left_type, TInt())
                if new_subst is None:
                    new_subst = subst.unify(left_type, TFloat())
                    if new_subst is None:
                        raise TypeError(f"Expected Int or Float for operator {op}")
                subst = new_subst.compose(subst)
                new_subst = subst.unify(right_type, left_type)
                if new_subst is None:
                    raise TypeError(f"Type mismatch in {op}")
                subst = new_subst.compose(subst)
                return subst, subst.apply(left_type)

            if op in ["<", "<=", ">", ">="]:
                new_subst = subst.unify(left_type, TInt())
                if new_subst is None:
                    new_subst = subst.unify(left_type, TFloat())
                    if new_subst is None:
                        raise TypeError(f"Expected Int or Float for operator {op}")
                subst = new_subst.compose(subst)
                new_subst = subst.unify(right_type, left_type)
                if new_subst is None:
                    raise TypeError(f"Type mismatch in {op}")
                subst = new_subst.compose(subst)
                return subst, TBool()

            if op in ["==", "!="]:
                new_subst = subst.unify(left_type, right_type)
                if new_subst is None:
                    raise TypeError(f"Type mismatch in {op}")
                subst = new_subst.compose(subst)
                return subst, TBool()

            if op in ["&&", "||"]:
                new_subst = subst.unify(left_type, TBool())
                if new_subst is None:
                    raise TypeError(f"Expected Bool for operator {op}")
                subst = new_subst.compose(subst)
                new_subst = subst.unify(right_type, TBool())
                if new_subst is None:
                    raise TypeError(f"Expected Bool for operator {op}")
                subst = new_subst.compose(subst)
                return subst, TBool()

            if op == "++":
                elem_type = self.fresh_var()
                new_subst = subst.unify(left_type, TList(elem_type))
                if new_subst is None:
                    raise TypeError(f"Expected List for operator ++")
                subst = new_subst.compose(subst)
                new_subst = subst.unify(right_type, TList(subst.apply(elem_type)))
                if new_subst is None:
                    raise TypeError(f"Type mismatch in ++")
                subst = new_subst.compose(subst)
                return subst, TList(subst.apply(elem_type))

            if op == "::":
                elem_type = left_type
                new_subst = subst.unify(right_type, TList(elem_type))
                if new_subst is None:
                    raise TypeError(f"Expected List for operator ::")
                subst = new_subst.compose(subst)
                return subst, TList(subst.apply(elem_type))

            raise TypeError(f"Unknown operator: {op}")

        if isinstance(expr, ast.UnaryOp):
            subst, operand_type = self._infer(expr.operand, subst)

            if expr.op == "-":
                new_subst = subst.unify(operand_type, TInt())
                if new_subst is None:
                    new_subst = subst.unify(operand_type, TFloat())
                    if new_subst is None:
                        raise TypeError(f"Expected Int or Float for operator -")
                subst = new_subst.compose(subst)
                return subst, subst.apply(operand_type)

            if expr.op == "!":
                new_subst = subst.unify(operand_type, TBool())
                if new_subst is None:
                    raise TypeError(f"Expected Bool for operator !")
                subst = new_subst.compose(subst)
                return subst, TBool()

            raise TypeError(f"Unknown unary operator: {expr.op}")

        if isinstance(expr, ast.If):
            subst, cond_type = self._infer(expr.cond, subst)
            new_subst = subst.unify(cond_type, TBool())
            if new_subst is None:
                raise TypeError(f"If condition must be Bool, got {cond_type}")
            subst = new_subst.compose(subst)

            subst, then_type = self._infer(expr.then_branch, subst)
            subst, else_type = self._infer(expr.else_branch, subst)

            new_subst = subst.unify(then_type, else_type)
            if new_subst is None:
                raise TypeError(
                    f"If branches must have same type: {then_type} vs {else_type}"
                )
            subst = new_subst.compose(subst)
            return subst, subst.apply(then_type)

        if isinstance(expr, ast.Let):
            subst, value_type = self._infer(expr.value, subst)
            scheme = self.generalize(self.env, value_type)
            old_env = self.env
            self.env = self.env.extend(expr.name, scheme)
            subst, body_type = self._infer(expr.body, subst)
            self.env = old_env
            return subst, body_type

        if isinstance(expr, ast.LetFunc):
            param_types = []
            new_env = self.env
            for param in expr.params:
                tv = self.fresh_var()
                param_types.append(tv)
                new_env = new_env.extend(param.name, Scheme((), tv))

            old_env = self.env
            self.env = new_env
            subst, value_type = self._infer(expr.value, subst)
            self.env = old_env

            for pt in reversed(param_types):
                value_type = TFun(subst.apply(pt), value_type)

            scheme = self.generalize(self.env, value_type)
            self.env = self.env.extend(expr.name, scheme)
            subst, body_type = self._infer(expr.body, subst)
            self.env = old_env
            return subst, body_type

        if isinstance(expr, ast.ListLit):
            if not expr.elements:
                return subst, TList(self.fresh_var())

            subst, first_type = self._infer(expr.elements[0], subst)
            elem_type = first_type

            for elem in expr.elements[1:]:
                subst, t = self._infer(elem, subst)
                new_subst = subst.unify(elem_type, t)
                if new_subst is None:
                    raise TypeError(f"List elements must have same type")
                subst = new_subst.compose(subst)
                elem_type = subst.apply(elem_type)

            return subst, TList(elem_type)

        if isinstance(expr, ast.TupleLit):
            types = []
            for elem in expr.elements:
                subst, t = self._infer(elem, subst)
                types.append(t)
            return subst, TTuple(tuple(types))

        if isinstance(expr, ast.Match):
            subst, scrutinee_type = self._infer(expr.scrutinee, subst)

            if not expr.cases:
                return subst, self.fresh_var()

            result_type = self.fresh_var()
            for case in expr.cases:
                case_env = self.env
                subst, pattern_type = self._infer_pattern(case.pattern, subst, case_env)

                new_subst = subst.unify(scrutinee_type, pattern_type)
                if new_subst is None:
                    raise TypeError(f"Pattern type mismatch")
                subst = new_subst.compose(subst)

                if case.guard:
                    subst, guard_type = self._infer(case.guard, subst)
                    new_subst = subst.unify(guard_type, TBool())
                    if new_subst is None:
                        raise TypeError(f"Guard must be Bool")
                    subst = new_subst.compose(subst)

                old_env = self.env
                self.env = case_env
                subst, body_type = self._infer(case.body, subst)
                self.env = old_env

                new_subst = subst.unify(result_type, body_type)
                if new_subst is None:
                    raise TypeError(f"Match cases must have same type")
                subst = new_subst.compose(subst)
                result_type = subst.apply(result_type)

            return subst, result_type

        if isinstance(expr, ast.FieldAccess):
            subst, expr_type = self._infer(expr.expr, subst)
            result_type = self.fresh_var()
            return subst, result_type

        if isinstance(expr, ast.IndexAccess):
            subst, expr_type = self._infer(expr.expr, subst)
            subst, index_type = self._infer(expr.index, subst)
            new_subst = subst.unify(index_type, TInt())
            if new_subst is None:
                raise TypeError(f"Index must be Int")
            subst = new_subst.compose(subst)
            result_type = self.fresh_var()
            return subst, result_type

        raise TypeError(f"Unknown expression type: {type(expr)}")

    def _infer_pattern(
        self, pattern: ast.Pattern, subst: Subst, env: TypeEnv
    ) -> tuple[Subst, Type]:
        if isinstance(pattern, ast.IntPattern):
            return subst, TInt()

        if isinstance(pattern, ast.FloatPattern):
            return subst, TFloat()

        if isinstance(pattern, ast.StringPattern):
            return subst, TString()

        if isinstance(pattern, ast.CharPattern):
            return subst, TChar()

        if isinstance(pattern, ast.BoolPattern):
            return subst, TBool()

        if isinstance(pattern, ast.VarPattern):
            tv = self.fresh_var()
            new_env = env.extend(pattern.name, Scheme((), tv))
            env.bindings.update(new_env.bindings)
            return subst, tv

        if isinstance(pattern, ast.WildcardPattern):
            return subst, self.fresh_var()

        if isinstance(pattern, ast.ListPattern):
            if not pattern.elements:
                return subst, TList(self.fresh_var())

            subst, first_type = self._infer_pattern(pattern.elements[0], subst, env)
            elem_type = first_type

            for elem in pattern.elements[1:]:
                subst, t = self._infer_pattern(elem, subst, env)
                new_subst = subst.unify(elem_type, t)
                if new_subst is None:
                    raise TypeError(f"Pattern elements must have same type")
                subst = new_subst.compose(subst)
                elem_type = subst.apply(elem_type)

            return subst, TList(elem_type)

        if isinstance(pattern, ast.ConsPattern):
            subst, head_type = self._infer_pattern(pattern.head, subst, env)
            subst, tail_type = self._infer_pattern(pattern.tail, subst, env)

            new_subst = subst.unify(tail_type, TList(head_type))
            if new_subst is None:
                raise TypeError(f"Cons pattern type mismatch")
            subst = new_subst.compose(subst)
            return subst, TList(subst.apply(head_type))

        if isinstance(pattern, ast.TuplePattern):
            types = []
            for elem in pattern.elements:
                subst, t = self._infer_pattern(elem, subst, env)
                types.append(t)
            return subst, TTuple(tuple(types))

        raise TypeError(f"Unknown pattern type: {type(pattern)}")

    def check_instance(self, class_name: str, type_: Type) -> bool:
        if isinstance(type_, TVar):
            return False
        inst = resolve_instance(self.class_ctx, class_name, type_)
        return inst is not None

    def get_instance_method(self, class_name: str, type_: Type, method_name: str):
        if isinstance(type_, TVar):
            return None
        inst = resolve_instance(self.class_ctx, class_name, type_)
        if inst:
            return inst.methods.get(method_name)
        return None

    def skolemize(self, t: Type) -> tuple[Type, list[tuple[str, TVar]]]:
        """Replace bound type variables with skolem constants.

        Used for checking higher-rank types.
        Returns the skolemized type and a list of (original_var, skolem_var) pairs.
        """
        if isinstance(t, TForall):
            skolems = []
            result = t.inner
            for var in t.vars:
                skolem = TVar(f"s_{var}_{self.var_counter}")
                self.var_counter += 1
                skolems.append((var, skolem))
                subst = Subst({var: skolem})
                result = subst.apply(result)
            return result, skolems
        return t, []

    def unskolemize(self, t: Type, skolems: list[tuple[str, TVar]]) -> Type:
        """Replace skolem constants back with bound type variables."""
        if not skolems:
            return t
        subst = Subst({sk.name: TVar(var) for var, sk in skolems})
        return subst.apply(t)

    def check_rank_n(self, expected: Type, actual: Type) -> Subst | None:
        """Check if actual type matches expected type, handling higher-rank types.

        This implements the subsumption check for Rank-N types.
        """
        expected = Subst().apply(expected)
        actual = Subst().apply(actual)

        if isinstance(expected, TForall):
            skolemized, skolems = self.skolemize(expected)
            subst = self.check_rank_n(skolemized, actual)
            if subst is None:
                return None
            return self.unskolemize_subst(subst, skolems)

        if isinstance(actual, TForall):
            return self.check_rank_n(expected, self.instantiate_forall(actual))

        return Subst().unify(expected, actual)

    def instantiate_forall(self, t: TForall) -> Type:
        """Instantiate a forall type with fresh type variables."""
        subst = Subst()
        for var in t.vars:
            subst.mapping[var] = self.fresh_var()
        return subst.apply(t.inner)

    def unskolemize_subst(self, subst: Subst, skolems: list[tuple[str, TVar]]) -> Subst:
        """Remove skolem variables from substitution."""
        new_mapping = {}
        for k, v in subst.mapping.items():
            if not any(sk.name == k for _, sk in skolems):
                new_mapping[k] = v
        return Subst(new_mapping)

    def infer_qualified(self, expr: ast.Expr) -> tuple[Type, tuple[TConstraint, ...]]:
        """Infer type with constraints for qualified types."""
        subst, t = self._infer(expr, Subst())
        t = subst.apply(t)
        return t, ()

    def check_constraint_satisfiable(self, constraint: TConstraint) -> bool:
        """Check if a type class constraint is satisfiable."""
        return self.check_instance(constraint.class_name, constraint.type_)

    def infer_with_effects(self, expr: ast.Expr) -> tuple[Type, EffectSet]:
        """Infer both type and effects for an expression."""
        t = self.infer(expr)
        effects = infer_effects(expr, EffectEnv())
        return t, effects

    def wrap_with_io(self, t: Type, effects: EffectSet) -> Type:
        """Wrap type with IO if there are IO effects."""
        if any(isinstance(e, IOEffect) for e in effects.effects):
            return TIO(t)
        return t

    def check_effect_safety(self, expr: ast.Expr) -> bool:
        """Check if expression's effects are properly handled."""
        effects = infer_effects(expr)
        return len(effects.effects) == 0
