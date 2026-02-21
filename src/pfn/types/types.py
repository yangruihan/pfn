from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Type:
    def __str__(self) -> str:
        return "Type"


@dataclass(frozen=True)
class TInt(Type):
    def __str__(self) -> str:
        return "Int"


@dataclass(frozen=True)
class TFloat(Type):
    def __str__(self) -> str:
        return "Float"


@dataclass(frozen=True)
class TString(Type):
    def __str__(self) -> str:
        return "String"


@dataclass(frozen=True)
class TBool(Type):
    def __str__(self) -> str:
        return "Bool"


@dataclass(frozen=True)
class TChar(Type):
    def __str__(self) -> str:
        return "Char"


@dataclass(frozen=True)
class TUnit(Type):
    def __str__(self) -> str:
        return "()"


@dataclass(frozen=True)
class TVar(Type):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class TFun(Type):
    param: Type
    result: Type

    def __str__(self) -> str:
        if isinstance(self.param, TFun):
            return f"({self.param}) -> {self.result}"
        return f"{self.param} -> {self.result}"


@dataclass(frozen=True)
class TList(Type):
    elem: Type

    def __str__(self) -> str:
        return f"[{self.elem}]"


@dataclass(frozen=True)
class TTuple(Type):
    elements: tuple[Type, ...]

    def __str__(self) -> str:
        elems = ", ".join(str(e) for e in self.elements)
        return f"({elems})"


@dataclass(frozen=True)
class TRecord(Type):
    fields: tuple[tuple[str, Type], ...]

    def __str__(self) -> str:
        fields = ", ".join(f"{k}: {v}" for k, v in self.fields)
        return f"{{{fields}}}"


@dataclass(frozen=True)
class Scheme:
    vars: tuple[str, ...]
    type: Type

    def __str__(self) -> str:
        if self.vars:
            vars_str = " ".join(self.vars)
            return f"forall {vars_str}. {self.type}"
        return str(self.type)


class Subst:
    def __init__(self, mapping: dict[str, Type] | None = None):
        self.mapping: dict[str, Type] = mapping.copy() if mapping else {}

    def __repr__(self) -> str:
        return f"Subst({self.mapping})"

    def apply(self, t: Type) -> Type:
        if isinstance(t, TInt):
            return t
        if isinstance(t, TFloat):
            return t
        if isinstance(t, TString):
            return t
        if isinstance(t, TBool):
            return t
        if isinstance(t, TChar):
            return t
        if isinstance(t, TUnit):
            return t
        if isinstance(t, TVar):
            if t.name in self.mapping:
                return self.apply(self.mapping[t.name])
            return t
        if isinstance(t, TFun):
            return TFun(self.apply(t.param), self.apply(t.result))
        if isinstance(t, TList):
            return TList(self.apply(t.elem))
        if isinstance(t, TTuple):
            return TTuple(tuple(self.apply(e) for e in t.elements))
        if isinstance(t, TRecord):
            return TRecord(tuple((k, self.apply(v)) for k, v in t.fields))
        return t

    def apply_scheme(self, scheme: Scheme) -> Scheme:
        new_mapping = {k: v for k, v in self.mapping.items() if k not in scheme.vars}
        s = Subst(new_mapping)
        return Scheme(scheme.vars, s.apply(scheme.type))

    def compose(self, other: Subst) -> Subst:
        new_mapping = {}
        for k, v in other.mapping.items():
            new_mapping[k] = self.apply(v)
        for k, v in self.mapping.items():
            if k not in new_mapping:
                new_mapping[k] = v
        return Subst(new_mapping)

    def free_vars(self, t: Type) -> set[str]:
        if isinstance(t, (TInt, TFloat, TString, TBool, TChar, TUnit)):
            return set()
        if isinstance(t, TVar):
            return {t.name}
        if isinstance(t, TFun):
            return self.free_vars(t.param) | self.free_vars(t.result)
        if isinstance(t, TList):
            return self.free_vars(t.elem)
        if isinstance(t, TTuple):
            result: set[str] = set()
            for e in t.elements:
                result |= self.free_vars(e)
            return result
        if isinstance(t, TRecord):
            result = set()
            for _, v in t.fields:
                result |= self.free_vars(v)
            return result
        return set()

    def free_vars_scheme(self, scheme: Scheme) -> set[str]:
        return self.free_vars(scheme.type) - set(scheme.vars)

    def free_vars_env(self, env: TypeEnv) -> set[str]:
        result: set[str] = set()
        for scheme in env.values():
            result |= self.free_vars_scheme(scheme)
        return result

    def occurs_in(self, var: str, t: Type) -> bool:
        return var in self.free_vars(t)

    def unify(self, t1: Type, t2: Type) -> Subst | None:
        t1 = self.apply(t1)
        t2 = self.apply(t2)

        if isinstance(t1, TInt) and isinstance(t2, TInt):
            return Subst()
        if isinstance(t1, TFloat) and isinstance(t2, TFloat):
            return Subst()
        if isinstance(t1, TString) and isinstance(t2, TString):
            return Subst()
        if isinstance(t1, TBool) and isinstance(t2, TBool):
            return Subst()
        if isinstance(t1, TChar) and isinstance(t2, TChar):
            return Subst()
        if isinstance(t1, TUnit) and isinstance(t2, TUnit):
            return Subst()

        if isinstance(t1, TVar):
            if isinstance(t2, TVar) and t1.name == t2.name:
                return Subst()
            if self.occurs_in(t1.name, t2):
                return None
            return Subst({t1.name: t2})

        if isinstance(t2, TVar):
            if self.occurs_in(t2.name, t1):
                return None
            return Subst({t2.name: t1})

        if isinstance(t1, TFun) and isinstance(t2, TFun):
            s1 = self.unify(t1.param, t2.param)
            if s1 is None:
                return None
            s1 = s1.compose(self)
            t1_result = s1.apply(t1.result)
            t2_result = s1.apply(t2.result)
            s2 = s1.unify(t1_result, t2_result)
            if s2 is None:
                return None
            return s2.compose(s1)

        if isinstance(t1, TList) and isinstance(t2, TList):
            return self.unify(t1.elem, t2.elem)

        if isinstance(t1, TTuple) and isinstance(t2, TTuple):
            if len(t1.elements) != len(t2.elements):
                return None
            result = Subst()
            for e1, e2 in zip(t1.elements, t2.elements):
                s = result.unify(e1, e2)
                if s is None:
                    return None
                result = s.compose(result)
            return result

        return None


class TypeEnv:
    def __init__(self, bindings: dict[str, Scheme] | None = None):
        self.bindings: dict[str, Scheme] = bindings.copy() if bindings else {}

    def __iter__(self):
        return iter(self.bindings.values())

    def values(self):
        return self.bindings.values()

    def lookup(self, name: str) -> Scheme | None:
        return self.bindings.get(name)

    def extend(self, name: str, scheme: Scheme) -> TypeEnv:
        new_bindings = self.bindings.copy()
        new_bindings[name] = scheme
        return TypeEnv(new_bindings)

    def remove(self, name: str) -> TypeEnv:
        new_bindings = self.bindings.copy()
        if name in new_bindings:
            del new_bindings[name]
        return TypeEnv(new_bindings)
