from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from dataclasses import dataclass
from typing import Union

class TInt:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TFloat:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TString:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TBool:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TChar:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class TUnit:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

@dataclass
class TVar:
    _field0: TVarData

@dataclass
class TFun:
    _field0: TFunData

@dataclass
class TList:
    _field0: TListData

@dataclass
class TTuple:
    _field0: TTupleData

@dataclass
class TCon:
    _field0: TConData

Type = Union[TInt, TFloat, TString, TBool, TChar, TUnit, TVar, TFun, TList, TTuple, TCon]
TInt = TInt()
TFloat = TFloat()
TString = TString()
TBool = TBool()
TChar = TChar()
TUnit = TUnit()

from dataclasses import dataclass

@dataclass
class TVarData:
    name: str

from dataclasses import dataclass

@dataclass
class TFunData:
    param: Type
    result: Type

from dataclasses import dataclass

@dataclass
class TListData:
    elem: Type

from dataclasses import dataclass

@dataclass
class TTupleData:
    elements: list[Type]

from dataclasses import dataclass

@dataclass
class TConData:
    name: str
    args: list[Type]

from dataclasses import dataclass

@dataclass
class Scheme:
    vars: list[str]
    typ: Type

from dataclasses import dataclass

@dataclass
class TypeEnv:
    bindings: Dict[str, Scheme]

emptyEnv = Record({"bindings": Dict.empty()})

def extendEnv(env): return lambda name: lambda scheme: Record({"bindings": Dict.insert(name)(scheme)(env.bindings)})

def lookupEnv(env): return lambda name: Dict.lookup(name)(env.bindings)

from dataclasses import dataclass

@dataclass
class Subst:
    mapping: Dict[str, Type]

emptySubst = Record({"mapping": Dict.empty()})

def singletonSubst(name): return lambda t: Record({"mapping": Dict.singleton(name)(t)})

def applySubst(subst): return lambda t: (lambda __match_val: (TInt if __match_val is TInt else (TFloat if __match_val is TFloat else (TString if __match_val is TString else (TBool if __match_val is TBool else (TChar if __match_val is TChar else (TUnit if __match_val is TUnit else (lambda __match_val: (applySubst(subst)(__match_val._field0) if isinstance(__match_val, Just) else (t if __match_val is Nothing else (TFun(Record({"param": applySubst(subst)(__match_val._field0.param), "result": applySubst(subst)(__match_val._field0.result)})) if isinstance(__match_val, TFun) else (TList(Record({"elem": applySubst(subst)(__match_val._field0.elem)})) if isinstance(__match_val, TList) else (TTuple(Record({"elements": List.map(lambda x: applySubst(subst)(x))(__match_val._field0.elements)})) if isinstance(__match_val, TTuple) else TCon(Record({"name": __match_val._field0.name, "args": List.map(lambda x: applySubst(subst)(x))(__match_val._field0.args)}))))))))(Dict.lookup(__match_val._field0.name)(subst.mapping)))))))))(t)

def composeSubst(s1): return lambda s2: (lambda applied: Record({"mapping": Dict.merge(s1.mapping)(applied)}))(Dict.map(lambda _: lambda v: applySubst(s1)(v))(s2.mapping))

def freeVars(t):
    return (lambda __match_val: (Set.empty() if __match_val is TInt else (Set.empty() if __match_val is TFloat else (Set.empty() if __match_val is TString else (Set.empty() if __match_val is TBool else (Set.empty() if __match_val is TChar else (Set.empty() if __match_val is TUnit else (Set.singleton(__match_val._field0.name) if isinstance(__match_val, TVar) else (Set.union(freeVars(__match_val._field0.param))(freeVars(__match_val._field0.result)) if isinstance(__match_val, TFun) else (freeVars(__match_val._field0.elem) if isinstance(__match_val, TList) else (List.foldl(lambda acc: lambda x: Set.union(acc)(freeVars(x)))(Set.empty())(__match_val._field0.elements) if isinstance(__match_val, TTuple) else List.foldl(lambda acc: lambda x: Set.union(acc)(freeVars(x)))(Set.empty())(__match_val._field0.args))))))))))))(t)

def freeVarsScheme(scheme):
    return Set.difference(freeVars(scheme.type))(Set.fromList(scheme.vars))

def freeVarsEnv(env):
    return Dict.foldl(lambda acc: lambda _: lambda scheme: Set.union(acc)(freeVarsScheme(scheme)))(Set.empty())(env.bindings)

def occursIn(name): return lambda t: Set.member(name)(freeVars(t))

def unify(t1): return lambda t2: (lambda __match_val: (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TInt and __match_val[1] is TInt else (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TFloat and __match_val[1] is TFloat else (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TString and __match_val[1] is TString else (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TBool and __match_val[1] is TBool else (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TChar and __match_val[1] is TChar else (Just(emptySubst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] is TUnit and __match_val[1] is TUnit else (Just(emptySubst) if __match_val[0]._field0.name == __match_val[1]._field0.name else Just(singletonSubst(__match_val[0]._field0.name)(t2)) if isinstance(__match_val, tuple) and len(__match_val) == 2 and isinstance(__match_val[0], TVar) and isinstance(__match_val[1], TVar) else (Nothing if occursIn(__match_val[0]._field0.name)(t2) else Just(singletonSubst(__match_val[0]._field0.name)(t2)) if isinstance(__match_val, tuple) and len(__match_val) == 2 and isinstance(__match_val[0], TVar) else (Nothing if occursIn(__match_val[1]._field0.name)(t1) else Just(singletonSubst(__match_val[1]._field0.name)(t1)) if isinstance(__match_val, tuple) and len(__match_val) == 2 and isinstance(__match_val[1], TVar) else (lambda __match_val: (lambda t1Result: (lambda t2Result: (lambda __match_val: (Just(composeSubst(__match_val._field0)(__match_val._field0)) if isinstance(__match_val, Just) else (Nothing if __match_val is Nothing else (Nothing if __match_val is Nothing else (unify(__match_val[0]._field0.elem)(__match_val[1]._field0.elem) if isinstance(__match_val, tuple) and len(__match_val) == 2 and isinstance(__match_val[0], TList) and isinstance(__match_val[1], TList) else (unifyList(__match_val[0]._field0.elements)(__match_val[1]._field0.elements)(emptySubst) if List.length(__match_val[0]._field0.elements) == List.length(__match_val[1]._field0.elements) else Nothing if isinstance(__match_val, tuple) and len(__match_val) == 2 and isinstance(__match_val[0], TTuple) and isinstance(__match_val[1], TTuple) else Nothing))))))(unify(t1Result)(t2Result)))(applySubst(__match_val._field0)(__match_val[1]._field0.result)))(applySubst(__match_val._field0)(__match_val[0]._field0.result)))(unify(__match_val[0]._field0.param)(__match_val[1]._field0.param))))))))))))((t1, t2))

def unifyList(ts1): return lambda ts2: lambda subst: (lambda __match_val: (Just(subst) if isinstance(__match_val, tuple) and len(__match_val) == 2 and __match_val[0] == [] and __match_val[1] == [] else (lambda __match_val: (unifyList(__match_val[0][1:])(__match_val[1][1:])(composeSubst(__match_val._field0)(subst)) if isinstance(__match_val, Just) else (Nothing if __match_val is Nothing else Nothing)))(unify(applySubst(subst)(__match_val[0][0]))(applySubst(subst)(__match_val[1][0])))))((ts1, ts2))

def tVar(name):
    return TVar(Record({"name": name}))

def tFun(param): return lambda result: TFun(Record({"param": param, "result": result}))

def tList(elem):
    return TList(Record({"elem": elem}))

def tTuple(elements):
    return TTuple(Record({"elements": elements}))

def tCon(name): return lambda args: TCon(Record({"name": name, "args": args}))

def monoScheme(t):
    return Record({"vars": [], "typ": t})

def polyScheme(vars): return lambda t: Record({"vars": vars, "typ": t})

def typeToString(t):
    return (lambda __match_val: ('Int' if __match_val is TInt else ('Float' if __match_val is TFloat else ('String' if __match_val is TString else ('Bool' if __match_val is TBool else ('Char' if __match_val is TChar else ('()' if __match_val is TUnit else (__match_val._field0.name if isinstance(__match_val, TVar) else ((lambda paramStr: paramStr + ' -> ' + typeToString(__match_val._field0.result))((lambda __match_val: ('(' + typeToString(__match_val._field0.param) + ')' if isinstance(__match_val, TFun) else typeToString(__match_val._field0.param)))(__match_val._field0.param)) if isinstance(__match_val, TFun) else ('[' + typeToString(__match_val._field0.elem) + ']' if isinstance(__match_val, TList) else ((lambda elems: '(' + elems + ')')(String.join(', ')(List.map(typeToString)(__match_val._field0.elements))) if isinstance(__match_val, TTuple) else __match_val._field0.name if List.isEmpty(__match_val._field0.args) else __match_val._field0.name + ' ' + String.join(' ')(List.map(typeToString)(__match_val._field0.args)))))))))))))(t)
