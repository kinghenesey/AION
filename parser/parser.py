# =============================================================
# AION Parser — Main Parser Engine
# =============================================================
# The Parser takes the flat list of tokens from the Lexer
# and builds an AST (Abstract Syntax Tree).
#
# Process:
#   1. Look at the current token
#   2. Decide what structure it starts
#   3. Consume tokens until that structure is complete
#   4. Return the matching Node
#   5. Repeat until EOF

from lexer.token_types import TokenType
from lexer.token import Token
from parser.nodes import (
    Program, IntegerLiteral, FloatLiteral, StringLiteral,
    BooleanLiteral, NullLiteral, Identifier, BinaryOp,
    UnaryOp, AssignStatement, ShowStatement, IfStatement,
    RepeatStatement, TaskStatement, ReturnStatement,
    UseStatement, CallExpression
)


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"\n  Line {line}: {message}")


class Parser:
    """
    Converts a list of Tokens into an AST.

    Usage:
        parser  = Parser(tokens)
        program = parser.parse()
    """

    def __init__(self, tokens: list):
        # Filter out blank newlines at the start
        self.tokens  = tokens
        self.pos     = 0

    # ----------------------------------------------------------
    # Public interface
    # ----------------------------------------------------------

    def parse(self) -> Program:
        """Parse all tokens and return the root Program node."""
        statements = []

        self._skip_newlines()

        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()

        return Program(statements)

    # ----------------------------------------------------------
    # Statement parsers
    # ----------------------------------------------------------

    def _parse_statement(self):
        """Decide which kind of statement to parse next."""
        token = self._current()

        if token.type == TokenType.SHOW:
            return self._parse_show()

        if token.type == TokenType.IF:
            return self._parse_if()

        if token.type == TokenType.REPEAT:
            return self._parse_repeat()

        if token.type == TokenType.TASK:
            return self._parse_task()

        if token.type == TokenType.RETURN:
            return self._parse_return()

        if token.type == TokenType.USE:
            return self._parse_use()

        if token.type == TokenType.IDENTIFIER:
            return self._parse_identifier_statement()

        if token.type in (TokenType.NEWLINE, TokenType.EOF):
            return None

        raise ParseError(
            f"Unexpected token '{token.value}' — "
            f"AION doesn't know what to do with this here.",
            token.line
        )

    def _parse_show(self):
        """Parse:  show <expression>"""
        line = self._current().line
        self._consume(TokenType.SHOW)
        expr = self._parse_expression()
        self._expect_newline_or_eof()
        return ShowStatement(expr)

    def _parse_if(self):
        """
        Parse:
            if <condition>:
                <body>
            else:
                <body>
        """
        line = self._current().line
        self._consume(TokenType.IF)
        condition = self._parse_expression()
        self._consume(TokenType.COLON)
        self._expect_newline_or_eof()
        self._skip_newlines()

        then_body = self._parse_block()
        else_body = []

        self._skip_newlines()

        if (not self._at_end() and
                self._current().type == TokenType.ELSE):
            self._consume(TokenType.ELSE)
            self._consume(TokenType.COLON)
            self._expect_newline_or_eof()
            self._skip_newlines()
            else_body = self._parse_block()

        return IfStatement(condition, then_body, else_body)

    def _parse_repeat(self):
        """
        Parse:
            repeat <count>:
                <body>
        """
        self._consume(TokenType.REPEAT)
        count = self._parse_expression()
        self._consume(TokenType.COLON)
        self._expect_newline_or_eof()
        self._skip_newlines()
        body = self._parse_block()
        return RepeatStatement(count, body)

    def _parse_task(self):
        """
        Parse:
            task <name>(<params>):
                <body>
        """
        self._consume(TokenType.TASK)
        name = self._consume(TokenType.IDENTIFIER).value

        self._consume(TokenType.LPAREN)
        params = []
        while self._current().type != TokenType.RPAREN:
            params.append(self._consume(TokenType.IDENTIFIER).value)
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._consume(TokenType.RPAREN)
        self._consume(TokenType.COLON)
        self._expect_newline_or_eof()
        self._skip_newlines()
        body = self._parse_block()
        return TaskStatement(name, params, body)

    def _parse_return(self):
        """Parse:  return <expression>"""
        self._consume(TokenType.RETURN)
        if self._current().type in (TokenType.NEWLINE, TokenType.EOF):
            return ReturnStatement(None)
        value = self._parse_expression()
        self._expect_newline_or_eof()
        return ReturnStatement(value)

    def _parse_use(self):
        """Parse:  use <module>"""
        self._consume(TokenType.USE)
        module = self._consume(TokenType.IDENTIFIER).value
        self._expect_newline_or_eof()
        return UseStatement(module)

    def _parse_identifier_statement(self):
        """
        An identifier can start two things:
            name = "value"     → assignment
            greet("Emmanuel")  → function call
        """
        name  = self._consume(TokenType.IDENTIFIER).value
        token = self._current()

        # Assignment
        if token.type == TokenType.ASSIGN:
            self._consume(TokenType.ASSIGN)
            value = self._parse_expression()
            self._expect_newline_or_eof()
            return AssignStatement(name, value)

        # Function call
        if token.type == TokenType.LPAREN:
            call = self._finish_call(name)
            self._expect_newline_or_eof()
            return call

        raise ParseError(
            f"Expected '=' or '(' after '{name}'.",
            token.line
        )

    # ----------------------------------------------------------
    # Block parser
    # ----------------------------------------------------------

    def _parse_block(self) -> list:
        """
        Parse an indented block of statements.
        Blocks start with INDENT and end with DEDENT.
        """
        statements = []

        if self._current().type != TokenType.INDENT:
            raise ParseError(
                "Expected an indented block here. "
                "Did you forget to indent?",
                self._current().line
            )

        self._consume(TokenType.INDENT)
        self._skip_newlines()

        while (not self._at_end() and
               self._current().type != TokenType.DEDENT):
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()

        if self._current().type == TokenType.DEDENT:
            self._consume(TokenType.DEDENT)

        return statements

    # ----------------------------------------------------------
    # Expression parsers
    # ----------------------------------------------------------

    def _parse_expression(self):
        """Parse an expression (handles comparisons)."""
        return self._parse_comparison()

    def _parse_comparison(self):
        """Parse comparison operators: == != < <= > >="""
        left = self._parse_addition()

        comparison_ops = {
            TokenType.EQUALS:     "==",
            TokenType.NOT_EQUALS: "!=",
            TokenType.LESS:       "<",
            TokenType.LESS_EQ:    "<=",
            TokenType.GREATER:    ">",
            TokenType.GREATER_EQ: ">=",
        }

        while self._current().type in comparison_ops:
            op  = comparison_ops[self._current().type]
            self._advance()
            right = self._parse_addition()
            left  = BinaryOp(left, op, right)

        return left

    def _parse_addition(self):
        """Parse + and - operators."""
        left = self._parse_multiplication()

        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op    = self._current().value
            self._advance()
            right = self._parse_multiplication()
            left  = BinaryOp(left, op, right)

        return left

    def _parse_multiplication(self):
        """Parse * / % ** operators."""
        left = self._parse_unary()

        while self._current().type in (
            TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO,   TokenType.POWER
        ):
            op    = self._current().value
            self._advance()
            right = self._parse_unary()
            left  = BinaryOp(left, op, right)

        return left

    def _parse_unary(self):
        """Parse unary operators: - not"""
        if self._current().type == TokenType.MINUS:
            self._advance()
            return UnaryOp("-", self._parse_primary())

        if self._current().type == TokenType.NOT:
            self._advance()
            return UnaryOp("not", self._parse_primary())

        return self._parse_primary()

    def _parse_primary(self):
        """Parse the most basic expressions — literals, identifiers, groups."""
        token = self._current()

        if token.type == TokenType.INTEGER:
            self._advance()
            return IntegerLiteral(token.value)

        if token.type == TokenType.FLOAT:
            self._advance()
            return FloatLiteral(token.value)

        if token.type == TokenType.STRING:
            self._advance()
            return StringLiteral(token.value)

        if token.type == TokenType.BOOLEAN:
            self._advance()
            return BooleanLiteral(token.value)

        if token.type == TokenType.NULL:
            self._advance()
            return NullLiteral()

        if token.type == TokenType.IDENTIFIER:
            self._advance()
            # Check if this is a function call
            if self._current().type == TokenType.LPAREN:
                return self._finish_call(token.value)
            return Identifier(token.value)

        if token.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"Unexpected '{token.value}' — "
            f"expected a value, variable, or expression.",
            token.line
        )

    def _finish_call(self, name: str) -> CallExpression:
        """Parse the argument list of a function call."""
        self._consume(TokenType.LPAREN)
        args = []
        while self._current().type != TokenType.RPAREN:
            args.append(self._parse_expression())
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._consume(TokenType.RPAREN)
        return CallExpression(name, args)

    # ----------------------------------------------------------
    # Utility methods
    # ----------------------------------------------------------

    def _current(self) -> Token:
        """Return the token at the current position."""
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        """Consume the current token and move forward."""
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def _at_end(self) -> bool:
        """Returns True when we reach EOF."""
        return self._current().type == TokenType.EOF

    def _consume(self, expected: TokenType) -> Token:
        """
        Consume the current token if it matches the expected type.
        Raises ParseError if it doesn't match.
        """
        token = self._current()
        if token.type != expected:
            raise ParseError(
                f"Expected '{expected.name}' but got "
                f"'{token.type.name}' ('{token.value}').",
                token.line
            )
        return self._advance()

    def _skip_newlines(self):
        """Skip over any newline tokens."""
        while (not self._at_end() and
               self._current().type == TokenType.NEWLINE):
            self._advance()

    def _expect_newline_or_eof(self):
        """After a statement, expect a newline or end of file."""
        if self._current().type == TokenType.NEWLINE:
            self._advance()
        elif self._current().type == TokenType.EOF:
            pass
        # If neither, we just continue — the next parse will catch errors