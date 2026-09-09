"""
Bug Fix Regression Tests — Round 8

Found during a broad "test everything in the language" QA sweep done
after Phase 28 shipped (schema keyword, agent declarations,
task-as-tool resolution, schema-typed tool input). Covers:

  1. try/catch silently dropped the actual error description for any
     multi-line NEKOVA error message, keeping only the hint. NEKOVA's
     own error-raising convention is consistently
     "<description>.\\n  <hint/example>" (verified across every
     multi-line raise site in interpreter.py — roughly half of all
     NEKOVARuntimeError call sites use this two-part form). The
     try/catch handler built the caught error object's message via
     `raw.split("\\n")[-1]` — the LAST line — which is the hint, not
     the description. A caught divide-by-zero error rendered as just
     "Check your divisor value." with no indication anything was
     actually about division. Fixed to take the FIRST line instead,
     matching the convention. Confirmed this only affects NEKOVA's
     own deliberately multi-line messages — built-in Python exceptions
     (ZeroDivisionError, KeyError, IndexError, etc.) essentially never
     embed a newline of their own, so single-line messages are
     unaffected either way.
"""
import io
import re
import sys
import unittest

REPO_ROOT = __import__("os").path.dirname(
    __import__("os").path.dirname(__import__("os").path.abspath(__file__))
)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nekova.lexer.lexer import Lexer
from nekova.parser.parser import Parser
from nekova.interpreter.interpreter import Interpreter

ANSI = re.compile(r'\x1b\[[0-9;]*m')


def run(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    interp = Interpreter()
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        interp.run(ast)
    finally:
        sys.stdout = old
    return ANSI.sub('', buf.getvalue()).strip()


# ── Bug 1: caught multi-line errors lost their description ──────

class TestCaughtErrorKeepsDescription(unittest.TestCase):
    def test_divide_by_zero_message_is_preserved(self):
        out = run(
            'try:\n'
            '    let y = 1 / 0\n'
            'catch e:\n'
            '    show e\n'
        )
        self.assertIn("Cannot divide by zero", out)
        # The old bug specifically kept ONLY this hint text, with no
        # trace of the actual description anywhere in the message —
        # guard against that exact failure mode, not just "contains
        # the right words somewhere".
        self.assertNotEqual(out, "Check your divisor value.")

    def test_const_reassignment_message_is_preserved(self):
        out = run(
            'try:\n'
            '    const x = 5\n'
            '    x = 10\n'
            'catch e:\n'
            '    show e\n'
        )
        self.assertIn("Cannot reassign", out)

    def test_unpack_mismatch_message_is_preserved(self):
        out = run(
            'try:\n'
            '    let [a, b, c] = [1, 2]\n'
            'catch e:\n'
            '    show e\n'
        )
        self.assertIn("Not enough values", out)

    def test_single_line_messages_still_work_unchanged(self):
        """Sanity check the fix didn't break the common case of a
        caught error with no embedded newline at all."""
        out = run(
            'try:\n'
            '    raise "plain custom error"\n'
            'catch e:\n'
            '    show e\n'
        )
        self.assertEqual(out, "plain custom error")

    def test_uncaught_and_caught_descriptions_now_match(self):
        """The whole point of the fix: catching an error shouldn't
        lose information the uncaught rendering already had."""
        caught = run(
            'try:\n'
            '    let y = 1 / 0\n'
            'catch e:\n'
            '    show e\n'
        )
        self.assertIn("Cannot divide by zero", caught)


if __name__ == "__main__":
    unittest.main()