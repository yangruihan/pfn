"""REPL (Read-Eval-Print Loop) for Pfn."""

from __future__ import annotations

import sys
from typing import Any

from pfn.codegen import CodeGenerator
from pfn.lexer import Lexer
from pfn.parser import Parser
from pfn.parser.ast import DefDecl
from pfn.typechecker import TypeChecker, TypeError as PfnTypeError
from pfn.types import Scheme, TFun, Subst, TypeEnv, TVar


class REPL:
    """Interactive REPL for Pfn."""

    def __init__(self):
        self.checker = TypeChecker()
        self.global_env = TypeEnv()
        self.namespace: dict[str, Any] = {}
        self.codegen = CodeGenerator()
        self.history: list[str] = []
        self.prompt = "pfn> "
        self.multi_line_buffer: list[str] = []
        self.in_multi_line = False

    def run(self) -> None:
        """Start the REPL."""
        print("Pfn REPL - Pure Functional Native")
        print("Type :help for commands, :quit to exit")
        print()

        while True:
            try:
                if self.in_multi_line:
                    prompt = "... "
                else:
                    prompt = self.prompt

                line = input(prompt)
                if not line:
                    continue

                self.history.append(line)

                if self._is_command(line):
                    self._handle_command(line)
                else:
                    self._eval_line(line)

            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\n(Use :quit to exit)")
                self.in_multi_line = False
                self.multi_line_buffer.clear()
            except Exception as e:
                print(f"Error: {e}")

    def _is_command(self, line: str) -> bool:
        return line.strip().startswith(":")

    def _handle_command(self, line: str) -> None:
        cmd = line.strip()[1:].split()
        if not cmd:
            return

        command = cmd[0]
        args = cmd[1:]

        if command in ("quit", "q", "exit"):
            raise EOFError

        if command in ("help", "h", "?"):
            self._print_help()
        elif command in ("type", "t"):
            if args:
                self._type_of(" ".join(args))
        elif command in ("load", "l"):
            if args:
                self._load_file(args[0])
        elif command in ("clear", "c"):
            self._clear()
        elif command in ("env", "e"):
            self._show_env()
        elif command in ("history", "hist"):
            self._show_history()
        else:
            print(f"Unknown command: {command}")
            print("Type :help for available commands")

    def _print_help(self) -> None:
        print("""
Available commands:
  :help, :h, :?     Show this help message
  :type, :t <expr>  Show type of expression
  :load, :l <file>  Load and evaluate a file
  :clear, :c       Clear the environment
  :env, :e         Show current environment
  :history, :hist   Show command history
  :quit, :q, :exit  Exit the REPL

Examples:
  pfn> 1 + 2
  3
  pfn> def add x y = x + y
  pfn> add 1 2
  3
  pfn> :type add
  (Int, Int) -> Int
        """)

    def _eval_line(self, line: str) -> None:
        if line.endswith("\\"):
            self.multi_line_buffer.append(line[:-1])
            self.in_multi_line = True
            return

        if self.in_multi_line:
            self.multi_line_buffer.append(line)
            full_code = "\n".join(self.multi_line_buffer)
            self.multi_line_buffer.clear()
            self.in_multi_line = False
        else:
            full_code = line

        result = self._eval(full_code)
        if result is not None:
            print(result)

    def _eval(self, code: str) -> Any:
        tokens = Lexer(code).tokenize()

        try:
            module = Parser(tokens).parse()
        except Exception as e:
            print(f"Parse error: {e}")
            return None

        for decl in module.declarations:
            if isinstance(decl, DefDecl):
                try:
                    self._typecheck_decl(decl)
                except PfnTypeError as e:
                    print(f"Type error: {e}")
                    return None

        generated = self.codegen.generate_module(module)

        try:
            exec(generated, self.namespace)
        except Exception as e:
            print(f"Runtime error: {e}")
            return None

        for decl in module.declarations:
            if isinstance(decl, DefDecl) and decl.name in self.namespace:
                result = self.namespace[decl.name]
                if callable(result):
                    return None
                return result

        return None

    def _typecheck_decl(self, decl: DefDecl) -> None:
        self.checker.env = self.global_env

        for param in decl.params:
            tv = self.checker.fresh_var()
            self.checker.env = self.checker.env.extend(param.name, Scheme((), tv))

        t = self.checker.infer(decl.body)

        for param in reversed(decl.params):
            scheme = self.checker.env.lookup(param.name)
            if scheme:
                t = TFun(scheme.type, t)

        subst = Subst()
        free_in_env = subst.free_vars_env(self.global_env)
        free_in_t = subst.free_vars(t)
        gen_vars = tuple(sorted(free_in_t - free_in_env))
        scheme = Scheme(gen_vars, t)

        self.global_env = self.global_env.extend(decl.name, scheme)
        print(f"{decl.name} : {t}")

    def _type_of(self, expr: str) -> None:
        code = f"_ = {expr}"
        tokens = Lexer(code).tokenize()

        try:
            module = Parser(tokens).parse()
        except Exception as e:
            print(f"Parse error: {e}")
            return

        if not module.declarations:
            return

        decl = module.declarations[0]
        if isinstance(decl, DefDecl):
            self.checker.env = self.global_env

            for param in decl.params:
                tv = self.checker.fresh_var()
                self.checker.env = self.checker.env.extend(param.name, Scheme((), tv))

            try:
                t = self.checker.infer(decl.body)
                print(f"{expr} : {t}")
            except PfnTypeError as e:
                print(f"Type error: {e}")

    def _load_file(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                code = f.read()
            print(f"Loading {filename}...")
            self._eval(code)
            print("Loaded successfully")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def _clear(self) -> None:
        self.global_env = TypeEnv()
        self.namespace.clear()
        print("Environment cleared")

    def _show_env(self) -> None:
        print("Current environment:")
        for name, scheme in self.global_env.bindings.items():
            print(f"  {name} : {scheme}")

    def _show_history(self) -> None:
        print("Command history:")
        for i, line in enumerate(self.history, 1):
            print(f"  {i}: {line}")


def start_repl() -> None:
    """Start the REPL."""
    repl = REPL()
    repl.run()


__all__ = ["REPL", "start_repl"]
