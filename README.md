# ADK Multiagent Systems

A lightweight multi-agent Python project with two example agents:
- `parent_and_subagents/agent.py` — parent agent that can spawn subagents; supports optional Cloud Logging.
- `workflow_agents/agent.py` — workflow-focused agent example.

This repo is set up for local development with a virtual environment, optional Google Cloud authentication, and VS Code debugging.

## Overview
This repository is a practical starting point inspired by Google’s "Build Multi-Agent Systems with ADK" codelab. It demonstrates how to organize and run multi-agent workflows using the Agent Development Kit (ADK) concepts:
- Hierarchical Agent Tree: Design a `root_agent` that delegates to specialized sub-agents, mirroring real-world team structures for predictable, debuggable flows.
- Reliability through specialization: Smaller agents focused on specific tasks are easier to reason about and improve.
- Maintainability and modularity: Agents created for one workflow can be reused in others.

From the codelab, useful workflow patterns you can adapt here:
- SequentialAgent — compose step-by-step workflows where each agent’s output feeds the next.
- LoopAgent — iterate for refinement cycles (e.g., draft → review → revise).
- ParallelAgent — “fan out and gather” to run independent tasks concurrently and consolidate results.

Practical skills highlighted in the codelab you can bring into this repo:
- Creating parent/sub-agent relationships and controlled handoffs.
- Using session state to store and retrieve information from tools.
- Reading values via key templating (e.g., `{my_key?}`).

How this repo maps to those ideas:
- `parent_and_subagents/agent.py` is where you can define your `root_agent` and register specialized sub-agents.
- `workflow_agents/agent.py` is a convenient place to experiment with Sequential/Loop/Parallel patterns for task orchestration.

For background and detailed walkthroughs, see the official codelab: https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/3-developing-agents/build-a-multi-agent-system-with-adk#0

## Continued experimentation

There are many ways to build on what you've learned. Here are some ideas:

- Add more agents: Try adding a new agent to your preproduction_team ParallelAgent. For example, you could create a marketing_agent that writes a tagline for the movie based on the PLOT_OUTLINE.
- Add more tools: Give your researcher agent more tools. You could create a tool that uses a Google Search API to find information that isn't on Wikipedia.
- Explore CustomAgent: The lab mentioned the CustomAgent for workflows that don't fit the standard templates. Try building one that, for example, conditionally runs an agent only if a specific key exists in the session state.

## Project Structure
```
.
├── .gitignore
├── .vscode/launch.json        # VS Code debug configs
├── requirements.txt           # Python dependencies
├── callback_logging.py        # Logging helper with guarded imports
├── parent_and_subagents/
│   ├── __init__.py
│   └── agent.py
└── workflow_agents/
    ├── __init__.py
    └── agent.py
```

## Prerequisites
- Python 3.11+ recommended
- macOS or Linux
- VS Code (optional, for debugging)
- Google Cloud SDK (`gcloud`) if you want Application Default Credentials (ADC) for Cloud Logging

## Setup
```bash
# From the project root
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration
Create a `.env` in the project root. Common variables:
```env
# LLM model (set to a valid model name for your environment)
MODEL="<your-model-name>"

# Optional: credentials JSON path
# Use either ADC or a Service Account key (see below)
GOOGLE_APPLICATION_CREDENTIALS="<path-to-credentials.json>"
```

### Credentials Options
- Option A — Application Default Credentials (ADC):
  ```bash
  gcloud auth application-default login
  # ADC file typically lives at:
  # ~/.config/gcloud/application_default_credentials.json
  ```
  - You can set `GOOGLE_APPLICATION_CREDENTIALS` to this path, or leave it unset to let ADC be discovered automatically.

- Option B — Service Account key (recommended for production):
  - Create a service account with appropriate roles (e.g., Logging Writer for Cloud Logging).
  - Download the JSON key and set:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account-key.json"
    ```

If the credentials file is invalid or missing, the agent falls back to standard Python logging.

## Run
- Using Python directly:
  ```bash
  source .venv/bin/activate
  python parent_and_subagents/agent.py
  ```

- If you have an `adk` CLI available:
  ```bash
  adk run parent_and_subagents
  ```

## Debugging (VS Code)
This repo includes `.vscode/launch.json` with two configurations:
- Debug agent (file)
- Debug agent (module)

Open the Run and Debug view, pick a configuration, and start debugging. The configurations use the project virtualenv (`.venv/bin/python`) and set `PYTHONPATH` to the workspace for consistent imports.

## Notes
- Secrets are excluded via `.gitignore` (env files, credentials JSONs, venvs, caches).
- Avoid committing credentials; use environment variables or secret managers.
- Cloud Logging is optional; if credentials are valid, it uses them, else it falls back to standard logging.

## References
- Build Multi-Agent Systems with ADK (Google Codelab): https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/3-developing-agents/build-a-multi-agent-system-with-adk#0

- ADK Python SDK:  https://github.com/google/adk-python


## Networking Behind Zscaler

### Best Fix: Trust Zscaler CA in Python

When running behind Zscaler (TLS inspection), Python `requests` may fail certificate verification because Zscaler re-signs TLS with your organization’s root CA, which is not in `certifi` by default. The most reliable fix is to add your Zscaler root CA to a combined trust bundle and point Python to it.

1) Export the Zscaler root certificate from macOS Keychain:
- Open `Keychain Access` → search for your org’s TLS inspection root (e.g., “Zscaler Root CA”).
- Right-click the certificate → Export… → save as `ZscalerRootCA.cer` (e.g., to `~/Downloads/`).

2) Convert to PEM if exported in DER:
```bash
openssl x509 -in ~/Downloads/ZscalerRootCA.cer -inform DER -out ~/Downloads/zscaler_root_ca.pem -outform PEM
```

3) Create a combined CA bundle (public CAs + Zscaler):
- Find the `certifi` CA bundle path:
```bash
~/Users/UserName/Downloads/Apps/GoogleAI/~adk_multiagent_systems/.venv/bin/python -c "import certifi,sys; print(certifi.where())"
```
- Build a combined bundle:
```bash
mkdir -p ~/.certs
```
```bash
cat $(~/Users/UserName/Downloads/Apps/GoogleAI/adk_multiagent_systems/.venv/bin/python -c "import certifi,sys; print(certifi.where())") ~/Downloads/zscaler_root_ca.pem > ~/.certs/combined-ca.pem
```

4) Point Python/requests to the combined bundle:
- Add to your project `.env`:


