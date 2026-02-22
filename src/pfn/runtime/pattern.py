"""Pattern matching utilities for Pfn runtime."""

from __future__ import annotations

from typing import Any, Callable


class MatchError(Exception):
    """Raised when no pattern matches."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"No pattern matched for {value!r}")


# ============ Pattern Matching Core ============


def match(value: Any, *cases: tuple[Any, Callable[[], Any]]) -> Any:
    """Match value against patterns.

    Args:
        value: The value to match
        *cases: Pairs of (pattern, result) or (pattern, callable)

    Returns:
        Result of the first matching pattern

    Example:
        def case1(): return "one"
        def case2(): return "other"
        result = match(x, (1, case1), (_, case2))
    """
    for pattern, result in cases:
        if _try_match(pattern, value):
            if callable(result):
                return result()
            return result
    raise MatchError(value)


def _try_match(pattern: Any, value: Any) -> bool:
    """Try to match pattern against value."""
    # Wildcard
    if pattern is None or pattern == "_" or pattern == ...:
        return True

    # Type-based matching
    if pattern is int:
        return isinstance(value, int)
    if pattern is float:
        return isinstance(value, float)
    if pattern is str:
        return isinstance(value, str)
    if pattern is bool:
        return isinstance(value, bool)
    if pattern is list:
        return isinstance(value, list)
    if pattern is dict:
        return isinstance(value, dict)
    if pattern is tuple:
        return isinstance(value, tuple)

    # Exact match
    return pattern == value


# ============ Case Expression ============


class Case:
    """Case expression for pattern matching."""

    def __init__(self, value: Any):
        self._value = value
        self._cases: list[tuple[Any, Callable[[], Any]]] = []

    def case(self, pattern: Any, result: Any) -> "Case":
        """Add a case to the case expression."""
        self._cases.append((pattern, result if callable(result) else lambda: result))
        return self

    def case_(self, pattern: Any, func: Callable[[], Any]) -> "Case":
        """Add a case with a callable result."""
        self._cases.append((pattern, func))
        return self

    def otherwise(self, result: Any) -> "Case":
        """Add default case."""
        return self.case(None, result)

    def run(self) -> Any:
        """Execute the case expression."""
        return match(self._value, *self._cases)


def case(value: Any) -> Case:
    """Create a case expression."""
    return Case(value)


# ============ Guards ============


def guard(condition: bool, message: str = "Guard failed") -> None:
    """Guard expression - raises if condition is False."""
    if not condition:
        raise MatchError(message)


# ============ Record Pattern Matching ============


def match_record(
    record: dict[str, Any], *patterns: tuple[set[str], dict[str, Any]]
) -> dict[str, Any] | None:
    """Match record against field patterns.

    Args:
        record: The record (dict) to match
        *patterns: Pairs of (required_fields, capture_dict)

    Returns:
        Capture dict if matched, None otherwise

    Example:
        result = match_record(
            {"name": "Alice", "age": 30},
            ({"name"}, {"name": name}),
            ({"age"}, {"age": age})
        )
    """
    for required_fields, capture in patterns:
        if required_fields.issubset(record.keys()):
            # Create capture dict with matched values
            result = {}
            for field, value in capture.items():
                if callable(value):
                    result[field] = value(record[field])
                elif isinstance(value, str) and value.startswith("$"):
                    # Capture variable
                    var_name = value[1:]
                    result[var_name] = record[field]
                else:
                    # Check expected value
                    if field not in record or record[field] != value:
                        break
            else:
                return result
    return None


# ============ Sum Type Pattern Matching ============


def match_sum_type(value: Any, *cases: tuple[type | str, Callable[[Any], Any]]) -> Any:
    """Match against a sum type (algebraic data type).

    Args:
        value: The value to match (must have __class__ attribute)
        *cases: Pairs of (constructor, handler)

    Returns:
        Result of the matching handler

    Example:
        # For Option type
        result = match_sum_type(
            some_value,
            (Some, lambda v: f"Got {v}"),
            (None_, lambda: "Got nothing")
        )
    """
    constructor = type(value)

    for pattern, handler in cases:
        if pattern is constructor or pattern == constructor.__name__:
            if callable(handler):
                return handler(value)
            return handler

    raise MatchError(value)


# ============ List Pattern Matching ============


def match_list(
    lst: list[Any],
    *cases: tuple[tuple[int | None, Callable[[list[Any]], Any]],],
) -> Any:
    """Match against list patterns.

    Args:
        lst: The list to match
        *cases: Pairs of (length_or_pattern, handler)

    Returns:
        Result of the matching handler

    Example:
        result = match_list(
            [1, 2, 3],
            (0, lambda: "empty"),
            (1, lambda xs: f"one: {xs[0]}"),
            (None, lambda xs: f"many: {len(xs)}")
        )
    """
    length = len(lst)

    for pattern, handler in cases:
        if pattern is None:
            # Match any non-empty
            if length > 0:
                return handler(lst)
        elif isinstance(pattern, int):
            if length == pattern:
                return handler(lst)

    raise MatchError(lst)


# ============ Tuple Pattern Matching ============


def match_tuple(
    tup: tuple[Any, ...],
    *cases: tuple[tuple[int, Callable[[tuple[Any, ...]], Any]]],
) -> Any:
    """Match against tuple patterns.

    Args:
        tup: The tuple to match
        *cases: Pairs of (arity, handler)

    Returns:
        Result of the matching handler
    """
    length = len(tup)

    for pattern, handler in cases:
        if isinstance(pattern, int) and length == pattern:
            return handler(tup)

    raise MatchError(tup)


# ============ Alternative Matching ============


def alt(*matchers: Callable[[], Any]) -> Callable[[], Any]:
    """Try multiple matchers in order, return first success.

    Example:
        result = alt(
            lambda: match1(),
            lambda: match2(),
            lambda: default
        )()
    """
    for matcher in matchers:
        try:
            return matcher()
        except (MatchError, ValueError):
            continue
    raise MatchError("All alternatives failed")


# ============ Optional Matching ============


def maybe(value: Any, *cases: tuple[bool, Any]) -> Any:
    """Match with optional patterns.

    Example:
        result = maybe(
            some_value,
            (True, "truthy"),
            (False, "falsy")
        )
    """
    truthy = bool(value)
    for pattern, result in cases:
        if pattern == truthy:
            return result
    return None


# ============ Prelude Exports ============


__all__ = [
    "MatchError",
    "match",
    "Case",
    "case",
    "guard",
    "match_record",
    "match_sum_type",
    "match_list",
    "match_tuple",
    "alt",
    "maybe",
]
