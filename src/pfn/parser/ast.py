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
    rest: Pattern | None = None  # For spread pattern: [a, b, ...rest]


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
class LetPattern(Expr):
    pattern: Pattern
    value: Expr
    body: Expr


@dataclass
class LetFunc(Expr):
    name: str
    params: list[Param]
    value: Expr
    body: Expr


@dataclass
class DoNotation(Expr):
    bindings: list[DoBinding]
    body: Expr


@dataclass
class DoBinding:
    name: str
    value: Expr


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
    is_exported: bool = False
    export_name: str | None = None


@dataclass
class TypeDecl(Decl):
    name: str
    params: list[str] = field(default_factory=list)
    constructors: list[Constructor] = field(default_factory=list)
    is_record: bool = False
    record_fields: list[tuple[str, TypeRef]] = field(default_factory=list)
    is_gadt: bool = False


@dataclass
class GADTConstructor:
    name: str
    params: list[TypeRef]
    result_type: TypeRef


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


@dataclass
class InterfaceDecl(Decl):
    """Type class interface definition"""

    name: str
    params: list[str] = field(default_factory=list)
    methods: list[InterfaceMethod] = field(default_factory=list)
    superclasses: list[str] = field(default_factory=list)


@dataclass
class InterfaceMethod:
    name: str
    type: TypeRef


@dataclass
class ImplDecl(Decl):
    """Type class instance implementation"""

    class_name: str
    type_ref: TypeRef
    methods: list[ImplMethod] = field(default_factory=list)


@dataclass
class ImplMethod:
    name: str
    params: list[Param]
    body: Expr


@dataclass
class EffectDecl(Decl):
    """Effect declaration"""

    name: str
    operations: list[EffectOp] = field(default_factory=list)


@dataclass
class EffectOp:
    name: str
    type: TypeRef


@dataclass
class HandlerDecl(Decl):
    """Handler declaration for custom effect handling"""

    effect_name: str
    handlers: list[HandlerCase] = field(default_factory=list)
    return_type: TypeRef | None = None


@dataclass
class HandlerCase:
    """Single handler case for an operation"""

    op_name: str
    body: Expr
    params: list[Param] = field(default_factory=list)
    resume_param: str | None = None


@dataclass
class HandleExpr(Expr):
    """Handle expression: handle expr with handler"""

    expr: Expr
    handler_cases: list[HandlerCase] = field(default_factory=list)
    handler_name: str | None = None


@dataclass
class PerformExpr(Expr):
    """Perform an effect operation"""

    effect_name: str
    op_name: str
    args: list[Expr] = field(default_factory=list)


# ============ Module ============


@dataclass
class Module:
    name: str | None = None
    declarations: list[Decl] = field(default_factory=list)
