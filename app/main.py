from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, init_db
from .models import Profile, Job
from .scoring import score_job

app = FastAPI(title="Workbench")

DEMO = [
    ("Senior Full Stack Engineer", "CivicFlow", "Python React autonomy transparency civic-tech series b", "https://example.com/jobs/1"),
    ("Software Engineer", "HealthLoop", "Python React health-tech inclusion belonging small team", "https://example.com/jobs/2"),
    ("Senior Software Engineer", "SensorForge", "Python React IoT hardware robotics autonomous teams", "https://example.com/jobs/3"),
    ("Fullstack Engineer", "Learnly", "Python React ed-tech empathy inclusion mission driven", "https://example.com/jobs/4"),
    ("Software Engineer", "OpenGov Labs", "Python React gov-tech transparency accountability remote", "https://example.com/jobs/5"),
]

@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        if not s.exec(select(Profile)).first():
            s.add(Profile())
            s.commit()

def page(body: str) -> HTMLResponse:
    return HTMLResponse(f'''<!doctype html><html><head><meta name="viewport" content="width=device-width"><title>Workbench</title><link rel="stylesheet" href="/static/style.css"></head><body><nav><b>Workbench</b><a href="/">Home</a><a href="/profile">My Profile</a></nav><main>{body}</main></body></html>''')

@app.get("/", response_class=HTMLResponse)
def home():
    with Session(engine) as s:
        jobs = s.exec(select(Job).order_by(Job.score.desc())).all()
    cards = "".join(f'''<article class="job-card"><div class="job-head"><div><h2>{j.title}</h2><p><b>{j.company}</b> · Remote</p></div><strong class="match">{j.score}</strong></div><p>{j.rationale}</p><div class="chips"><span>Python</span><span>React</span><span>Remote</span></div><div class="actions"><a class="button" href="{j.url}" target="_blank">View job</a><a class="button secondary" href="/job/{j.id}/save">Save</a><a class="button secondary" href="/job/{j.id}/skip">Skip</a></div></article>''' for j in jobs[:5])
    return page(f'''<header class="hero"><div><p class="eyebrow">YOUR DAILY CAREER SCOUT</p><h1>Welcome to Workbench</h1><p class="lead">Discover remote engineering opportunities that align with your skills, values, and goals.</p></div><div class="hero-actions"><a class="button" href="/scan">▷ Run today's scan</a><a class="button secondary" href="/rerun-test">↻ Re-run test</a></div></header><section><div class="section-head"><div><h2>Today's Matches</h2><p>Ranked based on your preferences, with culture as the strongest signal.</p></div><strong>{len(jobs[:5])} opportunities</strong></div>{cards or '<div class="empty">No jobs yet. Run today\'s scan.</div>'}</section>''')

@app.get("/scan")
def scan():
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        for title, company, desc, url in DEMO:
            if s.exec(select(Job).where(Job.company == company, Job.title == title)).first():
                continue
            j = Job(title=title, company=company, description=desc, location="Remote", url=url, source="demo")
            score_job(j, p)
            s.add(j)
        s.commit()
    return RedirectResponse("/", 303)

@app.get("/rerun-test")
def rerun_test():
    """Reset the demo jobs and run the test scan again from a clean state."""
    with Session(engine) as s:
        jobs = s.exec(select(Job)).all()
        for job in jobs:
            s.delete(job)
        s.commit()
    return RedirectResponse("/scan", 303)

@app.get("/job/{job_id}/{action}")
def action(job_id: int, action: str):
    with Session(engine) as s:
        j = s.get(Job, job_id)
        if j:
            j.status = "saved" if action == "save" else "skipped"
            s.add(j)
            s.commit()
    return RedirectResponse("/", 303)

@app.get("/profile", response_class=HTMLResponse)
def profile():
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
    return page(f'''<h1>Your Profile</h1><p class="lead">Tune the signals Workbench uses to rank opportunities.</p><form method="post"><label>Roles<input name="roles" value="{p.roles}"></label><label>Tech Stack<input name="stack" value="{p.stack}"></label><label>Culture Signals<textarea name="culture">{p.culture}</textarea></label><label>Industries<textarea name="industries">{p.industries}</textarea></label><label>Company Stage<input name="company_stage" value="{p.company_stage}"></label><label>Hard Requirement<input name="hard_requirement" value="{p.hard_requirement}"></label><label>Resume<textarea name="resume_text" rows="10">{p.resume_text}</textarea></label><button class="button">Save profile</button></form>''')

@app.post("/profile")
def save_profile(roles: str = Form(...), stack: str = Form(...), culture: str = Form(...), industries: str = Form(...), company_stage: str = Form(...), hard_requirement: str = Form(...), resume_text: str = Form("")):
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        p.roles, p.stack, p.culture = roles, stack, culture
        p.industries, p.company_stage, p.hard_requirement, p.resume_text = industries, company_stage, hard_requirement, resume_text
        s.add(p)
        s.commit()
    return RedirectResponse("/", 303)
