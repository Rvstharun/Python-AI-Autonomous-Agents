from llm import ask_json
from schemas import Plan

system = (
    "You are a planning agent. Reply with ONLY a JSON object with keys: "
    "doc_type (string), doc_title (string), assumptions (list of strings), "
    "tasks (list of objects with id (int), title, description). "
    "Use 3 to 8 tasks."
)
user = "Create a project plan for launching a customer support chatbot, 3-month timeline."

plan = ask_json(system, user, Plan)
print(plan.doc_title)
for t in plan.tasks:
    print(t.id, t.title)