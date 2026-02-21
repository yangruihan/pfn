"""Effect system for tracking side effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Effect:
    pass


@dataclass(frozen=True)
class IOEffect(Effect):
    pass


@dataclass(frozen=True)
class StateEffect(Effect):
    state_type: Any


@dataclass(frozen=True)
class ThrowEffect(Effect):
    error_type: Any


@dataclass(frozen=True)
class ReadEffect(Effect):
    pass


@dataclass(frozen=True)
class EffectSet:
    effects: frozenset[Effect] = field(default_factory=frozenset)

    def __str__(self) -> str:
        if not self.effects:
            return "Pure"
        return " | ".join(str(e) for e in self.effects)

    def union(self, other: EffectSet) -> EffectSet:
        return EffectSet(self.effects | other.effects)

    def contains(self, effect: Effect) -> bool:
        return effect in self.effects


PURE = EffectSet()


class EffectHandler:
    def handle(self, op: str, args: list[Any], continuation: Any) -> Any:
        raise NotImplementedError


class IOHandler(EffectHandler):
    def __init__(
        self,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[Any], None] = print,
    ):
        self.input_func = input_func
        self.output_func = output_func

    def handle(self, op: str, args: list[Any], continuation: Any) -> Any:
        if op == "input":
            result = self.input_func(args[0])
            return continuation(result)
        if op == "print":
            self.output_func(args[0])
            return continuation(None)
        if op == "readFile":
            with open(args[0], "r") as f:
                content = f.read()
            return continuation(content)
        if op == "writeFile":
            with open(args[0], "w") as f:
                f.write(args[1])
            return continuation(None)
        raise ValueError(f"Unknown IO operation: {op}")


class StateHandler(EffectHandler):
    def __init__(self, initial_state: Any):
        self.state = initial_state

    def handle(self, op: str, args: list[Any], continuation: Any) -> Any:
        if op == "get":
            return continuation(self.state)
        if op == "put":
            self.state = args[0]
            return continuation(None)
        if op == "modify":
            self.state = args[0](self.state)
            return continuation(None)
        raise ValueError(f"Unknown State operation: {op}")


class ThrowHandler(EffectHandler):
    def __init__(self):
        self.exception: Any = None
        self.has_exception = False

    def handle(self, op: str, args: list[Any], continuation: Any) -> Any:
        if op == "throw":
            self.has_exception = True
            self.exception = args[0]
            return None
        raise ValueError(f"Unknown Throw operation: {op}")


def run_io(action: Any, handler: IOHandler | None = None) -> Any:
    if handler is None:
        handler = IOHandler()
    return action()


def run_state(action: Any, initial_state: Any) -> tuple[Any, Any]:
    handler = StateHandler(initial_state)
    result = action()
    return result, handler.state


def run_throw(action: Any) -> Any:
    handler = ThrowHandler()
    try:
        return action()
    except Exception as e:
        handler.has_exception = True
        handler.exception = e
        return handler.exception
