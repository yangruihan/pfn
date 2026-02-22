from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pfn.types import Type, TRowPoly, Subst


@dataclass(frozen=True)
class Row:
    fields: dict[str, Type]
    rest: str | None = None


def row_empty() -> Row:
    return Row({})


def row_extend(row: Row, label: str, t: Type) -> Row:
    new_fields = dict(row.fields)
    new_fields[label] = t
    return Row(new_fields, row.rest)


def row_restrict(row: Row, label: str) -> Row:
    new_fields = dict(row.fields)
    if label in new_fields:
        del new_fields[label]
    return Row(new_fields, row.rest)


def row_has_field(row: Row, label: str) -> bool:
    return label in row.fields


def row_get_field(row: Row, label: str) -> Type | None:
    return row.fields.get(label)


def row_labels(row: Row) -> set[str]:
    return set(row.fields.keys())


def row_to_trowpoly(row: Row) -> TRowPoly:
    from pfn.types import TRowPoly

    return TRowPoly(row.fields, row.rest)


def trowpoly_to_row(t: TRowPoly) -> Row:
    return Row(t.fields, t.rest)


def unify_rows(r1: Row, r2: Row, subst: Subst) -> Subst | None:
    from pfn.types import Subst

    common_labels = row_labels(r1) & row_labels(r2)

    for label in common_labels:
        t1 = row_get_field(r1, label)
        t2 = row_get_field(r2, label)
        if t1 is not None and t2 is not None:
            result = subst.unify(t1, t2)
            if result is None:
                return None
            subst = result.compose(subst)

    r1_only = row_labels(r1) - common_labels
    r2_only = row_labels(r2) - common_labels

    if r1.rest is None and r2.rest is None:
        if r1_only or r2_only:
            return None
        return subst

    if r1.rest is not None and r2.rest is None:
        if r1_only:
            return None
        r2_extended = Row({}, r1.rest)
        for label in r2_only:
            r2_extended = row_extend(r2_extended, label, row_get_field(r2, label))
        return subst

    if r1.rest is None and r2.rest is not None:
        if r2_only:
            return None
        r1_extended = Row({}, r2.rest)
        for label in r1_only:
            r1_extended = row_extend(r1_extended, label, row_get_field(r1, label))
        return subst

    if r1.rest == r2.rest:
        return subst

    r1_rest = Row({label: row_get_field(r1, label) for label in r1_only}, r1.rest)
    r2_rest = Row({label: row_get_field(r2, label) for label in r2_only}, r2.rest)

    if r1.rest is not None:
        subst = Subst({r1.rest: row_to_trowpoly(r2_rest)})
    elif r2.rest is not None:
        subst = Subst({r2.rest: row_to_trowpoly(r1_rest)})

    return subst


def rewrite_row(row: Row, subst: Subst) -> Row:
    new_fields = {}
    for label, t in row.fields.items():
        new_fields[label] = subst.apply(t)

    new_rest = row.rest
    if row.rest and row.rest in subst.mapping:
        rest_type = subst.mapping[row.rest]
        if hasattr(rest_type, "fields"):
            for label, t in rest_type.fields.items():
                if label not in new_fields:
                    new_fields[label] = t
            new_rest = getattr(rest_type, "rest", None)

    return Row(new_fields, new_rest)


def row_free_vars(row: Row, subst: Subst) -> set[str]:
    result: set[str] = set()
    for t in row.fields.values():
        result |= subst.free_vars(t)
    if row.rest:
        result.add(row.rest)
    return result


def row_substitute(row: Row, subst: Subst) -> Row:
    new_fields = {}
    for label, t in row.fields.items():
        new_fields[label] = subst.apply(t)

    new_rest = row.rest
    if row.rest and row.rest in subst.mapping:
        rest_type = subst.mapping[row.rest]
        if hasattr(rest_type, "fields"):
            for label, t in rest_type.fields.items():
                if label not in new_fields:
                    new_fields[label] = t
            new_rest = getattr(rest_type, "rest", None)

    return Row(new_fields, new_rest)
