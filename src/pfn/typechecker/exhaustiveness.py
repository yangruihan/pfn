from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pfn.parser import ast
from pfn.types import (
    Type,
    TInt,
    TFloat,
    TString,
    TBool,
    TChar,
    TList,
    TTuple,
    TCon,
)


@dataclass(frozen=True)
class Pattern:
    pass


@dataclass(frozen=True)
class PWild(Pattern):
    pass


@dataclass(frozen=True)
class PVar(Pattern):
    name: str


@dataclass(frozen=True)
class PCon(Pattern):
    name: str
    args: tuple[Pattern, ...] = ()


@dataclass(frozen=True)
class PInt(Pattern):
    value: int


@dataclass(frozen=True)
class PFloat(Pattern):
    value: float


@dataclass(frozen=True)
class PString(Pattern):
    value: str


@dataclass(frozen=True)
class PBool(Pattern):
    value: bool


@dataclass(frozen=True)
class PChar(Pattern):
    value: str


@dataclass(frozen=True)
class PList(Pattern):
    elements: tuple[Pattern, ...]


@dataclass(frozen=True)
class PCons(Pattern):
    head: Pattern
    tail: Pattern


@dataclass(frozen=True)
class PTuple(Pattern):
    elements: tuple[Pattern, ...]


def convert_pattern(p: ast.Pattern) -> Pattern:
    from pfn.parser import ast as pfn_ast

    if isinstance(p, pfn_ast.IntPattern):
        return PInt(p.value)
    if isinstance(p, pfn_ast.FloatPattern):
        return PFloat(p.value)
    if isinstance(p, pfn_ast.StringPattern):
        return PString(p.value)
    if isinstance(p, pfn_ast.CharPattern):
        return PChar(p.value)
    if isinstance(p, pfn_ast.BoolPattern):
        return PBool(p.value)
    if isinstance(p, pfn_ast.VarPattern):
        return PVar(p.name)
    if isinstance(p, pfn_ast.WildcardPattern):
        return PWild()
    if isinstance(p, pfn_ast.ListPattern):
        return PList(tuple(convert_pattern(e) for e in p.elements))
    if isinstance(p, pfn_ast.ConsPattern):
        return PCons(convert_pattern(p.head), convert_pattern(p.tail))
    if isinstance(p, pfn_ast.TuplePattern):
        return PTuple(tuple(convert_pattern(e) for e in p.elements))
    if isinstance(p, pfn_ast.ConstructorPattern):
        return PCon(p.name, tuple(convert_pattern(a) for a in p.args))
    return PWild()


@dataclass
class ExhaustivenessResult:
    exhaustive: bool
    missing_patterns: list[Pattern]
    redundant_patterns: list[int]


def is_wild(p: Pattern) -> bool:
    return isinstance(p, PWild) or isinstance(p, PVar)


def patterns_overlap(p1: Pattern, p2: Pattern) -> bool:
    if is_wild(p1) or is_wild(p2):
        return True

    if isinstance(p1, PInt) and isinstance(p2, PInt):
        return p1.value == p2.value
    if isinstance(p1, PFloat) and isinstance(p2, PFloat):
        return p1.value == p2.value
    if isinstance(p1, PString) and isinstance(p2, PString):
        return p1.value == p2.value
    if isinstance(p1, PBool) and isinstance(p2, PBool):
        return p1.value == p2.value
    if isinstance(p1, PChar) and isinstance(p2, PChar):
        return p1.value == p2.value

    if isinstance(p1, PList) and isinstance(p2, PList):
        if len(p1.elements) != len(p2.elements):
            return False
        return all(patterns_overlap(e1, e2) for e1, e2 in zip(p1.elements, p2.elements))

    if isinstance(p1, PCons) and isinstance(p2, PCons):
        return patterns_overlap(p1.head, p2.head) and patterns_overlap(p1.tail, p2.tail)

    if isinstance(p1, PTuple) and isinstance(p2, PTuple):
        if len(p1.elements) != len(p2.elements):
            return False
        return all(patterns_overlap(e1, e2) for e1, e2 in zip(p1.elements, p2.elements))

    if isinstance(p1, PCon) and isinstance(p2, PCon):
        if p1.name != p2.name:
            return False
        if len(p1.args) != len(p2.args):
            return False
        return all(patterns_overlap(a1, a2) for a1, a2 in zip(p1.args, p2.args))

    return False


def pattern_covers(p1: Pattern, p2: Pattern) -> bool:
    if is_wild(p1):
        return True
    if is_wild(p2):
        return False

    if isinstance(p1, PInt) and isinstance(p2, PInt):
        return p1.value == p2.value
    if isinstance(p1, PFloat) and isinstance(p2, PFloat):
        return p1.value == p2.value
    if isinstance(p1, PString) and isinstance(p2, PString):
        return p1.value == p2.value
    if isinstance(p1, PBool) and isinstance(p2, PBool):
        return p1.value == p2.value
    if isinstance(p1, PChar) and isinstance(p2, PChar):
        return p1.value == p2.value

    if isinstance(p1, PList) and isinstance(p2, PList):
        if len(p1.elements) != len(p2.elements):
            return False
        return all(pattern_covers(e1, e2) for e1, e2 in zip(p1.elements, p2.elements))

    if isinstance(p1, PCons) and isinstance(p2, PCons):
        return pattern_covers(p1.head, p2.head) and pattern_covers(p1.tail, p2.tail)

    if isinstance(p1, PTuple) and isinstance(p2, PTuple):
        if len(p1.elements) != len(p2.elements):
            return False
        return all(pattern_covers(e1, e2) for e1, e2 in zip(p1.elements, p2.elements))

    if isinstance(p1, PCon) and isinstance(p2, PCon):
        if p1.name != p2.name:
            return False
        if len(p1.args) != len(p2.args):
            return False
        return all(pattern_covers(a1, a2) for a1, a2 in zip(p1.args, p2.args))

    return False


def get_constructors_for_type(t: Type) -> list[str]:
    if isinstance(t, TBool):
        return ["True", "False"]
    if isinstance(t, TCon):
        if t.name == "Option":
            return ["Some", "None"]
        if t.name == "Result":
            return ["Ok", "Error"]
        if t.name == "Ordering":
            return ["LT", "EQ", "GT"]
    return []


def generate_missing_patterns(t: Type, covered: list[Pattern]) -> list[Pattern]:
    constructors = get_constructors_for_type(t)

    if not constructors:
        for p in covered:
            if is_wild(p):
                return []
        return [PWild()]

    missing = []
    for con in constructors:
        con_pattern = PCon(con)
        is_covered = any(pattern_covers(p, con_pattern) for p in covered)
        if not is_covered:
            missing.append(con_pattern)

    return missing


def check_exhaustiveness(
    patterns: list[Pattern], scrutinee_type: Type | None = None
) -> ExhaustivenessResult:
    if not patterns:
        return ExhaustivenessResult(
            exhaustive=False,
            missing_patterns=[PWild()],
            redundant_patterns=[],
        )

    covered: list[Pattern] = []
    redundant: list[int] = []

    for i, p in enumerate(patterns):
        is_redundant = any(pattern_covers(prev, p) for prev in covered)
        if is_redundant:
            redundant.append(i)
        else:
            covered.append(p)

    if scrutinee_type:
        missing = generate_missing_patterns(scrutinee_type, covered)
    else:
        all_wild = any(is_wild(p) for p in covered)
        if all_wild:
            missing = []
        else:
            missing = [PWild()]

    return ExhaustivenessResult(
        exhaustive=len(missing) == 0,
        missing_patterns=missing,
        redundant_patterns=redundant,
    )


def check_match_exhaustiveness(
    cases: list[ast.Pattern], scrutinee_type: Type | None = None
) -> ExhaustivenessResult:
    patterns = [convert_pattern(c) for c in cases]
    return check_exhaustiveness(patterns, scrutinee_type)


def pattern_to_string(p: Pattern) -> str:
    if isinstance(p, PWild):
        return "_"
    if isinstance(p, PVar):
        return p.name
    if isinstance(p, PInt):
        return str(p.value)
    if isinstance(p, PFloat):
        return str(p.value)
    if isinstance(p, PString):
        return f'"{p.value}"'
    if isinstance(p, PBool):
        return "True" if p.value else "False"
    if isinstance(p, PChar):
        return f"'{p.value}'"
    if isinstance(p, PList):
        elems = ", ".join(pattern_to_string(e) for e in p.elements)
        return f"[{elems}]"
    if isinstance(p, PCons):
        return f"{pattern_to_string(p.head)} :: {pattern_to_string(p.tail)}"
    if isinstance(p, PTuple):
        elems = ", ".join(pattern_to_string(e) for e in p.elements)
        return f"({elems})"
    if isinstance(p, PCon):
        if p.args:
            args_str = " ".join(pattern_to_string(a) for a in p.args)
            return f"{p.name} {args_str}"
        return p.name
    return "_"


def format_missing_patterns(patterns: list[Pattern]) -> str:
    if not patterns:
        return ""
    if len(patterns) == 1:
        return pattern_to_string(patterns[0])
    return " | ".join(pattern_to_string(p) for p in patterns)
