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

def compile(source):
    return (lambda __match_val: (Err('Lexer error: ' + __match_val._field0.message) if isinstance(__match_val, Err) else (lambda __match_val: (Err('Parser error: ' + errorToString(__match_val._field0)) if isinstance(__match_val, Err) else (lambda typeCheckResult: (lambda __match_val: (Err('Type error: ' + __match_val._field0.message) if isinstance(__match_val, Err) else (lambda pythonCode: Ok(pythonCode))(generateModule(__match_val._field0))))(typeCheckResult))(typeCheckModule(__match_val._field0))))(parse(__match_val._field0))))(tokenize(source))

def typeCheckModule(mod):
    return typeCheckDecls(mod.declarations)(initTypeChecker)

def typeCheckDecls(decls): return lambda state: (lambda __match_val: (Ok(None) if __match_val == [] else (lambda __match_val: (typeCheckDecls(rest)(state) if isinstance(__match_val, Ok) else (Err(__match_val._field0) if isinstance(__match_val, Err) else typeCheckDecls(rest)(state))))(inferLetFunc(state)(emptySubst)(data.name)(data.params)(data.body)(UnitLit))))(decls)

def compileAndPrint(source):
    return (lambda __match_val: ('Generated Python:\n' + __match_val._field0 if isinstance(__match_val, Ok) else 'Error: ' + __match_val._field0))(compile(source))

# Disabled to avoid infinite loop during import
# example = (lambda source: compileAndPrint(source))('def add x y = x + y')
example = ''

main = 'Pfn Bootstrap Compiler\n\n' + example