"""Pfn runtime library.

This module provides the runtime support for compiled Pfn programs,
including:
- Core functional programming utilities (Lazy, Option, Result, etc.)
- Built-in type implementations
- Pattern matching helpers
- Python interoperability
- Utility functions
"""

from pfn.runtime.core import (
    # Lazy
    Lazy,
    lazy,
    # Function utilities
    curry,
    uncurry,
    compose,
    flip,
    # Option
    Some,
    None_,
    Option,
    is_some,
    is_none,
    from_some,
    from_opt,
    # Result
    Ok,
    Error,
    Result,
    is_ok,
    is_error,
    from_ok,
    from_error,
    # List
    foldl,
    foldr,
    map_,
    filter_,
    flat_map,
    concat,
    length,
    head,
    tail,
    last,
    init,
    take,
    drop,
    take_while,
    drop_while,
    reverse,
    append,
    cons,
    # String
    concat_strings,
    intersperse,
    unlines,
    unwords,
    # Generic
    id_,
    const,
    until,
    iterate,
    # Debug
    trace,
    trace_show,
)

from pfn.runtime.types import (
    # Tuple
    tuple_first,
    tuple_second,
    tuple_rest,
    tuple_len,
    # Dict
    Dict,
    # Set
    Set,
    # String
    string_len,
    string_is_empty,
    string_head,
    string_tail,
    string_append,
    string_split,
    string_join,
    string_trim,
    string_to_int,
    string_to_float,
    string_from_int,
    string_from_float,
    string_contains,
    string_starts_with,
    string_ends_with,
    string_replace,
    string_to_upper,
    string_to_lower,
    # Numeric
    int_to_string,
    float_to_string,
    int_to_float,
    float_to_int,
    int_abs,
    int_max,
    int_min,
    int_mod,
    int_pow,
    float_abs,
    float_max,
    float_min,
    float_pow,
    float_sqrt,
    float_ceil,
    float_floor,
    float_round,
    # Boolean
    bool_to_string,
    bool_not,
    bool_and,
    bool_or,
    # Conversion
    to_string,
    to_int,
    to_float,
    to_bool,
)

from pfn.runtime.pattern import (
    MatchError,
    match,
    Case,
    case,
    guard,
    match_record,
    match_sum_type,
    match_list,
    match_tuple,
    alt,
    maybe,
)

from pfn.runtime.python_compat import (
    # Module import
    PyModule,
    import_python_module,
    import_python_module_as,
    # Type conversion
    python_to_pfn,
    pfn_to_python,
    # Wrappers
    PyFunction,
    wrap_python_function,
    PyObject,
    to_py_object,
    # FFI
    py_call,
    py_getattr,
    py_setattr,
    py_getitem,
    py_setitem,
    py_instanceof,
    py_typeof,
    # Eval/Exec
    py_eval,
    py_exec,
    # Type checking
    is_python_object,
    is_pfn_native,
)

from pfn.runtime.utils import (
    # Errors
    PfnError,
    RuntimeError,
    TypeError,
    ValueError,
    IndexError,
    KeyError,
    # Unsafe
    panic,
    unreachable,
    todo,
    # Debug
    inspect,
    typeof,
    repr_ as repr,
    str_ as str,
    print_ as print,
    println,
    # Equality
    eq,
    neq,
    compare,
    # Identity
    id,
    const_ as const,
    # Function
    apply,
    pipe,
    compose as comp,
    memoize,
    # Time
    timeit,
    measure,
    # I/O
    read_file,
    write_file,
    read_lines,
    write_lines,
    # System
    exit,
    get_env,
    set_env,
)


# ============ Standard Library Prelude ============

# The prelude provides the most commonly used functions
__all__ = [
    # Core
    "Lazy",
    "lazy",
    "curry",
    "compose",
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
    # List operations
    "map_",
    "filter_",
    "foldl",
    "foldr",
    "length",
    "head",
    "tail",
    # Dict & Set
    "Dict",
    "Set",
    # Pattern matching
    "match",
    "MatchError",
    # Python interop
    "PyModule",
    "import_python_module",
    "PyFunction",
    "wrap_python_function",
    "python_to_pfn",
    "pfn_to_python",
    # Errors
    "PfnError",
    "panic",
    "unreachable",
    "todo",
    # Debug
    "inspect",
    "typeof",
    "repr",
    "str",
    "print",
    # I/O
    "read_file",
    "write_file",
    "exit",
]


# ============ Version Info ============

__version__ = "0.1.0"
