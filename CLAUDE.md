# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A learning repo that follows Google's "Build Multi-Agent Systems with ADK" codelab (`google-adk==1.17.0`). It has two independent ADK agent packages. Each one exposes a `root_agent` in `agent.py`, and its `__init__.py` does `from . import agent`, which is how the ADK CLI finds it. There is no test suite, linter or build step.

## Commands

`./run_local.sh` does all of this in one step: it creates `.venv`, installs requirements when they change, checks `.env` for `MODEL`, then starts `adk web` (port from `PORT`, default 8000). Any arguments are passed to `adk`, for example `./run_local.sh run workflow_agents` (the script adds the `agents/` prefix).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run from the repo root (the agent dir name is the argument)
adk run agents/parent_and_subagents   # interactive CLI
adk run agents/workflow_agents
adk web agents                        # dev UI; serves the agents/ folder
```

Configuration comes from a single root `.env` (gitignored), created from the committed `.env.example`. It sets `MODEL` (required), model access, and optionally `GOOGLE_APPLICATION_CREDENTIALS` and CA bundle paths for Zscaler. Model access is either `ANTHROPIC_API_KEY` (the default, Claude), Vertex AI through `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`, or a `GOOGLE_API_KEY`. When you add a new variable, add it to `.env.example` too. `.vscode/launch.json` debugs `agents/parent_and_subagents/agent.py` using the project's `.venv`.

## Architecture

- **`agents/` is the ADK agents directory.** `adk web agents` lists every non-hidden subfolder as an agent, so only agent packages go there. A non-agent folder inside it shows up in the UI and fails with "No root_agent found". Shared modules (`callback_logging.py`, `model_config.py`) stay at the repo root, and each `agent.py` adds the repo root to `sys.path` (two levels up) so it can import them.
- **`model_config.py`** (repo root) has `get_model()`, which every agent uses for its `model=` argument. A `MODEL` starting with `anthropic/` (for example `anthropic/claude-sonnet-5-5`) is wrapped in ADK's `LiteLlm` and calls the Anthropic API directly. Any other value, such as a Gemini name, is passed through as a string for ADK's native Gemini support. Don't use `os.getenv("MODEL")` directly in new agents.
- **`callback_logging.py`** (repo root) provides `log_query_to_model` and `log_model_response`. They are attached as `before_model_callback` and `after_model_callback` and log through Python `logging`, which goes to Cloud Logging when it is set up.
- **`agents/parent_and_subagents/`** is a travel planner (diagrammed in `agents_flow.md` in that folder; keep it in sync). The `steering` root agent hands off to the `travel_brainstormer` and `attractions_planner` sub-agents through LLM transfer. The tool `save_attractions_to_state` writes to `tool_context.state["attractions"]`, and an instruction reads it back with `{ attractions? }`. This module validates `GOOGLE_APPLICATION_CREDENTIALS` and falls back to plain `logging.basicConfig` when Cloud Logging is unavailable. 
- **`agents/workflow_agents/`** is a movie-pitch generator that shows the workflow agents in a nested setup. `agents_flow.md` in that folder has Mermaid diagrams of its control flow and state-key reads and writes, so update it when you change the agents, their tools or their state keys.
  - `greeter` (root `Agent`) stores the user's input in the `PROMPT` state key, then transfers to `film_concept_team`.
  - `film_concept_team` is a `SequentialAgent` that runs these steps in order:
    1. `writers_room`, a `LoopAgent` (`max_iterations=5`) that runs `researcher` (a Wikipedia tool through `LangchainTool`), then `screenwriter`, then `critic`. The critic ends the loop by calling `exit_loop`.
    2. `preproduction_team`, a `ParallelAgent` that runs `box_office_researcher` and `casting_agent`.
    3. `file_writer`, which saves the pitch to `movie_pitches/<title>.txt`. This path is relative to the current directory, so run from the repo root.
  - Agents pass data through session state. The `append_to_state` tool appends items to list keys (`PROMPT`, `PLOT_OUTLINE`, `research`, `CRITICAL_FEEDBACK`). The parallel agents use `output_key` instead (`box_office_report`, `casting_report`). Instructions read these keys with the optional template `{ KEY? }`. Key names are case-sensitive and must match exactly across tools, `output_key` values and instructions.
  - It tries Cloud Logging first and falls back to plain `logging.basicConfig` if that fails.
- **`movie_pitches/`** holds sample output that `workflow_agents` has produced and committed.

## Environment notes

The README explains how to work behind Zscaler TLS inspection: build a combined CA bundle from certifi plus the Zscaler root CA, then point Python or requests at it through `.env`.
