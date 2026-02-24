from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from bootstrap.Token import Span

from dataclasses import dataclass
from typing import Union

@dataclass
class SimpleTypeRef:
    _field0: SimpleTypeRefData

@dataclass
class FunTypeRef:
    _field0: FunTypeRefData

@dataclass
class TupleTypeRef:
    _field0: TupleTypeRefData

@dataclass
class RecordTypeRef:
    _field0: RecordTypeRefData

TypeRef = Union[SimpleTypeRef, FunTypeRef, TupleTypeRef, RecordTypeRef]

class SimpleTypeRefData(Record):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

class FunTypeRefData(Record):
    def __init__(self, param, result):
        super().__init__()
        self.param = param
        self.result = result

class TupleTypeRefData(Record):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

class RecordTypeRefData(Record):
    def __init__(self, fields):
        super().__init__()
        self.fields = fields

class Param(Record):
    def __init__(self, name, typeAnnotation):
        super().__init__()
        self.name = name
        self.typeAnnotation = typeAnnotation

from dataclasses import dataclass
from typing import Union

@dataclass
class IntPattern:
    _field0: int

@dataclass
class FloatPattern:
    _field0: float

@dataclass
class StringPattern:
    _field0: str

@dataclass
class CharPattern:
    _field0: Char

@dataclass
class BoolPattern:
    _field0: bool

@dataclass
class VarPattern:
    _field0: str

class WildcardPattern:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

@dataclass
class ConsPattern:
    _field0: ConsPatternData

@dataclass
class ListPattern:
    _field0: list[Pattern]

@dataclass
class TuplePattern:
    _field0: list[Pattern]

@dataclass
class RecordPattern:
    _field0: list[tuple[str, Pattern]]

@dataclass
class ConstructorPattern:
    _field0: ConstructorPatternData

Pattern = Union[IntPattern, FloatPattern, StringPattern, CharPattern, BoolPattern, VarPattern, WildcardPattern, ConsPattern, ListPattern, TuplePattern, RecordPattern, ConstructorPattern]
WildcardPattern = WildcardPattern()

class ConsPatternData(Record):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail

class ConstructorPatternData(Record):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

from dataclasses import dataclass
from typing import Union

@dataclass
class IntLit:
    _field0: int

@dataclass
class FloatLit:
    _field0: float

@dataclass
class StringLit:
    _field0: str

@dataclass
class CharLit:
    _field0: Char

@dataclass
class BoolLit:
    _field0: bool

class UnitLit:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

@dataclass
class Var:
    _field0: str

@dataclass
class Lambda:
    _field0: LambdaData

@dataclass
class App:
    _field0: AppData

@dataclass
class BinOp:
    _field0: BinOpData

@dataclass
class UnaryOp:
    _field0: UnaryOpData

@dataclass
class If:
    _field0: IfData

@dataclass
class Let:
    _field0: LetData

@dataclass
class LetFunc:
    _field0: LetFuncData

@dataclass
class Match:
    _field0: MatchData

@dataclass
class DoNotation:
    _field0: DoNotationData

@dataclass
class ListLit:
    _field0: list[Expr]

@dataclass
class TupleLit:
    _field0: list[Expr]

@dataclass
class RecordLit:
    _field0: list[RecordField]

@dataclass
class FieldAccess:
    _field0: FieldAccessData

@dataclass
class RecordUpdate:
    _field0: RecordUpdateData

@dataclass
class IndexAccess:
    _field0: IndexAccessData

@dataclass
class Slice:
    _field0: SliceData

@dataclass
class HandleExpr:
    _field0: HandleExprData

@dataclass
class PerformExpr:
    _field0: PerformExprData

Expr = Union[IntLit, FloatLit, StringLit, CharLit, BoolLit, UnitLit, Var, Lambda, App, BinOp, UnaryOp, If, Let, LetFunc, Match, DoNotation, ListLit, TupleLit, RecordLit, FieldAccess, RecordUpdate, IndexAccess, Slice, HandleExpr, PerformExpr]
UnitLit = UnitLit()

class LambdaData(Record):
    def __init__(self, params, body):
        super().__init__()
        self.params = params
        self.body = body

class AppData(Record):
    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args

class BinOpData(Record):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

class UnaryOpData(Record):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

class IfData(Record):
    def __init__(self, cond, thenBranch, elseBranch):
        super().__init__()
        self.cond = cond
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

class LetData(Record):
    def __init__(self, name, value, body):
        super().__init__()
        self.name = name
        self.value = value
        self.body = body

class LetFuncData(Record):
    def __init__(self, name, params, value, body):
        super().__init__()
        self.name = name
        self.params = params
        self.value = value
        self.body = body

class MatchData(Record):
    def __init__(self, scrutinee, cases):
        super().__init__()
        self.scrutinee = scrutinee
        self.cases = cases

class MatchCase(Record):
    def __init__(self, pattern, body, guard):
        super().__init__()
        self.pattern = pattern
        self.body = body
        self.guard = guard

class DoNotationData(Record):
    def __init__(self, bindings, body):
        super().__init__()
        self.bindings = bindings
        self.body = body

class DoBinding(Record):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

class RecordField(Record):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

class FieldAccessData(Record):
    def __init__(self, expr, field):
        super().__init__()
        self.expr = expr
        self.field = field

class RecordUpdateData(Record):
    def __init__(self, record, updates):
        super().__init__()
        self.record = record
        self.updates = updates

class IndexAccessData(Record):
    def __init__(self, expr, index):
        super().__init__()
        self.expr = expr
        self.index = index

class SliceData(Record):
    def __init__(self, expr, start, end, step):
        super().__init__()
        self.expr = expr
        self.start = start
        self.end = end
        self.step = step

class HandleExprData(Record):
    def __init__(self, expr, handlerCases, handlerName):
        super().__init__()
        self.expr = expr
        self.handlerCases = handlerCases
        self.handlerName = handlerName

class PerformExprData(Record):
    def __init__(self, effectName, opName, args):
        super().__init__()
        self.effectName = effectName
        self.opName = opName
        self.args = args

from dataclasses import dataclass
from typing import Union

@dataclass
class DefDecl:
    _field0: DefDeclData

@dataclass
class TypeDecl:
    _field0: TypeDeclData

@dataclass
class TypeAliasDecl:
    _field0: TypeAliasDeclData

@dataclass
class ImportDecl:
    _field0: ImportDeclData

@dataclass
class ExportDecl:
    _field0: ExportDeclData

@dataclass
class InterfaceDecl:
    _field0: InterfaceDeclData

@dataclass
class ImplDecl:
    _field0: ImplDeclData

@dataclass
class EffectDecl:
    _field0: EffectDeclData

@dataclass
class HandlerDecl:
    _field0: HandlerDeclData

Decl = Union[DefDecl, TypeDecl, TypeAliasDecl, ImportDecl, ExportDecl, InterfaceDecl, ImplDecl, EffectDecl, HandlerDecl]

class DefDeclData(Record):
    def __init__(self, name, params, body, returnType, isExported, exportName):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
        self.returnType = returnType
        self.isExported = isExported
        self.exportName = exportName

class TypeDeclData(Record):
    def __init__(self, name, params, constructors, isRecord, recordFields, isGadt):
        super().__init__()
        self.name = name
        self.params = params
        self.constructors = constructors
        self.isRecord = isRecord
        self.recordFields = recordFields
        self.isGadt = isGadt

class Constructor(Record):
    def __init__(self, name, fields):
        super().__init__()
        self.name = name
        self.fields = fields

class GADTConstructor(Record):
    def __init__(self, name, params, resultType):
        super().__init__()
        self.name = name
        self.params = params
        self.resultType = resultType

class TypeAliasDeclData(Record):
    def __init__(self, name, params, typeRef):
        super().__init__()
        self.name = name
        self.params = params
        self.typeRef = typeRef

class ImportDeclData(Record):
    def __init__(self, module, alias, exposing, isPython):
        super().__init__()
        self.module = module
        self.alias = alias
        self.exposing = exposing
        self.isPython = isPython

class ExportDeclData(Record):
    def __init__(self, names):
        super().__init__()
        self.names = names

class InterfaceDeclData(Record):
    def __init__(self, name, params, methods, superclasses):
        super().__init__()
        self.name = name
        self.params = params
        self.methods = methods
        self.superclasses = superclasses

class InterfaceMethod(Record):
    def __init__(self, name, typ):
        super().__init__()
        self.name = name
        self.typ = typ

class ImplDeclData(Record):
    def __init__(self, className, typeRef, methods):
        super().__init__()
        self.className = className
        self.typeRef = typeRef
        self.methods = methods

class ImplMethod(Record):
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

class EffectDeclData(Record):
    def __init__(self, name, operations):
        super().__init__()
        self.name = name
        self.operations = operations

class EffectOp(Record):
    def __init__(self, name, typ):
        super().__init__()
        self.name = name
        self.typ = typ

class HandlerDeclData(Record):
    def __init__(self, effectName, handlers, returnType):
        super().__init__()
        self.effectName = effectName
        self.handlers = handlers
        self.returnType = returnType

class HandlerCase(Record):
    def __init__(self, opName, body, params, resumeParam):
        super().__init__()
        self.opName = opName
        self.body = body
        self.params = params
        self.resumeParam = resumeParam

class Module(Record):
    def __init__(self, name, declarations):
        super().__init__()
        self.name = name
        self.declarations = declarations

def simpleType(name):
    return SimpleTypeRef(SimpleTypeRefData(name, []))

def typeApp(name): return lambda args: SimpleTypeRef(SimpleTypeRefData(name, args))

def funType(param): return lambda result: FunTypeRef(FunTypeRefData(param, result))

def tupleType(elements):
    return TupleTypeRef(TupleTypeRefData(elements))

def recordType(fields):
    return RecordTypeRef(RecordTypeRefData(fields))

def param(name):
    return Param(name, Nothing)

def typedParam(name): return lambda typeRef: Param(name, Just(typeRef))

def var(name):
    return Var(name)

def intLit(value):
    return IntLit(value)

def floatLit(value):
    return FloatLit(value)

def stringLit(value):
    return StringLit(value)

def boolLit(value):
    return BoolLit(value)

def binOp(left): return lambda op: lambda right: BinOp(BinOpData(left, op, right))

def app(func): return lambda args: App(AppData(func, args))

def _lambda_(params): return lambda body: Lambda(LambdaData(params, body))

def ifExpr(cond): return lambda thenBranch: lambda elseBranch: If(IfData(cond, thenBranch, elseBranch))

def letExpr(name): return lambda value: lambda body: Let(LetData(name, value, body))

def matchExpr(scrutinee): return lambda cases: Match(MatchData(scrutinee, cases))

def matchCase(pattern): return lambda body: MatchCase(pattern, body, Nothing)

def matchCaseWithGuard(pattern): return lambda body: lambda guard: MatchCase(pattern, body, Just(guard))

def listLit(elements):
    return ListLit(elements)

def tupleLit(elements):
    return TupleLit(elements)

def recordLit(fields):
    return RecordLit(fields)

def recordField(name): return lambda value: DoBinding(name, value)

def fieldAccess(expr): return lambda field: FieldAccess(FieldAccessData(expr, field))

def defDecl(name): return lambda params: lambda body: DefDecl(DefDeclData(name, params, body, Nothing, False, Nothing))

def typeDecl(name): return lambda params: lambda constructors: TypeDecl(TypeDeclData(name, params, constructors, False, [], False))

def constructor(name): return lambda fields: Constructor(name, fields)

def importDecl(module):
    return ImportDecl(ImportDeclData(module, Nothing, Nothing, False))

def pythonImport(module):
    return ImportDecl(ImportDeclData(module, Nothing, Nothing, True))

emptyModule = Module(Nothing, [])

def addDecl(decl): return lambda mod: Record({**mod, "declarations": mod.declarations + [decl]})

def setModuleName(name): return lambda mod: Record({**mod, "name": Just(name)})