"""Optimizer passes for Pfn compiler.

This module provides various optimization passes that can be applied
to the IR to improve the generated code.
"""

from __future__ import annotations

from typing import Any, Optional

from pfn.ir.core import (
    IRApp,
    IRBinOp,
    IRFieldAccess,
    IRIf,
    IRLam,
    IRLet,
    IRLit,
    IRList,
    IRMatch,
    IRModule,
    IRNode,
    IRTransformer,
    IRTuple,
    IRUnaryOp,
    IRVar,
)


# ============ Base Optimizer ============


class Optimizer(IRTransformer):
    """Base optimizer class."""

    def __init__(self):
        self.changed = False

    def optimize_module(self, module: IRModule) -> IRModule:
        """Optimize an entire module."""
        new_defs = {}
        for name, node in module.definitions.items():
            new_defs[name] = self.transform(node)
        module.definitions = new_defs
        return module


# ============ Constant Folding ============


class ConstantFolding(Optimizer):
    """Fold constant expressions at compile time."""

    def transform_BinOp(self, node: IRBinOp) -> IRNode:
        left = self.transform(node.left)
        right = self.transform(node.right)

        if isinstance(left, IRLit) and isinstance(right, IRLit):
            self.changed = True
            result = self._fold_binop(node.op, left.value, right.value)
            if result is not None:
                return IRLit(result)

        return IRBinOp(node.op, left, right)

    def transform_UnaryOp(self, node: IRUnaryOp) -> IRNode:
        operand = self.transform(node.operand)

        if isinstance(operand, IRLit):
            self.changed = True
            result = self._fold_unaryop(node.op, operand.value)
            if result is not None:
                return IRLit(result)

        return IRUnaryOp(node.op, operand)

    def _fold_binop(self, op: str, left: any, right: any) -> any:
        try:
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right
            if op == "%":
                return left % right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "<":
                return left < right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            if op == ">=":
                return left >= right
            if op == "&&":
                return left and right
            if op == "||":
                return left or right
            if op == "++":
                return left + right
        except (TypeError, ZeroDivisionError):
            pass
        return None

    def _fold_unaryop(self, op: str, operand: any) -> any:
        try:
            if op == "-":
                return -operand
            if op == "!":
                return not operand
        except TypeError:
            pass
        return None


# ============ Dead Code Elimination ============


class DeadCodeElimination(Optimizer):
    """Remove unreachable code and unused bindings."""

    def transform_If(self, node: IRIf) -> IRNode:
        cond = self.transform(node.cond)

        if isinstance(cond, IRLit):
            self.changed = True
            if cond.value:
                return self.transform(node.then_branch)
            else:
                return self.transform(node.else_branch)

        then_branch = self.transform(node.then_branch)
        else_branch = self.transform(node.else_branch)

        return IRIf(cond, then_branch, else_branch)

    def transform_Let(self, node: IRLet) -> IRNode:
        value = self.transform(node.value)
        body = self.transform(node.body)

        if self._is_trivial(value):
            self.changed = True
            return body

        return IRLet(node.name, value, body)

    def _is_trivial(self, node: IRNode) -> bool:
        return isinstance(node, (IRLit, IRVar))


# ============ Function Inlining ============


class Inlining(Optimizer):
    """Inline small functions."""

    def __init__(self, threshold: int = 10):
        super().__init__()
        self.threshold = threshold
        self.inline_candidates: dict[str, IRNode] = {}

    def set_inline_candidates(self, candidates: dict[str, IRNode]) -> None:
        self.inline_candidates = candidates

    def transform_App(self, node: IRApp) -> IRNode:
        func = self.transform(node.func)
        args = [self.transform(arg) for arg in node.args]

        if (
            isinstance(func, IRVar)
            and func.name in self.inline_candidates
            and len(args) <= 3
        ):
            definition = self.inline_candidates[func.name]
            if self._should_inline(definition, len(args)):
                self.changed = True
                return self._inline(definition, args)

        return IRApp(func, args)

    def _should_inline(self, definition: IRNode, num_args: int) -> bool:
        if not isinstance(definition, IRLam):
            return False
        body_size = self._estimate_size(definition.body)
        return body_size <= self.threshold

    def _estimate_size(self, node: IRNode) -> int:
        if isinstance(node, (IRLit, IRVar)):
            return 1
        if isinstance(node, IRLam):
            return 1 + self._estimate_size(node.body)
        if isinstance(node, IRApp):
            return 1 + sum(self._estimate_size(a) for a in node.args)
        if isinstance(node, IRLet):
            return 1 + self._estimate_size(node.value) + self._estimate_size(node.body)
        return 10

    def _inline(self, definition: IRLam, args: list[IRNode]) -> IRNode:
        if len(args) != 1:
            return IRApp(IRLam(definition.param, definition.body), args)

        body = definition.body
        param = definition.param

        return self._substitute(body, param, args[0])

    def _substitute(self, node: IRNode, var: str, replacement: IRNode) -> IRNode:
        if isinstance(node, IRVar):
            if node.name == var:
                return replacement
            return node
        if isinstance(node, IRLam):
            if node.param == var:
                return node
            return IRLam(node.param, self._substitute(node.body, var, replacement))
        if isinstance(node, IRLet):
            new_value = self._substitute(node.value, var, replacement)
            if node.name == var:
                return IRLet(node.name, new_value, node.body)
            new_body = self._substitute(node.body, var, replacement)
            return IRLet(node.name, new_value, new_body)
        if isinstance(node, IRApp):
            return IRApp(
                self._substitute(node.func, var, replacement),
                [self._substitute(arg, var, replacement) for arg in node.args],
            )
        return node


# ============ Beta Reduction ============


class BetaReduction(Optimizer):
    """Reduce lambda applications (beta reduction)."""

    def transform_App(self, node: IRApp) -> IRNode:
        func = self.transform(node.func)
        args = [self.transform(arg) for arg in node.args]

        if isinstance(func, IRLam) and len(args) == 1:
            self.changed = True
            return self._substitute(func.body, func.param, args[0])

        return IRApp(func, args)

    def _substitute(self, node: IRNode, var: str, replacement: IRNode) -> IRNode:
        if isinstance(node, IRVar):
            if node.name == var:
                return replacement
            return node
        if isinstance(node, IRLam):
            if node.param == var:
                return node
            return IRLam(node.param, self._substitute(node.body, var, replacement))
        if isinstance(node, IRLet):
            new_value = self._substitute(node.value, var, replacement)
            if node.name == var:
                return IRLet(node.name, new_value, node.body)
            new_body = self._substitute(node.body, var, replacement)
            return IRLet(node.name, new_value, new_body)
        if isinstance(node, IRApp):
            return IRApp(
                self._substitute(node.func, var, replacement),
                [self._substitute(arg, var, replacement) for arg in node.args],
            )
        return node


# ============ Tail Call Optimization ============


class TailCallOptimization(Optimizer):
    """Convert tail recursive calls to loops."""

    def __init__(self):
        super().__init__()
        self.current_function: str | None = None

    def transform_Let(self, node: IRLet) -> IRNode:
        old_function = self.current_function
        if isinstance(node.value, IRLam):
            self.current_function = node.name

        value = self.transform(node.value)
        body = self.transform(node.body)

        self.current_function = old_function
        return IRLet(node.name, value, body)

    def transform_App(self, node: IRApp) -> IRNode:
        func = self.transform(node.func)
        args = [self.transform(arg) for arg in node.args]

        if self._is_tail_call(func, self.current_function):
            self.changed = True

        return IRApp(func, args)

    def _is_tail_call(self, func: IRNode, function_name: str | None) -> bool:
        if function_name is None:
            return False
        if isinstance(func, IRVar):
            return func.name == function_name
        return False


# ============ Common Subexpression Elimination ============


class CommonSubexprElimination(Optimizer):
    """Eliminate duplicate expressions."""

    def __init__(self):
        super().__init__()
        self.expressions: dict[str, IRNode] = {}
        self.counter = 0

    def transform(self, node: IRNode) -> IRNode:
        key = self._make_key(node)
        if key in self.expressions:
            self.changed = True
            name = f"_cse_{self.counter}"
            self.counter += 1
            return IRVar(name)

        result = super().transform(node)
        if self._is_expensive(result):
            self.expressions[key] = result
        return result

    def _make_key(self, node: IRNode) -> str:
        return str(node)

    def _is_expensive(self, node: IRNode) -> bool:
        if isinstance(node, (IRLit, IRVar)):
            return False
        return True


# ============ Soda (Simplify Operations and Data Structures) ============


class SodaOptimizer(Optimizer):
    """Simplify operations and data structures."""

    def transform_If(self, node: IRIf) -> IRNode:
        cond = self.transform(node.cond)
        then_branch = self.transform(node.then_branch)
        else_branch = self.transform(node.else_branch)

        if isinstance(then_branch, IRLit) and isinstance(else_branch, IRLit):
            if then_branch.value == else_branch.value:
                self.changed = True
                return then_branch

        return IRIf(cond, then_branch, else_branch)

    def transform_List(self, node: IRList) -> IRNode:
        elements = [self.transform(e) for e in node.elements]
        if not elements:
            self.changed = True
            return IRVar("empty_list")
        return IRList(elements)

    def transform_Tuple(self, node: IRTuple) -> IRNode:
        elements = [self.transform(e) for e in node.elements]
        return IRTuple(elements)


# ============ Composition Passes ============


def run_optimizer(
    module: IRModule,
    passes: list[type[Optimizer]] | None = None,
) -> IRModule:
    """Run optimization passes on a module.

    Args:
        module: The module to optimize
        passes: List of optimizer classes to run (default: all)

    Returns:
        Optimized module
    """
    if passes is None:
        passes = [
            ConstantFolding,
            BetaReduction,
            DeadCodeElimination,
            SodaOptimizer,
        ]

    for pass_class in passes:
        optimizer = pass_class()
        changed = True
        while changed:
            changed = False
            module = optimizer.optimize_module(module)

    return module


__all__ = [
    "Optimizer",
    "ConstantFolding",
    "DeadCodeElimination",
    "Inlining",
    "BetaReduction",
    "TailCallOptimization",
    "CommonSubexprElimination",
    "SodaOptimizer",
    "run_optimizer",
]
