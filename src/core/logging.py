"""Structured JSONL logging for attack/defense experiments."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import AttackOutcome


def setup_logger(name: str, output_dir: str = "outputs", level: str = "INFO") -> logging.Logger:
    """Create a logger that writes to both console and JSONL file."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
        logger.addHandler(ch)

        # JSONL file handler
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(Path(output_dir) / f"{name}.jsonl")
        fh.setFormatter(_JsonlFormatter())
        logger.addHandler(fh)

    return logger


class _JsonlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            entry["data"] = record.extra_data
        return json.dumps(entry)


def log_outcome(logger: logging.Logger, outcome: AttackOutcome) -> None:
    """Log an attack outcome as structured JSONL."""
    record = logger.makeRecord(
        logger.name, logging.INFO, "", 0,
        f"{outcome.scenario.attack_class}/{outcome.scenario.variant} → {outcome.result.value}",
        (), None,
    )
    record.extra_data = {
        "attack_class": outcome.scenario.attack_class,
        "variant": outcome.scenario.variant,
        "agent": outcome.scenario.agent_name,
        "seed": outcome.scenario.seed,
        "result": outcome.result.value,
        "evidence": outcome.evidence,
        "cost_usd": outcome.cost_usd,
    }
    logger.handle(record)


def write_summary_json(path: str, data: dict[str, Any]) -> None:
    """Write a summary.json artifact per ARTIFACT_MANIFEST_SPEC."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2, default=str)
