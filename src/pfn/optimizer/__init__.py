"""Optimizer module for Pfn compiler.

This module provides optimization passes that can be applied to the IR
to generate more efficient Python code.
"""

from pfn.optimizer.passes import (
    BetaReduction,
    CommonSubexprElimination,
    ConstantFolding,
    DeadCodeElimination,
    Inlining,
    Optimizer,
    SodaOptimizer,
    TailCallOptimization,
    run_optimizer,
)


__all__ = [
    "Optimizer",
    "ConstantFolding",
    "DeadCodeElimination",
    "Inlining",
    "BetaReduction",
    "TailCallOptimization",
    "CommonSubexprElimination",
    "SodaOptimizer",
    "run_optimizer",
]
