# =============================================================
# AION Language — CLI Module
# =============================================================
# Handles all terminal output formatting.
# Kept separate so the interpreter never depends on colors.

import sys
from config import Color, AION_VERSION, AION_CODENAME


def print_banner():
    """Print the AION startup banner."""
    banner = f"""
{Color.CYAN}{Color.BOLD}
    ___    ____  ____  _   __
   /   |  /  _/ / __ \/ | / /
  / /| |  / /  / / / /  |/ / 
 / ___ |_/ /  / /_/ / /|  /  
/_/  |_/___/  \____/_/ |_/   
{Color.RESET}
  {Color.DIM}AI-Native Programming Language{Color.RESET}
  {Color.YELLOW}Version {AION_VERSION} · {AION_CODENAME}{Color.RESET}
  {Color.DIM}{"─" * 40}{Color.RESET}
"""
    print(banner)


def print_success(message: str):
    print(f"{Color.GREEN}✓ {message}{Color.RESET}")


def print_error(message: str):
    print(f"{Color.RED}✗ {message}{Color.RESET}", file=sys.stderr)


def print_info(message: str):
    print(f"{Color.CYAN}→ {message}{Color.RESET}")


def print_warning(message: str):
    print(f"{Color.YELLOW}⚠ {message}{Color.RESET}")


def print_separator():
    print(f"{Color.DIM}{'─' * 50}{Color.RESET}")