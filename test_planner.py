from planner import create_plan

requests = [
    "Create a project plan for launching a customer support chatbot, 3-month timeline.",
    "Put together something for leadership about why our onboarding is slow. "
    "Keep it short but thorough, include costs, we don't have the data yet.",
]

for r in requests:
    plan = create_plan(r)
    print("\n" + "=" * 60)
    print(f"{plan.doc_type}: {plan.doc_title}")
    print("Assumptions:")
    for a in plan.assumptions:
        print("  -", a)
    print("Tasks:")
    for t in plan.tasks:
        print(f"  {t.id}. {t.title} -> {t.description}")