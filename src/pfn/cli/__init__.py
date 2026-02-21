from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser
from pfn.parser.ast import DefDecl
from pfn.typechecker import TypeChecker, TypeError as PfnTypeError
from pfn.types import Scheme, TInt, Subst, TypeEnv, TVar, TFun


def compile_source(source: str) -> str:
    tokens = Lexer(source).tokenize()
    module = Parser(tokens).parse()
    return CodeGenerator().generate_module(module)


def typecheck_source(source: str) -> tuple[bool, str]:
    tokens = Lexer(source).tokenize()
    module = Parser(tokens).parse()

    checker = TypeChecker()
    global_env = TypeEnv()

    try:
        for decl in module.declarations:
            if isinstance(decl, DefDecl):
                checker.env = global_env

                for param in decl.params:
                    tv = checker.fresh_var()
                    checker.env = checker.env.extend(param.name, Scheme((), tv))

                t = checker.infer(decl.body)

                for param in reversed(decl.params):
                    scheme = checker.env.lookup(param.name)
                    if scheme:
                        t = TFun(scheme.type, t)

                subst = Subst()
                free_in_env = subst.free_vars_env(global_env)
                free_in_t = subst.free_vars(t)
                gen_vars = tuple(sorted(free_in_t - free_in_env))
                scheme = Scheme(gen_vars, t)

                global_env = global_env.extend(decl.name, scheme)
                print(f"{decl.name} : {t}")
        return True, "Type check passed"
    except PfnTypeError as e:
        return False, f"Type error: {e}"


def run_source(source: str, typecheck: bool = False) -> None:
    tokens = Lexer(source).tokenize()
    module = Parser(tokens).parse()

    if typecheck:
        checker = TypeChecker()
        global_env = TypeEnv()

        for decl in module.declarations:
            if isinstance(decl, DefDecl):
                checker.env = global_env

                for param in decl.params:
                    tv = checker.fresh_var()
                    checker.env = checker.env.extend(param.name, Scheme((), tv))

                t = checker.infer(decl.body)

                for param in reversed(decl.params):
                    scheme = checker.env.lookup(param.name)
                    if scheme:
                        t = TFun(scheme.type, t)

                subst = Subst()
                free_in_env = subst.free_vars_env(global_env)
                free_in_t = subst.free_vars(t)
                gen_vars = tuple(sorted(free_in_t - free_in_env))
                scheme = Scheme(gen_vars, t)

                global_env = global_env.extend(decl.name, scheme)

    generated = CodeGenerator().generate_module(module)

    namespace: dict = {}
    exec(generated, namespace)

    if "main" in namespace:
        result = namespace["main"]()
        if result is not None:
            print(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pfn",
        description="Pfn - Pure Functional Native compiler",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    compile_parser = subparsers.add_parser("compile", help="Compile Pfn to Python")
    compile_parser.add_argument("input", type=Path, help="Input .pfn file")
    compile_parser.add_argument(
        "-o", "--output", type=Path, help="Output .py file (default: stdout)"
    )
    compile_parser.add_argument(
        "--typecheck", action="store_true", help="Run type checker before compilation"
    )

    run_parser = subparsers.add_parser("run", help="Compile and run Pfn file")
    run_parser.add_argument("input", type=Path, help="Input .pfn file")
    run_parser.add_argument(
        "--typecheck", action="store_true", help="Run type checker before running"
    )

    check_parser = subparsers.add_parser("check", help="Type check Pfn file")
    check_parser.add_argument("input", type=Path, help="Input .pfn file")

    args = parser.parse_args(argv)

    if args.command == "compile":
        source = args.input.read_text()

        if args.typecheck:
            ok, msg = typecheck_source(source)
            if not ok:
                print(msg, file=sys.stderr)
                return 1

        python_code = compile_source(source)

        if args.output:
            args.output.write_text(python_code)
        else:
            print(python_code)
        return 0

    if args.command == "run":
        source = args.input.read_text()

        if args.typecheck:
            ok, msg = typecheck_source(source)
            if not ok:
                print(msg, file=sys.stderr)
                return 1

        run_source(source, typecheck=args.typecheck)
        return 0

    if args.command == "check":
        source = args.input.read_text()
        ok, msg = typecheck_source(source)
        print(msg)
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
