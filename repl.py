# =============================================================
# AION Language — Interactive REPL
# =============================================================
# Read-Eval-Print Loop for AION.
# Type AION code interactively and see results immediately.
#
# Usage:
#   python main.py --repl
#   python main.py repl

import sys
import os

from config import Color, AION_VERSION, AION_CODENAME
from interpreter.interpreter import Interpreter
from interpreter.environment import Environment


class REPL:
    """
    Interactive AION shell.
    Maintains state between inputs so variables persist.
    """

    PROMPT      = f"{Color.CYAN}AION>{Color.RESET} "
    PROMPT_CONT = f"{Color.DIM}  ...>{Color.RESET} "

    def __init__(self):
        # Single interpreter instance — keeps all variables
        self.interpreter = Interpreter()
        self.history     = []
        self.running     = True

    def start(self):
        """Start the REPL session."""
        self._print_welcome()

        while self.running:
            try:
                source = self._read_input()

                if not source:
                    continue

                # Handle special REPL commands
                if self._handle_command(source):
                    continue

                # Execute the AION code
                self._execute(source)

            except KeyboardInterrupt:
                print()
                print(f"{Color.YELLOW}  Use 'exit' "
                      f"to quit{Color.RESET}")

            except EOFError:
                self._quit()

    def _read_input(self) -> str:
        """
        Read one line or a complete block from the user.
        Handles multi-line input (if/repeat/while/task blocks).
        """
        try:
            line = input(self.PROMPT)
        except EOFError:
            raise

        if not line.strip():
            return ""

        # Check if line starts a block (ends with :)
        if line.rstrip().endswith(":"):
            lines = [line]
            # Keep reading indented lines
            while True:
                try:
                    cont = input(self.PROMPT_CONT)
                    # Empty line ends the block
                    if not cont.strip():
                        break
                    lines.append(cont)
                except EOFError:
                    break

            # Add proper indentation to block lines
            result = []
            result.append(lines[0])
            for l in lines[1:]:
                # Add 4 spaces if not already indented
                if not l.startswith(" ") and not l.startswith("\t"):
                    result.append("    " + l)
                else:
                    result.append(l)
            return "\n".join(result)

        return line.strip()

    def _execute(self, source: str):
        """Execute AION source code in the REPL."""
        try:
            from lexer import Lexer, LexerError
            from parser.parser import Parser, ParseError
            from interpreter.interpreter import RuntimeError

            # Tokenize
            tokens = Lexer(source).tokenize()

            # Parse
            parser  = Parser(tokens)
            program = parser.parse()

            if not program.statements:
                return

            # Execute each statement
            for stmt in program.statements:
                result = self.interpreter._execute_node(stmt)

                # Auto-print expression results
                if result is not None:
                    from parser.nodes import (
                        AssignStatement, ShowStatement,
                        UseStatement
                    )
                    if not isinstance(stmt, (
                        AssignStatement, ShowStatement,
                        UseStatement
                    )):
                        print(f"{Color.DIM}= "
                              f"{self.interpreter._to_string(result)}"
                              f"{Color.RESET}")

            # Save to history
            self.history.append(source)

        except Exception as e:
            # Show clean error without traceback
            msg = str(e).strip()
            print(f"{Color.RED}Error: {msg}{Color.RESET}")

    def _handle_command(self, source: str) -> bool:
        """
        Handle special REPL commands.
        Returns True if command was handled.
        """
        cmd = source.strip().lower()

        if cmd in ("exit", "quit", "q"):
            self._quit()
            return True

        if cmd == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            return True

        if cmd == "help":
            self._print_help()
            return True

        if cmd == "history":
            self._print_history()
            return True

        if cmd == "vars":
            self._print_vars()
            return True

        if cmd == "reset":
            self.interpreter = Interpreter()
            print(f"{Color.GREEN}✓ Session reset"
                  f"{Color.RESET}")
            return True

        return False

    def _print_welcome(self):
        """Print the REPL welcome message."""
        print(f"""
{Color.CYAN}{Color.BOLD}AION Interactive Shell{Color.RESET}
{Color.DIM}Version {AION_VERSION} · {AION_CODENAME}{Color.RESET}
{Color.DIM}Type 'help' for commands, 'exit' to quit{Color.RESET}
{Color.DIM}{'─' * 40}{Color.RESET}
""")

    def _print_help(self):
        """Print REPL help."""
        print(f"""
{Color.CYAN}REPL Commands:{Color.RESET}
  {Color.BOLD}exit{Color.RESET}      Quit the REPL
  {Color.BOLD}clear{Color.RESET}     Clear the screen
  {Color.BOLD}vars{Color.RESET}      Show all variables
  {Color.BOLD}history{Color.RESET}   Show command history
  {Color.BOLD}reset{Color.RESET}     Reset the session

{Color.CYAN}AION Examples:{Color.RESET}
  {Color.DIM}name = "Emmanuel"{Color.RESET}
  {Color.DIM}show "Hello " + name{Color.RESET}
  {Color.DIM}show 2 + 3{Color.RESET}
  {Color.DIM}use math{Color.RESET}
  {Color.DIM}show sqrt(16){Color.RESET}
""")

    def _print_history(self):
        """Print command history."""
        if not self.history:
            print(f"{Color.DIM}No history yet.{Color.RESET}")
            return
        print(f"{Color.CYAN}History:{Color.RESET}")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {Color.DIM}{i:>3}.{Color.RESET} {cmd}")

    def _print_vars(self):
        """Print all current variables."""
        variables = self.interpreter.globals.variables
        if not variables:
            print(f"{Color.DIM}No variables defined yet."
                  f"{Color.RESET}")
            return
        print(f"{Color.CYAN}Variables:{Color.RESET}")
        for name, value in variables.items():
            if not callable(value) and not isinstance(
                    value, type):
                print(f"  {Color.BOLD}{name}{Color.RESET}"
                      f" = {repr(value)}")

    def _quit(self):
        """Exit the REPL."""
        print(f"\n{Color.CYAN}Goodbye! Keep building "
              f"with AION. 🚀{Color.RESET}\n")
        self.running = False
        sys.exit(0)