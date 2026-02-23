# Agent Wrapper Monorepo

This repository contains the autonomous agent frameworks.

## Structure

*   **`agent-framework/`**: The core coding agent (LangGraph + DSPy + OneContext).
*   **`video-agent/`**: The local video generation agent (Flux + LivePortrait).

## Setup

Each folder is a self-contained Poetry project.

```bash
# To run the coding agent:
cd agent-framework
poetry install
python src/agent_wrapper/main.py build "Your task"

# To run the video agent:
cd video-agent
poetry install
python src/video_agent/main.py generate "A cyberpunk city"
```
