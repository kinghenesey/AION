# =============================================================
# AION Standard Library — Package Init
# =============================================================
# This is the central registry for all AION stdlib modules.
# When AION sees "use math" it calls load_module("math")
# which returns all functions for that module.
#
# Adding a new module in the future is as simple as:
#   1. Create stdlib/yourmodule_module.py with a load() fn
#   2. Add it to the MODULES registry below

from stdlib import (
    math_module,
    text_module,
    files_module,
    datetime_module,
    collections_module,
)
from ai import ai_module


# ── Module registry ───────────────────────────────────────────

MODULES = {
    "math":        math_module,
    "text":        text_module,
    "files":       files_module,
    "datetime":    datetime_module,
    "collections": collections_module,
    "ai":          ai_module,
}


def load_module(name: str) -> dict:
    """
    Load a stdlib module by name.
    Returns a dict of function_name → callable.
    Raises ImportError if module doesn't exist.
    """
    if name not in MODULES:
        available = ", ".join(MODULES.keys())
        raise ImportError(
            f"Module '{name}' was not found.\n"
            f"  Available modules: {available}"
        )

    return MODULES[name].load()


def available_modules() -> list:
    """Return a list of all available module names."""
    return list(MODULES.keys())