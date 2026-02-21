from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser


def compile_source(source: str) -> str:
    tokens = Lexer(source).tokenize()
    module = Parser(tokens).parse()
    return CodeGenerator().generate_module(module)


def run_source(source: str) -> None:
    tokens = Lexer(source).tokenize()
    module = Parser(tokens).parse()

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

    run_parser = subparsers.add_parser("run", help="Compile and run Pfn file")
    run_parser.add_argument("input", type=Path, help="Input .pfn file")

    args = parser.parse_args(argv)

    if args.command == "compile":
        source = args.input.read_text()
        python_code = compile_source(source)

        if args.output:
            args.output.write_text(python_code)
        else:
            print(python_code)
        return 0

    if args.command == "run":
        source = args.input.read_text()
        run_source(source)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
