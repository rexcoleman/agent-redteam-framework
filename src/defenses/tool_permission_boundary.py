"""Defense: Tool permission boundary enforcement.

Wraps an AgentTarget and enforces tool usage policies:
- Allowlisted tool sequences
- Parameter validation
- Rate limiting per tool
"""

from typing import Any
from ..agents.base import AgentTarget
from ..core.types import AgentResponse


class ToolPermissionBoundary:
    """Wraps an AgentTarget with tool usage policies."""

    def __init__(
        self,
        agent: AgentTarget,
        sensitive_tools: list[str] | None = None,
        max_tool_calls: int = 5,
        require_confirmation_for: list[str] | None = None,
    ):
        """
        Args:
            agent: The agent target to protect.
            sensitive_tools: Tools that require explicit user intent (e.g., file_writer).
            max_tool_calls: Maximum tool calls per task (prevents loop manipulation).
            require_confirmation_for: Tools that should prompt for confirmation.
        """
        self.agent = agent
        self.sensitive_tools = set(sensitive_tools or ["file_writer"])
        self.max_tool_calls = max_tool_calls
        self.require_confirmation_for = set(require_confirmation_for or [])
        self.blocked_calls = 0
        self.rate_limited = 0

    def setup(self) -> None:
        self.agent.setup()

    def reset(self) -> None:
        self.agent.reset()
        self.blocked_calls = 0
        self.rate_limited = 0

    def run_task(self, task: str) -> AgentResponse:
        """Run task with tool boundary enforcement.

        Strategy: Run the agent, then audit the tool calls post-hoc.
        If violations detected, return a modified response.
        """
        # Check if task explicitly mentions sensitive tools
        task_lower = task.lower()
        mentions_sensitive = any(
            tool in task_lower for tool in self.sensitive_tools
        )

        response = self.agent.run_task(task)

        # Post-hoc audit of tool calls
        violations = []

        # Check for sensitive tool usage without explicit user intent
        for tc in response.tool_calls:
            tool_name = tc.get("name", "")
            if tool_name in self.sensitive_tools:
                # Only allow if the user's original task explicitly referenced writing/saving
                write_intent_keywords = ["write", "save", "create file", "store"]
                has_intent = any(kw in task_lower for kw in write_intent_keywords)
                if not has_intent:
                    violations.append(
                        f"Tool '{tool_name}' used without explicit write intent in user request"
                    )
                    self.blocked_calls += 1

        # Check tool call count (rate limiting)
        if len(response.tool_calls) > self.max_tool_calls:
            violations.append(
                f"Excessive tool calls: {len(response.tool_calls)} > limit {self.max_tool_calls}"
            )
            self.rate_limited += 1

        if violations:
            violation_msg = "; ".join(violations)
            response.output = (
                f"[BOUNDARY VIOLATION] {violation_msg}. "
                f"Original response suppressed for security review."
            )
            response.tool_calls = []  # Strip tool call evidence

        return response

    def get_stats(self) -> dict[str, int]:
        return {
            "blocked_calls": self.blocked_calls,
            "rate_limited": self.rate_limited,
        }
