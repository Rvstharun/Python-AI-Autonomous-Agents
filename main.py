import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from schemas import AgentRequest
from planner import create_plan
from executor import run_tasks
from docx_builder import build_docx, OUTPUT_DIR

app = FastAPI(title="Autonomous Document Agent")

DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@app.post("/agent")
def run_agent(body: AgentRequest):
    # 1. Plan
    try:
        plan = create_plan(body.request)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=f"Planning failed: {e}")

    # 2. Execute each task
    sections, task_log = run_tasks(plan)

    # 3. Build the Word document
    path = build_docx(plan, sections)
    filename = os.path.basename(path)

    failed = [t["title"] for t in task_log if t["status"] == "failed"]
    return {
        "message": f"Created '{plan.doc_title}' with {len(sections)} sections."
                   + (f" {len(failed)} section(s) need manual review." if failed else ""),
        "doc_type": plan.doc_type,
        "assumptions": plan.assumptions,
        "plan": [t.model_dump() for t in plan.tasks],
        "task_log": task_log,
        "document": filename,
        "download_url": f"/download/{filename}",
    }


@app.get("/download/{filename}")
def download(filename: str):
    safe_name = os.path.basename(filename)  # blocks path tricks like ../../
    path = os.path.join(OUTPUT_DIR, safe_name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type=DOCX_TYPE, filename=safe_name)