"""Core runtime types and functions for Pfn."""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, Union

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")


# ============ Lazy Values ============


class Lazy(Generic[T]):
    """Lazy value - evaluated only when needed."""

    def __init__(self, thunk: Callable[[], T]):
        self._thunk = thunk
        self._value: T | None = None
        self._computed = False

    def force(self) -> T:
        if not self._computed:
            self._value = self._thunk()
            self._computed = True
        return self._value  # type: ignore

    def __repr__(self) -> str:
        if self._computed:
            return f"Lazy({self._value!r})"
        return "Lazy(<thunk>)"


def lazy(thunk: Callable[[], T]) -> Lazy[T]:
    """Create a lazy value."""
    return Lazy(thunk)


# ============ Function Utilities ============


def curry(f: Callable[..., Any], n: int | None = None) -> Callable[[Any], Any]:
    """Curry a function.

    Example:
        curry(lambda x, y: x + y)(1)(2) == 3
    """
    if n is None:
        # Try to infer arity
        import inspect

        try:
            sig = inspect.signature(f)
            n = len(sig.parameters)
        except ValueError:
            n = 2

    if n <= 1:
        return f

    def curried(*args: Any) -> Any:
        def inner(arg: Any) -> Any:
            combined = args + (arg,)
            if len(combined) >= n:
                return f(*combined)
            return curry(lambda *rest: f(*(combined + rest)), n - len(combined))

        return inner

    return curried


def uncurry(f: Callable[[Any], Any]) -> Callable[[list[Any]], Any]:
    """Uncurry a curried function.

    Example:
        uncurry(lambda x: lambda y: x + y)([1, 2]) == 3
    """
    return lambda args: f(*args)


def compose(f: Callable[[B], Any], g: Callable[[A], B]) -> Callable[[A], Any]:
    """Function composition.

    Example:
        compose(lambda x: x * 2, lambda x: x + 1)(3) == 8
    """
    return lambda x: f(g(x))


def flip(f: Callable[..., Any]) -> Callable[..., Any]:
    """Flip function arguments.

    Example:
        flip(lambda x, y: x - y)(1, 2) == 1
    """
    import inspect

    sig = inspect.signature(f)
    params = list(sig.parameters.keys())
    if len(params) == 2:

        def flipped(x: Any, y: Any) -> Any:
            return f(y, x)

        return flipped
    return f


# ============ Option Type ============


class _Some(Generic[T]):
    """Some constructor for Option type."""
    __slots__ = ("value",)
    def __init__(self, value: T):
        self.value = value
    @property
    def _field0(self) -> T:
        """Alias for value, used by Pfn pattern matching."""
        return self.value
    def __repr__(self) -> str:
        return f"Some({self.value!r})"
    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Some):
            return self.value == other.value
        return False
    def __hash__(self) -> int:
        return hash(("Some", self.value))


class _None:
    """None constructor for Option type (singleton)."""

    _instance: "_None | None" = None

    def __new__(cls) -> "_None":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "None"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _None)

    def __hash__(self) -> int:
        return hash("None")


# Singleton instances
Some = _Some
None_ = _None()

Option = Union[Some[T], _None]


def is_some(opt: Option[T]) -> bool:
    """Check if Option is Some."""
    return isinstance(opt, _Some)


def is_none(opt: Option[T]) -> bool:
    """Check if Option is None."""
    return isinstance(opt, _None)


def from_some(opt: Option[T]) -> T:
    """Unwrap Some value, raises if None."""
    if isinstance(opt, _Some):
        return opt.value
    raise ValueError("Cannot unwrap None")


def from_opt(default: T, opt: Option[T]) -> T:
    """Get value from Option or default."""
    if isinstance(opt, _Some):
        return opt.value
    return default


# ============ Result Type ============


class _Ok(Generic[T]):
    """Ok constructor for Result type."""
    __slots__ = ("value",)
    def __init__(self, value: T):
        self.value = value
    @property
    def _field0(self) -> T:
        """Alias for value, used by Pfn pattern matching."""
        return self.value
    def __repr__(self) -> str:
        return f"Ok({self.value!r})"
    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Ok):
            return self.value == other.value
        return False


class _Error(Generic[T]):
    """Error constructor for Result type."""
    __slots__ = ("value",)
    def __init__(self, value: T):
        self.value = value
    @property
    def _field0(self) -> T:
        """Alias for value, used by Pfn pattern matching."""
        return self.value
    def __repr__(self) -> str:
        return f"Error({self.value!r})"
    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Error):
            return self.value == other.value
        return False


Ok = _Ok
Error = _Error

Result = Union[Ok[T], Error[Any]]


def is_ok(res: Result[T, Any]) -> bool:
    """Check if Result is Ok."""
    return isinstance(res, _Ok)


def is_error(res: Result[T, Any]) -> bool:
    """Check if Result is Error."""
    return isinstance(res, _Error)


def from_ok(res: Result[T, Any]) -> T:
    """Unwrap Ok value, raises if Error."""
    if isinstance(res, _Ok):
        return res.value
    raise ValueError(f"Cannot unwrap Error: {res.value}")


def from_error(res: Result[Any, T]) -> T:
    """Unwrap Error value, raises if Ok."""
    if isinstance(res, _Error):
        return res.value
    raise ValueError("Cannot unwrap Ok")


# ============ List Utilities ============


def foldl(f: Callable[[Any, T], Any], acc: Any, xs: list[T]) -> Any:
    """Left fold over a list."""
    for x in xs:
        acc = f(acc, x)
    return acc


def foldr(f: Callable[[T, Any], Any], acc: Any, xs: list[T]) -> Any:
    """Right fold over a list."""
    for x in reversed(xs):
        acc = f(x, acc)
    return acc


def map_(f: Callable[[T], Any], xs: list[T]) -> list[Any]:
    """Map function over list."""
    return [f(x) for x in xs]


def filter_(pred: Callable[[T], bool], xs: list[T]) -> list[T]:
    """Filter list by predicate."""
    return [x for x in xs if pred(x)]


def flat_map(f: Callable[[T], list[Any]], xs: list[T]) -> list[Any]:
    """Flat map function over list."""
    result: list[Any] = []
    for x in xs:
        result.extend(f(x))
    return result


def concat(xss: list[list[T]]) -> list[T]:
    """Concatenate list of lists."""
    result: list[T] = []
    for xs in xss:
        result.extend(xs)
    return result


def length(xs: list[Any]) -> int:
    """Get list length."""
    return len(xs)


def member(elem: Any) -> Callable[[list[Any]], bool]:
    """Check if element is in list."""
    return lambda xs: elem in xs


def head(xs: list[T]) -> Option[T]:
    """Get first element."""
    if xs:
        return Some(xs[0])
    return None_


def tail(xs: list[T]) -> Option[list[T]]:
    """Get list without first element."""
    if xs:
        return Some(xs[1:])
    return None_


def last(xs: list[T]) -> Option[T]:
    """Get last element."""
    if xs:
        return Some(xs[-1])
    return None_


def init(xs: list[T]) -> Option[list[T]]:
    """Get list without last element."""
    if xs:
        return Some(xs[:-1])
    return None_


def take(n: int, xs: list[T]) -> list[T]:
    """Take first n elements."""
    return xs[:n]


def drop(n: int, xs: list[T]) -> list[T]:
    """Drop first n elements."""
    return xs[n:]


def take_while(pred: Callable[[T], bool], xs: list[T]) -> list[T]:
    """Take elements while predicate is true."""
    result: list[T] = []
    for x in xs:
        if pred(x):
            result.append(x)
        else:
            break
    return result


def drop_while(pred: Callable[[T], bool], xs: list[T]) -> list[T]:
    """Drop elements while predicate is true."""
    for i, x in enumerate(xs):
        if not pred(x):
            return xs[i:]
    return []


def reverse(xs: list[T]) -> list[T]:
    """Reverse list."""
    return list(reversed(xs))


def append(x: T, xs: list[T]) -> list[T]:
    """Append element to list."""
    return xs + [x]


def cons(x: T, xs: list[T]) -> list[T]:
    """Prepend element to list."""
    return [x] + xs


# ============ String Utilities ============


def concat_strings(xs: list[str]) -> str:
    """Concatenate list of strings."""
    return "".join(xs)


def intersperse(sep: str, xs: list[str]) -> list[str]:
    """Intersperse separator between elements."""
    if not xs:
        return []
    result: list[str] = [xs[0]]
    for x in xs[1:]:
        result.append(sep)
        result.append(x)
    return result


def unlines(xs: list[str]) -> str:
    """Join lines with newlines."""
    return "\n".join(xs)


def unwords(xs: list[str]) -> str:
    """Join words with spaces."""
    return " ".join(xs)


# ============ Numeric Utilities ============


def id_(x: T) -> T:
    """Identity function."""
    return x


def const(x: T) -> Callable[[Any], T]:
    """Constant function."""
    return lambda _: x


def until(pred: Callable[[T], bool], f: Callable[[T], T], x: T) -> T:
    """Apply f until predicate is true."""
    while not pred(x):
        x = f(x)
    return x


def iterate(f: Callable[[T], T], x: T) -> list[T]:
    """Generate infinite list by iterating f."""
    result: list[T] = [x]
    current = x
    while True:
        current = f(current)
        result.append(current)
    return result  # Note: infinite!


# ============ Debugging Utilities ============


def trace(msg: str, x: T) -> T:
    """Debug trace - prints message and returns value."""
    print(f"TRACE: {msg} = {x!r}")
    return x


def trace_show(x: T) -> T:
    """Debug trace - shows value."""
    print(f"TRACE: {x!r}")
    return x


# ============ Prelude Exports ============


__all__ = [
    # Lazy
    "Lazy",
    "lazy",
    # Function utilities
    "curry",
    "uncurry",
    "compose",
    "flip",
    # Option
    "Some",
    "None_",
    "Option",
    "is_some",
    "is_none",
    "from_some",
    "from_opt",
    # Result
    "Ok",
    "Error",
    "Result",
    "is_ok",
    "is_error",
    "from_ok",
    "from_error",
    # List
    "foldl",
    "foldr",
    "map_",
    "filter_",
    "flat_map",
    "concat",
    "length",
    "member",
    "head",
    "tail",
    "last",
    "init",
    "take",
    "drop",
    "take_while",
    "drop_while",
    "reverse",
    "append",
    "cons",
    # String
    "concat_strings",
    "intersperse",
    "unlines",
    "unwords",
    # Generic
    "id_",
    "const",
    "until",
    "iterate",
    # Debug
    "trace",
    "trace_show",
]
