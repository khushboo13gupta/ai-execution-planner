# Execution Planner

An agent that breaks a problem into a checklist, works through each step with OpenAI tool calls, and returns a structured answer. A Gradio UI shows the plan, execution log and progress live.

## How it works

1. The model calls `create_checklist` to plan 4-7 steps.
2. It calls `mark_complete` with a short note as each step is done.
3. It replies with a Markdown answer split into sections, shown as cards in the UI.

## Files

| File | Role |
| --- | --- |
| `backend.py` | State, tool definitions, OpenAI tool-calling loop (`run_agent`) |
| `ui.py` | Gradio interface |

## Setup

Requires Python 3.10+.

```powershell
python -m venv .venv
.venv\Scripts\pip install "gradio>=6" openai python-dotenv rich markdown-it-py
```

Create a `.env` file in this folder with your key:

```
OPENAI_API_KEY=sk-...
```

Run:

```powershell
.venv\Scripts\python.exe ui.py
```

The model is set by `MODEL_NAME` in `backend.py`.

## Notes

Agent state is kept in module-level lists, so run one session at a time. It is not designed for multiple concurrent users.
