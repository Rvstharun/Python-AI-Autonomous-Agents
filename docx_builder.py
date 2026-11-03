import os
import re
from datetime import datetime
from docx import Document
from schemas import Plan, Section

OUTPUT_DIR = "outputs"


def build_docx(plan: Plan, sections: list[Section]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = Document()

    doc.add_heading(plan.doc_title, level=0)
    doc.add_paragraph(f"{plan.doc_type}  |  Generated {datetime.now():%d %B %Y}")

    doc.add_heading("Assumptions", level=1)
    for a in plan.assumptions:
        doc.add_paragraph(a, style="List Bullet")

    for s in sections:
        doc.add_heading(s.heading, level=1)
        for p in s.paragraphs:
            doc.add_paragraph(p)
        for b in s.bullets:
            doc.add_paragraph(b, style="List Bullet")

        if s.table and s.table.headers:
            cols = len(s.table.headers)
            table = doc.add_table(rows=1, cols=cols)
            table.style = "Table Grid"
            for i, h in enumerate(s.table.headers):
                cell = table.rows[0].cells[i]
                cell.text = ""
                cell.paragraphs[0].add_run(str(h)).bold = True
            for row in s.table.rows:
                row = (list(row) + [""] * cols)[:cols]  # pad or trim bad rows
                cells = table.add_row().cells
                is_total = str(row[0]).strip().lower() == "total"
                for i, value in enumerate(row):
                    cells[i].text = ""
                    cells[i].paragraphs[0].add_run(str(value)).bold = is_total
            doc.add_paragraph()

    slug = re.sub(r"[^a-z0-9]+", "-", plan.doc_title.lower()).strip("-")[:50]
    filename = f"{slug}-{datetime.now():%H%M%S}.docx"
    path = os.path.join(OUTPUT_DIR, filename)
    doc.save(path)
    return path