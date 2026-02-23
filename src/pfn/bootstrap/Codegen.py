from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from bootstrap.AST import *

def generateModule(mod):
    return generateDecls(mod.declarations)([])

def generateDecls(decls): return lambda lines: (lambda __match_val: (String.join('\n\n')(List.reverse(lines)) if __match_val == [] else (lambda code: generateDecls(__match_val[1:])(lines) if code == '' else generateDecls(__match_val[1:])([code] + lines))(generateDecl(__match_val[0]))))(decls)

def generateDecl(decl):
    return (lambda __match_val: (generateDefDecl(__match_val._field0) if isinstance(__match_val, DefDecl) else (generateTypeDecl(__match_val._field0) if isinstance(__match_val, TypeDecl) else (generateImportDecl(__match_val._field0) if isinstance(__match_val, ImportDecl) else ''))))(decl)

def generateDefDecl(decl):
    return (lambda paramsStr: (lambda bodyCode: (lambda funcDef: (lambda exportName: funcDef + '\n\n' + exportName + ' = ' + decl.name)((lambda __match_val: (__match_val._field0 if isinstance(__match_val, Just) else decl.name))(decl.exportName)) if decl.isExported else funcDef)(generateFuncDef(decl.name)(decl.params)(bodyCode)))(generateExpr(decl.body)))(generateParams(decl.params))

def generateParams(params):
    return String.join(', ')(List.map(lambda p: p.name)(params))

def generateFuncDef(name): return lambda params: lambda bodyCode: (lambda __match_val: ('def ' + name + '():\n    return ' + bodyCode if __match_val == [] else ('def ' + name + '(' + __match_val[0].name + '):\n    return ' + bodyCode if isinstance(__match_val, list) and len(__match_val) == 1 else (lambda innerBody: 'def ' + name + '(' + __match_val[0].name + '): return ' + innerBody)(generateCurriedBody(__match_val[1:])(bodyCode)))))(params)

def generateCurriedBody(params): return lambda body: (lambda __match_val: (body if __match_val == [] else generateCurriedBody(__match_val[1:])('lambda ' + __match_val[0].name + ': ' + body)))(params)

def generateTypeDecl(decl):
    return generateRecordType(decl) if decl.isRecord else generateSumType(decl)

def generateRecordType(decl):
    return (lambda header: (lambda fields: header + '\n' + String.join('\n')(fields))(generateRecordFields(decl.recordFields)([])))('from dataclasses import dataclass\n\n@dataclass\nclass ' + decl.name + ':')

def generateRecordFields(fields): return lambda lines: (lambda __match_val: (List.reverse(lines) if __match_val == [] else (lambda typeStr: generateRecordFields(__match_val[1:])(['    ' + __match_val[0][0] + ': ' + typeStr] + lines))(generateTypeRef(__match_val[0][1]))))(fields)

def generateSumType(decl):
    return (lambda header: (lambda ctors: (lambda ctorNames: (lambda unionDef: header + String.join('\n')(ctors) + unionDef)('\n' + decl.name + ' = Union[' + String.join(', ')(ctorNames) + ']'))(List.map(lambda c: c.name)(decl.constructors)))(generateConstructors(decl.constructors)([])))('from dataclasses import dataclass\nfrom typing import Union\n')

def generateConstructors(ctors): return lambda lines: (lambda __match_val: (List.reverse(lines) if __match_val == [] else (lambda ctorCode: generateConstructors(__match_val[1:])([ctorCode] + lines))(generateConstructor(__match_val[0]))))(ctors)

def generateConstructor(ctor):
    return '@dataclass\nclass ' + ctor.name + ':\n    pass\n' if List.isEmpty(ctor.fields) else (lambda fields: '@dataclass\nclass ' + ctor.name + ':\n' + String.join('\n')(fields) + '\n')(generateCtorFields(ctor.fields)(0)([]))

def generateCtorFields(fields): return lambda index: lambda lines: (lambda __match_val: (List.reverse(lines) if __match_val == [] else (lambda typeStr: (lambda fieldName: generateCtorFields(__match_val[1:])(index + 1)(['    ' + fieldName + ': ' + typeStr] + lines))('_field' + toString(index)))(generateTypeRef(__match_val[0]))))(fields)

def generateImportDecl(decl):
    return (lambda __match_val: ('import ' + decl.module + ' as ' + __match_val._field0 if isinstance(__match_val, Just) else 'import ' + decl.module))(decl.alias)

def generateTypeRef(typeRef):
    return (lambda __match_val: (generateSimpleTypeRef(__match_val._field0) if isinstance(__match_val, SimpleTypeRef) else ('Callable[[...], ...]' if isinstance(__match_val, FunTypeRef) else ((lambda elems: 'tuple[' + elems + ']')(String.join(', ')(List.map(generateTypeRef)(__match_val._field0.elements))) if isinstance(__match_val, TupleTypeRef) else 'dict'))))(typeRef)

def generateSimpleTypeRef(data):
    return (lambda name: name if List.isEmpty(data.args) else (lambda argsStr: name + '[' + argsStr + ']')(String.join(', ')(List.map(generateTypeRef)(data.args))))(mapTypeName(data.name))

def mapTypeName(name):
    return (lambda __match_val: ('int' if __match_val == 'Int' else ('float' if __match_val == 'Float' else ('str' if __match_val == 'String' else ('bool' if __match_val == 'Bool' else ('list' if __match_val == 'List' else name))))))(name)

def generateExpr(expr):
    return (lambda __match_val: (toString(__match_val._field0) if isinstance(__match_val, IntLit) else (toString(__match_val._field0) if isinstance(__match_val, FloatLit) else (reprString(__match_val._field0) if isinstance(__match_val, StringLit) else (reprChar(__match_val._field0) if isinstance(__match_val, CharLit) else ('True' if __match_val._field0 else 'False' if isinstance(__match_val, BoolLit) else ('None' if __match_val is UnitLit else (__match_val._field0 if isinstance(__match_val, Var) else (generateLambda(__match_val._field0) if isinstance(__match_val, Lambda) else (generateApp(__match_val._field0) if isinstance(__match_val, App) else (generateBinOp(__match_val._field0) if isinstance(__match_val, BinOp) else (generateUnaryOp(__match_val._field0) if isinstance(__match_val, UnaryOp) else (generateIf(__match_val._field0) if isinstance(__match_val, If) else (generateLet(__match_val._field0) if isinstance(__match_val, Let) else (generateLetFunc(__match_val._field0) if isinstance(__match_val, LetFunc) else (generateMatch(__match_val._field0) if isinstance(__match_val, Match) else (generateList(__match_val._field0) if isinstance(__match_val, ListLit) else (generateTuple(__match_val._field0) if isinstance(__match_val, TupleLit) else (generateRecord(__match_val._field0) if isinstance(__match_val, RecordLit) else (generateFieldAccess(__match_val._field0) if isinstance(__match_val, FieldAccess) else (generateIndexAccess(__match_val._field0) if isinstance(__match_val, IndexAccess) else (generateDo(__match_val._field0) if isinstance(__match_val, DoNotation) else ''))))))))))))))))))))))(expr)

def generateLambda(data):
    return (lambda paramsStr: (lambda bodyCode: 'lambda ' + paramsStr + ': ' + bodyCode)(generateExpr(data.body)))(String.join(', ')(List.map(lambda p: p.name)(data.params)))

def generateApp(data):
    return (lambda funcCode: (lambda argsStr: funcCode + '(' + argsStr + ')')(String.join(', ')(List.map(generateExpr)(data.args))))(generateExpr(data.func))

def generateBinOp(data):
    return (lambda leftCode: (lambda rightCode: (lambda __match_val: ('[' + leftCode + '] + ' + rightCode if __match_val == '::' else (leftCode + ' + ' + rightCode if __match_val == '++' else leftCode + ' ' + data.op + ' ' + rightCode)))(data.op))(generateExpr(data.right)))(generateExpr(data.left))

def generateUnaryOp(data):
    return (lambda operandCode: data.op + operandCode)(generateExpr(data.operand))

def generateIf(data):
    return (lambda condCode: (lambda thenCode: (lambda elseCode: thenCode + ' if ' + condCode + ' else ' + elseCode)(generateExpr(data.elseBranch)))(generateExpr(data.thenBranch)))(generateExpr(data.cond))

def generateLet(data):
    return (lambda valueCode: (lambda bodyCode: '(' + bodyCode + ' if (' + data.name + ' := ' + valueCode + ') is not None else None)')(generateExpr(data.body)))(generateExpr(data.value))

def generateLetFunc(data):
    return (lambda paramsStr: (lambda valueCode: (lambda bodyCode: '(lambda ' + paramsStr + ': ' + bodyCode + ')(' + valueCode + ')')(generateExpr(data.body)))(generateExpr(data.value)))(String.join(', ')(List.map(lambda p: p.name)(data.params)))

def generateMatch(data):
    return 'None' if List.isEmpty(data.cases) else (lambda scrutineeCode: (lambda casesCode: '(lambda __match_val: ' + casesCode + ')(' + scrutineeCode + ')')(generateMatchCases(data.cases)('__match_val')))(generateExpr(data.scrutinee))

def generateMatchCases(cases): return lambda var: (lambda __match_val: ('None' if __match_val == [] else ((lambda __let_val_0: (lambda bodyCode: bodyCode if __let_val_0[0] == 'True' else '(' + bodyCode + ' if ' + __let_val_0[0] + ' else None)')(generateExprWithBindings(__match_val[0].body)(__let_val_0[1])) if isinstance(__let_val_0, tuple) and len(__let_val_0) == 2 else None)(generatePatternCheck(__match_val[0].pattern)(var)) if isinstance(__match_val, list) and len(__match_val) == 1 else (lambda __let_val_1: (lambda bodyCode: (lambda restCode: bodyCode if __let_val_1[0] == 'True' else '(' + bodyCode + ' if ' + __let_val_1[0] + ' else ' + restCode + ')')(generateMatchCases(__match_val[1:])(var)))(generateExprWithBindings(__match_val[0].body)(__let_val_1[1])) if isinstance(__let_val_1, tuple) and len(__let_val_1) == 2 else None)(generatePatternCheck(__match_val[0].pattern)(var)))))(cases)

def generateExprWithBindings(expr): return lambda bindings: (lambda __match_val: (generateExpr(expr) if __match_val == [] else (lambda code: String.replace(__match_val[0][0])(__match_val[0][1])(code))(generateExprWithBindings(expr)(__match_val[1:]))))(bindings)

def generatePatternCheck(pattern): return lambda var: (lambda __match_val: ((var + ' == ' + toString(__match_val._field0), []) if isinstance(__match_val, IntPattern) else ((var + ' == ' + toString(__match_val._field0), []) if isinstance(__match_val, FloatPattern) else ((var + ' == ' + reprString(__match_val._field0), []) if isinstance(__match_val, StringPattern) else ((var + ' == ' + reprChar(__match_val._field0), []) if isinstance(__match_val, CharPattern) else ((var + ' is ' + 'True' if __match_val._field0 else 'False', []) if isinstance(__match_val, BoolPattern) else (('True', [(__match_val._field0, var)]) if isinstance(__match_val, VarPattern) else (('True', []) if __match_val is WildcardPattern else ((var + ' == []', []) if List.isEmpty(__match_val._field0) else ('isinstance(' + var + ', list)', []) if isinstance(__match_val, ListPattern) else ((lambda check: (lambda __let_val_3: (lambda __let_val_2: (lambda finalCheck: (lambda finalCheck2: (finalCheck2, __let_val_3[1] + __let_val_2[1]))(finalCheck if __let_val_2[0] == 'True' else finalCheck + ' and ' + __let_val_2[0]))(check if __let_val_3[0] == 'True' else check + ' and ' + __let_val_3[0]) if isinstance(__let_val_2, tuple) and len(__let_val_2) == 2 else None)(generatePatternCheck(__match_val._field0.tail)(var + '[1:]')) if isinstance(__let_val_3, tuple) and len(__let_val_3) == 2 else None)(generatePatternCheck(__match_val._field0.head)(var + '[0]')))('isinstance(' + var + ', list) and len(' + var + ') > 0') if isinstance(__match_val, ConsPattern) else ((lambda check: (lambda bindings: (check, bindings))(generateTuplePatternBindings(__match_val._field0)(var)(0)([])))('isinstance(' + var + ', tuple) and len(' + var + ') == ' + toString(List.length(__match_val._field0))) if isinstance(__match_val, TuplePattern) else ((var + ' is ' + __match_val._field0.name, []) if List.isEmpty(__match_val._field0.args) else (lambda check: (lambda bindings: (check, bindings))(generateConstructorPatternBindings(__match_val._field0.args)(var)(0)([])))('isinstance(' + var + ', ' + __match_val._field0.name + ')') if isinstance(__match_val, ConstructorPattern) else ('True', [])))))))))))))(pattern)

def generateList(elements):
    return (lambda elemsStr: '[' + elemsStr + ']')(String.join(', ')(List.map(generateExpr)(elements)))

def generateTuple(elements):
    return (lambda elemsStr: '(' + elemsStr + ')')(String.join(', ')(List.map(generateExpr)(elements)))

def generateRecord(fields):
    return (lambda fieldsStr: '{' + fieldsStr + '}')(String.join(', ')(List.map(generateRecordField)(fields)))

def generateRecordField(field):
    return '"' + field.name + '": ' + generateExpr(field.value)

def generateFieldAccess(data):
    return (lambda exprCode: exprCode + '.' + data.field)(generateExpr(data.expr))

def generateIndexAccess(data):
    return (lambda exprCode: (lambda indexCode: exprCode + '[' + indexCode + ']')(generateExpr(data.index)))(generateExpr(data.expr))

def generateDo(data):
    return (lambda bodyCode: generateDoBindings(List.reverse(data.bindings))(bodyCode))(generateExpr(data.body))

def generateDoBindings(bindings): return lambda result: (lambda __match_val: (result if __match_val == [] else (lambda valueCode: generateDoBindings(__match_val[1:])('(lambda ' + __match_val[0].name + ': ' + result + ')(' + valueCode + ')'))(generateExpr(__match_val[0].value))))(bindings)

def reprString(s):
    return '"' + escapeString(s) + '"'

def escapeString(s):
    return s

def reprChar(c):
    return "'" + toString(c) + "'"

def generateTuplePatternBindings(elements): return lambda var: lambda index: lambda bindings: (lambda __match_val: (List.reverse(bindings) if __match_val == [] else (lambda elemVar: (lambda __let_val_4: generateTuplePatternBindings(__match_val[1:])(var)(index + 1)(__let_val_4[1] + bindings) if isinstance(__let_val_4, tuple) and len(__let_val_4) == 2 else None)(generatePatternCheck(__match_val[0])(elemVar)))(var + '[' + toString(index) + ']')))(elements)

def generateConstructorPatternBindings(args): return lambda var: lambda index: lambda bindings: (lambda __match_val: (List.reverse(bindings) if __match_val == [] else (lambda argVar: (lambda __let_val_5: generateConstructorPatternBindings(__match_val[1:])(var)(index + 1)(__let_val_5[1] + bindings) if isinstance(__let_val_5, tuple) and len(__let_val_5) == 2 else None)(generatePatternCheck(__match_val[0])(argVar)))(var + '._field' + toString(index))))(args)
