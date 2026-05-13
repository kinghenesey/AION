# =============================================================
# AION CLI — Error Display System
# =============================================================
# Transforms raw Python exceptions into beautiful, beginner-
# friendly error messages with source context and hints.
#
# Design goals:
#   - Show exactly where the error happened
#   - Explain what went wrong in plain English
#   - Suggest how to fix it
#   - Never intimidate beginners

from config import Color


# ── Error type definitions ────────────────────────────────────
# Maps error categories to friendly names and hints.

ERROR_HINTS = {
    "NameError": {
        "title": "Variable Not Found",
        "hint":  "Did you forget to define this variable before using it?",
        "example": "Try adding:  variable_name = value",
    },
    "SyntaxError": {
        "title": "Syntax Error",
        "hint":  "There's a mistake in how this line is written.",
        "example": "Check for missing quotes, colons, or brackets.",
    },
    "ParseError": {
        "title": "Parse Error",
        "hint":  "AION couldn't understand the structure of your code.",
        "example": "Check your indentation and statement structure.",
    },
    "RuntimeError": {
        "title": "Runtime Error",
        "hint":  "Something went wrong while running your program.",
        "example": "Check the values your variables hold.",
    },
    "TypeError": {
        "title": "Type Error",
        "hint":  "You're mixing incompatible types of values.",
        "example": "Make sure you're not adding a number to a string.",
    },
    "ZeroDivisionError": {
        "title": "Division By Zero",
        "hint":  "You cannot divide a number by zero.",
        "example": "Check that your divisor is never 0.",
    },
    "ImportError": {
        "title": "Module Not Found",
        "hint":  "This module doesn't exist in AION's standard library.",
        "example": "Available: math, text, files, datetime, collections",
    },
}


def display_error(
    error_type: str,
    message: str,
    source: str = "",
    filepath: str = "",
    line: int = 0,
):
    """
    Display a beautifully formatted AION error message.

    Args:
        error_type  — category of error (e.g. 'NameError')
        message     — the raw error message
        source      — full source code (for context display)
        filepath    — path to the .aion file
        line        — line number where error occurred
    """
    info = ERROR_HINTS.get(error_type, {
        "title":   error_type,
        "hint":    "An unexpected error occurred.",
        "example": "Review the line shown above.",
    })

    width = 50

    # ── Header ────────────────────────────────────────────────
    print()
    print(f"{Color.RED}{'━' * width}{Color.RESET}")
    print(f"{Color.RED}{Color.BOLD}  AION Error — {info['title']}{Color.RESET}")

    if filepath and line:
        print(f"{Color.DIM}  Line {line} in {filepath}{Color.RESET}")
    elif line:
        print(f"{Color.DIM}  Line {line}{Color.RESET}")

    print(f"{Color.RED}{'━' * width}{Color.RESET}")

    # ── Source context ────────────────────────────────────────
    if source and line:
        lines = source.splitlines()
        _show_source_context(lines, line)

    # ── Error message ─────────────────────────────────────────
    print()
    clean_message = _clean_message(message)
    print(f"  {Color.WHITE}{clean_message}{Color.RESET}")

    # ── Hint ──────────────────────────────────────────────────
    print()
    print(f"  {Color.YELLOW}💡 {info['hint']}{Color.RESET}")
    print(f"  {Color.DIM}{info['example']}{Color.RESET}")

    # ── Footer ────────────────────────────────────────────────
    print(f"{Color.RED}{'━' * width}{Color.RESET}")
    print()


def _show_source_context(lines: list, error_line: int):
    """
    Show the lines around the error with the error line
    highlighted and a pointer underneath it.
    """
    # Show up to 2 lines before and the error line
    start = max(0, error_line - 3)
    end   = min(len(lines), error_line + 1)

    print()
    for i in range(start, end):
        line_num = i + 1
        content  = lines[i]

        if line_num == error_line:
            # Highlight the error line in red
            print(f"  {Color.RED}{Color.BOLD}{line_num:>3} │  {content}{Color.RESET}")
            # Add pointer underneath
            print(f"  {Color.RED}    │  {'▲' * max(1, len(content.strip()))}{Color.RESET}")
        else:
            # Surrounding lines in dim
            print(f"  {Color.DIM}{line_num:>3} │  {content}{Color.RESET}")


def _clean_message(message: str) -> str:
    """
    Clean up raw Python error messages into
    more readable AION-style messages.
    """
    # Remove leading newlines and extra whitespace
    message = message.strip()

    # Remove Python internal references
    replacements = [
        ("\n  ", " — "),
        ("'NoneType'", "'null'"),
        ("'bool'",     "'boolean'"),
        ("'str'",      "'text'"),
        ("'int'",      "'number'"),
        ("'float'",    "'decimal'"),
        ("'list'",     "'list'"),
    ]

    for old, new in replacements:
        message = message.replace(old, new)

    return message