"""AICL-Action (AX) — a Turing-complete sub-language for Behavior Actions.

AX replaces free-form English prose in ``Action:`` sections with a strict,
deterministically-compilable grammar (if/while/for/recursion/arithmetic/lists).
The compiler can translate any valid AX program to executable Python (and
later Rust/JS/Go) without pattern-matching heuristics.

Public API:
    parse(source) -> List[Stmt]                 tokenize + parse AX source
    emit_python(stmts, indent) -> str           render AX as Python source
    is_ax(source) -> bool                       heuristic: does this look like AX?
    AXSyntaxError                               raised on lex/parse errors
"""

from .lexer import tokenize, AXSyntaxError
from .parser import parse
from .emitter_python import emit_python
from . import ast

__all__ = ["tokenize", "parse", "emit_python", "ast", "AXSyntaxError"]


def is_ax(source: str) -> bool:
    """Heuristic: does ``source`` look like AX rather than English prose?

    AX is detected when the text contains structural markers (assignment ``=``,
    control keywords with ``:``, or multi-line indented blocks) AND it parses
    successfully. Plain English ("partition the array around a pivot") will
    fail to parse and return False, so the BehaviorCompiler falls back to its
    existing pattern/fallback path.
    """
    s = source.strip()
    if not s:
        return False
    # quick structural pre-check before paying for a full parse
    structural = any(
        marker in s
        for marker in (" = ", " += ", " -= ", "for ", "while ", "if ", "return ", "\n    ")
    )
    if not structural:
        return False
    try:
        parse(source)
        return True
    except AXSyntaxError:
        return False
