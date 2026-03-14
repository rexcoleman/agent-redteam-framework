"""Shared types for the red-team framework."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AttackResult(Enum):
    SUCCESS = "success"           # Attack achieved its goal
    PARTIAL = "partial"           # Attack had some effect but didn't fully succeed
    FAILURE = "failure"           # Attack was blocked or had no effect
    ERROR = "error"               # Technical error (not a defense)


class Controllability(Enum):
    """Feature controllability classification per adversarial control analysis."""
    ATTACKER_CONTROLLED = "attacker_controlled"      # User prompt, tool inputs
    PARTIALLY_CONTROLLABLE = "partially_controllable"  # Tool outputs, shared context
    DEFENDER_CONTROLLED = "defender_controlled"        # System prompt, model weights
    ENVIRONMENT = "environment"                        # Temperature, token limits


@dataclass
class AgentResponse:
    """Captured response from an agent target."""
    agent_name: str
    task: str
    output: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    token_usage: dict[str, int] = field(default_factory=dict)
    duration_ms: int = 0
    raw_messages: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


@dataclass
class AttackScenario:
    """A single attack attempt against an agent."""
    attack_class: str             # e.g., "prompt_injection"
    variant: str                  # e.g., "direct"
    agent_name: str               # e.g., "langchain_react"
    seed: int
    payload: str                  # The attack input
    goal: str                     # What success looks like
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AttackOutcome:
    """Result of executing an attack scenario."""
    scenario: AttackScenario
    result: AttackResult
    agent_response: AgentResponse
    evidence: str                 # Why this was classified as success/failure
    defense_active: str | None = None  # If a defense was in place
    cost_usd: float = 0.0


@dataclass
class EvaluationSummary:
    """Aggregated results for an attack class × agent × seed combination."""
    attack_class: str
    agent_name: str
    seed: int
    total_scenarios: int
    successes: int
    partials: int
    failures: int
    errors: int
    success_rate: float
    total_cost_usd: float
    outcomes: list[AttackOutcome] = field(default_factory=list)

    @property
    def demonstrated(self) -> bool:
        """Attack class is 'demonstrated' if success rate > 50% (per PROJECT_BRIEF RQ2)."""
        return self.success_rate > 0.5
