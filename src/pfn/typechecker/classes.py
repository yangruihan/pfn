from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any
from pfn.types import (
    Type,
    TVar,
    TFun,
    TCon,
    TConstraint,
    TQualified,
    Scheme,
    Subst,
)


@dataclass
class ClassInfo:
    """Type class definition with methods, superclasses, and default implementations."""

    name: str
    params: tuple[str, ...]
    methods: dict[str, Type]
    superclasses: tuple[str, ...] = ()
    defaults: dict[str, Callable[..., Any]] = field(default_factory=dict)

    def __str__(self) -> str:
        params_str = " ".join(self.params)
        methods_str = ", ".join(f"{k}: {v}" for k, v in self.methods.items())
        if self.superclasses:
            supers_str = ", ".join(self.superclasses)
            return f"interface {self.name} {params_str} extends {supers_str} where {methods_str}"
        return f"interface {self.name} {params_str} where {methods_str}"


@dataclass
class InstanceInfo:
    """Type class instance with methods and constraints."""

    class_name: str
    type_: Type
    methods: dict[str, Any]
    constraints: tuple[TConstraint, ...] = ()

    def __str__(self) -> str:
        if self.constraints:
            cs = ", ".join(str(c) for c in self.constraints)
            return f"impl {cs} => {self.class_name} {self.type_}"
        return f"impl {self.class_name} {self.type_}"


@dataclass
class ClassContext:
    """Type class context holding class definitions and instances."""

    classes: dict[str, ClassInfo] = field(default_factory=dict)
    instances: dict[tuple[str, str], InstanceInfo] = field(default_factory=dict)

    def add_class(
        self,
        name: str,
        params: list[str] | tuple[str, ...],
        methods: dict[str, Type],
        superclasses: list[str] | tuple[str, ...] = (),
        defaults: dict[str, Callable[..., Any]] | None = None,
    ) -> None:
        """Add a type class definition."""
        self.classes[name] = ClassInfo(
            name=name,
            params=tuple(params) if isinstance(params, list) else params,
            methods=methods,
            superclasses=tuple(superclasses)
            if isinstance(superclasses, list)
            else superclasses,
            defaults=defaults or {},
        )

    def add_instance(
        self,
        class_name: str,
        type_: Type,
        methods: dict[str, Any],
        constraints: tuple[TConstraint, ...] = (),
    ) -> None:
        """Add a type class instance."""
        type_key = self._type_key(type_)
        self.instances[(class_name, type_key)] = InstanceInfo(
            class_name=class_name,
            type_=type_,
            methods=methods,
            constraints=constraints,
        )

    def _type_key(self, t: Type) -> str:
        """Generate a string key for a type for instance lookup."""
        if isinstance(t, TVar):
            return f"var:{t.name}"
        if isinstance(t, TCon):
            if t.args:
                args_str = ",".join(self._type_key(a) for a in t.args)
                return f"{t.name}[{args_str}]"
            return t.name
        return str(t)

    def lookup_class(self, name: str) -> ClassInfo | None:
        """Look up a type class by name."""
        return self.classes.get(name)

    def lookup_instance(self, class_name: str, type_: Type) -> InstanceInfo | None:
        """Look up an instance by class name and type."""
        type_key = self._type_key(type_)
        return self.instances.get((class_name, type_key))

    def get_method(self, class_name: str, type_: Type, method_name: str) -> Any | None:
        """Get a method implementation from an instance."""
        inst = self.lookup_instance(class_name, type_)
        if inst:
            return inst.methods.get(method_name)
        # Check for default method
        cls = self.lookup_class(class_name)
        if cls and method_name in cls.defaults:
            return cls.defaults[method_name]
        return None

    def get_method_type(self, class_name: str, method_name: str) -> Type | None:
        """Get the type signature of a method from a type class."""
        cls = self.lookup_class(class_name)
        if cls:
            return cls.methods.get(method_name)
        return None

    def check_superclasses(self, class_name: str) -> bool:
        """Check that all superclasses of a class are defined."""
        cls = self.lookup_class(class_name)
        if not cls:
            return False
        for super_name in cls.superclasses:
            if super_name not in self.classes:
                return False
        return True

    def get_all_superclasses(self, class_name: str) -> set[str]:
        """Get all superclasses transitively."""
        result: set[str] = set()
        cls = self.lookup_class(class_name)
        if not cls:
            return result
        for super_name in cls.superclasses:
            result.add(super_name)
            result |= self.get_all_superclasses(super_name)
        return result


def create_default_context() -> ClassContext:
    """Create a context with standard type classes."""
    ctx = ClassContext()

    # Eq class
    ctx.add_class(
        "Eq",
        ["a"],
        {
            "eq": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
            "neq": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
        },
    )

    # Ord class (extends Eq)
    ctx.add_class(
        "Ord",
        ["a"],
        {
            "compare": TFun(TVar("a"), TFun(TVar("a"), TCon("Ordering"))),
            "lt": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
            "gt": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
            "le": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
            "ge": TFun(TVar("a"), TFun(TVar("a"), TCon("Bool"))),
        },
        superclasses=["Eq"],
    )

    # Show class
    ctx.add_class(
        "Show",
        ["a"],
        {
            "show": TFun(TVar("a"), TCon("String")),
        },
    )

    # Read class
    ctx.add_class(
        "Read",
        ["a"],
        {
            "read": TFun(TCon("String"), TVar("a")),
        },
    )

    # Num class
    ctx.add_class(
        "Num",
        ["a"],
        {
            "add": TFun(TVar("a"), TFun(TVar("a"), TVar("a"))),
            "sub": TFun(TVar("a"), TFun(TVar("a"), TVar("a"))),
            "mul": TFun(TVar("a"), TFun(TVar("a"), TVar("a"))),
            "negate": TFun(TVar("a"), TVar("a")),
            "zero": TVar("a"),
        },
    )

    # Fractional class (extends Num)
    ctx.add_class(
        "Fractional",
        ["a"],
        {
            "div": TFun(TVar("a"), TFun(TVar("a"), TVar("a"))),
            "recip": TFun(TVar("a"), TVar("a")),
            "one": TVar("a"),
        },
        superclasses=["Num"],
    )

    # Functor class (higher-kinded)
    ctx.add_class(
        "Functor",
        ["f"],
        {
            "fmap": TFun(
                TFun(TVar("a"), TVar("b")),
                TFun(TCon("f", (TVar("a"),)), TCon("f", (TVar("b"),))),
            ),
        },
    )

    # Applicative class (extends Functor)
    ctx.add_class(
        "Applicative",
        ["f"],
        {
            "pure": TFun(TVar("a"), TCon("f", (TVar("a"),))),
            "ap": TFun(
                TCon("f", (TFun(TVar("a"), TVar("b")),)),
                TFun(TCon("f", (TVar("a"),)), TCon("f", (TVar("b"),))),
            ),
        },
        superclasses=["Functor"],
    )

    # Monad class (extends Applicative)
    ctx.add_class(
        "Monad",
        ["m"],
        {
            "return": TFun(TVar("a"), TCon("m", (TVar("a"),))),
            "bind": TFun(
                TCon("m", (TVar("a"),)),
                TFun(TFun(TVar("a"), TCon("m", (TVar("b"),))), TCon("m", (TVar("b"),))),
            ),
        },
        superclasses=["Applicative"],
    )

    # Foldable class
    ctx.add_class(
        "Foldable",
        ["t"],
        {
            "foldl": TFun(
                TFun(TVar("b"), TFun(TVar("a"), TVar("b"))),
                TFun(TVar("b"), TFun(TCon("t", (TVar("a"),)), TVar("b"))),
            ),
            "foldr": TFun(
                TFun(TVar("a"), TFun(TVar("b"), TVar("b"))),
                TFun(TVar("b"), TFun(TCon("t", (TVar("a"),)), TVar("b"))),
            ),
        },
    )

    # Traversable class (extends Functor and Foldable)
    ctx.add_class(
        "Traversable",
        ["t"],
        {
            "traverse": TFun(
                TFun(TVar("a"), TCon("f", (TVar("b"),))),
                TFun(TCon("t", (TVar("a"),)), TCon("f", (TCon("t", (TVar("b"),)),))),
            ),
        },
        superclasses=["Functor", "Foldable"],
    )

    # Semigroup class
    ctx.add_class(
        "Semigroup",
        ["a"],
        {
            "append": TFun(TVar("a"), TFun(TVar("a"), TVar("a"))),
        },
    )

    # Monoid class (extends Semigroup)
    ctx.add_class(
        "Monoid",
        ["a"],
        {
            "empty": TVar("a"),
        },
        superclasses=["Semigroup"],
    )

    # Add built-in instances
    _add_builtin_instances(ctx)

    return ctx


def _add_builtin_instances(ctx: ClassContext) -> None:
    """Add built-in instances for primitive types."""

    # Eq Int
    ctx.add_instance(
        "Eq",
        TCon("Int"),
        {
            "eq": lambda x, y: x == y,
            "neq": lambda x, y: x != y,
        },
    )

    # Eq Float
    ctx.add_instance(
        "Eq",
        TCon("Float"),
        {
            "eq": lambda x, y: x == y,
            "neq": lambda x, y: x != y,
        },
    )

    # Eq Bool
    ctx.add_instance(
        "Eq",
        TCon("Bool"),
        {
            "eq": lambda x, y: x == y,
            "neq": lambda x, y: x != y,
        },
    )

    # Eq String
    ctx.add_instance(
        "Eq",
        TCon("String"),
        {
            "eq": lambda x, y: x == y,
            "neq": lambda x, y: x != y,
        },
    )

    # Show Int
    ctx.add_instance(
        "Show",
        TCon("Int"),
        {"show": lambda x: str(x)},
    )

    # Show Float
    ctx.add_instance(
        "Show",
        TCon("Float"),
        {"show": lambda x: str(x)},
    )

    # Show Bool
    ctx.add_instance(
        "Show",
        TCon("Bool"),
        {"show": lambda x: str(x)},
    )

    # Show String
    ctx.add_instance(
        "Show",
        TCon("String"),
        {"show": lambda x: x},
    )

    # Num Int
    ctx.add_instance(
        "Num",
        TCon("Int"),
        {
            "add": lambda x, y: x + y,
            "sub": lambda x, y: x - y,
            "mul": lambda x, y: x * y,
            "negate": lambda x: -x,
            "zero": 0,
        },
    )

    # Num Float
    ctx.add_instance(
        "Num",
        TCon("Float"),
        {
            "add": lambda x, y: x + y,
            "sub": lambda x, y: x - y,
            "mul": lambda x, y: x * y,
            "negate": lambda x: -x,
            "zero": 0.0,
        },
    )

    # Fractional Float
    ctx.add_instance(
        "Fractional",
        TCon("Float"),
        {
            "div": lambda x, y: x / y,
            "recip": lambda x: 1.0 / x,
            "one": 1.0,
        },
    )

    # Semigroup String
    ctx.add_instance(
        "Semigroup",
        TCon("String"),
        {"append": lambda x, y: x + y},
    )

    # Monoid String
    ctx.add_instance(
        "Monoid",
        TCon("String"),
        {"empty": ""},
    )


# Global default context
DEFAULT_CLASSES = create_default_context()


def get_default_context() -> ClassContext:
    """Get the default type class context."""
    return DEFAULT_CLASSES


def resolve_instance(
    ctx: ClassContext, class_name: str, type_: Type
) -> InstanceInfo | None:
    """Resolve a type class instance for a given type."""
    return ctx.lookup_instance(class_name, type_)


def check_constraint(
    ctx: ClassContext, constraint: TConstraint, subst: Subst | None = None
) -> bool:
    """Check if a constraint is satisfiable."""
    if subst:
        type_ = subst.apply(constraint.type_)
    else:
        type_ = constraint.type_
    return ctx.lookup_instance(constraint.class_name, type_) is not None


def solve_constraints(
    ctx: ClassContext, constraints: tuple[TConstraint, ...], subst: Subst
) -> bool:
    """Check if all constraints are satisfiable."""
    for constraint in constraints:
        if not check_constraint(ctx, constraint, subst):
            return False
    return True


def build_dictionary(
    ctx: ClassContext, class_name: str, type_: Type
) -> dict[str, Any] | None:
    """Build a dictionary of method implementations for a type class instance.

    This is used for dictionary-passing transformation.
    """
    inst = ctx.lookup_instance(class_name, type_)
    if inst:
        return inst.methods.copy()

    # Check for default methods
    cls = ctx.lookup_class(class_name)
    if cls:
        return cls.defaults.copy()

    return None


def get_qualified_type(
    ctx: ClassContext, type_: Type, constraints: tuple[TConstraint, ...]
) -> TQualified | Type:
    """Create a qualified type if there are constraints, otherwise return the type."""
    if constraints:
        return TQualified(constraints, type_)
    return type_


def instantiate_qualified(
    ctx: ClassContext, scheme: Scheme, subst: Subst
) -> tuple[Type, tuple[TConstraint, ...]]:
    """Instantiate a scheme, returning the type and any constraints."""
    # Apply substitution to the type
    t = subst.apply(scheme.type)

    # Apply substitution to constraints
    constraints = tuple(
        TConstraint(c.class_name, subst.apply(c.type_)) for c in scheme.constraints
    )

    return t, constraints
