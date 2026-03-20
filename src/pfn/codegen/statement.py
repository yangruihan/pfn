"""Statement AST nodes for statement-level code generation."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union


@dataclass
class Statement:
    """Base class for statements"""

    pass


@dataclass
class Assign(Statement):
    """Assignment statement: target = value"""

    target: str
    value: str


@dataclass
class Return(Statement):
    """Return statement: return value"""

    value: str


@dataclass
class ExprStatement(Statement):
    """Expression as statement (for side effects)"""

    expr: str


@dataclass
class IfStatement(Statement):
    """If statement with then/else branches"""

    cond: str
    then_stmts: list[Statement]
    else_stmts: list[Statement]


@dataclass
class WhileStatement(Statement):
    """While loop statement"""

    cond: str
    body_stmts: list[Statement]


@dataclass
class PassStatement(Statement):
    """Pass statement (no-op)"""

    pass


def statements_to_python(stmts: list[Statement], indent_level: int = 0) -> str:
    """Convert statements to Python code string."""
    indent_str = "    " * indent_level
    lines = []

    for stmt in stmts:
        if isinstance(stmt, Assign):
            lines.append(f"{indent_str}{stmt.target} = {stmt.value}")
        elif isinstance(stmt, Return):
            lines.append(f"{indent_str}return {stmt.value}")
        elif isinstance(stmt, ExprStatement):
            lines.append(f"{indent_str}{stmt.expr}")
        elif isinstance(stmt, IfStatement):
            lines.append(f"{indent_str}if {stmt.cond}:")
            then_code = statements_to_python(stmt.then_stmts, indent_level + 1)
            if then_code:
                lines.append(then_code)
            else:
                lines.append(f"{indent_str}    pass")
            if stmt.else_stmts:
                lines.append(f"{indent_str}else:")
                else_code = statements_to_python(stmt.else_stmts, indent_level + 1)
                if else_code:
                    lines.append(else_code)
                else:
                    lines.append(f"{indent_str}    pass")
        elif isinstance(stmt, WhileStatement):
            lines.append(f"{indent_str}while {stmt.cond}:")
            body_code = statements_to_python(stmt.body_stmts, indent_level + 1)
            if body_code:
                lines.append(body_code)
            else:
                lines.append(f"{indent_str}    pass")
        elif isinstance(stmt, PassStatement):
            lines.append(f"{indent_str}pass")

    return "\n".join(lines)
