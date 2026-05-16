# =============================================================
# AION Language — CLI Entry Point
# =============================================================

import sys
import os


def main():
    """Main entry point for the aion command."""
    # Find AION installation directory
    aion_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, aion_dir)

    # Handle --version flag directly
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        from config import AION_VERSION, AION_CODENAME
        print(f"AION v{AION_VERSION} · {AION_CODENAME}")
        return

    # Run main
    from main import main as aion_main
    aion_main()


if __name__ == "__main__":
    main()