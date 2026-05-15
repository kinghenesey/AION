# =============================================================
# AION Interpreter — Main Execution Engine
# =============================================================
# The Interpreter walks the AST tree and executes each node.
#
# Process:
#   1. Receive the root Program node
#   2. Execute each statement one by one
#   3. For each node type call the matching execute_ method
#   4. Return the result
#
# This is called a "tree-walk interpreter" — the simplest
# and most readable interpreter architecture possible.

from parser.nodes import (
    Program, IntegerLiteral, FloatLiteral, StringLiteral,
    BooleanLiteral, NullLiteral, Identifier, BinaryOp,
    UnaryOp, AssignStatement, ShowStatement, IfStatement,
    RepeatStatement, WhileStatement, TaskStatement,
    ReturnStatement, UseStatement, CallExpression
)
from interpreter.environment import Environment
from runtime import ReturnSignal


class RuntimeError(Exception):
    """Raised when something goes wrong during execution."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"\n  {message}")

class AIONImportError(Exception):
    """Raised when a module cannot be found."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"\n  {message}")


class AIONNameError(Exception):
    """Raised when a variable is not found."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"\n  {message}")


class Interpreter:
    """
    Executes an AION AST produced by the Parser.

    Usage:
        interpreter = Interpreter()
        interpreter.execute(program)
    """

    def __init__(self):
        # Global environment — lives for the entire program
        self.globals = Environment()
        self.env     = self.globals

        # Built-in functions available everywhere in AION
        self._register_builtins()

    # ----------------------------------------------------------
    # Public interface
    # ----------------------------------------------------------

    def execute(self, program: Program):
        """Execute a full AION program."""
        for statement in program.statements:
            self._execute_node(statement)

    # ----------------------------------------------------------
    # Node dispatcher
    # ----------------------------------------------------------

    def _execute_node(self, node):
        """
        Route a node to its matching execute method.
        This is the heart of the interpreter.
        """
        method_name = f"_exec_{type(node).__name__}"
        method      = getattr(self, method_name, None)

        if method is None:
            raise RuntimeError(
                f"AION doesn't know how to execute "
                f"'{type(node).__name__}' yet."
            )

        return method(node)

    # ----------------------------------------------------------
    # Statement executors
    # ----------------------------------------------------------

    def _exec_Program(self, node: Program):
        for stmt in node.statements:
            self._execute_node(stmt)

    def _exec_AssignStatement(self, node: AssignStatement):
        """Execute:  name = value"""
        value = self._execute_node(node.value)
        self.env.set(node.name, value)
        return value

    def _exec_ShowStatement(self, node: ShowStatement):
        """Execute:  show <expression>"""
        value = self._execute_node(node.expression)
        print(self._to_string(value))
        return value

    def _exec_IfStatement(self, node: IfStatement):
        """
        Execute:
            if <condition>:
                <then_body>
            else:
                <else_body>
        """
        condition = self._execute_node(node.condition)

        if self._is_truthy(condition):
            self._execute_block(node.then_body)
        else:
            self._execute_block(node.else_body)

    def _exec_RepeatStatement(self, node: RepeatStatement):
        """
        Execute:
            repeat <count>:
                <body>
        """
        count = self._execute_node(node.count)

        if not isinstance(count, (int, float)):
            raise RuntimeError(
                f"'repeat' needs a number, not '{count}'.\n"
                f"  Example:  repeat 5:"
            )

        for _ in range(int(count)):
            self._execute_block(node.body)
    
    def _exec_WhileStatement(self, node: WhileStatement):
        """
        Execute:
            while <condition>:
                <body>
        """
        max_iterations = 10000
        count = 0

        while self._is_truthy(
                self._execute_node(node.condition)):
            # No new scope — variables update in current scope
            self._execute_block(node.body, new_scope=False)
            count += 1
            if count >= max_iterations:
                raise RuntimeError(
                    "While loop ran too many times.\n"
                    "  Check your loop condition."
                )

    def _exec_TaskStatement(self, node: TaskStatement):
        """
        Execute:  task greet(name): ...
        Stores the task definition in the environment.
        The task body is NOT executed yet — only when called.
        """
        self.env.set(node.name, node)

    def _exec_ReturnStatement(self, node: ReturnStatement):
        """
        Execute:  return <value>
        Raises ReturnSignal to unwind the call stack.
        """
        value = None
        if node.value is not None:
            value = self._execute_node(node.value)
        raise ReturnSignal(value)

    def _exec_UseStatement(self, node: UseStatement):
        module_name = node.module
        from stdlib import load_module
        try:
            stdlib = load_module(module_name)
            for name, func in stdlib.items():
                self.env.set(name, func)
        except ImportError as e:
            raise AIONImportError(str(e))

    def _exec_CallExpression(self, node: CallExpression):
        """
        Execute:  greet("Emmanuel")
        Looks up the task and runs it with the given arguments.
        """
        # Check built-ins first
        callee = self.env.get(node.name)

        # Evaluate all arguments
        args = [self._execute_node(arg) for arg in node.args]

        # Built-in Python function
        if callable(callee) and not isinstance(callee, TaskStatement):
            return callee(*args)

        # AION task
        if isinstance(callee, TaskStatement):
            return self._call_task(callee, args)

        raise RuntimeError(
            f"'{node.name}' is not a task you can call.\n"
            f"  Define it first with:  task {node.name}(...):"
        )

    # ----------------------------------------------------------
    # Expression evaluators
    # ----------------------------------------------------------

    def _exec_BinaryOp(self, node: BinaryOp):
        """Evaluate a binary operation like age + 1 or x == y."""
        left  = self._execute_node(node.left)
        right = self._execute_node(node.right)
        op    = node.operator

        try:
            if op == "+":
                # Support string concatenation
                if isinstance(left, str) or isinstance(right, str):
                    return self._to_string(left) + self._to_string(right)
                return left + right
            if op == "-":  return left - right
            if op == "*":  return left * right
            if op == "/":
                if right == 0:
                    raise RuntimeError(
                        "Cannot divide by zero.\n"
                        "  Check your divisor value."
                    )
                return left / right
            if op == "%":  return left % right
            if op == "**": return left ** right
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<":  return left <  right
            if op == "<=": return left <= right
            if op == ">":  return left >  right
            if op == ">=": return left >= right

        except TypeError:
            raise RuntimeError(
                f"Cannot use '{op}' between "
                f"'{type(left).__name__}' and '{type(right).__name__}'.\n"
                f"  Check that both values are the right type."
            )

        raise RuntimeError(f"Unknown operator '{op}'.")

    def _exec_UnaryOp(self, node: UnaryOp):
        """Evaluate a unary operation like -x or not true."""
        operand = self._execute_node(node.operand)

        if node.operator == "-":
            return -operand
        if node.operator == "not":
            return not self._is_truthy(operand)

        raise RuntimeError(f"Unknown operator '{node.operator}'.")

    # ── Literals ──────────────────────────────────────────────

    def _exec_IntegerLiteral(self, node: IntegerLiteral):
        return node.value

    def _exec_FloatLiteral(self, node: FloatLiteral):
        return node.value

    def _exec_StringLiteral(self, node: StringLiteral):
        """
        Execute a string literal.
        Supports interpolation: "Hello {name}!"
        """
        import re
        value = node.value

        # Find all {variable} patterns
        def replace_var(match):
            var_name = match.group(1).strip()
            try:
                val = self.env.get(var_name)
                return self._to_string(val)
            except Exception:
                return match.group(0)

        return re.sub(r'\{(\w+)\}', replace_var, value)

    def _exec_BooleanLiteral(self, node: BooleanLiteral):
        return node.value

    def _exec_NullLiteral(self, node: NullLiteral):
        return None

    def _exec_Identifier(self, node: Identifier):
        """Look up a variable's value in the current scope."""
        try:
            return self.env.get(node.name)
        except NameError as e:
            raise AIONNameError(str(e))

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def _execute_block(self, statements: list,
                       new_scope: bool = True):
        """
        Execute a list of statements.
        new_scope=False keeps variables in the current scope.
        Used by while loops so counter updates propagate.
        """
        if new_scope:
            previous = self.env
            self.env = Environment(parent=previous)
        try:
            for stmt in statements:
                self._execute_node(stmt)
        finally:
            if new_scope:
                self.env = previous

    def _call_task(self, task: TaskStatement, args: list):
        """
        Execute a task with the given arguments.
        Creates a fresh local scope for the task.
        """
        if len(args) != len(task.params):
            raise RuntimeError(
                f"Task '{task.name}' expects "
                f"{len(task.params)} argument(s) "
                f"but got {len(args)}."
            )

        # Create a new local scope with params as variables
        local_env    = Environment(parent=self.globals)
        previous_env = self.env

        for param, value in zip(task.params, args):
            local_env.set(param, value)

        self.env = local_env

        try:
            for stmt in task.body:
                self._execute_node(stmt)
            return None

        except ReturnSignal as r:
            return r.value

        finally:
            self.env = previous_env

    def _is_truthy(self, value) -> bool:
        """
        Determine if a value is considered true in AION.
        Rules:
            null  → false
            false → false
            0     → false
            ""    → false
            everything else → true
        """
        if value is None:        return False
        if value is False:       return False
        if value == 0:           return False
        if value == "":          return False
        return True

    def _to_string(self, value) -> str:
        """Convert any AION value to a printable string."""
        if value is None:        return "null"
        if value is True:        return "true"
        if value is False:       return "false"
        return str(value)

    def _register_builtins(self):
        """Register built-in functions available in all AION programs."""
        self.globals.set("type_of",   lambda x: type(x).__name__)
        self.globals.set("to_number", lambda x: float(x)
                         if "." in str(x) else int(x))
        self.globals.set("to_text",   lambda x: str(x))
        self.globals.set("length",    lambda x: len(x))
        self.globals.set("ask",       lambda prompt="": input(str(prompt)))
        self.globals.set("clear",     lambda: print("\033[H\033[J", end=""))
        self.globals.set("sleep",     lambda s=1: __import__("time").sleep(float(s)))
        self.globals.set("random_num",lambda a, b: __import__("random").randint(int(a), int(b)))

    def _load_stdlib(self, name: str) -> dict:
        """
        Load a standard library module.
        Delegates to the stdlib package registry.
        """
        from stdlib import load_module
        try:
            return load_module(name)
        except ImportError:
            return None