from __future__ import annotations

import inspect
import sys
import types
from dataclasses import dataclass, field
from typing import Any, Callable, get_type_hints

from pfn.types import (
    Type,
    TInt,
    TFloat,
    TString,
    TBool,
    TList,
    TTuple,
    TDict,
    TSet,
    TVar,
    TFun,
    TCon,
    TIO,
    Scheme,
    TypeEnv,
)


@dataclass
class PyTypeInfo:
    py_type: type
    pfn_type: Type
    is_optional: bool = False
    is_generic: bool = False


PYTHON_TYPE_MAP: dict[type, Type] = {
    int: TInt(),
    float: TFloat(),
    str: TString(),
    bool: TBool(),
    type(None): TCon("Unit"),
}

PYTHON_CONTAINER_MAP: dict[type, str] = {
    list: "List",
    dict: "Dict",
    tuple: "Tuple",
    set: "Set",
}


def python_type_to_pfn(py_type: type) -> Type:
    if py_type in PYTHON_TYPE_MAP:
        return PYTHON_TYPE_MAP[py_type]

    origin = getattr(py_type, "__origin__", None)
    args = getattr(py_type, "__args__", ())

    if origin is list:
        if args:
            elem_type = python_type_to_pfn(args[0])
            return TList(elem_type)
        return TList(TVar("a"))

    if origin is dict:
        if len(args) >= 2:
            key_type = python_type_to_pfn(args[0])
            val_type = python_type_to_pfn(args[1])
            return TDict(key_type, val_type)
        return TCon("Dict")

    if origin is tuple:
        if args:
            elem_types = tuple(python_type_to_pfn(a) for a in args)
            return TTuple(elem_types)
        return TTuple(())

    if origin is set:
        if args:
            elem_type = python_type_to_pfn(args[0])
            return TSet(elem_type)
        return TCon("Set")

    if hasattr(py_type, "__name__"):
        return TCon(py_type.__name__)

    return TVar("a")


def pfn_type_to_python(t: Type) -> type:
    if isinstance(t, TInt):
        return int
    if isinstance(t, TFloat):
        return float
    if isinstance(t, TString):
        return str
    if isinstance(t, TBool):
        return bool
    if isinstance(t, TList):
        return list
    if isinstance(t, TTuple):
        return tuple
    if isinstance(t, TCon):
        if t.name == "Unit":
            return type(None)
        return object
    return object


def infer_python_function_type(func: Callable[..., Any]) -> Scheme:
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    param_types: list[Type] = []
    for param in params:
        if param.name in hints:
            param_types.append(python_type_to_pfn(hints[param.name]))
        else:
            param_types.append(TVar(f"t_{param.name}"))

    return_type = TInt()
    if "return" in hints:
        return_type = python_type_to_pfn(hints["return"])

    result_type = return_type
    for pt in reversed(param_types):
        result_type = TFun(pt, result_type)

    free_vars: set[str] = set()
    for pt in param_types:
        if isinstance(pt, TVar):
            free_vars.add(pt.name)
    if isinstance(return_type, TVar):
        free_vars.add(return_type.name)

    return Scheme(tuple(sorted(free_vars)), result_type)


@dataclass
class ExportRegistry:
    exports: dict[str, Callable[..., Any]] = field(default_factory=dict)
    type_schemes: dict[str, Scheme] = field(default_factory=dict)

    def register(self, name: str, func: Callable[..., Any]) -> None:
        self.exports[name] = func
        self.type_schemes[name] = infer_python_function_type(func)

    def get(self, name: str) -> Callable[..., Any] | None:
        return self.exports.get(name)

    def get_type(self, name: str) -> Scheme | None:
        return self.type_schemes.get(name)

    def all_exports(self) -> dict[str, Callable[..., Any]]:
        return self.exports.copy()

    def to_type_env(self) -> TypeEnv:
        env = TypeEnv()
        for name, scheme in self.type_schemes.items():
            env = env.extend(name, scheme)
        return env


_global_registry = ExportRegistry()


def get_export_registry() -> ExportRegistry:
    return _global_registry


def export(
    name: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        export_name = name or func.__name__
        _global_registry.register(export_name, func)
        return func

    return decorator


def is_exported(func: Callable[..., Any]) -> bool:
    name = getattr(func, "__name__", None)
    if name:
        return name in _global_registry.exports
    return False


def get_export_name(func: Callable[..., Any]) -> str | None:
    name = getattr(func, "__name__", None)
    if name and name in _global_registry.exports:
        return name
    return None


@dataclass
class PythonModuleInfo:
    name: str
    functions: dict[str, Scheme] = field(default_factory=dict)
    classes: dict[str, type] = field(default_factory=dict)
    constants: dict[str, Type] = field(default_factory=dict)


def inspect_python_module(module: types.ModuleType) -> PythonModuleInfo:
    info = PythonModuleInfo(name=module.__name__)

    for name in dir(module):
        if name.startswith("_"):
            continue

        obj = getattr(module, name)

        if callable(obj) and not isinstance(obj, type):
            try:
                info.functions[name] = infer_python_function_type(obj)
            except Exception:
                pass

        elif isinstance(obj, type):
            info.classes[name] = obj

        else:
            try:
                py_type = type(obj)
                info.constants[name] = python_type_to_pfn(py_type)
            except Exception:
                pass

    return info


def create_pfn_type_env_for_module(module: types.ModuleType) -> TypeEnv:
    info = inspect_python_module(module)
    env = TypeEnv()

    for name, scheme in info.functions.items():
        env = env.extend(name, scheme)

    for name, t in info.constants.items():
        env = env.extend(name, Scheme((), t))

    return env


class PyImport:
    def __init__(self, module_name: str, alias: str | None = None):
        self.module_name = module_name
        self.alias = alias
        self._module: types.ModuleType | None = None
        self._type_env: TypeEnv | None = None

    def load(self) -> types.ModuleType:
        if self._module is None:
            import importlib

            self._module = importlib.import_module(self.module_name)
        return self._module

    def get_type_env(self) -> TypeEnv:
        if self._type_env is None:
            self._type_env = create_pfn_type_env_for_module(self.load())
        return self._type_env

    def __getattr__(self, name: str) -> Any:
        return getattr(self.load(), name)


def py_import(module_name: str, alias: str | None = None) -> PyImport:
    return PyImport(module_name, alias)


__all__ = [
    "python_type_to_pfn",
    "pfn_type_to_python",
    "infer_python_function_type",
    "ExportRegistry",
    "get_export_registry",
    "export",
    "is_exported",
    "get_export_name",
    "PythonModuleInfo",
    "inspect_python_module",
    "create_pfn_type_env_for_module",
    "PyImport",
    "py_import",
]
