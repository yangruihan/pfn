"""Python interoperability utilities for Pfn runtime."""

from __future__ import annotations

import sys
import types
from typing import Any, Callable


# ============ Module Import System ============


class PyModule:
    """Wrapper for Python module."""

    def __init__(self, module: types.ModuleType):
        self._module = module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)

    def __repr__(self) -> str:
        return f"PyModule({self._module.__name__})"


# Module cache
_module_cache: dict[str, Any] = {}


def import_python_module(name: str) -> PyModule:
    """Import a Python module by name.

    Example:
        math = import_python_module("math")
        result = math.sin(3.14)
    """
    if name in _module_cache:
        return _module_cache[name]

    try:
        import importlib

        module = importlib.import_module(name)
        py_module = PyModule(module)
        _module_cache[name] = py_module
        return py_module
    except ImportError as e:
        raise ImportError(f"Cannot import Python module '{name}': {e}")


def import_python_module_as(name: str, alias: str) -> PyModule:
    """Import a Python module with an alias.

    Example:
        np = import_python_module_as("numpy", "np")
    """
    module = import_python_module(name)
    _module_cache[alias] = module
    return module


# ============ Type Conversion ============


# Type mapping from Python to Pfn
PYTHON_TO_PFN_TYPE: dict[type, str] = {
    int: "Int",
    float: "Float",
    str: "String",
    bool: "Bool",
    list: "List",
    dict: "Dict",
    tuple: "Tuple",
    type(None): "()",
}

# Type mapping from Pfn to Python
PFN_TO_PYTHON_TYPE: dict[str, type] = {
    "Int": int,
    "Float": float,
    "String": str,
    "Bool": bool,
    "List": list,
    "Dict": dict,
    "Tuple": tuple,
    "()": type(None),
}


def python_to_pfn(value: Any) -> Any:
    """Convert Python value to Pfn equivalent.

    Args:
        value: Python value to convert

    Returns:
        Pfn-compatible value
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    if isinstance(value, list):
        return [python_to_pfn(item) for item in value]
    if isinstance(value, tuple):
        return tuple(python_to_pfn(item) for item in value)
    if isinstance(value, dict):
        return {str(k): python_to_pfn(v) for k, v in value.items()}
    # For objects, keep as-is but wrap
    return value


def pfn_to_python(value: Any) -> Any:
    """Convert Pfn value to Python equivalent.

    Args:
        value: Pfn value to convert

    Returns:
        Python-compatible value
    """
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return type(value)(pfn_to_python(item) for item in value)
    if isinstance(value, dict):
        return {k: pfn_to_python(v) for k, v in value.items()}
    return value


# ============ Python Function Wrapper ============


class PyFunction:
    """Wrapper for Python function."""

    def __init__(self, func: Callable[..., Any], name: str | None = None):
        self._func = func
        self._name = name or getattr(func, "__name__", repr(func))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # Convert Pfn arguments to Python
        py_args = [pfn_to_python(arg) for arg in args]
        py_kwargs = {k: pfn_to_python(v) for k, v in kwargs.items()}

        result = self._func(*py_args, **py_kwargs)

        # Convert result back to Pfn
        return python_to_pfn(result)

    def __repr__(self) -> str:
        return f"PyFunction({self._name})"


def wrap_python_function(func: Callable[..., Any]) -> PyFunction:
    """Wrap a Python function for Pfn.

    Example:
        wrapped = wrap_python_function(len)
        result = wrapped([1, 2, 3])  # Returns 3
    """
    return PyFunction(func)


# ============ Python Object Wrapper ============


class PyObject:
    """Wrapper for arbitrary Python object."""

    def __init__(self, obj: Any):
        self._obj = obj

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._obj, name)
        if callable(attr):
            return PyFunction(attr)
        return python_to_pfn(attr)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._obj, name, pfn_to_python(value))

    def __repr__(self) -> str:
        return f"PyObject({self._obj!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PyObject):
            return self._obj == other._obj
        return False


def to_py_object(obj: Any) -> PyObject:
    """Convert Python object to PyObject wrapper."""
    if isinstance(obj, PyObject):
        return obj
    return PyObject(obj)


# ============ FFI Functions ============


def py_call(obj: Any, *args: Any, **kwargs: Any) -> Any:
    """Call a Python object as function.

    Example:
        result = py_call(math.sqrt, 4)
    """
    if hasattr(obj, "__call__"):
        py_args = [pfn_to_python(arg) for arg in args]
        py_kwargs = {k: pfn_to_python(v) for k, v in kwargs.items()}
        result = obj(*py_args, **py_kwargs)
        return python_to_pfn(result)
    raise TypeError(f"Object {obj} is not callable")


def py_getattr(obj: Any, name: str) -> Any:
    """Get attribute from Python object.

    Example:
        name = py_getattr(person, "name")
    """
    result = getattr(obj, name)
    return python_to_pfn(result)


def py_setattr(obj: Any, name: str, value: Any) -> None:
    """Set attribute on Python object.

    Example:
        py_setattr(person, "name", "Alice")
    """
    setattr(obj, name, pfn_to_python(value))


def py_getitem(obj: Any, key: Any) -> Any:
    """Get item from Python object.

    Example:
        value = py_getattr(arr, 0)
    """
    result = obj[pfn_to_python(key)]
    return python_to_pfn(result)


def py_setitem(obj: Any, key: Any, value: Any) -> None:
    """Set item on Python object.

    Example:
        py_setitem(arr, 0, 42)
    """
    obj[pfn_to_python(key)] = pfn_to_python(value)


def py_instanceof(obj: Any, class_name: str) -> bool:
    """Check if object is instance of class.

    Example:
        is_list = py_instanceof(x, "list")
    """
    return type(obj).__name__ == class_name


def py_typeof(obj: Any) -> str:
    """Get type name of object.

    Example:
        t = py_typeof(42)  # Returns "int"
    """
    return type(obj).__name__


# ============ Python Eval/Exec ============


def py_eval(source: str, globals_dict: dict[str, Any] | None = None) -> Any:
    """Evaluate Python expression.

    Example:
        result = py_eval("1 + 2")
    """
    if globals_dict is None:
        globals_dict = {}
    result = eval(source, globals_dict)
    return python_to_pfn(result)


def py_exec(source: str, globals_dict: dict[str, Any] | None = None) -> None:
    """Execute Python code.

    Example:
        py_exec("x = 1 + 2")
    """
    if globals_dict is None:
        globals_dict = {}
    exec(source, globals_dict)


# ============ Type Checking ============


def is_python_object(x: Any) -> bool:
    """Check if value is a Python object (not Pfn native)."""
    return isinstance(x, (PyObject, PyFunction, PyModule))


def is_pfn_native(x: Any) -> bool:
    """Check if value is Pfn native type."""
    return not is_python_object(x)


# ============ Prelude Exports ============


__all__ = [
    # Module import
    "PyModule",
    "import_python_module",
    "import_python_module_as",
    # Type conversion
    "python_to_pfn",
    "pfn_to_python",
    # Wrappers
    "PyFunction",
    "wrap_python_function",
    "PyObject",
    "to_py_object",
    # FFI
    "py_call",
    "py_getattr",
    "py_setattr",
    "py_getitem",
    "py_setitem",
    "py_instanceof",
    "py_typeof",
    # Eval/Exec
    "py_eval",
    "py_exec",
    # Type checking
    "is_python_object",
    "is_pfn_native",
]
