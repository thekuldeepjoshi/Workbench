from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = "Candidate"
    resume_text: str = ""
    roles: str = "Software Engineer, Senior Software Engineer, Fullstack Engineer"
    stack: str = "Python, React"
    culture: str = "empathy, humility, transparency, autonomy, accountability, belonging, inclusion"
    industries: str = "ed-tech, health-tech, civic-tech, gov-tech"
    company_stage: str = "Series A-C or equivalent"
    hard_requirement: str = "Remote"

class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str = "Remote"
    url: str = ""
    posted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    source: str = "demo"
    score: int = 0
    culture_score: int = 0
    stack_score: int = 0
    role_score: int = 0
    mission_score: int = 0
    stage_score: int = 0
    hardtech_score: int = 0
    status: str = "new"
    rationale: str = ""
    concerns: str = ""
