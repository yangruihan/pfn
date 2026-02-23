from __future__ import annotations

from stdlib import String, List, Dict, Set, Maybe, Result, Just, Nothing, Ok, Err, Record

from stdlib import reverse, _not_

from bootstrap.Token import *

from bootstrap.Lexer import *

from bootstrap.AST import *

from bootstrap.Parser import *

from bootstrap.Types import *

from bootstrap.TypeChecker import *

from bootstrap.Codegen import *

from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str

def testResult(name): return lambda passed: lambda message: Record({"name": name, "passed": passed, "message": message})

def _pass_(name):
    return testResult(name)(True)('OK')

def fail(name): return lambda message: testResult(name)(False)(message)

testKeywords = (lambda kw: (lambda __match_val: (_pass_('keywords lookup') if isinstance(__match_val, Just) and isinstance(__match_val._field0, KW_DEF) else fail('keywords lookup')("Expected KW_DEF for 'def'")))(kw))(lookupKeyword('def'))

testTokenCreation = (lambda span: (lambda tok: _pass_('token creation') if tok.tokenType == IDENT and getTokenString(tok) == 'foo' else fail('token creation')('Token not created correctly'))(stringToken(IDENT)('foo')(span)))(makeSpan(0)(3)(1)(1))

testLexerSimple = (lambda tokens: (lambda __match_val: ((lambda __match_val: (_pass_('lexer simple') if __match_val._field0.tokenType == KW_DEF else fail('lexer simple')('First token should be KW_DEF') if isinstance(__match_val, Just) else fail('lexer simple')('No tokens')))(List.getAt(0)(__match_val._field0)) if List.length(__match_val._field0) >= 4 else fail('lexer simple')('Expected at least 4 tokens') if isinstance(__match_val, Ok) else fail('lexer simple')('Lexer error')))(tokens))(tokenize('def foo = 42'))

testLexerString = (lambda tokens: (lambda __match_val: (lambda __match_val: (_pass_('lexer string') if __match_val._field0.tokenType == STRING and getTokenString(__match_val._field0) == 'hello world' else fail('lexer string')('String not lexed correctly') if isinstance(__match_val, Just) else (fail('lexer string')('No tokens') if isinstance(__match_val, Nothing) else fail('lexer string')('Lexer error'))))(List.getAt(0)(__match_val._field0)))(tokens))(tokenize('"hello world"'))

testLexerOperators = (lambda tokens: (lambda __match_val: (_pass_('lexer operators') if List.length(__match_val._field0) >= 5 else fail('lexer operators')('Not enough operator tokens') if isinstance(__match_val, Ok) else fail('lexer operators')('Lexer error')))(tokens))(tokenize('-> => :: ++ ||'))

testParseInt = (lambda tokens: (lambda __match_val: (lambda __match_val: (_pass_('parse int - empty module') if List.isEmpty(__match_val._field0.declarations) else fail('parse int')('Expected empty module for lone int') if isinstance(__match_val, Ok) else (fail('parse int')(errorToString(__match_val._field0)) if isinstance(__match_val, Err) else fail('parse int')('Lexer error'))))(parse(__match_val._field0)))(tokens))(tokenize('42'))

testParseDef = (lambda tokens: (lambda __match_val: (lambda __match_val: fail('parse def')('Expected one declaration') if List.isEmpty(__match_val._field0.declarations) else (lambda __match_val: (_pass_('parse def') if __match_val._field0._field0.name == 'add' and List.length(__match_val._field0._field0.params) == 2 else fail('parse def')('Function not parsed correctly') if isinstance(__match_val, Just) and isinstance(__match_val._field0, DefDecl) else fail('parse def')('Expected DefDecl')))(List.getAt(0)(__match_val._field0.declarations)))(parse(__match_val._field0)))(tokens))(tokenize('def add x y = x + y'))

testParseLambda = (lambda tokens: (lambda __match_val: (lambda __match_val: (lambda __match_val: (_pass_('parse lambda') if List.length(__match_val._field0.params) == 1 else fail('parse lambda')('Lambda params incorrect') if isinstance(__match_val, Lambda) else fail('parse lambda')('Expected Lambda')))(__match_val._field0[0]))(parseExpr(initParser(__match_val._field0))))(tokens))(tokenize('fn x => x + 1'))

testParseList = (lambda tokens: (lambda __match_val: (lambda __match_val: (lambda __match_val: (_pass_('parse list') if List.length(__match_val._field0) == 3 else fail('parse list')('List length incorrect') if isinstance(__match_val, ListLit) else fail('parse list')('Expected ListLit')))(__match_val._field0[0]))(parseExpr(initParser(__match_val._field0))))(tokens))(tokenize('[1, 2, 3]'))

testUnifyInt = (lambda __match_val: (_pass_('unify int') if isinstance(__match_val, Just) else fail('unify int')('Int should unify with Int')))(unify(TInt)(TInt))

testUnifyVar = (lambda tv: (lambda __match_val: (lambda result: (lambda __match_val: (_pass_('unify var') if isinstance(__match_val, TInt) else fail('unify var')('Variable should be substituted to Int')))(result))(applySubst(__match_val._field0)(tv)))(unify(tv)(TInt)))(tVar('a'))

testUnifyFun = (lambda t1: (lambda t2: (lambda __match_val: (lambda result: (lambda __match_val: (_pass_('unify fun') if isinstance(__match_val, TString) else fail('unify fun')('Type variable should be String')))(result))(applySubst(__match_val._field0)(tVar('a'))))(unify(t1)(t2)))(tFun(TInt)(TString)))(tFun(TInt)(tVar('a')))

testFreeVars = (lambda t: (lambda fv: _pass_('free vars') if Set.member('a')(fv) and Set.member('b')(fv) else fail('free vars')('Should have a and b as free vars'))(freeVars(t)))(tFun(tVar('a'))(tVar('b')))

testInferInt = (lambda state: (lambda __match_val: (lambda __match_val: (_pass_('infer int') if isinstance(__match_val, TInt) else fail('infer int')('Expected Int type')))(__match_val._field0.type))(infer(state)(IntLit(42))))(initTypeChecker)

testInferString = (lambda state: (lambda __match_val: (lambda __match_val: (_pass_('infer string') if isinstance(__match_val, TString) else fail('infer string')('Expected String type')))(__match_val._field0.type))(infer(state)(StringLit('hello'))))(initTypeChecker)

testInferLambda = (lambda state: (lambda expr: (lambda __match_val: (lambda __match_val: (_pass_('infer lambda') if isinstance(__match_val, TFun) else fail('infer lambda')('Expected function type')))(__match_val._field0.type))(infer(state)(expr)))(Lambda(Record({"params": [param('x')], "body": Var('x')}))))(initTypeChecker)

testInferList = (lambda state: (lambda expr: (lambda __match_val: (lambda __match_val: (lambda __match_val: (_pass_('infer list') if isinstance(__match_val, TInt) else fail('infer list')('Expected Int element type')))(__match_val._field0.elem))(__match_val._field0.type))(infer(state)(expr)))(ListLit([IntLit(1), IntLit(2), IntLit(3)])))(initTypeChecker)

testCodegenInt = (lambda code: _pass_('codegen int') if code == '42' else fail('codegen int')("Expected '42', got: " + code))(generateExpr(IntLit(42)))

testCodegenString = (lambda code: _pass_('codegen string') if code == '"hello"' else fail('codegen string')('Expected \'"hello"\', got: ' + code))(generateExpr(StringLit('hello')))

testCodegenLambda = (lambda expr: (lambda code: _pass_('codegen lambda') if code == 'lambda x: x' else fail('codegen lambda')("Expected 'lambda x: x', got: " + code))(generateExpr(expr)))(Lambda(Record({"params": [param('x')], "body": Var('x')})))

testCodegenList = (lambda expr: (lambda code: _pass_('codegen list') if code == '[1, 2, 3]' else fail('codegen list')("Expected '[1, 2, 3]', got: " + code))(generateExpr(expr)))(ListLit([IntLit(1), IntLit(2), IntLit(3)]))

testCodegenBinOp = (lambda expr: (lambda code: _pass_('codegen binop') if code == '1 + 2' else fail('codegen binop')("Expected '1 + 2', got: " + code))(generateExpr(expr)))(BinOp(Record({"left": IntLit(1), "op": '+', "right": IntLit(2)})))

testCodegenIf = (lambda expr: (lambda code: _pass_('codegen if') if code == '1 if x else 0' else fail('codegen if')("Expected '1 if x else 0', got: " + code))(generateExpr(expr)))(If(Record({"cond": Var('x'), "thenBranch": IntLit(1), "elseBranch": IntLit(0)})))

runTests = [testKeywords, testTokenCreation, testLexerSimple, testLexerString, testLexerOperators, testParseInt, testParseDef, testParseLambda, testParseList, testUnifyInt, testUnifyVar, testUnifyFun, testFreeVars, testInferInt, testInferString, testInferLambda, testInferList, testCodegenInt, testCodegenString, testCodegenLambda, testCodegenList, testCodegenBinOp, testCodegenIf]

def countPassed(results):
    return List.foldl(lambda acc: lambda r: acc + 1 if r.passed else acc)(0)(results)

def printResults(results):
    return (lambda passed: (lambda total: (lambda header: (lambda details: header + details)(String.join('\n')(List.map(formatResult)(results))))('Bootstrap Tests: ' + toString(passed) + '/' + toString(total) + ' passed\n'))(List.length(results)))(countPassed(results))

def formatResult(r):
    return '  ✓ ' + r.name if r.passed else '  ✗ ' + r.name + ': ' + r.message

main = printResults(runTests)