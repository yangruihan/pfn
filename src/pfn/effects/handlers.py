from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from pfn.parser import ast
from pfn.effects import Effect, EffectSet, IOEffect, StateEffect, ThrowEffect


@dataclass
class HandlerContext:
    effect_name: str
    operations: dict[str, Callable[..., Any]] = field(default_factory=dict)
    finalizer: Callable[[Any], Any] | None = None


@dataclass
class HandlerResult:
    value: Any
    remaining_effects: EffectSet


class HandlerRegistry:
    def __init__(self):
        self.handlers: dict[str, HandlerContext] = {}
        self.effect_operations: dict[str, list[str]] = {}

    def register_handler(self, name: str, ctx: HandlerContext) -> None:
        self.handlers[name] = ctx

    def register_effect_ops(self, effect_name: str, ops: list[str]) -> None:
        self.effect_operations[effect_name] = ops

    def get_handler(self, name: str) -> HandlerContext | None:
        return self.handlers.get(name)

    def get_effect_ops(self, effect_name: str) -> list[str] | None:
        return self.effect_operations.get(effect_name)


_global_registry = HandlerRegistry()


def get_handler_registry() -> HandlerRegistry:
    return _global_registry


def register_builtin_handlers() -> None:
    _global_registry.register_effect_ops(
        "IO", ["input", "print", "readFile", "writeFile"]
    )
    _global_registry.register_effect_ops("State", ["get", "put", "modify"])
    _global_registry.register_effect_ops("Throw", ["throw", "catch"])
    _global_registry.register_effect_ops("Read", ["read"])


register_builtin_handlers()


@dataclass
class HandlerBuilder:
    effect_name: str
    operations: dict[str, Callable[..., Any]] = field(default_factory=dict)
    finalizer: Callable[[Any], Any] | None = None

    def handle(
        self, op_name: str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.operations[op_name] = func
            return func

        return decorator

    def finally_(self, func: Callable[[Any], Any]) -> None:
        self.finalizer = func

    def build(self) -> HandlerContext:
        return HandlerContext(self.effect_name, self.operations, self.finalizer)

    def register(self, name: str) -> None:
        ctx = self.build()
        _global_registry.register_handler(name, ctx)


def handler(effect_name: str) -> HandlerBuilder:
    return HandlerBuilder(effect_name)


class EffectRunner:
    def __init__(self):
        self.handlers: list[HandlerContext] = []
        self.state: dict[str, Any] = {}

    def push_handler(self, ctx: HandlerContext) -> None:
        self.handlers.append(ctx)

    def pop_handler(self) -> HandlerContext | None:
        if self.handlers:
            return self.handlers.pop()
        return None

    def perform(self, effect_name: str, op_name: str, args: list[Any]) -> Any:
        for ctx in reversed(self.handlers):
            if ctx.effect_name == effect_name and op_name in ctx.operations:
                return ctx.operations[op_name](*args, resume=lambda x: x)

        raise RuntimeError(f"No handler for {effect_name}.{op_name}")

    def run(self, action: Callable[[], Any]) -> Any:
        try:
            return action()
        except Exception as e:
            for ctx in reversed(self.handlers):
                if ctx.effect_name == "Throw" and "catch" in ctx.operations:
                    return ctx.operations["catch"](e, resume=lambda x: x)
            raise


def run_with_handler(action: Callable[[], Any], ctx: HandlerContext) -> Any:
    runner = EffectRunner()
    runner.push_handler(ctx)
    return runner.run(action)


def create_handler_from_ast(decl: ast.HandlerDecl) -> HandlerContext:
    operations: dict[str, Callable[..., Any]] = {}

    for case in decl.handlers:

        def make_handler(
            body: ast.Expr, params: list[ast.Param], resume_param: str | None
        ):
            def handler_func(
                *args: Any, resume: Callable[[Any], Any] = lambda x: x
            ) -> Any:
                return resume(args[0] if args else None)

            return handler_func

        operations[case.op_name] = make_handler(
            case.body, case.params, case.resume_param
        )

    return HandlerContext(decl.effect_name, operations)
