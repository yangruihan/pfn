"""Utility functions for Pfn runtime."""

from __future__ import annotations

import sys
from typing import Any, Callable


# ============ Error Handling ============


class PfnError(Exception):
    """Base exception for Pfn runtime errors."""

    pass


class RuntimeError(PfnError):
    """Runtime error."""

    pass


class TypeError(PfnError):
    """Type error."""

    pass


class ValueError(PfnError):
    """Value error."""

    pass


class IndexError(PfnError):
    """Index error."""

    pass


class KeyError(PfnError):
    """Key error."""

    pass


# ============ Panic/Unsafe Operations ============


def panic(message: str) -> Any:
    """Panic with message (halts execution).

    This is an unsafe operation that should be avoided in production.
    """
    raise PfnError(f"PANIC: {message}")


def unreachable() -> Any:
    """Mark code as unreachable (for exhaustive pattern matching).

    This function should never be called. If it's reached, there's a bug.
    """
    raise PfnError("UNREACHABLE: This code should not be reachable")


def todo(message: str = "Not yet implemented") -> Any:
    """Mark code as TODO (not yet implemented).

    This is useful for marking incomplete features during development.
    """
    raise PfnError(f"TODO: {message}")


# ============ Debugging Utilities ============


def inspect(value: Any) -> None:
    """Inspect and print a value (debug helper).

    Args:
        value: Any value to inspect
    """
    import pprint

    pprint.pprint(value)


def typeof(value: Any) -> str:
    """Get the type name of a value.

    Args:
        value: Value to check

    Returns:
        Type name as string
    """
    return type(value).__name__


def repr_(value: Any) -> str:
    """Get string representation of value.

    Args:
        value: Value to represent

    Returns:
        String representation
    """
    return repr(value)


def str_(value: Any) -> str:
    """Get string of value.

    Args:
        value: Value to convert

    Returns:
        String
    """
    return str(value)


def print_(value: Any) -> None:
    """Print value to stdout.

    Args:
        value: Value to print
    """
    print(value)


def println(value: Any) -> None:
    """Print value with newline.

    Args:
        value: Value to print
    """
    print(value, flush=True)


# ============ Equality and Comparison ============


def eq(a: Any, b: Any) -> bool:
    """Check equality of two values.

    Args:
        a: First value
        b: Second value

    Returns:
        True if equal, False otherwise
    """
    return a == b


def neq(a: Any, b: Any) -> bool:
    """Check inequality of two values.

    Args:
        a: First value
        b: Second value

    Returns:
        True if not equal, False otherwise
    """
    return a != b


def compare(a: Any, b: Any) -> int:
    """Compare two values.

    Args:
        a: First value
        b: Second value

    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b
    """
    if a < b:
        return -1
    elif a > b:
        return 1
    return 0


# ============ Identity ============


def id(x: Any) -> Any:
    """Return the argument unchanged (identity function).

    Args:
        x: Any value

    Returns:
        The same value
    """
    return x


def const_(x: Any) -> Callable[[Any], Any]:
    """Create a constant function.

    Args:
        x: The constant value

    Returns:
        Function that always returns x
    """
    return lambda _: x


# ============ Function Application ============


def apply(f: Callable[[Any], Any], x: Any) -> Any:
    """Apply a function to a value.

    Args:
        f: Function to apply
        x: Value to apply to

    Returns:
        Result of f(x)
    """
    return f(x)


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose functions left to right.

    Args:
        *funcs: Functions to compose

    Returns:
        Composed function

    Example:
        f = pipe(lambda x: x + 1, lambda x: x * 2)
        result = f(3)  # (3 + 1) * 2 = 8
    """

    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result

    return piped


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose functions right to left.

    Args:
        *funcs: Functions to compose

    Returns:
        Composed function

    Example:
        f = compose(lambda x: x * 2, lambda x: x + 1)
        result = f(3)  # (3 + 1) * 2 = 8
    """

    def composed(x: Any) -> Any:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result

    return composed


# ============ Memoization ============


def memoize(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Memoize a function (cache results).

    Args:
        f: Function to memoize

    Returns:
        Memoized version of f
    """
    cache: dict[Any, Any] = {}

    def memoized(x: Any) -> Any:
        if x not in cache:
            cache[x] = f(x)
        return cache[x]

    return memoized


# ============ Time and Performance ============


def timeit(f: Callable[[], Any]) -> tuple[Any, float]:
    """Time the execution of a function.

    Args:
        f: Function to time

    Returns:
        Tuple of (result, elapsed_time_seconds)
    """
    import time

    start = time.perf_counter()
    result = f()
    elapsed = time.perf_counter() - start
    return result, elapsed


def measure(f: Callable[[], Any]) -> float:
    """Measure execution time of a function.

    Args:
        f: Function to measure

    Returns:
        Elapsed time in seconds
    """
    import time

    start = time.perf_counter()
    f()
    return time.perf_counter() - start


# ============ I/O Utilities ============


def read_file(path: str) -> str:
    """Read entire file into string.

    Args:
        path: Path to file

    Returns:
        File contents as string
    """
    with open(path, "r") as f:
        return f.read()


def write_file(path: str, contents: str) -> None:
    """Write string to file.

    Args:
        path: Path to file
        contents: Contents to write
    """
    with open(path, "w") as f:
        f.write(contents)


def read_lines(path: str) -> list[str]:
    """Read file as list of lines.

    Args:
        path: Path to file

    Returns:
        List of lines (with newlines removed)
    """
    with open(path, "r") as f:
        return f.read().splitlines()


def write_lines(path: str, lines: list[str]) -> None:
    """Write list of lines to file.

    Args:
        path: Path to file
        lines: Lines to write (newlines added automatically)
    """
    with open(path, "w") as f:
        f.write("\n".join(lines))


# ============ System Utilities ============


def exit(code: int = 0) -> None:
    """Exit the program.

    Args:
        code: Exit code
    """
    sys.exit(code)


def get_env(name: str) -> str | None:
    """Get environment variable.

    Args:
        name: Variable name

    Returns:
        Variable value or None if not set
    """
    return __builtins__.get("__builtins__", {}).get("__dict__", {}).get(name)  # type: ignore


def set_env(name: str, value: str) -> None:
    """Set environment variable.

    Args:
        name: Variable name
        value: Variable value
    """
    import os

    os.environ[name] = value


# ============ Prelude Exports ============


__all__ = [
    # Errors
    "PfnError",
    "RuntimeError",
    "TypeError",
    "ValueError",
    "IndexError",
    "KeyError",
    # Unsafe
    "panic",
    "unreachable",
    "todo",
    # Debug
    "inspect",
    "typeof",
    "repr_",
    "str_",
    "print_",
    "println",
    # Equality
    "eq",
    "neq",
    "compare",
    # Identity
    "id",
    "const_",
    # Function
    "apply",
    "pipe",
    "compose",
    "memoize",
    # Time
    "timeit",
    "measure",
    # I/O
    "read_file",
    "write_file",
    "read_lines",
    "write_lines",
    # System
    "exit",
    "get_env",
    "set_env",
]
