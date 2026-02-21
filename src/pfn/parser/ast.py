from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass
class Span:
    start: int
    end: int
    line: int
    column: int


@dataclass
class TypeRef:
    pass


@dataclass
class SimpleTypeRef(TypeRef):
    name: str
    args: list[TypeRef] = field(default_factory=list)


@dataclass
class FunTypeRef(TypeRef):
    param: TypeRef
    result: TypeRef


@dataclass
class TupleTypeRef(TypeRef):
    elements: list[TypeRef]


@dataclass
class RecordTypeRef(TypeRef):
    fields: list[tuple[str, TypeRef]]


@dataclass
class Param:
    name: str
    type_annotation: TypeRef | None = None


# ============ Patterns ============


@dataclass
class Pattern:
    pass


@dataclass
class IntPattern(Pattern):
    value: int


@dataclass
class FloatPattern(Pattern):
    value: float


@dataclass
class StringPattern(Pattern):
    value: str


@dataclass
class CharPattern(Pattern):
    value: str


@dataclass
class BoolPattern(Pattern):
    value: bool


@dataclass
class VarPattern(Pattern):
    name: str


@dataclass
class WildcardPattern(Pattern):
    pass


@dataclass
class ConsPattern(Pattern):
    head: Pattern
    tail: Pattern


@dataclass
class ListPattern(Pattern):
    elements: list[Pattern]


@dataclass
class TuplePattern(Pattern):
    elements: list[Pattern]


@dataclass
class RecordPattern(Pattern):
    fields: list[tuple[str, Pattern]]


@dataclass
class ConstructorPattern(Pattern):
    name: str
    args: list[Pattern] = field(default_factory=list)


# ============ Expressions ============


@dataclass
class Expr:
    pass


@dataclass
class IntLit(Expr):
    value: int


@dataclass
class FloatLit(Expr):
    value: float


@dataclass
class StringLit(Expr):
    value: str


@dataclass
class CharLit(Expr):
    value: str


@dataclass
class BoolLit(Expr):
    value: bool


@dataclass
class UnitLit(Expr):
    pass


@dataclass
class Var(Expr):
    name: str


@dataclass
class Lambda(Expr):
    params: list[Param]
    body: Expr


@dataclass
class App(Expr):
    func: Expr
    args: list[Expr]


@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass
class If(Expr):
    cond: Expr
    then_branch: Expr
    else_branch: Expr


@dataclass
class Let(Expr):
    name: str
    value: Expr
    body: Expr


@dataclass
class LetFunc(Expr):
    name: str
    params: list[Param]
    value: Expr
    body: Expr


@dataclass
class Match(Expr):
    scrutinee: Expr
    cases: list[MatchCase]


@dataclass
class MatchCase:
    pattern: Pattern
    body: Expr
    guard: Expr | None = None


@dataclass
class ListLit(Expr):
    elements: list[Expr]


@dataclass
class TupleLit(Expr):
    elements: list[Expr]


@dataclass
class RecordLit(Expr):
    fields: list[RecordField]


@dataclass
class RecordField:
    name: str
    value: Expr


@dataclass
class FieldAccess(Expr):
    expr: Expr
    field: str


@dataclass
class RecordUpdate(Expr):
    record: Expr
    updates: list[RecordField]


@dataclass
class IndexAccess(Expr):
    expr: Expr
    index: Expr


@dataclass
class Slice(Expr):
    expr: Expr
    start: Expr | None
    end: Expr | None
    step: Expr | None


# ============ Declarations ============


@dataclass
class Decl:
    pass


@dataclass
class DefDecl(Decl):
    name: str
    params: list[Param]
    body: Expr
    return_type: TypeRef | None = None


@dataclass
class TypeDecl(Decl):
    name: str
    params: list[str] = field(default_factory=list)
    constructors: list[Constructor] = field(default_factory=list)
    is_record: bool = False
    record_fields: list[tuple[str, TypeRef]] = field(default_factory=list)


@dataclass
class Constructor:
    name: str
    fields: list[TypeRef] = field(default_factory=list)


@dataclass
class TypeAliasDecl(Decl):
    name: str
    params: list[str]
    type_ref: TypeRef


@dataclass
class ImportDecl(Decl):
    module: str
    alias: str | None = None
    exposing: list[str] | None = None
    is_python: bool = False


@dataclass
class ExportDecl(Decl):
    names: list[str]


# ============ Module ============


@dataclass
class Module:
    name: str | None = None
    declarations: list[Decl] = field(default_factory=list)
