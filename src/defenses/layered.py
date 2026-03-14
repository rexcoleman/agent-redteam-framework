"""Defense: Layered defense combining input sanitizer + tool permission boundary.

Defense-in-depth: sanitize inputs THEN enforce tool boundaries.
"""

from typing import Any

from ..agents.base import AgentTarget
from ..core.types import AgentResponse
from .input_sanitizer import InputSanitizer
from .tool_permission_boundary import ToolPermissionBoundary


class LayeredDefense:
    """Combines input sanitization and tool boundary enforcement."""

    def __init__(self, agent: AgentTarget):
        # Layer 1: Input sanitizer (blocks known injection patterns)
        self._sanitizer = InputSanitizer(agent, mode="block")
        # Layer 2: Tool boundary (enforces write permissions + rate limiting)
        self._boundary = ToolPermissionBoundary(
            agent,
            sensitive_tools=["file_writer"],
            max_tool_calls=5,
        )
        self.agent = agent

    def setup(self) -> None:
        self.agent.setup()

    def reset(self) -> None:
        self.agent.reset()
        self._sanitizer.blocked_count = 0
        self._sanitizer.warned_count = 0
        self._boundary.blocked_calls = 0
        self._boundary.rate_limited = 0

    def run_task(self, task: str) -> AgentResponse:
        # Layer 1: Check input for injection patterns
        sanitizer_response = self._sanitizer.run_task(task)
        if "[BLOCKED]" in sanitizer_response.output:
            return sanitizer_response

        # Layer 2: Run through tool boundary (re-execute since sanitizer passed through)
        self._boundary.reset()
        return self._boundary.run_task(task)

    def get_stats(self) -> dict[str, Any]:
        return {
            "input_sanitizer": self._sanitizer.get_stats(),
            "tool_boundary": self._boundary.get_stats(),
        }
