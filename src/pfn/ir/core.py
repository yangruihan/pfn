"""Intermediate Representation (IR) for Pfn.

This module defines the core IR nodes used for optimization and code generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IRNode:
    """Base class for all IR nodes."""

    def __repr__(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class IRVar(IRNode):
    """Variable reference."""

    name: str

    def __repr__(self) -> str:
        return f"Var({self.name!r})"


@dataclass(frozen=True)
class IRLit(IRNode):
    """Literal value."""

    value: Any
    type: str = "unknown"

    def __repr__(self) -> str:
        return f"Lit({self.value!r})"


@dataclass(frozen=True)
class IRFun(IRNode):
    """Function definition."""

    name: str
    params: list[str]
    body: IRNode

    def __repr__(self) -> str:
        return f"Fun({self.name}, {self.params}, ...)"


@dataclass(frozen=True)
class IRApp(IRNode):
    """Function application."""

    func: IRNode
    args: list[IRNode]

    def __repr__(self) -> str:
        return f"App({self.func}, {self.args})"


@dataclass(frozen=True)
class IRLam(IRNode):
    """Lambda expression."""

    param: str
    body: IRNode

    def __repr__(self) -> str:
        return f"Lam({self.param}, ...)"


@dataclass(frozen=True)
class IRLet(IRNode):
    """Let binding."""

    name: str
    value: IRNode
    body: IRNode

    def __repr__(self) -> str:
        return f"Let({self.name}, ..., ...)"


@dataclass(frozen=True)
class IRIf(IRNode):
    """If expression."""

    cond: IRNode
    then_branch: IRNode
    else_branch: IRNode

    def __repr__(self) -> str:
        return f"If({self.cond}, ..., ...)"


@dataclass(frozen=True)
class IRMatch(IRNode):
    """Pattern matching."""

    scrutinee: IRNode
    cases: list[IRCase]

    def __repr__(self) -> str:
        return f"Match({self.scrutinee}, {len(self.cases)} cases)"


@dataclass(frozen=True)
class IRCase(IRNode):
    """Match case."""

    pattern: IRPattern
    body: IRNode


@dataclass(frozen=True)
class IRPattern:
    """Base class for patterns."""

    pass


@dataclass(frozen=True)
class IRPWildcard(IRPattern):
    """Wildcard pattern."""

    name: str | None = None


@dataclass(frozen=True)
class IRPVar(IRPattern):
    """Variable pattern."""

    name: str


@dataclass(frozen=True)
class IRPLit(IRPattern):
    """Literal pattern."""

    value: Any


@dataclass(frozen=True)
class IRPCon(IRPattern):
    """Constructor pattern."""

    name: str
    args: list[IRPattern]


@dataclass(frozen=True)
class IRBinOp(IRNode):
    """Binary operation."""

    op: str
    left: IRNode
    right: IRNode

    def __repr__(self) -> str:
        return f"BinOp({self.op}, {self.left}, {self.right})"


@dataclass(frozen=True)
class IRUnaryOp(IRNode):
    """Unary operation."""

    op: str
    operand: IRNode

    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.operand})"


@dataclass(frozen=True)
class IRList(IRNode):
    """List literal."""

    elements: list[IRNode]

    def __repr__(self) -> str:
        return f"List({self.elements})"


@dataclass(frozen=True)
class IRTuple(IRNode):
    """Tuple literal."""

    elements: list[IRNode]

    def __repr__(self) -> str:
        return f"Tuple({self.elements})"


@dataclass(frozen=True)
class IRRecord(IRNode):
    """Record literal."""

    fields: list[tuple[str, IRNode]]

    def __repr__(self) -> str:
        return f"Record({self.fields})"


@dataclass(frozen=True)
class IRFieldAccess(IRNode):
    """Field access."""

    record: IRNode
    field: str

    def __repr__(self) -> str:
        return f"FieldAccess({self.record}.{self.field})"


@dataclass(frozen=True)
class IRIndexAccess(IRNode):
    """Index access."""

    collection: IRNode
    index: IRNode

    def __repr__(self) -> str:
        return f"IndexAccess({self.collection}[{self.index}])"


# ============ Module ============


@dataclass
class IRModule:
    """IR Module (not frozen since it's mutable during compilation)."""

    definitions: dict[str, IRNode] = field(default_factory=dict)

    def add_def(self, name: str, node: IRNode) -> None:
        self.definitions[name] = node

    def get_def(self, name: str) -> IRNode | None:
        return self.definitions.get(name)


# ============ Visitor Pattern ============


class IRVisitor:
    """Visitor for IR nodes."""

    def visit(self, node: IRNode) -> Any:
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: IRNode) -> Any:
        raise NotImplementedError(f"No visitor for {node.__class__.__name__}")


class IRTransformer:
    """Transformer for IR nodes (mutates or creates new nodes)."""

    def transform(self, node: IRNode) -> IRNode:
        method_name = f"transform_{node.__class__.__name__}"
        transformer = getattr(self, method_name, self.generic_transform)
        return transformer(node)

    def generic_transform(self, node: IRNode) -> IRNode:
        return node


__all__ = [
    "IRNode",
    "IRVar",
    "IRLit",
    "IRFun",
    "IRApp",
    "IRLam",
    "IRLet",
    "IRIf",
    "IRMatch",
    "IRCase",
    "IRPattern",
    "IRPWildcard",
    "IRPVar",
    "IRPLit",
    "IRPCon",
    "IRBinOp",
    "IRUnaryOp",
    "IRList",
    "IRTuple",
    "IRRecord",
    "IRFieldAccess",
    "IRIndexAccess",
    "IRModule",
    "IRVisitor",
    "IRTransformer",
]
