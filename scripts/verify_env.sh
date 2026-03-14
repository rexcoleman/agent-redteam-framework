#!/usr/bin/env bash
# Phase 0 gate: verify environment and framework imports
set -e

echo "=== Environment Verification ==="

# Check conda env
echo -n "Conda env 'agent-redteam': "
conda run -n agent-redteam python --version 2>/dev/null && echo "OK" || { echo "FAIL"; exit 1; }

# Check disk space (ISS-039)
AVAIL_GB=$(df -BG --output=avail /home | tail -1 | tr -d ' G')
echo -n "Disk headroom (${AVAIL_GB}GB free): "
if [ "$AVAIL_GB" -lt 3 ]; then
    echo "FAIL — need ≥3GB free"
    exit 1
fi
echo "OK"

# Check data disk
echo -n "Data disk /data: "
if mountpoint -q /data 2>/dev/null; then
    echo "OK ($(df -BG --output=avail /data | tail -1 | tr -d ' G')GB free)"
else
    echo "WARN — not mounted (optional)"
fi

# Check framework imports
echo ""
echo "=== Framework Imports ==="

conda run -n agent-redteam python -c "
import sys
failures = []

# LangChain + LangGraph
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import StructuredTool
    from langchain_anthropic import ChatAnthropic
    print('LangChain + LangGraph: OK')
except ImportError as e:
    print(f'LangChain: FAIL — {e}')
    failures.append('langchain')

# CrewAI
try:
    from crewai import Agent, Crew, Task
    print('CrewAI: OK')
except ImportError as e:
    print(f'CrewAI: FAIL — {e}')
    failures.append('crewai')

# AutoGen
try:
    from autogen_agentchat.agents import AssistantAgent
    print('AutoGen: OK')
except ImportError as e:
    print(f'AutoGen: FAIL — {e}')
    failures.append('autogen')

# Core dependencies
try:
    import click, rich, yaml, tqdm
    print('Core deps (click, rich, yaml, tqdm): OK')
except ImportError as e:
    print(f'Core deps: FAIL — {e}')
    failures.append('core')

# Project imports
try:
    sys.path.insert(0, '.')
    from src.core.config import load_config
    from src.core.types import AttackResult, AgentResponse
    from src.agents.base import AgentTarget
    print('Project imports: OK')
except ImportError as e:
    print(f'Project imports: FAIL — {e}')
    failures.append('project')

if failures:
    print(f'\nFAILED: {failures}')
    sys.exit(1)
else:
    print('\nAll imports OK.')
"

# Check API keys
echo ""
echo "=== API Keys ==="
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "ANTHROPIC_API_KEY: SET"
else
    echo "ANTHROPIC_API_KEY: NOT SET — required for agent targets"
fi
if [ -n "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY: SET"
else
    echo "OPENAI_API_KEY: NOT SET (optional)"
fi

echo ""
echo "=== Environment verification complete ==="
