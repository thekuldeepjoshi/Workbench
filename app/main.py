from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, init_db
from .models import Profile, Job
from .scoring import score_job

app = FastAPI(title="Workbench")

DEMO = [
    ("Manager, Technical Account Management", "EnterprisePay", "Dublin, Ireland", "Hybrid", "Enterprise payments TAM leadership, executive relationships, QBRs and adoption.", "Salary available", 3),
    ("Technical Support Engineering Manager", "CloudStack", "Dublin, Ireland", "Hybrid", "Lead TSEs working on APIs, cloud infrastructure and enterprise SaaS.", "Salary available", 7),
    ("Senior Technical Account Manager", "DataPlatform", "London, UK", "Hybrid", "Strategic enterprise accounts, technical architecture, adoption and executive reviews.", "Salary available", 12),
    ("Enterprise Customer Success Manager", "AIWorks", "Amsterdam, Netherlands", "Hybrid", "Enterprise adoption, technical strategy and expansion for AI SaaS.", "Salary available", 18),
    ("Solutions Architect", "DeveloperCloud", "Remote worldwide", "Remote", "Customer-facing architecture across APIs, cloud and developer platforms.", "Salary not listed", 22),
]

@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        if not s.exec(select(Profile)).first():
            s.add(Profile())
            s.commit()

def page(body: str, active: str = "home") -> HTMLResponse:
    nav = f'''<aside class="sidebar"><div class="brand"><div class="brand-mark"></div><span>Workbench</span></div><div class="brand-sub">Personal career intelligence</div><nav><a class="nav-item {'active' if active == 'home' else ''}" href="/">Job Scout</a><a class="nav-item {'active' if active == 'profile' else ''}" href="/profile">My Profile</a></nav><div class="sidebar-quote">Find work that fits your strengths.<small>Job Scout</small></div></aside>'''
    return HTMLResponse(f'''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Workbench</title><link rel="stylesheet" href="/static/style.css"></head><body><div class="app-shell">{nav}<div class="main-content">{body}</div></div></body></html>''')

def clear_jobs(s):
    for job in s.exec(select(Job)).all():
        s.delete(job)

def run_scan(s, p, window):
    hours = 24 if window == "24h" else 168 if window == "7d" else 720
    now = datetime.now(timezone.utc)
    for title, company, location, work_model, desc, salary, age_hours in DEMO:
        if age_hours > hours:
            continue
        j = Job(title=title, company=company, description=desc, location=location, work_model=work_model, url="https://example.com/jobs", source="demo", salary=salary, posted_at=now - timedelta(hours=age_hours))
        score_job(j, p)
        s.add(j)

@app.get("/", response_class=HTMLResponse)
def home():
    with Session(engine) as s:
        jobs = s.exec(select(Job).order_by(Job.score.desc(), Job.posted_at.desc())).all()
    cards = "".join(f'''<article class="job-card"><div class="job-top"><div class="company-icon">{j.company[:1]}</div><div class="job-main"><h3>{j.title}</h3><h4>{j.company}</h4><div class="meta"><span>{j.location}</span><span>{j.work_model}</span><span>{j.posted_at.strftime('%d %b %H:%M')}</span></div></div><div class="match-score">{j.score}</div></div><p class="job-desc">{j.description}</p><div class="chips"><span>{j.work_model}</span><span>{j.location}</span><span>{j.salary}</span></div><div class="job-actions"><a class="outline-btn" href="{j.url}" target="_blank">View job</a><a class="save-btn" href="/job/{j.id}/save">Save</a><a class="skip-btn" href="/job/{j.id}/skip">Skip</a></div></article>''' for j in jobs[:5])
    return page(f'''<header class="hero"><div><p class="eyebrow">YOUR DAILY CAREER SCOUT</p><h1>Find your next role.</h1><p class="lead">Role and location fit come first.</p></div><div class="hero-actions"><a class="primary-btn" href="/scan?window=24h">Run today’s scan</a><a class="outline-btn" href="/rerun-test">Re-run test</a></div></header><div class="layout"><section class="feed"><div class="section-head"><div><h2>Today's Matches</h2><p>24-hour jobs first · then 7 days · then 30 days.</p></div><strong>{len(jobs[:5])} matches</strong></div>{cards or '<div class="empty">No matches yet. Run today’s scan.</div>'}</section><aside class="right-rail"><div class="panel profile-panel"><div class="panel-title"><span>◉</span><h3>Profile signals</h3><a href="/profile">Edit</a></div><b>Roles</b><p>TAM → TSE → CSM → SA</p><b>Location</b><p>Dublin → Ireland → Europe → Remote worldwide</p><div class="stats"><div><span>Seniority</span><b>Manager / Lead first</b></div><div><span>Work model</span><b>Hybrid / On-site first</b></div><div><span>Freshness</span><b>24h first</b></div></div></div><div class="quote-panel"><span>“</span><p>Role and location are the strongest signals. Salary is shown when available.</p><small>Current sourcing strategy</small></div></aside></div>''')

@app.get("/scan")
def scan(window: str = Query("24h")):
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        clear_jobs(s)
        run_scan(s, p, window)
        s.commit()
    return RedirectResponse("/", 303)

@app.get("/rerun-test")
def rerun_test():
    return RedirectResponse("/scan?window=24h", 303)

@app.get("/job/{job_id}/{action}")
def action(job_id: int, action: str):
    if action not in {"save", "skip"}:
        return RedirectResponse("/", 303)
    with Session(engine) as s:
        j = s.get(Job, job_id)
        if not j:
            return RedirectResponse("/", 303)
        j.status = "saved" if action == "save" else "skipped"
        s.add(j)
        if action == "skip":
            clear_jobs(s)
            p = s.exec(select(Profile)).first()
            # Skipping the current 24h set broadens the next search to 7d.
            run_scan(s, p, "7d")
        s.commit()
    return RedirectResponse("/", 303)

@app.get("/profile", response_class=HTMLResponse)
def profile():
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
    return page(f'''<div class="profile-page"><p class="eyebrow">PERSONAL SOURCING PROFILE</p><h1>My Profile</h1><p class="lead">Saving your profile clears old matches and starts a fresh 24-hour scan.</p><form class="profile-form" method="post"><label>Target roles<input name="roles" value="{p.roles}"></label><label>Seniority<input name="seniority" value="{p.seniority}"></label><label>Location priority<input name="location_priority" value="{p.location_priority}"></label><label>Work model<input name="work_model" value="{p.work_model}"></label><label>Technical stack<textarea name="stack" rows="3">{p.stack}</textarea></label><label>Industries<input name="industries" value="{p.industries}"></label><label>Culture signals<textarea name="culture" rows="3">{p.culture}</textarea></label><label>Travel<input name="travel" value="{p.travel}"></label><label>Salary preference<input name="salary_preference" value="{p.salary_preference}"></label><label>Freshness strategy<input name="freshness_window" value="{p.freshness_window}"></label><button class="primary-btn" type="submit">Save profile & re-run scan</button></form></div>''', "profile")

@app.post("/profile")
def save_profile(roles: str = Form(...), seniority: str = Form(...), location_priority: str = Form(...), work_model: str = Form(...), stack: str = Form(...), industries: str = Form(...), culture: str = Form(...), travel: str = Form(...), salary_preference: str = Form(...), freshness_window: str = Form(...)):
    with Session(engine) as s:
        p = s.exec(select(Profile)).first()
        p.roles, p.seniority, p.location_priority = roles, seniority, location_priority
        p.work_model, p.stack, p.industries = work_model, stack, industries
        p.culture, p.travel, p.salary_preference = culture, travel, salary_preference
        p.freshness_window = freshness_window
        s.add(p)
        clear_jobs(s)
        run_scan(s, p, "24h")
        s.commit()
    return RedirectResponse("/", 303)
