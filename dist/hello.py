#!/usr/bin/env python3
"""
hello — Built with AION v0.1.0
Generated on 2026-05-14 19:40
"""

SOURCE = """
# My first AION program

name = "Emmanuel"
age  = 20

show "Welcome to AION"
show "Hello " + name

if age >= 18:
    show "You are an adult"
else:
    show "You are a minor"

repeat 3:
    show "AION is alive!"
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
