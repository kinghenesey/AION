# =============================================================
# AION Web IDE — Server
# =============================================================
# Flask server that powers the AION Web IDE.
# Provides API endpoints for running code, loading files,
# and saving files.
#
# Usage:
#   python main.py ide

import os
import sys
import json
import traceback
from io import StringIO
from flask import Flask, request, jsonify, send_from_directory

# Add project root to path
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

from config import AION_VERSION, AION_CODENAME


def create_ide_app() -> Flask:
    """Create and configure the IDE Flask app."""

    static_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static"
    )

    app = Flask(__name__,
                static_folder=static_dir,
                static_url_path="/static")

    # ── Routes ────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Serve the IDE interface."""
        return send_from_directory(static_dir, "index.html")

    @app.route("/api/run", methods=["POST"])
    def run_code():
        """
        Execute AION code and return output.
        POST body: { "code": "show 'Hello'" }
        """
        data   = request.get_json()
        code   = data.get("code", "")

        if not code.strip():
            return jsonify({
                "output": "",
                "error":  None,
                "time":   0
            })

        output, error, elapsed = _execute_code(code)

        return jsonify({
            "output":  output,
            "error":   error,
            "time":    elapsed,
            "version": AION_VERSION,
        })

    @app.route("/api/examples", methods=["GET"])
    def get_examples():
        """Return list of example programs."""
        return jsonify({
            "examples": EXAMPLES
        })

    @app.route("/api/version", methods=["GET"])
    def get_version():
        """Return AION version info."""
        return jsonify({
            "version":  AION_VERSION,
            "codename": AION_CODENAME,
        })

    @app.route("/api/complete", methods=["POST"])
    def autocomplete():
        """
        Basic autocomplete suggestions.
        POST body: { "code": "sh", "cursor": 2 }
        """
        data   = request.get_json()
        prefix = data.get("code", "").split()[-1] \
            if data.get("code") else ""

        suggestions = _get_completions(prefix)

        return jsonify({
            "suggestions": suggestions
        })

    return app


def _execute_code(source: str):
    """
    Execute AION source code safely.
    Returns (output, error, elapsed_ms).
    """
    import time

    # Capture stdout
    captured   = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    start      = time.perf_counter()
    error      = None

    try:
        from lexer import Lexer, LexerError
        from parser.parser import Parser, ParseError
        from interpreter.interpreter import (
            Interpreter, RuntimeError)

        tokens      = Lexer(source).tokenize()
        program     = Parser(tokens).parse()
        interpreter = Interpreter()
        interpreter.execute(program)

    except Exception as e:
        error = str(e).strip()
        # Clean up internal paths from error messages
        error = error.replace(
            os.path.dirname(
                os.path.abspath(__file__)), "")

    finally:
        sys.stdout = old_stdout

    elapsed = (time.perf_counter() - start) * 1000
    output  = captured.getvalue()

    return output, error, round(elapsed, 2)


def _get_completions(prefix: str) -> list:
    """Return autocomplete suggestions for a prefix."""
    keywords = [
        "show", "if", "else", "repeat", "while",
        "task", "return", "use", "import", "and",
        "or", "not", "true", "false", "null",
    ]

    builtins = [
        "to_text", "to_number", "length", "ask",
        "clear", "sleep", "type_of", "random_num",
    ]

    modules = [
        "math", "text", "files", "datetime",
        "collections", "ai", "ui", "web",
        "database", "agents",
    ]

    all_suggestions = keywords + builtins + modules

    if not prefix:
        return keywords[:10]

    return [
        s for s in all_suggestions
        if s.startswith(prefix.lower())
    ][:10]


# ── Example programs ──────────────────────────────────────────

EXAMPLES = [
    {
        "name":  "Hello World",
        "code":  'show "Hello, World!"',
    },
    {
        "name":  "Variables",
        "code":  'name = "Emmanuel"\nage = 20\nshow "Hello {name}!"\nshow "Age: {age}"',
    },
    {
        "name":  "If / Else",
        "code":  'age = 20\nif age >= 18:\n    show "You are an adult"\nelse:\n    show "You are a minor"',
    },
    {
        "name":  "Repeat Loop",
        "code":  'repeat 5:\n    show "AION is awesome!"',
    },
    {
        "name":  "While Loop",
        "code":  'count = 1\nwhile count <= 5:\n    show count\n    count = count + 1',
    },
    {
        "name":  "Task / Function",
        "code":  'task greet(name):\n    show "Hello {name}!"\n\ngreet("Emmanuel")\ngreet("World")',
    },
    {
        "name":  "Math Module",
        "code":  'use math\nshow sqrt(144)\nshow round(pi)\nshow abs(-42)',
    },
    {
        "name":  "String Interpolation",
        "code":  'name = "AION"\nversion = "0.1.0"\nshow "Welcome to {name} v{version}!"',
    },
    {
        "name":  "FizzBuzz",
        "code":  'count = 1\nwhile count <= 20:\n    result = to_text(count)\n    if count % 15 == 0:\n        result = "FizzBuzz"\n    if count % 3 == 0:\n        result = "Fizz"\n    if count % 5 == 0:\n        result = "Buzz"\n    show result\n    count = count + 1',
    },
    {
        "name":  "AI Demo",
        "code":  'use ai\nanswer = ai_ask("What is AION programming language?")\nshow answer',
    },
]


def start_ide(port: int = 3000):
    """Start the AION Web IDE server."""
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    from config import Color
    print()
    print(f"{Color.CYAN}{Color.BOLD}"
          f"  AION Web IDE{Color.RESET}")
    print(f"  {Color.DIM}{'─' * 40}{Color.RESET}")
    print(f"  {Color.GREEN}✓ IDE running at "
          f"http://localhost:{port}{Color.RESET}")
    print(f"  {Color.DIM}Press Ctrl+C to stop"
          f"{Color.RESET}")
    print()

    app = create_ide_app()
    app.run(host="0.0.0.0",
            port=int(port),
            debug=False,
            use_reloader=False)