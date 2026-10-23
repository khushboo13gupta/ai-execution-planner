"""Execution Planner backend: tools, OpenAI loop and state. No UI code lives here."""

## imports
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
import json
import re

# load environment variables
load_dotenv(override=True)

# create console
console = Console()

# create OpenAI client
openai = OpenAI()

checklist = []
completed = []
step_notes: list[str] = []

MODEL_NAME = "gpt-5.5"


def show(text: str) -> None:
    try:
        console.print(text)
    except Exception as e:
        console.print(f"Error showing text: {e}")


def reset_checklist() -> None:
    checklist.clear()
    completed.clear()
    step_notes.clear()


def get_checklist_report() -> str:
    result = ""
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result


def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return f"Checklist created with {len(descriptions)} items"


def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return "No checklist at this index."
    show(completion_notes)
    step_notes.append(f"**Step {index}:** {rich_to_markdown(completion_notes)}")
    return get_checklist_report()


create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                "type": "array",
                "items": {"type": "string"},
                "title": "Descriptions of checklist items",
            }
        },
        "required": ["descriptions"],
        "additionalProperties": False,
    },
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        "properties": {
            "index": {
                "description": "The 1-based index of the checklist item to mark as complete",
                "title": "Index",
                "type": "integer",
            },
            "completion_notes": {
                "description": "Notes about how you completed the checklist item, as one plain-text sentence",
                "title": "Completion Notes",
                "type": "string",
            },
        },
        "required": ["index", "completion_notes"],
        "type": "object",
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": create_checklist_json},
    {"type": "function", "function": mark_complete_json},
]


TOOL_FUNCTIONS = {
    "create_checklist": create_checklist,
    "mark_complete": mark_complete,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = TOOL_FUNCTIONS.get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results


system_message = """
You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
Now create a plan, set the checklist, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Plan 4-7 checklist steps, each a short imperative phrase (max ~12 words).
When marking a step complete, write completion_notes as one plain-text sentence (max ~30 words) stating the concrete result.
Format the final solution in Markdown (not Rich markup, no code blocks):
- Start with a 1-2 sentence summary.
- Then 3-5 sections, each with a heading like "## 1. Requirements", "## 2. Approach", "## 3. Key Trade-offs & Considerations".
- Use concise bullet points under each section; tables are fine for numbers or comparisons.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""
system = [{"role": "system", "content": system_message}]


def rich_to_markdown(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\[strike\](.*?)\[/strike\]", r"~~\1~~", text, flags=re.DOTALL)
    text = re.sub(r"\[/?[a-zA-Z0-9_#= -]+\]", "", text)
    return text.strip()


def snapshot(status: str, solution: str = "") -> tuple[str, str]:
    return status, solution


def run_agent(problem: str):
    reset_checklist()
    problem = (problem or "").strip()
    if not problem:
        yield snapshot("Enter a problem to solve.", "")
        return

    messages = system + [{"role": "user", "content": problem}]
    yield snapshot("Planning a checklist...", "")

    response = openai.chat.completions.create(
        model=MODEL_NAME, messages=messages, tools=tools
    )
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        results = handle_tool_calls(assistant_message.tool_calls)
        messages.append(assistant_message)
        messages.extend(results)
        yield snapshot("Working through the checklist...", "")
        response = openai.chat.completions.create(
            model=MODEL_NAME, messages=messages, tools=tools
        )

    solution = rich_to_markdown(response.choices[0].message.content or "")
    show(response.choices[0].message.content)
    yield snapshot("Done.", solution)
