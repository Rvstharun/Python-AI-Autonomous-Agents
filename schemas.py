from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    # Guardrail: reject empty or absurdly long requests before calling the LLM
    request: str = Field(min_length=10, max_length=2000)


class Task(BaseModel):
    id: int
    title: str
    description: str


class Plan(BaseModel):
    doc_type: str            # e.g. "Project Plan", "Business Report"
    doc_title: str
    assumptions: list[str]   # what the agent assumed when info was missing
    tasks: list[Task] = Field(min_length=3, max_length=8)


class Table(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    add_total: bool = False   # LLM sets True for cost/budget tables


class Section(BaseModel):
    heading: str
    paragraphs: list[str] = Field(min_length=1)
    bullets: list[str] = []
    table: Table | None = None