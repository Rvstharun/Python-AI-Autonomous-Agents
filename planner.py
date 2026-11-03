from llm import ask_json
from schemas import Plan

PLANNER_SYSTEM = """You are the planning module of an autonomous document-writing agent.
Given a user's request, decide what business document should be produced and break the work into tasks.

Rules:
1. Choose the most suitable doc_type (e.g. Project Plan, Business Report, Proposal,
   Meeting Minutes, SOP, Technical Design, Product Specification).
2. Create 3 to 8 tasks. Each task produces ONE section of the final document,
   so the task title should work as a section heading. Order them logically.
3. NEVER ask the user questions. If information is missing, ambiguous, or the
   requirements conflict, make a reasonable assumption and record it in "assumptions".
   Example: "No data provided, so illustrative mock figures will be used."
4. If requirements conflict (e.g. "short but thorough"), state how you resolved it
   in "assumptions".
5. Each task description must say what that section should contain, in one or two sentences.

Reply with ONLY a JSON object in exactly this format:
{
  "doc_type": "string",
  "doc_title": "string",
  "assumptions": ["string", "string"],
  "tasks": [
    {"id": 1, "title": "string", "description": "string"}
  ]
}"""


def create_plan(user_request: str) -> Plan:
    return ask_json(PLANNER_SYSTEM, user_request, Plan)