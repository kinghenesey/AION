# =============================================================
# AION Parser — AST Nodes
# =============================================================
# Every possible structure in AION code is represented as a
# Node. The Parser builds a tree of these nodes. The
# Interpreter then walks the tree and executes each node.
#
# Think of nodes like LEGO pieces — each one represents one
# concept in your program.

class Node:
    """Base class for all AST nodes."""
    pass


# ── Program ───────────────────────────────────────────────────

class Program(Node):
    """
    The root node — represents the entire AION program.
    Every other node lives inside this one.
    """
    def __init__(self, statements: list):
        self.statements = statements

    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


# ── Literals ──────────────────────────────────────────────────

class IntegerLiteral(Node):
    """A whole number like 42."""
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"


class FloatLiteral(Node):
    """A decimal number like 3.14."""
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class StringLiteral(Node):
    """A string like "Hello"."""
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"String({repr(self.value)})"


class BooleanLiteral(Node):
    """true or false."""
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value})"


class NullLiteral(Node):
    """null — the absence of a value."""
    def __repr__(self):
        return "Null"


# ── Identifier ────────────────────────────────────────────────

class Identifier(Node):
    """
    A variable name like 'age' or 'name'.
    When the interpreter sees this it looks up the value
    in the current scope.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


# ── Expressions ───────────────────────────────────────────────

class BinaryOp(Node):
    """
    An operation between two values.
    Examples:
        age + 1
        name == "AION"
        x >= 18
    """
    def __init__(self, left: Node, operator: str, right: Node):
        self.left     = left
        self.operator = operator
        self.right    = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOp(Node):
    """
    An operation on a single value.
    Examples:
        not true
        -42
    """
    def __init__(self, operator: str, operand: Node):
        self.operator = operator
        self.operand  = operand

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


# ── Statements ────────────────────────────────────────────────

class AssignStatement(Node):
    """
    Assigns a value to a variable.
    Example:
        name = "Emmanuel"
    """
    def __init__(self, name: str, value: Node):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Assign({self.name} = {self.value})"


class ShowStatement(Node):
    """
    Prints a value to the terminal.
    Example:
        show "Hello"
    """
    def __init__(self, expression: Node):
        self.expression = expression

    def __repr__(self):
        return f"Show({self.expression})"


class IfStatement(Node):
    """
    A conditional block.
    Example:
        if age >= 18:
            show "Adult"
        else:
            show "Minor"
    """
    def __init__(self, condition: Node,
                 then_body: list,
                 else_body: list = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []

    def __repr__(self):
        return f"If({self.condition})"


class RepeatStatement(Node):
    """
    Repeats a block a fixed number of times.
    Example:
        repeat 5:
            show "Hello"
    """
    def __init__(self, count: Node, body: list):
        self.count = count
        self.body  = body

    def __repr__(self):
        return f"Repeat({self.count})"


class TaskStatement(Node):
    """
    Defines a reusable task (function).
    Example:
        task greet(name):
            show "Hello " + name
    """
    def __init__(self, name: str, params: list, body: list):
        self.name   = name
        self.params = params
        self.body   = body

    def __repr__(self):
        return f"Task({self.name}, params={self.params})"


class ReturnStatement(Node):
    """
    Returns a value from a task.
    Example:
        return result
    """
    def __init__(self, value: Node = None):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


class UseStatement(Node):
    """
    Imports a standard library module.
    Example:
        use math
    """
    def __init__(self, module: str):
        self.module = module

    def __repr__(self):
        return f"Use({self.module})"

class WhileStatement(Node):
    """
    Loops while a condition is true.
    Example:
        while count < 5:
            show count
            count = count + 1
    """
    def __init__(self, condition: Node, body: list):
        self.condition = condition
        self.body      = body

    def __repr__(self):
        return f"While({self.condition})"

class CallExpression(Node):
    """
    Calls a task with arguments.
    Example:
        greet("Emmanuel")
    """
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Call({self.name}, args={self.args})"