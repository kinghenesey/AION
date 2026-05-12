#!/usr/bin/env python3
# =============================================================
# AION Language — Main Entry Point
# =============================================================
# Usage:
#   python main.py app.aion
#   python main.py app.aion --debug
#   python main.py --version
#   python main.py --help

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AION_VERSION, AION_CODENAME, Color
from cli    import print_banner, print_error, print_info
from runner import AIONRunner


HELP_TEXT = f"""
{Color.CYAN}{Color.BOLD}AION Programming Language{Color.RESET} v{AION_VERSION} · {AION_CODENAME}

{Color.BOLD}Usage:{Color.RESET}
  python main.py <file.aion>            Run an AION source file
  python main.py <file.aion> --debug    Run with debug output
  python main.py --version              Show version info
  python main.py --help                 Show this help message

{Color.BOLD}Examples:{Color.RESET}
  python main.py examples/hello.aion
  python main.py examples/hello.aion --debug
"""


def parse_args(argv: list) -> dict:
    args = {
        "file":    None,
        "debug":   False,
        "version": False,
        "help":    False,
    }

    flags  = {a for a in argv if a.startswith("--")}
    values = [a for a in argv if not a.startswith("--")]

    args["debug"]   = "--debug"   in flags
    args["version"] = "--version" in flags
    args["help"]    = "--help"    in flags

    if values:
        args["file"] = values[0]

    return args


def main():
    argv = sys.argv[1:]

    if not argv:
        print_banner()
        print(HELP_TEXT)
        sys.exit(0)

    args = parse_args(argv)

    if args["version"]:
        print(f"AION v{AION_VERSION} · {AION_CODENAME}")
        sys.exit(0)

    if args["help"]:
        print_banner()
        print(HELP_TEXT)
        sys.exit(0)

    if not args["file"]:
        print_error("No file specified. Run 'python main.py --help' for usage.")
        sys.exit(1)

    print_banner()

    runner = AIONRunner(filepath=args["file"], debug=args["debug"])
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()