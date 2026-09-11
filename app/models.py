from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = "Candidate"
    resume_text: str = """10+ years of technical and customer-facing leadership experience across TAM, technical support, software engineering, enterprise SaaS, payments and cloud infrastructure. Current experience includes managing a team of Technical Account Managers supporting enterprise customers across EMEA, executive relationships, QBRs/EBCs, critical escalations, customer adoption, commercial opportunities and technical strategy. Strong experience with payments platforms, APIs and SaaS products.

Previous technical support leadership includes managing TSEs, customer escalations, API troubleshooting, cloud services, database performance and automation. Engineering background includes Python, Java, PHP, React, JavaScript, REST APIs, microservices, GCP, AWS, Kubernetes, Docker, CI/CD, observability and SQL.

Commercial and customer strengths include enterprise sales, C-level selling, strategic account management, customer expansion, cross-sell/upsell, GTM strategy, sales enablement, business cases and revenue growth. Leadership strengths include team leadership, stakeholder management, hiring, performance management, mentoring, strategic planning, QBRs and executive business reviews.

Education includes an Executive MBA from London Business School-equivalent executive management education and MSc-level Computing Science education."""
    roles: str = "Technical Account Manager, TAM, Technical Support Engineer, TSE, Customer Success Manager, CSM, Solutions Architect, SA"
    seniority: str = "Manager, Lead, Senior, Principal, IC"
    stack: str = "Python, Java, PHP, React, JavaScript, REST APIs, microservices, GCP, AWS, Kubernetes, Docker, SaaS, payments"
    culture: str = "empathy, humility, transparency, autonomy, accountability, belonging, inclusion"
    industries: str = "FinTech, payments, SaaS, cloud, infrastructure, AI, developer tools, APIs, cybersecurity, IoT, health-tech, ed-tech, gov-tech"
    company_stage: str = "Any"
    hard_requirement: str = ""
    location_priority: str = "Dublin, Ireland, Europe, Remote worldwide"
    work_model: str = "Hybrid/on-site Dublin first, then Ireland/Europe; remote worldwide also eligible"
    travel: str = "No restriction"
    salary_preference: str = "Show salary when available; no salary filter"
    freshness_window: str = "24h, then 7d, then 30d"

class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str = "Remote"
    work_model: str = "Remote"
    url: str = ""
    posted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    salary: str = ""
    source: str = "demo"
    score: int = 0
    culture_score: int = 0
    stack_score: int = 0
    role_score: int = 0
    mission_score: int = 0
    stage_score: int = 0
    hardtech_score: int = 0
    location_score: int = 0
    seniority_score: int = 0
    status: str = "new"
    rationale: str = ""
    concerns: str = ""
