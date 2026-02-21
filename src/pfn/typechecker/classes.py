from __future__ import annotations

from dataclasses import dataclass, field
from pfn.types import Type, TVar


@dataclass
class ClassContext:
    classes: dict[str, ClassInfo] = field(default_factory=dict)
    instances: dict[tuple[str, str], InstanceInfo] = field(default_factory=dict)

    def add_class(self, name: str, params: list[str], methods: dict[str, Type]) -> None:
        self.classes[name] = ClassInfo(name, params, methods)

    def add_instance(
        self, class_name: str, type_name: str, methods: dict[str, Type]
    ) -> None:
        self.instances[(class_name, type_name)] = InstanceInfo(
            class_name, type_name, methods
        )

    def lookup_instance(self, class_name: str, type_name: str) -> InstanceInfo | None:
        return self.instances.get((class_name, type_name))

    def get_method(
        self, class_name: str, type_name: str, method_name: str
    ) -> Type | None:
        inst = self.lookup_instance(class_name, type_name)
        if inst:
            return inst.methods.get(method_name)
        return None


@dataclass
class ClassInfo:
    name: str
    params: list[str]
    methods: dict[str, Type]


@dataclass
class InstanceInfo:
    class_name: str
    type_name: str
    methods: dict[str, Type]


DEFAULT_CLASSES = ClassContext()


DEFAULT_CLASSES.add_class(
    "Eq",
    ["a"],
    {
        "eq": TVar("a"),
    },
)


DEFAULT_CLASSES.add_class(
    "Ord",
    ["a"],
    {
        "compare": TVar("a"),
    },
)


DEFAULT_CLASSES.add_class(
    "Show",
    ["a"],
    {
        "show": TVar("a"),
    },
)


DEFAULT_CLASSES.add_class(
    "Functor",
    ["f"],
    {
        "fmap": TVar("f"),
    },
)


DEFAULT_CLASSES.add_class(
    "Monad",
    ["m"],
    {
        "return": TVar("m"),
        "bind": TVar("m"),
    },
)


def get_default_context() -> ClassContext:
    return DEFAULT_CLASSES


def resolve_instance(
    ctx: ClassContext, class_name: str, type_name: str
) -> InstanceInfo | None:
    return ctx.lookup_instance(class_name, type_name)
