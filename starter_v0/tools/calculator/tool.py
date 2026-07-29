from __future__ import annotations

import ast
import operator
from typing import Any


_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float | int:
    """Recursively evaluate an AST node with only arithmetic operations."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op_func = _ALLOWED_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return op_func(left, right)
    if isinstance(node, ast.UnaryOp):
        op_func = _ALLOWED_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op_func(_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def evaluate_math(expression: str = "") -> dict[str, Any]:
    """Safely evaluate a basic math expression and return the result."""
    if not expression.strip():
        return {"tool": "calculator", "error": "empty_expression", "message": "No expression provided."}
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree)
        return {
            "tool": "calculator",
            "expression": expression.strip(),
            "result": result,
        }
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as exc:
        return {
            "tool": "calculator",
            "expression": expression.strip(),
            "error": type(exc).__name__,
            "message": str(exc),
        }
