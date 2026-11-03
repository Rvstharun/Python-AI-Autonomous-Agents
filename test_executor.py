from planner import create_plan
from executor import run_tasks

plan = create_plan("Put together something for leadership about why our onboarding is slow. "
                   "Keep it short but thorough, include costs, we don't have the data yet.")
sections, log = run_tasks(plan)

for s in sections:
    print("\n##", s.heading)
    print(s.paragraphs[0][:200])
    if s.table:
        print("TABLE:", s.table.headers)
        for row in s.table.rows:
            print("  ", row)

print("\nTask log:")
for entry in log:
    print(entry)