#!/usr/bin/env python3
# =============================================================
# AION Language — Main Entry Point
# =============================================================
# Usage:
#   python main.py <file.aion>              Run a file
#   python main.py run <file.aion>          Run a file
#   python main.py test                     Run all tests
#   python main.py build <file.aion>        Validate a file
#   python main.py new <project>            Create a project
#   python main.py info                     System info
#   python main.py clean                    Remove cache
#   python main.py --install <package>      Install package
#   python main.py --uninstall <package>    Uninstall package
#   python main.py --packages               List packages
#   python main.py --version                Show version
#   python main.py --help                   Show help

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AION_VERSION, AION_CODENAME, Color
from cli    import print_banner, print_error, print_info
from runner import AIONRunner


HELP_TEXT = f"""
{Color.CYAN}{Color.BOLD}AION Programming Language{Color.RESET} \
v{AION_VERSION} · {AION_CODENAME}

{Color.BOLD}Running files:{Color.RESET}
  python main.py <file.aion>              Run an AION file
  python main.py <file.aion> --debug      Run with debug output
  python main.py run <file.aion>          Run an AION file

{Color.BOLD}Developer tools:{Color.RESET}
  python main.py test                     Run all test suites
  python main.py build <file.aion>        Validate a file
  python main.py new <project-name>       Create a new project
  python main.py info                     Show system info
  python main.py clean                    Remove cache files

{Color.BOLD}Package manager:{Color.RESET}
  python main.py --packages               List all packages
  python main.py --install <package>      Install a package
  python main.py --uninstall <package>    Uninstall a package

{Color.BOLD}Other:{Color.RESET}
  python main.py --version                Show version
  python main.py --help                   Show this help

{Color.BOLD}Examples:{Color.RESET}
  python main.py examples/hello.aion
  python main.py --install charts
  python main.py new myapp
  python main.py test
"""


def parse_args(argv: list) -> dict:
    args = {
        "file":      None,
        "command":   None,
        "arg":       None,
        "debug":     False,
        "compile":   False,
        "version":   False,
        "help":      False,
        "packages":  False,
        "install":   None,
        "uninstall": None,
    }

    if not argv:
        return args

    flags  = {a for a in argv if a.startswith("--")}
    values = [a for a in argv if not a.startswith("--")]

    args["debug"]    = "--debug"    in flags
    args["version"]  = "--version"  in flags
    args["help"]     = "--help"     in flags
    args["packages"] = "--packages" in flags
    args["compile"]  = "--compile"  in flags
    # Handle --install and --uninstall
    argv_list = list(argv)
    for i, arg in enumerate(argv_list):
        if arg == "--install" and i + 1 < len(argv_list):
            args["install"] = argv_list[i + 1]
        if arg == "--uninstall" and i + 1 < len(argv_list):
            args["uninstall"] = argv_list[i + 1]

    # Handle subcommands: run, test, build, new, info, clean
    commands = {"run", "test", "build", "new", "info", "clean"}
    if values and values[0] in commands:
        args["command"] = values[0]
        if len(values) > 1:
            args["arg"] = values[1]
    elif values:
        args["file"] = values[0]

    return args


def main():
    argv = sys.argv[1:]

    if not argv:
        print_banner()
        print(HELP_TEXT)
        sys.exit(0)

    args = parse_args(argv)

    # ── Flag commands ─────────────────────────────────────────

    if args["version"]:
        print(f"AION v{AION_VERSION} · {AION_CODENAME}")
        sys.exit(0)

    if args["help"]:
        print_banner()
        print(HELP_TEXT)
        sys.exit(0)

    if args["packages"]:
        print_banner()
        from cli.package_manager import list_packages
        list_packages()
        sys.exit(0)

    if args["install"]:
        print_banner()
        from cli.package_manager import install_package
        success = install_package(args["install"])
        sys.exit(0 if success else 1)

    if args["uninstall"]:
        print_banner()
        from cli.package_manager import uninstall_package
        success = uninstall_package(args["uninstall"])
        sys.exit(0 if success else 1)

    # ── Subcommands ───────────────────────────────────────────

    if args["command"]:
        print_banner()
        cmd = args["command"]
        arg = args["arg"]

        from cli.commands import (
            cmd_info, cmd_new, cmd_test,
            cmd_build, cmd_clean
        )

        if cmd == "info":
            cmd_info()
            sys.exit(0)

        if cmd == "test":
            success = cmd_test()
            sys.exit(0 if success else 1)

        if cmd == "clean":
            cmd_clean()
            sys.exit(0)

        if cmd == "new":
            success = cmd_new(arg)
            sys.exit(0 if success else 1)

        if cmd == "build":
            success = cmd_build(arg)
            sys.exit(0 if success else 1)

        if cmd == "run":
            if not arg:
                print_error(
                    "Please provide a file to run.\n"
                    "  Usage: python main.py run app.aion"
                )
                sys.exit(1)
            runner    = AIONRunner(filepath=arg,
                                   debug=args["debug"],
                                   compile_mode=args["compile"])
            exit_code = runner.run()
            sys.exit(exit_code)

    # ── Direct file execution ─────────────────────────────────

    if args["file"]:
        print_banner()
        runner    = AIONRunner(filepath=args["file"],
                               debug=args["debug"],
                               compile_mode=args["compile"])
        exit_code = runner.run()
        sys.exit(exit_code)

    # ── Nothing matched ───────────────────────────────────────
    print_error(
        "Unknown command. "
        "Run 'python main.py --help' for usage."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()