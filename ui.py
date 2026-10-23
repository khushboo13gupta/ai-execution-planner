"""Execution Planner UI: Gradio layout and HTML rendering. All agent logic lives in backend.py."""

## imports
import re
import time
from html import escape

import gradio as gr
from markdown_it import MarkdownIt

import backend

md = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])

ICONS = {
    "layers": '<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><line x1="7" y1="8" x2="17" y2="8"/><line x1="7" y1="12" x2="14" y2="12"/>',
    "list": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="3.5" cy="6" r="1"/><circle cx="3.5" cy="12" r="1"/><circle cx="3.5" cy="18" r="1"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/>',
    "bolt": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "chart": '<line x1="6" y1="20" x2="6" y2="14"/><line x1="12" y1="20" x2="12" y2="8"/><line x1="18" y1="20" x2="18" y2="4"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
}

SECTION_ICONS = ["target", "layers", "chart", "list", "bolt", "file"]

SHOWCASE_PROBLEM = "How would you design a URL shortener like Bitly that handles 10 million requests per day?"

EXAMPLES = [
    ("System design", SHOWCASE_PROBLEM),
    ("AI / RAG", "Plan a production RAG chatbot over 50,000 internal company documents, including cost per month."),
    ("Go-to-market", "Create a go-to-market plan for a B2B SaaS tool targeting 1,000 paying customers in 12 months."),
    ("Travel", "Plan a 7-day Japan trip for two on a $4,000 budget, with daily costs."),
]


AUTHOR = "https://github.com/khushboo13gupta"


def icon(name: str, size: int = 20) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
    )


def panel_head(icon_name: str, title: str, subtitle: str, size: str = "") -> str:
    return (
        f'<div class="panel-head {size}"><span class="tile">{icon(icon_name, 22)}</span>'
        f"<div><h3>{escape(title)}</h3><p>{escape(subtitle)}</p></div></div>"
    )


CSS = """
.gradio-container {
  --ep-bg: #070b18;
  --ep-panel: #0e1528;
  --ep-panel-2: #121b33;
  --ep-border: #1e2a47;
  --ep-text: #e6e9f2;
  --ep-muted: #8b95b0;
  --ep-accent: #6366f1;
  --ep-accent-2: #a855f7;
  --ep-green: #22c55e;
}
.gradio-container {
  max-width: 1280px !important; margin: 0 auto !important; color: var(--ep-text);
  --body-text-color: var(--ep-text);
  --body-text-color-subdued: var(--ep-muted);
  --block-background-fill: transparent;
  --block-border-width: 0px;
  --input-background-fill: #0a1124;
  --input-border-color: var(--ep-border);
  --input-border-color-focus: var(--ep-accent);
  --border-color-primary: var(--ep-border);
}
footer { display: none !important; }

/* header */
.ep-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; padding: 18px 4px 6px; }
.ep-brand { display: flex; align-items: center; gap: 16px; }
.ep-logo { width: 60px; height: 60px; border-radius: 14px; display: grid; place-items: center;
  background: linear-gradient(145deg, #1b2547, #10172e); border: 1px solid var(--ep-border); color: #a5b4fc; }
.ep-brand h1 { margin: 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; color: var(--ep-text); }
.ep-brand p { margin: 2px 0 0; color: var(--ep-muted); font-size: 0.98rem; }
.ep-badges { display: flex; gap: 10px; flex-wrap: wrap; }
.ep-badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px;
  border: 1px solid var(--ep-border); background: rgba(17,25,48,0.7); font-size: 0.85rem; color: var(--ep-text); }
.ep-badge.y svg { stroke: #facc15 !important; } .ep-badge.b svg { stroke: #60a5fa !important; } .ep-badge.p svg { stroke: #c084fc !important; }

/* panels */
.ep-panel { background: linear-gradient(180deg, var(--ep-panel-2), var(--ep-panel)) !important;
  border: 1px solid var(--ep-border) !important; border-radius: 16px !important; padding: 18px 20px !important; }
.panel-head { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 14px; }
.panel-head .tile { flex: none; width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center;
  background: linear-gradient(145deg, #4f46e5, #7c3aed); color: #fff; }
.panel-head.plain .tile { background: rgba(99,102,241,0.15); color: #a5b4fc; }
.panel-head h3 { margin: 0; font-size: 1.12rem; font-weight: 650; color: var(--ep-text); }
.panel-head p { margin: 2px 0 0; font-size: 0.84rem; color: var(--ep-muted); }

#problem, #problem > label { background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
#problem textarea { font-size: 1.02rem !important; padding: 14px 16px !important; border-radius: 10px !important; }
#run-btn { background: linear-gradient(90deg, #4f46e5, #7c3aed 60%, #a855f7) !important; border: none !important;
  color: #fff !important; font-weight: 600; font-size: 1rem; border-radius: 10px !important; min-height: 44px; }
#run-btn:hover { filter: brightness(1.1); }

/* progress */
.ep-progress { display: flex; align-items: center; gap: 18px; padding: 6px 20px; flex-wrap: wrap; }
.ep-progress .label { font-weight: 650; }
.ep-progress .segs { display: flex; gap: 4px; flex: 1 1 260px; max-width: 580px; }
.ep-progress .seg { flex: 1; height: 7px; border-radius: 999px; background: #1c2742; }
.ep-progress .seg.on { background: var(--ep-green); }
.ep-progress .count { display: inline-flex; align-items: center; gap: 8px; font-size: 0.9rem; }
.ep-progress .count .ok { width: 20px; height: 20px; border-radius: 50%; display: grid; place-items: center; background: var(--ep-green); color: #04140a; }
.ep-progress .time { margin-left: auto; display: inline-flex; align-items: center; gap: 8px; color: var(--ep-muted); font-size: 0.88rem; }
.ep-progress .time svg { color: #818cf8; }
.ep-progress .time.warn { color: #fbbf24; }
.pulse { animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

/* plan */
.plan-list { border: 1px solid var(--ep-border); border-radius: 12px; background: rgba(8,13,28,0.55); padding: 4px 14px; }
.plan-row { display: flex; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid rgba(30,42,71,0.7); }
.plan-row:last-child { border-bottom: none; }
.plan-row .mark { flex: none; width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  border: 1.5px solid #33416a; color: transparent; }
.plan-row.done .mark { background: var(--ep-green); border-color: var(--ep-green); color: #04140a; }
.plan-row.current .mark { border-color: #818cf8; box-shadow: 0 0 0 3px rgba(129,140,248,0.2); }
.plan-row .tag { flex: none; font-size: 0.8rem; padding: 3px 10px; border-radius: 6px; background: #1a2440; color: #c7d0e6; }
.plan-row .txt { font-size: 0.92rem; line-height: 1.4; }
.plan-row.pending .txt { color: var(--ep-muted); }

/* log */
.log { position: relative; display: flex; flex-direction: column; gap: 8px; }
.log-row { display: flex; gap: 14px; align-items: center; position: relative; }
.log-row:not(:last-child)::before { content: ""; position: absolute; left: 13px; top: 28px; bottom: -12px; width: 2px; background: #2a3870; }
.log-row .n { flex: none; width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; font-size: 0.8rem;
  font-weight: 600; background: #4f46e5; color: #fff; box-shadow: 0 0 0 4px rgba(79,70,229,0.18); z-index: 1; }
.log-row .body { flex: 1; display: flex; gap: 12px; align-items: center; justify-content: space-between;
  border: 1px solid var(--ep-border); border-radius: 10px; background: rgba(8,13,28,0.55); padding: 9px 12px; font-size: 0.88rem; line-height: 1.45; }
.log-row .dur { flex: none; font-size: 0.75rem; padding: 2px 8px; border-radius: 6px; background: #1a2440; color: #aab4cf; }
.empty { color: var(--ep-muted); font-style: italic; padding: 10px 2px; font-size: 0.9rem; }

/* example chips */
.chip-row { gap: 8px !important; flex-wrap: wrap !important; justify-content: flex-start !important; align-items: center !important; }
.chip-row > * { flex-grow: 0 !important; width: auto !important; min-width: 0 !important; }
.chip-row > .chip-label { flex: 0 0 34px !important; width: 34px !important; min-width: 34px !important; padding: 0 !important; }
.chip-label { color: var(--ep-muted); font-size: 0.84rem; align-self: center; margin-right: 2px; }
.chip { flex: 0 0 auto !important; min-width: 0 !important; background: rgba(99,102,241,0.1) !important;
  border: 1px solid rgba(99,102,241,0.35) !important; color: #c7d2fe !important; border-radius: 999px !important;
  font-size: 0.82rem !important; padding: 4px 12px !important; }
.chip:hover { background: rgba(99,102,241,0.22) !important; }

.ep-progress .meta { color: var(--ep-muted); font-size: 0.84rem; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--ep-border); }

/* final output */
#copy-btn { max-width: 96px; margin-left: auto; background: transparent !important; border: 1px solid var(--ep-border) !important; color: var(--ep-text) !important; }
.out-intro { color: #c7d0e6; margin: 0 0 14px; font-size: 0.95rem; line-height: 1.55; }
.out-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }
.out-card { border: 1px solid var(--ep-border); border-radius: 12px; background: rgba(8,13,28,0.55); padding: 14px 16px; }
.out-card h4 { display: flex; align-items: center; gap: 10px; margin: 0 0 10px; font-size: 1rem; font-weight: 650; color: var(--ep-text); }
.out-card h4 svg { color: #818cf8; }
.out-card .md { font-size: 0.9rem; line-height: 1.6; color: #d5dbea; }
.out-card .md ul, .out-card .md ol { padding-left: 1.1rem; margin: 0.3rem 0; }
.out-card .md li::marker { color: #818cf8; }
.out-card .md p { margin: 0.35rem 0; }
.out-card .md strong { color: #fff; }
.out-card .md table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
.out-card .md th, .out-card .md td { border: 1px solid var(--ep-border); padding: 4px 8px; }
.out-placeholder { border: 1px dashed #2a3870; border-radius: 12px; padding: 28px; text-align: center;
  color: var(--ep-muted); font-size: 0.92rem; background: rgba(8,13,28,0.35); }

.ep-footer { text-align: center; color: var(--ep-muted); font-size: 0.82rem; padding: 10px 0 18px; }
.ep-footer b { color: #c7d2fe; font-weight: 600; }
"""

HEADER = f"""
<div class="ep-header">
  <div class="ep-brand">
    <div class="ep-logo">{icon("layers", 30)}</div>
    <div><h1>Execution Planner</h1><p>Plan tasks, execute step-by-step, and track progress in real time.</p></div>
  </div>
  <div class="ep-badges">
    <span class="ep-badge y">{icon("bolt", 16)}AI Agent</span>
    <span class="ep-badge b">{icon("chart", 16)}Step-by-step execution</span>
    <span class="ep-badge p">{icon("target", 16)}Clear, structured output</span>
  </div>
</div>
"""


def progress_html(status: str = "", elapsed: float | None = None, rounds: int = 0) -> str:
    total, done = len(backend.checklist), sum(backend.completed)
    segs = "".join(
        f'<span class="seg{" on" if i < done else ""}"></span>' for i in range(max(total, 1))
    )
    count = (
        f'<span class="count"><span class="ok">{icon("check", 13)}</span>{done} / {total} steps complete</span>'
        if total and done == total
        else f'<span class="count">{done} / {total} steps complete</span>'
    )
    if status.startswith("Done") and elapsed is not None:
        right = f'<span class="time">{icon("clock", 18)}Completed in {elapsed:.0f} seconds</span>'
    elif status.startswith(("Enter", "Failed")):
        right = f'<span class="time warn">{escape(status)}</span>'
    elif status:
        right = f'<span class="time pulse">{icon("clock", 18)}{escape(status)} {elapsed or 0:.0f}s</span>'
    else:
        right = f'<span class="time">{icon("clock", 18)}Ready</span>'
    meta = f"{backend.MODEL_NAME} · {total} steps · {rounds} tool round{'s' if rounds != 1 else ''}"
    meta_html = f'<span class="meta">{escape(meta)}</span>' if total else ""
    return (
        f'<div class="ep-progress"><span class="label">Progress</span><div class="segs">{segs}</div>{count}'
        f"{right}{meta_html}</div>"
    )


def plan_html(finished: bool = False) -> str:
    head = panel_head("list", "Plan", "High-level plan to solve the problem.", "plain")
    items, flags = backend.checklist, backend.completed
    if not items:
        return head + '<div class="plan-list"><div class="empty">The plan will appear here once the agent starts.</div></div>'
    current = None if finished else next((i for i, f in enumerate(flags) if not f), None)
    rows = []
    for index, item in enumerate(items):
        cls = "done" if flags[index] else ("current" if index == current else "pending")
        rows.append(
            f'<div class="plan-row {cls}"><span class="mark">{icon("check", 13)}</span>'
            f'<span class="tag">Step {index + 1}</span><span class="txt">{escape(item)}</span></div>'
        )
    return head + f'<div class="plan-list">{"".join(rows)}</div>'


def note_to_html(text: str) -> str:
    text = escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    return text.replace("\n", "<br>")


def log_html(durations: dict[int, float]) -> str:
    head = panel_head("gear", "Execution Log", "Agent working through the plan step by step.", "plain")
    if not backend.step_notes:
        return head + '<div class="empty">Each completed step will be logged here.</div>'
    rows = []
    for note in backend.step_notes:
        match = re.match(r"\*\*Step (\d+):\*\*\s*(.*)", note, flags=re.DOTALL)
        step, body = (int(match.group(1)), match.group(2)) if match else (None, note)
        dur = f'<span class="dur">{durations[step]:.0f}s</span>' if step in durations else ""
        rows.append(
            f'<div class="log-row"><span class="n">{step or "•"}</span>'
            f'<div class="body"><span>{note_to_html(body)}</span>{dur}</div></div>'
        )
    return head + f'<div class="log">{"".join(rows)}</div>'


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    intro, sections, title, buf = [], [], None, []
    for line in text.splitlines():
        heading = re.match(r"^#{1,4}\s+(.*)", line)
        if heading:
            if title is not None:
                sections.append((title, "\n".join(buf)))
            title, buf = heading.group(1).strip(), []
        elif title is None:
            intro.append(line)
        else:
            buf.append(line)
    if title is not None:
        sections.append((title, "\n".join(buf)))
    return "\n".join(intro).strip(), sections


OUTPUT_PLACEHOLDER = '<div class="out-placeholder">Your structured solution will appear here once the agent finishes.</div>'


def output_head_html(problem: str = "") -> str:
    problem = " ".join((problem or "").split())
    if not problem:
        return panel_head("file", "Final Output", "Complete solution for the problem.")
    short = problem if len(problem) <= 70 else problem[:67].rstrip() + "…"
    return panel_head("file", "Final Output", f"Solution for: {short}")


def output_html(solution: str) -> str:
    intro, sections = split_sections(solution)
    if not sections:
        sections, intro = [("Answer", solution)], ""
    cards = "".join(
        f'<div class="out-card"><h4>{icon(SECTION_ICONS[i % len(SECTION_ICONS)], 20)}{escape(title)}</h4>'
        f'<div class="md">{md.render(body)}</div></div>'
        for i, (title, body) in enumerate(sections)
    )
    intro_html = f'<div class="out-intro">{md.render(intro)}</div>' if intro else ""
    return intro_html + f'<div class="out-grid">{cards}</div>'


def run(problem: str):
    start = last = time.monotonic()
    durations: dict[int, float] = {}
    rounds = 0
    agent = backend.run_agent(problem)
    while True:
        try:
            status, solution = next(agent)
        except StopIteration:
            return
        except Exception as e:
            yield (
                progress_html(f"Failed: {type(e).__name__}: {str(e)[:120]}", time.monotonic() - start, rounds),
                plan_html(),
                log_html(durations),
                output_head_html(problem),
                OUTPUT_PLACEHOLDER,
                "",
                gr.update(visible=False),
            )
            return
        if status.startswith("Working"):
            rounds += 1
        now = time.monotonic()
        newly_done = [i + 1 for i, f in enumerate(backend.completed) if f and i + 1 not in durations]
        for step in newly_done:
            durations[step] = (now - last) / len(newly_done)
        if newly_done:
            last = now
        finished = status.startswith("Done")
        yield (
            progress_html(status, now - start, rounds),
            plan_html(finished),
            log_html(durations),
            output_head_html(problem),
            output_html(solution) if solution else OUTPUT_PLACEHOLDER,
            solution,
            gr.update(visible=bool(solution)),
        )


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Execution Planner") as demo:
        gr.HTML(HEADER)
        with gr.Column(elem_classes="ep-panel"):
            gr.HTML(panel_head("message", "Problem", "Describe the problem you want to solve. The agent will plan the steps, execute them, and show progress."))
            problem = gr.Textbox(
                value=SHOWCASE_PROBLEM,
                show_label=False,
                lines=2,
                max_lines=8,
                placeholder="e.g. How would you design a URL shortener that handles 10 million requests per day?",
                elem_id="problem",
            )
            with gr.Row(elem_classes="chip-row"):
                gr.HTML('<span class="chip-label">Try:</span>', elem_classes="chip-label")
                chips = [
                    (gr.Button(label, size="sm", elem_classes="chip"), prompt) for label, prompt in EXAMPLES
                ]
            run_btn = gr.Button("▶  Run Agent", elem_id="run-btn")
        progress = gr.HTML(progress_html())
        with gr.Row(equal_height=True):
            with gr.Column(elem_classes="ep-panel"):
                plan_view = gr.HTML(plan_html())
            with gr.Column(elem_classes="ep-panel"):
                log_view = gr.HTML(log_html({}))
        with gr.Column(elem_classes="ep-panel"):
            with gr.Row(equal_height=False):
                output_head = gr.HTML(output_head_html())
                copy_btn = gr.Button("Copy", size="sm", elem_id="copy-btn", scale=0, min_width=90, visible=False)
            output_view = gr.HTML(OUTPUT_PLACEHOLDER)
        raw_solution = gr.Textbox(visible=False)
        credit = f" · by <b>{escape(AUTHOR)}</b>" if AUTHOR else ""
        gr.HTML(f'<div class="ep-footer">Built with OpenAI tool calling + Gradio{credit}</div>')

        run_btn.click(
            fn=run,
            inputs=[problem],
            outputs=[progress, plan_view, log_view, output_head, output_view, raw_solution, copy_btn],
        )
        for chip, prompt in chips:
            chip.click(fn=lambda p=prompt: p, outputs=[problem])
        copy_btn.click(fn=None, inputs=[raw_solution], js="(t) => { navigator.clipboard.writeText(t); }")
    return demo


BACKGROUND = "radial-gradient(1200px 600px at 10% -10%, #131c3a 0%, #070b18 55%)"
THEME = gr.themes.Base(primary_hue="indigo", font=[gr.themes.GoogleFont("Inter"), "sans-serif"]).set(
    body_background_fill=BACKGROUND,
    body_background_fill_dark=BACKGROUND,
)

FORCE_DARK = "() => { document.body.classList.add('dark'); }"


if __name__ == "__main__":
    build_ui().queue().launch(
        theme=THEME,
        css=CSS,
        js=FORCE_DARK,
    )
