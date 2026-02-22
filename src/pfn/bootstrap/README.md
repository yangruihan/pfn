# Pfn Bootstrap Compiler

This directory contains the self-hosted Pfn compiler - a complete implementation of the Pfn compiler written in Pfn itself.

## Overview

The bootstrap compiler implements all major components needed to compile Pfn code to Python:

- **Token.pfn** - Token type definitions and keyword lookup
- **Lexer.pfn** - Lexical analysis (tokenization)
- **AST.pfn** - Abstract Syntax Tree definitions
- **Parser.pfn** - Syntax analysis (parsing)
- **Types.pfn** - Type representation and unification
- **TypeChecker.pfn** - Type inference and checking
- **Codegen.pfn** - Python code generation
- **Tests.pfn** - Test suite for all components
- **Main.pfn** - Compiler entry point

## Architecture

```
Source Code (Pfn)
      │
      ▼
┌─────────────┐
│   Lexer     │  Tokenization
└─────────────┘
      │
      ▼
┌─────────────┐
│   Parser    │  Parse tokens to AST
└─────────────┘
      │
      ▼
┌─────────────┐
│ TypeChecker │  Type inference
└─────────────┘
      │
      ▼
┌─────────────┐
│   Codegen   │  Generate Python
└─────────────┘
      │
      ▼
Python Code
```

## Components

### Token.pfn

Defines all token types used by the lexer:
- Literals: INT, FLOAT, STRING, CHAR
- Keywords: def, let, if, match, type, etc.
- Operators: +, -, *, /, ::, ++, etc.
- Punctuation: (, ), [, ], {, }, etc.

### Lexer.pfn

Converts source code text into tokens:
- String tokenization with escape sequences
- Number parsing (integers and floats)
- Identifier and keyword recognition
- Operator and punctuation handling
- Comment filtering

### AST.pfn

Defines the Abstract Syntax Tree:
- Type references (Simple, Fun, Tuple, Record)
- Patterns (Int, String, Var, List, Tuple, etc.)
- Expressions (Literals, Var, Lambda, App, BinOp, etc.)
- Declarations (Def, Type, Import, Interface, etc.)
- Module structure

### Parser.pfn

Parses tokens into an AST:
- Declaration parsing (def, type, import, interface, impl, effect)
- Expression parsing with operator precedence
- Pattern parsing
- Type reference parsing
- Error handling with position information

### Types.pfn

Type system representation:
- Core types (Int, Float, String, Bool, Char, Unit)
- Type variables for inference
- Function types
- List and tuple types
- Type constructors
- Substitution and unification

### TypeChecker.pfn

Hindley-Milner type inference:
- Type inference for all expressions
- Pattern type inference
- Instantiation and generalization
- Unification with occurs check
- Error reporting

### Codegen.pfn

Python code generation:
- Function definitions with currying
- Type declarations (dataclasses)
- Expression code generation
- Pattern matching compilation
- Do notation desugaring

## Usage

The bootstrap compiler can be used to compile Pfn source code:

```pfn
import Bootstrap.Main (compile)

def result = compile("def add x y = x + y")
-- Result: Ok("def add(x): return lambda y: x + y")
```

## Testing

Run the test suite:

```pfn
import Bootstrap.Tests (runTests, printResults)

def main = printResults(runTests)
```

## Bootstrap Process

The bootstrap process involves:

1. **Phase 1**: Write the compiler in Python (completed)
2. **Phase 2**: Write the compiler in Pfn (this directory)
3. **Phase 3**: Use the Python compiler to compile the Pfn compiler
4. **Phase 4**: Use the compiled Pfn compiler to compile itself
5. **Phase 5**: Verify both compilers produce identical output

## Status

The bootstrap compiler is feature-complete for the core language:

- ✅ Lexer - Full tokenization support
- ✅ Parser - Complete syntax support
- ✅ Type Checker - Hindley-Milner inference
- ✅ Codegen - Python code generation
- ✅ Tests - Comprehensive test suite

## Future Work

- Effect system integration
- GADT support in type checker
- Optimization passes
- Better error messages
- Source map generation
