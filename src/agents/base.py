"""Base class for agent targets.

All agent frameworks (LangChain, CrewAI, AutoGen) implement this interface.
The red-team framework interacts with agents ONLY through this abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.types import AgentResponse


class AgentTarget(ABC):
    """Abstract agent target that the red-team framework attacks."""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config
        self._initialized = False

    @abstractmethod
    def setup(self) -> None:
        """Initialize the agent (create LLM client, register tools, etc).

        Called once before any tasks are sent.
        """

    @abstractmethod
    def run_task(self, task: str) -> AgentResponse:
        """Send a task to the agent and capture the full response.

        Args:
            task: The user message / task description to send.

        Returns:
            AgentResponse with output, tool calls, token usage, timing.
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state (memory, conversation history) between scenarios.

        Critical for memory poisoning experiments — ensures each scenario
        starts from a clean state.
        """

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent's current system prompt.

        Used for controllability analysis — system prompt is defender-controlled.
        """

    @abstractmethod
    def get_tools(self) -> list[dict[str, Any]]:
        """Return the agent's registered tools and their schemas.

        Used for tool misuse attack planning — identifies attack surface.
        """

    def inject_context(self, context: str) -> None:
        """Inject content into the agent's context/memory.

        Default: no-op. Override for agents that support memory/context injection.
        Used for memory poisoning attacks.
        """

    def get_conversation_history(self) -> list[dict[str, Any]]:
        """Return the agent's conversation history.

        Default: empty. Override for agents that maintain history.
        Used for memory poisoning evidence collection.
        """
        return []
