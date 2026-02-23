"""Stdlib shim for compiled Pfn code."""
from pfn.runtime.types import Dict as _Dict, Set as _Set, string_len, to_string
from pfn.runtime.core import (
    Option, Result, Some, None_, Ok, Error, Lazy, foldl,
    is_some, is_none, from_some, from_opt, is_ok, is_error, from_ok, from_error
)
from pfn.runtime.pattern import match as _match_pattern
from typing import Generic, TypeVar, Any

K = TypeVar('K')
V = TypeVar('V')
T = TypeVar('T')

# Record class that supports both dict and attribute access
class Record(dict):
    """Record type that supports both dict and attribute access."""
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

# String class with Pfn-expected methods
class String:
    """String class with Pfn-expected methods."""
    
    @staticmethod
    def length(s):
        return len(s)
    
    @staticmethod
    def unsafeAt(index):
        def inner(s):
            return s[index]
        return inner
    
    @staticmethod
    def fromList(chars):
        return ''.join(chars)
    
    @staticmethod
    def toList(s):
        return list(s)
    
    @staticmethod
    def toFloat(s):
        return float(s)
    
    @staticmethod
    def toInt(s):
        return int(s)
    
    @staticmethod
    def join(sep):
        def inner(parts):
            return sep.join(parts)
        return inner
    
    @staticmethod
    def concat(strings):
        return ''.join(strings)
    
    @staticmethod
    def split(sep):
        def inner(s):
            return s.split(sep)
        return inner
    
    @staticmethod
    def trim(s):
        return s.strip()
    
    @staticmethod
    def toUpper(s):
        return s.upper()
    
    @staticmethod
    def toLower(s):
        return s.lower()

# Wrapper classes with Pfn-expected methods
class Dict(Generic[K, V]):
    """Dict wrapper with Pfn-expected methods."""
    
    @staticmethod
    def empty():
        return Dict()
    
    @staticmethod
    def fromList(items):
        d = Dict()
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                d._data[item[0]] = item[1]
        return d
    
    @staticmethod
    def singleton(key):
        def inner(value):
            return Dict({key: value})
        return inner
    
    @staticmethod
    def lookup(key):
        def inner(d):
            from pfn.runtime.core import Some, None_
            if key in d._data:
                return Some(d._data[key])
            return None_
        return inner
    
    @staticmethod
    def insert(key):
        def inner1(value):
            def inner2(d):
                new_dict = Dict(d._data.copy())
                new_dict._data[key] = value
                return new_dict
            return inner2
        return inner1
    
    @staticmethod
    def merge(d1):
        def inner(d2):
            new_dict = Dict(d1._data.copy())
            new_dict._data.update(d2._data)
            return new_dict
        return inner
    
    def __init__(self, data=None):
        self._data = dict(data) if data else {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def set(self, key, value):
        new_dict = Dict(self._data.copy())
        new_dict._data[key] = value
        return new_dict
    
    def delete(self, key):
        new_dict = Dict(self._data.copy())
        new_dict._data.pop(key, None)
        return new_dict
    
    def contains(self, key):
        return key in self._data
    
    def keys(self):
        return list(self._data.keys())
    
    def values(self):
        return list(self._data.values())
    
    def items(self):
        return list(self._data.items())
    
    def to_dict(self):
        return self._data.copy()
    
    def __repr__(self):
        return f"Dict({self._data})"
    
    def __eq__(self, other):
        if isinstance(other, Dict):
            return self._data == other._data
        return False
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value

class Set(Generic[T]):
    """Set wrapper with Pfn-expected methods."""
    
    @staticmethod
    def empty():
        return Set()
    
    @staticmethod
    def fromList(items):
        return Set(items)
    
    def __init__(self, data=None):
        self._data = set(data) if data else set()
    
    def contains(self, elem):
        return elem in self._data
    
    def add(self, elem):
        new_set = Set(self._data.copy())
        new_set._data.add(elem)
        return new_set
    
    def remove(self, elem):
        new_set = Set(self._data.copy())
        new_set._data.discard(elem)
        return new_set
    
    def union(self, other):
        return Set(self._data | other._data)
    
    def intersection(self, other):
        return Set(self._data & other._data)
    
    def difference(self, other):
        return Set(self._data - other._data)
    
    def to_list(self):
        return list(self._data)
    
    def __repr__(self):
        return f"Set({self._data})"
    
    def __eq__(self, other):
        if isinstance(other, Set):
            return self._data == other._data
        return False
    
    def __len__(self):
        return len(self._data)
    
    def __iter__(self):
        return iter(self._data)

# List class with Pfn-expected methods
class List:
    """List class with Pfn-expected methods."""
    
    @staticmethod
    def length(lst):
        return len(lst)
    
    @staticmethod
    def isEmpty(lst):
        return len(lst) == 0
    
    @staticmethod
    def head(lst):
        return lst[0] if lst else None
    
    @staticmethod
    def tail(lst):
        return lst[1:] if lst else []
    
    @staticmethod
    def getAt(index):
        def inner(lst):
            from pfn.runtime.core import Some, None_
            return Some(lst[index]) if 0 <= index < len(lst) else None_
        return inner
    
    @staticmethod
    def map(f):
        def inner(lst):
            return [f(x) for x in lst]
        return inner
    
    @staticmethod
    def filter(pred):
        def inner(lst):
            return [x for x in lst if pred(x)]
        return inner
    
    @staticmethod
    def foldl(f):
        def inner1(acc):
            def inner2(lst):
                result = acc
                for x in lst:
                    result = f(result, x)
                return result
            return inner2
        return inner1
    
    @staticmethod
    def reverse(lst):
        return lst[::-1]
    
    @staticmethod
    def concat(lists):
        result = []
        for lst in lists:
            result.extend(lst)
        return result
    
    @staticmethod
    def intersperse(sep):
        def inner(lst):
            if not lst:
                return []
            result = [lst[0]]
            for x in lst[1:]:
                result.append(sep)
                result.append(x)
            return result
        return inner

# Aliases for Pfn naming conventions
Just = Some
Nothing = None_
Err = Error

# Re-export commonly used items
Maybe = Option
Result = Result
Just = Just
Nothing = Nothing
Ok = Ok
Err = Err

def reverse(lst):
    return lst[::-1]

def _not_(x):
    return not x

def error(msg):
    """Raise a runtime error."""
    raise RuntimeError(msg)

__all__ = [
    'String', 'List', 'Dict', 'Set', 'Maybe', 'Result', 
    'Just', 'Nothing', 'Ok', 'Err', 'Record',
    'reverse', '_not_', 'string_len', 'to_string', 'error',
    'Some', 'None_', 'Error', 'Option'
]


# ============ Primitive Functions ============
# These are low-level functions that Pfn stdlib modules depend on

# String primitives
def stringLength(s):
    """Get string length."""
    return len(s)

def stringAt(index):
    """Get character at index (curried)."""
    def inner(s):
        return s[index]
    return inner

def stringSlice(start):
    """Slice string from start to end (curried)."""
    def inner1(end):
        def inner2(s):
            return s[start:end]
        return inner2
    return inner1

def charToUpper(c):
    """Convert character to uppercase."""
    return c.upper()

def charToLower(c):
    """Convert character to lowercase."""
    return c.lower()

def ord(c):
    """Get ASCII code of character."""
    return __builtins__['ord'](c) if isinstance(__builtins__, dict) else __builtins__.ord(c)

def chr(n):
    """Get character from ASCII code."""
    return __builtins__['chr'](n) if isinstance(__builtins__, dict) else __builtins__.chr(n)

# Dict primitives
def dictEmpty():
    """Create empty dict."""
    return {}

def dictSingleton(key):
    """Create dict with single key-value pair (curried)."""
    def inner(value):
        return {key: value}
    return inner

def dictLookup(key):
    """Lookup key in dict, returns Maybe (curried)."""
    def inner(d):
        if key in d:
            return Some(d[key])
        return None_
    return inner

def dictInsert(key):
    """Insert key-value pair into dict (curried)."""
    def inner1(value):
        def inner2(d):
            new_d = d.copy()
            new_d[key] = value
            return new_d
        return inner2
    return inner1

def dictRemove(key):
    """Remove key from dict (curried)."""
    def inner(d):
        new_d = d.copy()
        new_d.pop(key, None)
        return new_d
    return inner

def dictSize(d):
    """Get dict size."""
    return len(d)

def dictToPairs(d):
    """Convert dict to list of (key, value) pairs."""
    return list(d.items())

def dictFromPairs(pairs):
    """Create dict from list of (key, value) pairs."""
    return dict(pairs)

def dictKeys(d):
    """Get dict keys as list."""
    return list(d.keys())

def dictValues(d):
    """Get dict values as list."""
    return list(d.values())

def dictMember(key):
    """Check if key exists in dict (curried)."""
    def inner(d):
        return key in d
    return inner

# Set primitives
def setEmpty():
    """Create empty set."""
    return set()

def setSingleton(x):
    """Create set with single element."""
    return {x}

def setToList(s):
    """Convert set to list."""
    return list(s)

def setFromList(lst):
    """Create set from list."""
    return set(lst)

def setSize(s):
    """Get set size."""
    return len(s)

def setMember(x):
    """Check if element is in set (curried)."""
    def inner(s):
        return x in s
    return inner

def setInsert(x):
    """Insert element into set (curried)."""
    def inner(s):
        new_s = s.copy()
        new_s.add(x)
        return new_s
    return inner

def setDelete(x):
    """Delete element from set (curried)."""
    def inner(s):
        new_s = s.copy()
        new_s.discard(x)
        return new_s
    return inner

def setUnion(s1):
    """Union of two sets (curried)."""
    def inner(s2):
        return s1 | s2
    return inner

def setIntersection(s1):
    """Intersection of two sets (curried)."""
    def inner(s2):
        return s1 & s2
    return inner

def setDifference(s1):
    """Difference of two sets (curried)."""
    def inner(s2):
        return s1 - s2
    return inner

# Numeric primitives
def pow(base):
    """Power function (curried)."""
    def inner(exp):
        return base ** exp
    return inner

def abs_(x):
    """Absolute value."""
    return __builtins__['abs'](x) if isinstance(__builtins__, dict) else __builtins__.abs(x)

def negate(x):
    """Negate a number."""
    return -x

# Comparison primitives
def compare(a):
    """Compare two values (curried). Returns LT, EQ, or GT."""
    def inner(b):
        if a < b:
            return LT
        elif a > b:
            return GT
        else:
            return EQ
    return inner

# Ordering type
class LT:
    def __repr__(self):
        return "LT"
    def __eq__(self, other):
        return isinstance(other, LT)

class EQ:
    def __repr__(self):
        return "EQ"
    def __eq__(self, other):
        return isinstance(other, EQ)

class GT:
    def __repr__(self):
        return "GT"
    def __eq__(self, other):
        return isinstance(other, GT)

LT = LT()
EQ = EQ()
GT = GT()

# IO primitives (basic implementations)
def printIO(x):
    """Print value to stdout."""
    print(x)
    return None

def putStrIO(s):
    """Print string without newline."""
    print(s, end='')
    return None

def getLineIO():
    """Read line from stdin."""
    return input()

def readFileIO(path):
    """Read file contents."""
    with open(path, 'r') as f:
        return f.read()

def writeFileIO(path):
    """Write to file (curried)."""
    def inner(content):
        with open(path, 'w') as f:
            f.write(content)
        return None
    return inner

def appendFileIO(path):
    """Append to file (curried)."""
    def inner(content):
        with open(path, 'a') as f:
            f.write(content)
        return None
    return inner

def doesFileExistIO(path):
    """Check if file exists."""
    import os
    return os.path.isfile(path)

def doesDirectoryExistIO(path):
    """Check if directory exists."""
    import os
    return os.path.isdir(path)

def getCurrentDirectoryIO():
    """Get current working directory."""
    import os
    return os.getcwd()

def getArgsIO():
    """Get command line arguments."""
    import sys
    return sys.argv[1:]

def getProgNameIO():
    """Get program name."""
    import sys
    return sys.argv[0] if sys.argv else ""

def getEnvIO(name):
    """Get environment variable."""
    import os
    return os.environ.get(name, "")

def tryGetEnvIO(name):
    """Try to get environment variable (returns Maybe)."""
    import os
    value = os.environ.get(name)
    if value is not None:
        return Some(value)
    return None_

def randomIO():
    """Get random float between 0 and 1."""
    import random
    return random.random()

def randomIntIO(min_val):
    """Get random int in range (curried)."""
    def inner(max_val):
        import random
        return random.randint(min_val, max_val)
    return inner

def randomFloatIO(min_val):
    """Get random float in range (curried)."""
    def inner(max_val):
        import random
        return random.uniform(min_val, max_val)
    return inner

def getTimeIO():
    """Get current time in seconds."""
    import time
    return time.time()

def delayIO(ms):
    """Delay for milliseconds."""
    import time
    time.sleep(ms / 1000.0)
    return None

# IO monad primitives
def pure(x):
    """Lift value into IO monad."""
    return x

def mapIO(f):
    """Map function over IO value (curried)."""
    def inner(io):
        return f(io)
    return inner

def bindIO(f):
    """Bind IO computation (curried)."""
    def inner(io):
        return f(io)
    return inner

def thenIO(io1):
    """Sequence IO computations (curried)."""
    def inner(io2):
        io1  # evaluate io1
        return io2
    return inner

def tryIO(io):
    """Try IO computation, return Result."""
    try:
        return Ok(io)
    except Exception as e:
        return Error(str(e))

def catchIO(handler):
    """Catch IO exception (curried)."""
    def inner(io):
        try:
            return io
        except Exception as e:
            return handler(e)
    return inner

def throwIO(e):
    """Throw IO exception."""
    raise RuntimeError(e)

# Update __all__
__all__.extend([
    # String primitives
    'stringLength', 'stringAt', 'stringSlice', 'charToUpper', 'charToLower', 'ord', 'chr',
    # Dict primitives
    'dictEmpty', 'dictSingleton', 'dictLookup', 'dictInsert', 'dictRemove', 
    'dictSize', 'dictToPairs', 'dictFromPairs', 'dictKeys', 'dictValues', 'dictMember',
    # Set primitives
    'setEmpty', 'setSingleton', 'setToList', 'setFromList', 'setSize', 
    'setMember', 'setInsert', 'setDelete', 'setUnion', 'setIntersection', 'setDifference',
    # Numeric primitives
    'pow', 'abs_', 'negate', 'compare',
    # Ordering
    'LT', 'EQ', 'GT',
    # IO primitives
    'printIO', 'putStrIO', 'getLineIO', 'readFileIO', 'writeFileIO', 'appendFileIO',
    'doesFileExistIO', 'doesDirectoryExistIO', 'getCurrentDirectoryIO',
    'getArgsIO', 'getProgNameIO', 'getEnvIO', 'tryGetEnvIO',
    'randomIO', 'randomIntIO', 'randomFloatIO', 'getTimeIO', 'delayIO',
    # IO monad
    'pure', 'mapIO', 'bindIO', 'thenIO', 'tryIO', 'catchIO', 'throwIO',
])
