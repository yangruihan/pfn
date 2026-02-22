from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pfn.parser import ast
from pfn.effects import (
    Effect,
    EffectSet,
    IOEffect,
    StateEffect,
    ThrowEffect,
    ReadEffect,
    PURE,
)


@dataclass
class EffectEnv:
    bindings: dict[str, EffectSet] = field(default_factory=dict)

    def extend(self, name: str, effects: EffectSet) -> EffectEnv:
        new_bindings = self.bindings.copy()
        new_bindings[name] = effects
        return EffectEnv(new_bindings)

    def lookup(self, name: str) -> EffectSet | None:
        return self.bindings.get(name)

    def merge(self, other: EffectEnv) -> EffectEnv:
        new_bindings = self.bindings.copy()
        new_bindings.update(other.bindings)
        return EffectEnv(new_bindings)


@dataclass
class EffectInferenceResult:
    effects: EffectSet
    env: EffectEnv


class EffectInferer:
    def __init__(self, env: EffectEnv | None = None):
        self.env = env or EffectEnv()
        self.effect_decls: dict[str, list[str]] = {}
        self.handler_stack: list[str] = []

    def register_effect(self, name: str, operations: list[str]) -> None:
        self.effect_decls[name] = operations

    def infer(self, expr: ast.Expr) -> EffectSet:
        result = self._infer(expr)
        return result.effects

    def _infer(self, expr: ast.Expr) -> EffectInferenceResult:
        if isinstance(expr, ast.IntLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.FloatLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.StringLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.CharLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.BoolLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.UnitLit):
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.Var):
            stored = self.env.lookup(expr.name)
            if stored:
                return EffectInferenceResult(stored, self.env)
            return EffectInferenceResult(PURE, self.env)

        if isinstance(expr, ast.Lambda):
            new_env = self.env
            for param in expr.params:
                new_env = new_env.extend(param.name, PURE)

            old_env = self.env
            self.env = new_env
            body_result = self._infer(expr.body)
            self.env = old_env

            return EffectInferenceResult(body_result.effects, self.env)

        if isinstance(expr, ast.App):
            func_result = self._infer(expr.func)
            combined = func_result.effects

            for arg in expr.args:
                arg_result = self._infer(arg)
                combined = combined.union(arg_result.effects)

            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.BinOp):
            left_result = self._infer(expr.left)
            right_result = self._infer(expr.right)
            combined = left_result.effects.union(right_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.UnaryOp):
            operand_result = self._infer(expr.operand)
            return EffectInferenceResult(operand_result.effects, self.env)

        if isinstance(expr, ast.If):
            cond_result = self._infer(expr.cond)
            then_result = self._infer(expr.then_branch)
            else_result = self._infer(expr.else_branch)

            combined = cond_result.effects.union(then_result.effects)
            combined = combined.union(else_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.Let):
            value_result = self._infer(expr.value)
            new_env = self.env.extend(expr.name, value_result.effects)

            old_env = self.env
            self.env = new_env
            body_result = self._infer(expr.body)
            self.env = old_env

            combined = value_result.effects.union(body_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.LetFunc):
            new_env = self.env
            for param in expr.params:
                new_env = new_env.extend(param.name, PURE)

            old_env = self.env
            self.env = new_env
            value_result = self._infer(expr.value)
            self.env = old_env

            new_env = self.env.extend(expr.name, value_result.effects)
            self.env = new_env
            body_result = self._infer(expr.body)
            self.env = old_env

            combined = value_result.effects.union(body_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.Match):
            scrutinee_result = self._infer(expr.scrutinee)
            combined = scrutinee_result.effects

            for case in expr.cases:
                case_env = self.env
                pattern_effects = self._infer_pattern_effects(case.pattern)
                for name, eff in pattern_effects.items():
                    case_env = case_env.extend(name, eff)

                old_env = self.env
                self.env = case_env
                body_result = self._infer(case.body)
                self.env = old_env

                combined = combined.union(body_result.effects)

                if case.guard:
                    guard_result = self._infer(case.guard)
                    combined = combined.union(guard_result.effects)

            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.ListLit):
            combined = PURE
            for elem in expr.elements:
                elem_result = self._infer(elem)
                combined = combined.union(elem_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.TupleLit):
            combined = PURE
            for elem in expr.elements:
                elem_result = self._infer(elem)
                combined = combined.union(elem_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.RecordLit):
            combined = PURE
            for field in expr.fields:
                field_result = self._infer(field.value)
                combined = combined.union(field_result.effects)
            return EffectInferenceResult(combined, self.env)

        if isinstance(expr, ast.FieldAccess):
            return self._infer(expr.expr)

        if isinstance(expr, ast.IndexAccess):
            expr_result = self._infer(expr.expr)
            index_result = self._infer(expr.index)
            return EffectInferenceResult(
                expr_result.effects.union(index_result.effects), self.env
            )

        if isinstance(expr, ast.DoNotation):
            combined = PURE
            for binding in expr.bindings:
                binding_result = self._infer(binding.value)
                combined = combined.union(binding_result.effects)
                self.env = self.env.extend(binding.name, binding_result.effects)

            body_result = self._infer(expr.body)
            combined = combined.union(body_result.effects)
            return EffectInferenceResult(combined, self.env)

        return EffectInferenceResult(PURE, self.env)

    def _infer_pattern_effects(self, pattern: ast.Pattern) -> dict[str, EffectSet]:
        result: dict[str, EffectSet] = {}

        if isinstance(pattern, ast.VarPattern):
            result[pattern.name] = PURE

        elif isinstance(pattern, ast.ListPattern):
            for elem in pattern.elements:
                result.update(self._infer_pattern_effects(elem))

        elif isinstance(pattern, ast.ConsPattern):
            result.update(self._infer_pattern_effects(pattern.head))
            result.update(self._infer_pattern_effects(pattern.tail))

        elif isinstance(pattern, ast.TuplePattern):
            for elem in pattern.elements:
                result.update(self._infer_pattern_effects(elem))

        elif isinstance(pattern, ast.RecordPattern):
            for _, p in pattern.fields:
                result.update(self._infer_pattern_effects(p))

        elif isinstance(pattern, ast.ConstructorPattern):
            for arg in pattern.args:
                result.update(self._infer_pattern_effects(arg))

        return result

    def infer_operation_effect(self, effect_name: str, op_name: str) -> Effect:
        if effect_name == "IO":
            return IOEffect()
        if effect_name == "State":
            return StateEffect(None)
        if effect_name == "Throw":
            return ThrowEffect(None)
        if effect_name == "Read":
            return ReadEffect()

        return Effect()

    def check_effect_handled(self, effect: Effect) -> bool:
        return len(self.handler_stack) > 0

    def push_handler(self, effect_name: str) -> None:
        self.handler_stack.append(effect_name)

    def pop_handler(self) -> str | None:
        if self.handler_stack:
            return self.handler_stack.pop()
        return None


def infer_effects(expr: ast.Expr, env: EffectEnv | None = None) -> EffectSet:
    inferer = EffectInferer(env)
    return inferer.infer(expr)


def is_pure(expr: ast.Expr) -> bool:
    effects = infer_effects(expr)
    return len(effects.effects) == 0


def get_effect_names(effects: EffectSet) -> set[str]:
    result: set[str] = set()
    for eff in effects.effects:
        if isinstance(eff, IOEffect):
            result.add("IO")
        elif isinstance(eff, StateEffect):
            result.add("State")
        elif isinstance(eff, ThrowEffect):
            result.add("Throw")
        elif isinstance(eff, ReadEffect):
            result.add("Read")
        else:
            result.add(type(eff).__name__.replace("Effect", ""))
    return result
