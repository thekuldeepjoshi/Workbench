from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, init_db
from .models import Profile, Job
from .scoring import score_job

app = FastAPI(title="Workbench")

DEMO = [
    ("Manager, Technical Account Management", "EnterprisePay", "Dublin, Ireland", "Hybrid", "Enterprise payments TAM leadership, executive relationships, QBRs and adoption.", "Salary available"),
    ("Technical Support Engineering Manager", "CloudStack", "Dublin, Ireland", "Hybrid", "Lead TSEs working on APIs, cloud infrastructure and enterprise SaaS.", "Salary available"),
    ("Senior Technical Account Manager", "DataPlatform", "London, UK", "Hybrid", "Strategic enterprise accounts, technical architecture, adoption and executive reviews.", "Salary available"),
    ("Enterprise Customer Success Manager", "AIWorks", "Amsterdam, Netherlands", "Hybrid", "Enterprise adoption, technical strategy and expansion for AI SaaS.", "Salary available"),
    ("Solutions Architect", "DeveloperCloud", "Remote worldwide", "Remote", "Customer-facing architecture across APIs, cloud and developer platforms.", "Salary not listed"),
]

@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        if not s.exec(select(Profile)).first():
            s.add(Profile())
            s.commit()

def page(body: str, active: str = "home") -> HTMLResponse:
    nav = f'''<aside class="sidebar"><div class="brand"><div class="brand-mark"></div><span>Workbench</span></div><div class="brand-sub">Personal career intelligence</div><nav><a class="nav-item {'active' if active == 'home' else ''}" href="/">Job Scout</a><a class="nav-item {'active' if active == 'profile' else ''}" href="/profile">My Profile</a></nav></aside>'''
    return HTMLResponse(f'''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Workbench</title><link rel="stylesheet" href="/static/style.css"></head><body><div class="app-shell">{nav}<div class="main-content">{body}</div></div></body></html>''')

@app.get("/", response_class=HTMLResponse)
def home():
    with Session(engine) as s:
        jobs = s.exec(select(Job).order_by(Job.score.desc(), Job.posted_at.desc())).all()
    cards = "".join(f'''<article class="job-card"><div class="job-top"><div class="company-icon">{j.company[:1]}</div><div class="job-main"><h3>{j.title}</h3><h4>{j.company}</h4><div class="meta"><span>{j.location}</span><span>{j.work_model}</span></div></div><div class="match-score">{j.score}</div></div><p class="job-desc">{j.description}</p><div class="chips"><span>{j.work_model}</span><span>{j.location}</span><span>{j.salary}</span></div><div class="job-actions"><a class="outline-btn" href="{j.url}" target="_blank">View job</a><a class="save-btn" href="/job/{j.id}/save">Save</a><a class="skip-btn" href="/job/{j.id}/skip">Skip</a></div></article>''' for j in jobs[:5])
    return page(f'''<header class="hero"><div><p class="eyebrow">YOUR DAILY CAREER SCOUT</p><h1>Find your next role.</h1><p class="lead">Role and location fit come first.</p></div><div class="hero-actions"><a class="primary-btn" href="/scan">Run today’s scan</a><a class="outline-btn" href="/rerun-test">Re-run test</a></div></header><div class="layout"><section class="feed"><div class="section-head"><div><h2>Today's Matches</h2><p>24-hour jobs first.</p></div><strong>{len(jobs[:5])} matches</strong></div>{cards or '<div class="empty">No matches yet. Run today’s scan.</div>'}</section><aside class="right-rail"><div class="panel profile-panel"><div class="panel-title"><h3>Profile signals</h3><a href="/profile">Edit</a></div><b>Roles</b><p>TAM → TSE → CSM → SA</p><b>Location</b><p>Dublin → Ireland → Europe → Remote worldwide</p><div class="stats"><div><span>Seniority</span><b>Manager / Lead first</b></div><div><span>Work model</span><b>Hybrid / On-site first</b></div><div><span>Freshness</span><b>24h first</b></div></div></div></aside></div>''')

@app.get("/scan")
def scan():
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        for job in s.exec(select(Job)).all():
            s.delete(job)
        for title, company, location, work_model, desc, salary in DEMO:
            j = Job(title=title, company=company, description=desc, location=location, work_model=work_model, url="https://example.com/jobs", source="demo", salary=salary)
            score_job(j, p)
            s.add(j)
        s.commit()
    return RedirectResponse("/", 303)

@app.get("/rerun-test")
def rerun_test():
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
    return page(f'''<div class="profile-page"><p class="eyebrow">PERSONAL SOURCING PROFILE</p><h1>My Profile</h1><p class="lead">Saving your profile clears old matches and starts a fresh scan.</p><form class="profile-form" method="post"><label>Target roles<input name="roles" value="{p.roles}"></label><label>Seniority<input name="seniority" value="{p.seniority}"></label><label>Location priority<input name="location_priority" value="{p.location_priority}"></label><label>Work model<input name="work_model" value="{p.work_model}"></label><label>Technical stack<textarea name="stack" rows="3">{p.stack}</textarea></label><label>Industries<input name="industries" value="{p.industries}"></label><label>Culture signals<textarea name="culture" rows="3">{p.culture}</textarea></label><label>Travel<input name="travel" value="{p.travel}"></label><label>Salary preference<input name="salary_preference" value="{p.salary_preference}"></label><label>Freshness strategy<input name="freshness_window" value="{p.freshness_window}"></label><button class="primary-btn" type="submit">Save profile & re-run scan</button></form></div>''', "profile")

@app.post("/profile")
def save_profile(roles: str = Form(...), seniority: str = Form(...), location_priority: str = Form(...), work_model: str = Form(...), stack: str = Form(...), industries: str = Form(...), culture: str = Form(...), travel: str = Form(...), salary_preference: str = Form(...), freshness_window: str = Form(...)):
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        p.roles, p.seniority, p.location_priority = roles, seniority, location_priority
        p.work_model, p.stack, p.industries = work_model, stack, industries
        p.culture, p.travel, p.salary_preference = culture, travel, salary_preference
        p.freshness_window = freshness_window
        s.add(p)
        for job in s.exec(select(Job)).all():
            s.delete(job)
        s.commit()
    return RedirectResponse("/scan", 303)
