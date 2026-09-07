"""
Phase 28 — Agent System + Unified Schema (agent declaration, part 2)

Tests for the first-class `agent "Name": ...` declaration, which
compiles down to exactly the same agent_create()/agent_tool() calls
the older function-call API already used — see AgentDefinition's
docstring in nodes.py and _exec_AgentDefinition in interpreter.py.

Also covers a real bug found and fixed alongside this work:
AgentRunner's provider is a long-lived singleton reused across every
agent_run() call (agents_module._agent_run caches a single module-level
_runner). Without an unconditional reset, one agent's `model:` choice
would silently leak into the next agent's run if that next agent had
no model of its own configured.
"""
import io
import re
import sys
import unittest

from nekova.lexer.lexer import Lexer
from nekova.parser.parser import Parser
from nekova.interpreter.interpreter import Interpreter
from nekova.interpreter.exceptions import NEKOVARuntimeError
from nekova.ai.agents_module import _agents, _runner
import nekova.ai.agents_module as agents_module

ANSI = re.compile(r'\x1b\[[0-9;]*m')


def run(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    interp = Interpreter()
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        interp.run(ast)
    finally:
        sys.stdout = old
    return ANSI.sub('', buf.getvalue()).strip()


class AgentTestBase(unittest.TestCase):
    """_agents (and the cached _runner) are module-level globals in
    agents_module.py — clear them between tests so one test's agents
    can't leak into another's, same precaution test_agents_security.py
    already takes."""

    def setUp(self):
        _agents.clear()
        agents_module._runner = None


class TestAgentDeclarationBasics(AgentTestBase):
    def test_let_captures_agent_name(self):
        out = run(
            'use agents\n'
            'let researcher = agent "Research Assistant":\n'
            '    tools: [summarize]\n'
            'show researcher\n'
        )
        self.assertIn("Research Assistant", out)

    def test_bare_statement_form_works(self):
        run(
            'use agents\n'
            'agent "Simple Bot":\n'
            '    tools: [summarize]\n'
        )
        self.assertIn("Simple Bot", _agents)

    def test_goal_field_applied(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    goal: "Do the thing"\n'
        )
        self.assertEqual(_agents["Bot"].goal, "Do the thing")

    def test_goal_defaults_when_omitted(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [summarize]\n'
        )
        self.assertEqual(_agents["Bot"].goal, "Complete tasks")

    def test_tools_field_registers_tools(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [summarize, calculate]\n'
        )
        self.assertEqual(set(_agents["Bot"].tools.keys()),
                          {"summarize", "calculate"})

    def test_agent_declared_without_tools_is_fine(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    goal: "Just talk"\n'
        )
        self.assertEqual(_agents["Bot"].tools, {})

    def test_model_field_sets_agent_model(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    model: "gpt-4o"\n'
        )
        self.assertEqual(_agents["Bot"].model, "gpt-4o")

    def test_no_model_field_leaves_model_none(self):
        run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [summarize]\n'
        )
        self.assertIsNone(_agents["Bot"].model)

    def test_agent_as_ordinary_variable_still_works(self):
        """'agent' is a soft keyword — using it as a plain variable
        name must keep working, exactly like 'prompt'/'schema' do."""
        out = run('let agent = 5\nshow agent\n')
        self.assertEqual(out, "5")


class TestAgentDeclarationInterop(AgentTestBase):
    """Agents built via the new declaration must be fully usable
    through the old function-call API, and vice versa — both syntaxes
    share the same underlying _agents registry."""

    def test_declared_agent_works_with_agent_run(self):
        out = run(
            'use agents\n'
            'let bot = agent "Bot":\n'
            '    tools: [summarize]\n'
            'show agent_run(bot, "hello world")\n'
        )
        self.assertIn("summarize", out.lower())

    def test_declared_agent_works_with_agent_status(self):
        out = run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [summarize]\n'
            'show agent_status("Bot")\n'
        )
        self.assertTrue(out.endswith("idle"))

    def test_function_call_agent_unaffected(self):
        """Plain old-style agent_create/agent_tool must still work
        exactly as before, unmodified by any of this."""
        out = run(
            'use agents\n'
            'agent_create("Classic", "old style")\n'
            'agent_tool("Classic", "summarize", "")\n'
            'show agent_status("Classic")\n'
        )
        self.assertTrue(out.endswith("idle"))


class TestAgentDeclarationErrors(AgentTestBase):
    def test_tools_must_be_a_list(self):
        with self.assertRaises(NEKOVARuntimeError):
            run(
                'use agents\n'
                'agent "Bot":\n'
                '    tools: "summarize"\n'
            )

    def test_tools_entry_must_be_name_or_call(self):
        with self.assertRaises(NEKOVARuntimeError):
            run(
                'use agents\n'
                'agent "Bot":\n'
                '    tools: [42]\n'
            )


class TestAgentModelDoesNotLeak(AgentTestBase):
    """Regression test for the AgentRunner singleton-provider bug:
    since agents_module._agent_run reuses one cached AgentRunner (and
    therefore one cached provider) across every call, an agent with no
    model of its own must never inherit a previous agent's choice."""

    def test_model_reset_between_agents(self):
        run(
            'use agents\n'
            'agent "First":\n'
            '    model: "gpt-4o"\n'
            'agent_run("First", "task one")\n'
            'agent "Second":\n'
            '    tools: [summarize]\n'
            'agent_run("Second", "task two")\n'
        )
        # After Second's run, the shared runner's provider must not
        # still be carrying First's model.
        self.assertIsNone(agents_module._runner.provider.model)


class TestTaskAsToolResolution(AgentTestBase):
    """Phase 28 step 3: tools: [...] can reference a NEKOVA task in
    scope, not just the four built-ins. Only reachable through the
    agent "Name": ... declaration — the old agent_tool(...) function
    has no interpreter/environment access to resolve a task by name,
    so this is deliberately not retrofitted onto it."""

    def test_custom_task_is_called_as_the_tool(self):
        out = run(
            'use agents\n'
            'task loud_echo(x):\n'
            '    return "ECHO: " + x\n'
            'agent "Echoer":\n'
            '    tools: [loud_echo]\n'
            'show agent_run("Echoer", "hello")\n'
        )
        self.assertIn("ECHO: ", out)
        self.assertIn("hello", out)

    def test_custom_task_takes_priority_over_builtin_of_same_name(self):
        """A user's own `task calculate(...)` must shadow the
        built-in calculate tool, not be silently overridden by it."""
        out = run(
            'use agents\n'
            'task calculate(x):\n'
            '    return "CUSTOM CALC RAN"\n'
            'agent "Bot":\n'
            '    tools: [calculate]\n'
            'show agent_run("Bot", "2 + 2")\n'
        )
        self.assertIn("CUSTOM CALC RAN", out)

    def test_unrecognized_name_still_falls_back_gracefully(self):
        """Names that are neither a built-in nor a task in scope must
        keep working exactly as before (the pre-existing generic
        AI-prompt fallback in _agent_tool) — not error."""
        out = run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [some_totally_unknown_name]\n'
            'show agent_run("Bot", "hi")\n'
        )
        self.assertIn("some_totally_unknown_name", out)

    def test_builtin_tool_unaffected_when_no_matching_task_exists(self):
        """The task-lookup check must not interfere with ordinary
        built-in tool resolution when there's no task shadowing it."""
        out = run(
            'use agents\n'
            'agent "Bot":\n'
            '    tools: [calculate]\n'
            'show agent_run("Bot", "2 + 2")\n'
        )
        self.assertIn("calculate", out)


class TestSchemaTypedToolInput(AgentTestBase):
    """
    Phase 28 step 4 — the actual fix for the design gap behind the
    original calculate() eval() vulnerability: agent_runner.py used
    to hand every tool the agent's ENTIRE raw plan text, unparsed and
    untyped, with no way for a tool to ask for "just the numbers" or
    "just the query". A tool declared with a schema — e.g.
    calculate(CalcInput) — now gets only the fields that schema
    names, extracted via the exact same _coerce_schema machinery
    `think ... as Person` already uses, instead of the whole plan.

    These tests use a custom task-as-tool (Phase 28 step 3) as a
    probe that echoes back exactly what argument it received, so the
    contrast between "gets the raw plan" and "gets an extracted
    value" is direct and unambiguous rather than inferred from a
    built-in tool's behavior.
    """

    def test_schema_typed_tool_does_not_receive_the_raw_plan_text(self):
        marker = "SECRET_PLAN_MARKER_XYZ"
        out = run(
            'use agents\n'
            'schema CalcInput:\n'
            '    expression: text\n'
            'task capture_arg(x):\n'
            '    return "GOT: " + x\n'
            'agent "Bot":\n'
            '    tools: [capture_arg(CalcInput)]\n'
            f'show agent_run("Bot", "{marker}")\n'
        )
        # The agent's own diagnostic printout echoes the raw task
        # argument regardless of tool behavior (that's separate from
        # what any given tool receives) — what actually matters is
        # the tool's own result, which must show neither the marker
        # nor any of the plan-wrapping text a schema-less tool would
        # have seen.
        self.assertIn("[capture_arg]: GOT:", out)
        tool_result_line = next(
            line for line in out.splitlines() if "[capture_arg]:" in line
        )
        self.assertNotIn(marker, tool_result_line)
        self.assertNotIn("thinking about", tool_result_line)
        self.assertNotIn("Available tools", tool_result_line)

    def test_schemaless_tool_still_receives_the_full_plan_text(self):
        """Contrast case: a tool with NO schema is completely
        unaffected by this feature — same as before step 4 landed."""
        marker = "SECRET_PLAN_MARKER_XYZ"
        out = run(
            'use agents\n'
            'task capture_arg(x):\n'
            '    return "GOT: " + x\n'
            'agent "Bot":\n'
            '    tools: [capture_arg]\n'
            f'show agent_run("Bot", "{marker}")\n'
        )
        self.assertIn(marker, out)
        self.assertIn("thinking about", out)

    def test_single_field_schema_unwraps_to_a_bare_value(self):
        """A one-field schema should hand the tool the bare value
        directly (matching the single-arg convention every built-in
        tool already uses), not a {"expression": ...} dict it would
        have to unpack itself."""
        out = run(
            'use agents\n'
            'schema CalcInput:\n'
            '    expression: text\n'
            'task capture_type(x):\n'
            '    return type_of(x)\n'
            'agent "Bot":\n'
            '    tools: [capture_type(CalcInput)]\n'
            'show agent_run("Bot", "anything")\n'
        )
        self.assertIn("str", out)

    def test_multi_field_schema_passes_a_dict(self):
        """A multi-field schema has no single unambiguous value to
        unwrap to, so the tool gets the whole extracted dict."""
        out = run(
            'use agents\n'
            'schema TwoFields:\n'
            '    a: text\n'
            '    b: text\n'
            'task capture_type(x):\n'
            '    return type_of(x)\n'
            'agent "Bot":\n'
            '    tools: [capture_type(TwoFields)]\n'
            'show agent_run("Bot", "anything")\n'
        )
        self.assertIn("dict", out)

    def test_unknown_schema_reference_raises_clear_error(self):
        with self.assertRaises(NEKOVARuntimeError) as ctx:
            run(
                'use agents\n'
                'agent "Bot":\n'
                '    tools: [calculate(NoSuchSchema)]\n'
            )
        self.assertIn("no such schema", str(ctx.exception).lower())

    def test_non_schema_reference_raises_clear_error(self):
        with self.assertRaises(NEKOVARuntimeError) as ctx:
            run(
                'use agents\n'
                'shape NotASchema:\n'
                '    name str\n'
                'agent "Bot":\n'
                '    tools: [calculate(NotASchema)]\n'
            )
        self.assertIn("isn't a schema", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()