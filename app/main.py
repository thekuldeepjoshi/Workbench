from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from .database import engine, init_db
from .models import Profile, Job
from .scoring import score_job

app = FastAPI(title="Workbench")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

DEMO = [
    ("Senior Full Stack Engineer", "CivicFlow", "Python React autonomy transparency civic-tech series b", "https://example.com/jobs/1", "Series B", "Civic Tech"),
    ("Software Engineer", "HealthLoop", "Python React health-tech inclusion belonging small team", "https://example.com/jobs/2", "Series A", "Health Tech"),
    ("Senior Software Engineer", "SensorForge", "Python React IoT hardware robotics autonomous teams", "https://example.com/jobs/3", "Series B", "Robotics / Hardware"),
    ("Fullstack Engineer", "Learnly", "Python React ed-tech empathy inclusion mission driven", "https://example.com/jobs/4", "Seed", "Ed Tech"),
    ("Software Engineer", "OpenGov Labs", "Python React gov-tech transparency accountability remote", "https://example.com/jobs/5", "Series A", "Gov Tech"),
]

@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        if not s.exec(select(Profile)).first():
            s.add(Profile())
            s.commit()

def page(content: str) -> HTMLResponse:
    html = f'''<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Workbench</title><link rel="stylesheet" href="/static/style.css"></head>
<body>
<div class="app-shell">
<aside class="sidebar">
  <div class="brand"><span class="brand-mark">◇</span><span>Workbench</span></div>
  <div class="brand-sub">Tools for a more intentional career</div>
  <nav>
    <a class="nav-item active" href="/"><span>⌂</span>Home</a>
    <a class="nav-item" href="/scan"><span>⌕</span>Find Jobs</a>
    <a class="nav-item" href="/profile"><span>♙</span>My Profile</a>
    <a class="nav-item" href="/#saved"><span>▢</span>Saved Jobs</a>
    <a class="nav-item" href="/#skipped"><span>⊘</span>Skipped Jobs</a>
    <a class="nav-item" href="/#history"><span>◷</span>Job History</a>
    <a class="nav-item" href="/profile"><span>⚙</span>Settings</a>
  </nav>
  <div class="sidebar-quote">“Better tools.<br>A more intentional career.”<small>— Workbench</small></div>
</aside>
<main class="main-content">
  <header class="topbar"><span>Find work that fits your skills, values, and life.</span></header>
  {content}
</main>
</div></body></html>'''
    return HTMLResponse(html)

@app.get("/", response_class=HTMLResponse)
def home():
    with Session(engine) as s:
        jobs = s.exec(select(Job).order_by(Job.score.desc())).all()
        profile = s.exec(select(Profile)).first()
    matches = jobs[:5]
    avg = round(sum(j.score for j in matches) / len(matches)) if matches else 0
    saved = sum(j.status == "saved" for j in jobs)
    skipped = sum(j.status == "skipped" for j in jobs)
    cards = "".join(job_card(j) for j in matches)
    profile_roles = profile.roles if profile else "Software Engineer, Senior Engineer, Fullstack Engineer"
    profile_stack = profile.stack if profile else "Python, React"
    return page(f'''
<section class="hero">
  <div><p class="eyebrow">YOUR DAILY CAREER SCOUT</p><h1>Welcome to Workbench</h1><p>Discover remote engineering opportunities that align with your skills, values, and goals.</p></div>
  <a class="primary-btn" href="/scan"><span>▷</span> Run today's scan</a>
</section>
<div class="layout">
  <section class="feed">
    <div class="section-head"><div><h2>Today's Matches</h2><p>Ranked based on your preferences, with culture as the strongest signal.</p></div><strong>{len(matches)} opportunities</strong></div>
    {cards or '<div class="empty">No jobs yet. Run today\'s scan.</div>'}
  </section>
  <aside class="right-rail">
    <div class="panel profile-panel"><div class="panel-title"><span>♙</span><h3>Your Profile</h3><a href="/profile">Edit</a></div>
      <b>Roles</b><p>{profile_roles}</p><b>Tech Stack</b><p>{profile_stack}</p><b>Work Style</b><p>Remote only</p><b>Culture Focus</b><p>Mission-driven, collaborative, high-trust, meaningful impact</p><b>Industries</b><p>IoT, hardware, hard-tech, developer tools</p><b>Company Stage</b><p>Early-stage, small to mid-size</p>
    </div>
    <div class="panel"><div class="panel-title"><span>▥</span><h3>Scan Summary</h3></div><div class="stats"><div><span>Total opportunities</span><b>{len(matches)}</b></div><div><span>Average match score</span><b>{avg}</b></div><div><span>Saved</span><b>{saved}</b></div><div><span>Skipped</span><b>{skipped}</b></div></div></div>
    <div class="quote-panel"><span>◒</span><p>“The best opportunities align with who you are, not just what you can do.”</p><small>— Workbench</small></div>
    <div class="panel"><div class="panel-title"><span>♧</span><h3>Tips</h3></div><ul><li>Run a new scan daily for fresh opportunities.</li><li>Keep your profile up to date for better matches.</li><li>Use Save and Skip to refine future results.</li><li>Focus on opportunities that excite you.</li></ul></div>
    <div class="panel"><div class="panel-title"><span>◎</span><h3>Next Steps</h3></div><ol class="steps"><li>Review today's matches</li><li>Save interesting opportunities</li><li>Update your profile preferences</li><li>Run another scan tomorrow</li></ol></div>
  </aside>
</div>''')

def job_card(j: Job) -> str:
    score = max(0, min(100, j.score))
    return f'''<article class="job-card">
      <div class="job-top"><div class="company-icon">{j.company[:1]}</div><div class="job-main"><h3>{j.company}</h3><h4>{j.title}</h4><div class="meta"><span>⌖ Remote</span><span>▤ {j.company} · {stage_for(j)}</span><span>◌ {sector_for(j)}</span></div></div><div class="match-score">{score}</div></div>
      <p class="job-desc">{j.description.title()}. Looking for a collaborative engineer to build meaningful products with a high-trust team.</p>
      <div class="chips"><span>Python</span><span>React</span>{'<span>IoT</span>' if j.hardtech_score > 0 else ''}<span>{sector_for(j)}</span></div>
      <div class="job-actions"><a class="outline-btn" href="{j.url or '#'}" target="_blank">↗ View job</a><a class="save-btn" href="/job/{j.id}/save">♧ Save</a><a class="skip-btn" href="/job/{j.id}/skip">⊘ Skip</a></div>
    </article>'''

def stage_for(j: Job) -> str:
    for _, company, _, _, stage, _ in DEMO:
        if company == j.company:
            return stage
    return "Remote"

def sector_for(j: Job) -> str:
    for _, company, _, _, _, sector in DEMO:
        if company == j.company:
            return sector
    return "Technology"

@app.get("/scan")
def scan():
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        for title, company, desc, url, _, _ in DEMO:
            if s.exec(select(Job).where(Job.company == company, Job.title == title)).first():
                continue
            j = Job(title=title, company=company, description=desc, location="Remote", url=url, source="demo")
            score_job(j, p)
            s.add(j)
        s.commit()
    return RedirectResponse("/", 303)

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
    return page(f'''<section class="profile-page"><p class="eyebrow">PERSONALIZATION</p><h1>Your Profile</h1><p class="lead">Tune the signals Workbench uses to rank opportunities for you.</p><form method="post" class="profile-form">
      <label>Roles<input name="roles" value="{p.roles}"></label><label>Tech Stack<input name="stack" value="{p.stack}"></label><label>Culture Signals<textarea name="culture" rows="4">{p.culture}</textarea></label><label>Industries<textarea name="industries" rows="3">{p.industries}</textarea></label><label>Company Stage<input name="company_stage" value="{p.company_stage}"></label><label>Hard Requirement<input name="hard_requirement" value="{p.hard_requirement}"></label><label>Resume<textarea name="resume_text" rows="10">{p.resume_text}</textarea></label><button class="primary-btn" type="submit">Save profile</button></form></section>''')

@app.post("/profile")
def save_profile(roles: str = Form(...), stack: str = Form(...), culture: str = Form(...), industries: str = Form(...), company_stage: str = Form(...), hard_requirement: str = Form(...), resume_text: str = Form("")):
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        p.roles, p.stack, p.culture = roles, stack, culture
        p.industries, p.company_stage, p.hard_requirement, p.resume_text = industries, company_stage, hard_requirement, resume_text
        s.add(p)
        s.commit()
    return RedirectResponse("/", 303)
