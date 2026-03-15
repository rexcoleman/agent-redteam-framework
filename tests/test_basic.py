"""Basic tests for FP-02 agent red-team framework."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_core_imports():
    from src.core.config import load_config
    from src.core.types import AttackResult, AgentResponse, Controllability
    from src.core.logging import setup_logger
    assert AttackResult.SUCCESS.value == "success"


def test_agent_base_class():
    from src.agents.base import AgentTarget
    assert hasattr(AgentTarget, "run_task")
    assert hasattr(AgentTarget, "reset")
    assert hasattr(AgentTarget, "get_system_prompt")


def test_tool_registry():
    from src.agents.tools import TOOL_REGISTRY, calculator, search_notes
    assert "calculator" in TOOL_REGISTRY
    assert calculator("2 + 3") == "5"
    assert "meeting" in search_notes("budget").lower() or "50K" in search_notes("budget")


def test_config_loads():
    from src.core.config import load_config
    config = load_config("config/base.yaml")
    assert "llm" in config
    assert "agents" in config
    assert "attacks" in config


def test_findings_exists():
    assert Path("FINDINGS.md").exists()
