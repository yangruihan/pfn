"""Builtin type implementations for Pfn runtime."""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# ============ Tuple ============


def tuple_first(t: tuple[Any, ...]) -> Any:
    """Get first element of tuple."""
    return t[0] if t else None


def tuple_second(t: tuple[Any, ...]) -> Any:
    """Get second element of tuple."""
    return t[1] if len(t) > 1 else None


def tuple_rest(t: tuple[Any, ...]) -> tuple[Any, ...]:
    """Get tuple without first element."""
    return t[1:] if t else ()


def tuple_len(t: tuple[Any, ...]) -> int:
    """Get tuple length."""
    return len(t)


# ============ Dictionary/Map ============


class Dict(Generic[K, V]):
    """Dictionary wrapper with functional operations."""

    def __init__(self, data: dict[K, V] | None = None):
        self._data: dict[K, V] = data.copy() if data else {}

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get value by key."""
        return self._data.get(key, default)

    def set(self, key: K, value: V) -> Dict[K, V]:
        """Return new dict with key set."""
        new_data = self._data.copy()
        new_data[key] = value
        return Dict(new_data)

    def delete(self, key: K) -> Dict[K, V]:
        """Return new dict with key deleted."""
        new_data = self._data.copy()
        if key in new_data:
            del new_data[key]
        return Dict(new_data)

    def contains(self, key: K) -> bool:
        """Check if key exists."""
        return key in self._data

    def keys(self) -> list[K]:
        """Get all keys."""
        return list(self._data.keys())

    def values(self) -> list[V]:
        """Get all values."""
        return list(self._data.values())

    def items(self) -> list[tuple[K, V]]:
        """Get all key-value pairs."""
        return list(self._data.items())

    def to_dict(self) -> dict[K, V]:
        """Convert to plain dict."""
        return self._data.copy()

    def map(self, f: Callable[[K, V], tuple[K, V]]) -> Dict[K, V]:
        """Map over key-value pairs."""
        new_data = dict(f(k, v) for k, v in self._data.items())
        return Dict(new_data)

    def filter(self, pred: Callable[[K, V], bool]) -> Dict[K, V]:
        """Filter by predicate."""
        new_data = {k: v for k, v in self._data.items() if pred(k, v)}
        return Dict(new_data)

    def fold(self, acc: Any, f: Callable[[Any, K, V], Any]) -> Any:
        """Fold over entries."""
        result = acc
        for k, v in self._data.items():
            result = f(result, k, v)
        return result

    def __repr__(self) -> str:
        return f"Dict({self._data!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dict):
            return self._data == other._data
        return False

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __setitem__(self, key: K, value: V) -> None:
        self._data[key] = value


# ============ Set ============


class Set(Generic[T]):
    """Set wrapper with functional operations."""

    def __init__(self, data: set[T] | None = None):
        self._data: set[T] = data.copy() if data else set()

    def contains(self, elem: T) -> bool:
        """Check if element exists."""
        return elem in self._data

    def add(self, elem: T) -> Set[T]:
        """Return new set with element added."""
        new_data = self._data.copy()
        new_data.add(elem)
        return Set(new_data)

    def remove(self, elem: T) -> Set[T]:
        """Return new set with element removed."""
        new_data = self._data.copy()
        new_data.discard(elem)
        return Set(new_data)

    def union(self, other: Set[T]) -> Set[T]:
        """Union of two sets."""
        return Set(self._data | other._data)

    def intersection(self, other: Set[T]) -> Set[T]:
        """Intersection of two sets."""
        return Set(self._data & other._data)

    def difference(self, other: Set[T]) -> Set[T]:
        """Difference of two sets."""
        return Set(self._data - other._data)

    def to_list(self) -> list[T]:
        """Convert to list."""
        return list(self._data)

    def to_set(self) -> set[T]:
        """Convert to plain set."""
        return self._data.copy()

    def __repr__(self) -> str:
        return f"Set({self._data!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Set):
            return self._data == other._data
        return False

    def __len__(self) -> int:
        return len(self._data)


# ============ String Extensions ============


def string_len(s: str) -> int:
    """Get string length."""
    return len(s)


def string_is_empty(s: str) -> bool:
    """Check if string is empty."""
    return len(s) == 0


def string_head(s: str) -> str:
    """Get first character."""
    return s[0] if s else ""


def string_tail(s: str) -> str:
    """Get string without first character."""
    return s[1:] if s else ""


def string_append(s1: str, s2: str) -> str:
    """Append two strings."""
    return s1 + s2


def string_split(sep: str, s: str) -> list[str]:
    """Split string by separator."""
    return s.split(sep)


def string_join(sep: str, xs: list[str]) -> str:
    """Join strings with separator."""
    return sep.join(xs)


def string_trim(s: str) -> str:
    """Trim whitespace from string."""
    return s.strip()


def string_to_int(s: str) -> int:
    """Parse string to int."""
    return int(s)


def string_to_float(s: str) -> float:
    """Parse string to float."""
    return float(s)


def string_from_int(n: int) -> str:
    """Convert int to string."""
    return str(n)


def string_from_float(n: float) -> str:
    """Convert float to string."""
    return str(n)


def string_contains(sub: str, s: str) -> bool:
    """Check if substring contains."""
    return sub in s


def string_starts_with(prefix: str, s: str) -> bool:
    """Check if string starts with prefix."""
    return s.startswith(prefix)


def string_ends_with(suffix: str, s: str) -> bool:
    """Check if string ends with suffix."""
    return s.endswith(suffix)


def string_replace(old: str, new: str, s: str) -> str:
    """Replace substring."""
    return s.replace(old, new)


def string_to_upper(s: str) -> str:
    """Convert to uppercase."""
    return s.upper()


def string_to_lower(s: str) -> str:
    """Convert to lowercase."""
    return s.lower()


# ============ Numeric Extensions ============


def int_to_string(n: int) -> str:
    """Convert int to string."""
    return str(n)


def float_to_string(n: float) -> str:
    """Convert float to string."""
    return str(n)


def int_to_float(n: int) -> float:
    """Convert int to float."""
    return float(n)


def float_to_int(n: float) -> int:
    """Convert float to int (truncates)."""
    return int(n)


def int_abs(n: int) -> int:
    """Absolute value."""
    return abs(n)


def int_max(a: int, b: int) -> int:
    """Maximum of two ints."""
    return max(a, b)


def int_min(a: int, b: int) -> int:
    """Minimum of two ints."""
    return min(a, b)


def int_mod(a: int, b: int) -> int:
    """Modulo operation."""
    return a % b


def int_pow(base: int, exp: int) -> int:
    """Power operation."""
    return base**exp


def float_abs(n: float) -> float:
    """Absolute value."""
    return abs(n)


def float_max(a: float, b: float) -> float:
    """Maximum of two floats."""
    return max(a, b)


def float_min(a: float, b: float) -> float:
    """Minimum of two floats."""
    return min(a, b)


def float_pow(base: float, exp: float) -> float:
    """Power operation."""
    return base**exp


def float_sqrt(n: float) -> float:
    """Square root."""
    return n**0.5


def float_ceil(n: float) -> int:
    """Ceiling."""
    import math

    return math.ceil(n)


def float_floor(n: float) -> int:
    """Floor."""
    import math

    return math.floor(n)


def float_round(n: float) -> int:
    """Round."""
    return round(n)


# ============ Boolean Extensions ============


def bool_to_string(b: bool) -> str:
    """Convert bool to string."""
    return "True" if b else "False"


def bool_not(b: bool) -> bool:
    """Logical not."""
    return not b


def bool_and(a: bool, b: bool) -> bool:
    """Logical and."""
    return a and b


def bool_or(a: bool, b: bool) -> bool:
    """Logical or."""
    return a or b


# ============ Conversion Functions ============


def to_string(x: Any) -> str:
    """Generic to string conversion."""
    return str(x)


def to_int(x: Any) -> int:
    """Generic to int conversion."""
    return int(x)


def to_float(x: Any) -> float:
    """Generic to float conversion."""
    return float(x)


def to_bool(x: Any) -> bool:
    """Generic to bool conversion."""
    return bool(x)


# ============ Prelude Exports ============


__all__ = [
    # Tuple
    "tuple_first",
    "tuple_second",
    "tuple_rest",
    "tuple_len",
    # Dict
    "Dict",
    # Set
    "Set",
    # String
    "string_len",
    "string_is_empty",
    "string_head",
    "string_tail",
    "string_append",
    "string_split",
    "string_join",
    "string_trim",
    "string_to_int",
    "string_to_float",
    "string_from_int",
    "string_from_float",
    "string_contains",
    "string_starts_with",
    "string_ends_with",
    "string_replace",
    "string_to_upper",
    "string_to_lower",
    # Numeric
    "int_to_string",
    "float_to_string",
    "int_to_float",
    "float_to_int",
    "int_abs",
    "int_max",
    "int_min",
    "int_mod",
    "int_pow",
    "float_abs",
    "float_max",
    "float_min",
    "float_pow",
    "float_sqrt",
    "float_ceil",
    "float_floor",
    "float_round",
    # Boolean
    "bool_to_string",
    "bool_not",
    "bool_and",
    "bool_or",
    # Conversion
    "to_string",
    "to_int",
    "to_float",
    "to_bool",
]
