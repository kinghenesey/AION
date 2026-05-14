#!/usr/bin/env python3
"""
ui_demo — Built with AION v0.1.0
Generated on 2026-05-14 19:41
"""

SOURCE = """
# AION UI Framework Demo
# This builds a real HTML app with multiple pages

use ui

# Create the app
ui_app("AION Demo App")

# ── Page 1: Home ──────────────────────────────
ui_page("Home")
ui_title("Welcome to AION")
ui_text("The AI-native programming language that makes building apps easy.")
ui_text("Write clean code. Build beautiful interfaces. Integrate AI natively.")
ui_divider()
ui_button("Get Started", "Dashboard")
ui_button("Learn More", "About")
ui_space(2)

# ── Page 2: Dashboard ─────────────────────────
ui_page("Dashboard")
ui_title("Your Dashboard")
ui_text("Welcome back! Here is your AI workspace.")
ui_divider()
ui_text("Quick Actions:")
ui_button("New Project", "Home")
ui_button("Run AI Task", "Home")
ui_space(1)
ui_text("AION makes it simple to build, run, and deploy AI-powered apps.")

# ── Page 3: About ─────────────────────────────
ui_page("About")
ui_title("About AION")
ui_text("AION is an AI-native programming language built with Python.")
ui_text("It combines simplicity, readability, and AI integration into one elegant system.")
ui_divider()
ui_text("Version 0.1.0 · Genesis")
ui_text("Built by Emmanuel with Claude")
ui_space(1)
ui_button("Back to Home", "Home")

# Save the app
ui_save("examples/my_app.html")
"""

import sys
import os

# Add AION to path
AION_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AION_PATH)

try:
    from lexer import Lexer
    from parser.parser import Parser
    from interpreter.interpreter import Interpreter

    tokens      = Lexer(SOURCE).tokenize()
    program     = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.execute(program)

except ImportError:
    print("Error: AION runtime not found.")
    print("Make sure the AION folder is in your path.")
    sys.exit(1)
