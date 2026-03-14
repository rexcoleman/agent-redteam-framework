"""Defense: Full defense stack — all 3 layers.

Layer 1: Input Sanitizer (regex patterns — fast, free)
Layer 2: LLM Judge (semantic intent detection — catches reasoning hijack)
Layer 3: Tool Permission Boundary (post-hoc audit — catches unauthorized writes + loops)
"""

from typing import Any

from ..agents.base import AgentTarget
from ..core.types import AgentResponse
from .input_sanitizer import InputSanitizer
from .llm_judge import LLMJudgeDefense
from .tool_permission_boundary import ToolPermissionBoundary


class FullDefense:
    """Three-layer defense-in-depth."""

    def __init__(self, agent: AgentTarget, llm_config: dict[str, Any]):
        self.agent = agent
        self.llm_config = llm_config
        self._sanitizer = InputSanitizer(agent, mode="block")
        self._judge = LLMJudgeDefense(agent, llm_config, threshold="MALICIOUS")
        self._boundary = ToolPermissionBoundary(
            agent, sensitive_tools=["file_writer"], max_tool_calls=5,
        )

    def setup(self) -> None:
        self.agent.setup()
        self._judge.setup()

    def reset(self) -> None:
        self.agent.reset()
        self._sanitizer.blocked_count = 0
        self._sanitizer.warned_count = 0
        self._judge.blocked_count = 0
        self._judge.suspicious_count = 0
        self._boundary.blocked_calls = 0
        self._boundary.rate_limited = 0

    def run_task(self, task: str) -> AgentResponse:
        # Layer 1: Pattern-based input sanitizer (free, fast)
        sanitizer_response = self._sanitizer.run_task(task)
        if "[BLOCKED]" in sanitizer_response.output:
            return sanitizer_response

        # Layer 2: LLM Judge (semantic, catches reasoning hijack)
        judge_response = self._judge.run_task(task)
        if "[BLOCKED by LLM Judge]" in judge_response.output:
            return judge_response

        # Layer 3: Tool boundary (post-hoc audit)
        return self._boundary.run_task(task)

    def get_stats(self) -> dict[str, Any]:
        return {
            "input_sanitizer": self._sanitizer.get_stats(),
            "llm_judge": self._judge.get_stats(),
            "tool_boundary": self._boundary.get_stats(),
        }
