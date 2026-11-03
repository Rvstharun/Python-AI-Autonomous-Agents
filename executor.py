from llm import ask_json
from schemas import Plan, Section
from tools import add_total_row

COST_WORDS = ("cost", "budget", "pricing", "financial", "expense")

SECTION_SYSTEM = """You are the writing module of an autonomous document-writing agent.
You write ONE section of a business document.

Rules:
- Write professional, concrete content. Use clearly illustrative mock data where
  real data is missing, and make mock figures plausible.
- Respect the stated assumptions. Do not repeat content from other sections.
- Use "bullets" for short lists and "table" only when a table genuinely helps
  (timelines, budgets, comparisons, risks). Otherwise set "table" to null.
- For cost or budget tables, put the numeric amount in the LAST column and set
  "add_total" to true. Do not calculate the total yourself.
- Keep it concise: 1 to 3 short paragraphs.

Reply with ONLY a JSON object in exactly this format:
{
  "heading": "string",
  "paragraphs": ["string"],
  "bullets": ["string"],
  "table": null
}
When a table is needed, use:
"table": {"headers": ["A", "B"], "rows": [["x", "y"]], "add_total": false}"""


def run_tasks(plan: Plan) -> tuple[list[Section], list[dict]]:
    sections: list[Section] = []
    task_log: list[dict] = []
    all_titles = [t.title for t in plan.tasks]

    for task in plan.tasks:
        print(f"[executor] Task {task.id}/{len(plan.tasks)}: {task.title}")

        previous = ""
        if sections:
            previous = f"Previous section ({sections[-1].heading}) began: {sections[-1].paragraphs[0][:200]}"

        user_prompt = (
            f"Document: {plan.doc_type} - {plan.doc_title}\n"
            f"Assumptions: {'; '.join(plan.assumptions)}\n"
            f"All sections in this document: {', '.join(all_titles)}\n"
            f"{previous}\n\n"
            f"Write this section now.\n"
            f"Section title: {task.title}\n"
            f"What it must contain: {task.description}"
        )
        text = f"{task.title} {task.description}".lower()
        if any(word in text for word in COST_WORDS):
            user_prompt += (
                "\n\nThis section MUST include a table itemizing the costs. "
                'Use headers like ["Item", "Amount (USD)"], put the numeric amount '
                'in the LAST column (e.g. "$12,000"), and set "add_total": true. '
                "Do not add a Total row yourself."
            )
        entry = {"task_id": task.id, "title": task.title, "status": "done", "tool_used": None}
        try:
            section = ask_json(SECTION_SYSTEM, user_prompt, Section)
            section.heading = task.title  # keep headings consistent with the plan
            if section.table and section.table.add_total:
                section.table = add_total_row(section.table)
                entry["tool_used"] = "add_total_row"
        except RuntimeError as e:
            print(f"[executor] Task {task.id} failed: {e}")
            section = Section(
                heading=task.title,
                paragraphs=["This section could not be generated automatically and needs manual review."],
            )
            entry["status"] = "failed"

        sections.append(section)
        task_log.append(entry)

    return sections, task_log