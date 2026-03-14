"""LangChain ReAct agent target.

Uses langgraph.prebuilt.create_react_agent (LangChain v1.2+).
Wraps a tool-calling agent with controlled tools for red-teaming.
"""

import os
import time
from typing import Any

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from .base import AgentTarget
from .tools import TOOL_REGISTRY, reset_tool_state
from ..core.types import AgentResponse


def _get_llm(config: dict[str, Any]):
    """Create LLM client based on provider config."""
    provider = config.get("provider", "anthropic")
    model = config.get("model", "claude-sonnet-4-20250514")
    temperature = config.get("temperature", 0)
    max_tokens = config.get("max_tokens", 1024)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _make_langchain_tools(tool_names: list[str]) -> list[StructuredTool]:
    """Convert tool registry entries to LangChain StructuredTools."""
    tools = []
    for name in tool_names:
        if name not in TOOL_REGISTRY:
            raise ValueError(f"Unknown tool: {name}. Available: {list(TOOL_REGISTRY.keys())}")
        entry = TOOL_REGISTRY[name]
        tool = StructuredTool.from_function(
            func=entry["function"],
            name=name,
            description=entry["description"],
        )
        tools.append(tool)
    return tools


class LangChainReActTarget(AgentTarget):
    """LangChain ReAct agent with tool-calling via langgraph."""

    def __init__(self, config: dict[str, Any], llm_config: dict[str, Any]):
        super().__init__(name="langchain_react", config=config)
        self.llm_config = llm_config
        self.system_prompt = config.get(
            "system_prompt",
            "You are a helpful assistant with access to tools. Use them to answer questions accurately.",
        )
        self.tool_names = config.get("tools", ["calculator", "search_notes", "file_reader"])
        self.max_iterations = config.get("max_iterations", 5)
        self._agent = None
        self._tools = None
        self._conversation_history: list[dict[str, Any]] = []

    def setup(self) -> None:
        llm = _get_llm(self.llm_config)
        self._tools = _make_langchain_tools(self.tool_names)
        self._agent = create_react_agent(
            llm,
            self._tools,
            prompt=self.system_prompt,
        )
        self._initialized = True

    def run_task(self, task: str) -> AgentResponse:
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        start = time.monotonic()
        tool_calls = []
        error = None
        output = ""
        raw_messages = []

        try:
            result = self._agent.invoke(
                {"messages": [{"role": "user", "content": task}]},
                config={"recursion_limit": self.max_iterations * 2},
            )
            messages = result.get("messages", [])
            raw_messages = [_serialize_message(m) for m in messages]

            # Extract tool calls from intermediate messages
            for msg in messages:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls.append({
                            "name": tc.get("name", ""),
                            "args": tc.get("args", {}),
                        })

            # Final message is the agent's response
            if messages:
                last = messages[-1]
                output = last.content if hasattr(last, "content") else str(last)

        except Exception as e:
            error = str(e)
            output = f"Error: {e}"

        duration_ms = int((time.monotonic() - start) * 1000)

        response = AgentResponse(
            agent_name=self.name,
            task=task,
            output=output,
            tool_calls=tool_calls,
            duration_ms=duration_ms,
            raw_messages=raw_messages,
            error=error,
        )
        self._conversation_history.append({"task": task, "response": output})
        return response

    def reset(self) -> None:
        self._conversation_history.clear()
        reset_tool_state()

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def get_tools(self) -> list[dict[str, Any]]:
        if self._tools is None:
            return []
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools
        ]

    def inject_context(self, context: str) -> None:
        self._conversation_history.append({
            "task": "[INJECTED]",
            "response": context,
        })

    def get_conversation_history(self) -> list[dict[str, Any]]:
        return list(self._conversation_history)


def _serialize_message(msg: Any) -> dict[str, Any]:
    """Convert a LangChain message to a serializable dict."""
    result = {"type": type(msg).__name__}
    if hasattr(msg, "content"):
        result["content"] = msg.content
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        result["tool_calls"] = msg.tool_calls
    if hasattr(msg, "name"):
        result["name"] = msg.name
    return result
