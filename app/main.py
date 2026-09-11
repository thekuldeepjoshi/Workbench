from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, init_db
from .models import Profile, Job
from .scoring import score_job
app=FastAPI(title="Workbench")
DEMO=[("Senior Full Stack Engineer","CivicFlow","Python React autonomy transparency civic-tech series b"),("Software Engineer","HealthLoop","Python React health-tech inclusion belonging small team"),("Senior Software Engineer","SensorForge","Python React IoT hardware robotics autonomous teams"),("Fullstack Engineer","Learnly","Python React ed-tech empathy inclusion mission driven"),("Software Engineer","OpenGov Labs","Python React gov-tech transparency accountability remote")]
@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        if not s.exec(select(Profile)).first(): s.add(Profile()); s.commit()
def page(body):
    return HTMLResponse("<html><head><meta name='viewport' content='width=device-width'><style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:0 20px}nav{display:flex;gap:20px;margin-bottom:40px}article{border:1px solid #ddd;border-radius:12px;padding:20px;margin:15px 0}a{color:#111}.button{display:inline-block;padding:10px 14px;background:#111;color:white;border-radius:8px;text-decoration:none}input,textarea{display:block;width:100%;box-sizing:border-box;padding:10px;margin-top:6px}label{display:block;margin:15px 0}</style></head><body><nav><b>Workbench</b><a href='/'>Dashboard</a><a href='/profile'>Profile</a></nav>"+body+"</body></html>")
@app.get("/",response_class=HTMLResponse)
def home():
    with Session(engine) as s: jobs=s.exec(select(Job).order_by(Job.score.desc())).all()
    cards="".join(f"<article><h2>{j.title}</h2><p><b>{j.company}</b> · {j.location}</p><p>{j.rationale}</p><b>Match {j.score}/100</b><p><a href='/job/{j.id}/save'>Save</a> · <a href='/job/{j.id}/skip'>Skip</a></p></article>" for j in jobs[:5])
    return page(f"<h1>Remote opportunities</h1><p>Ranked by culture, skills, role, mission, stage and hard-tech fit.</p><p><a class='button' href='/scan'>Run today's scan</a></p>{cards or '<p>No jobs yet. Run a scan.</p>'}")
@app.get("/scan")
def scan():
    with Session(engine) as s:
        p=s.exec(select(Profile)).first()
        for title,company,desc in DEMO:
            if s.exec(select(Job).where(Job.company==company,Job.title==title)).first(): continue
            j=Job(title=title,company=company,description=desc,location="Remote"); score_job(j,p); s.add(j)
        s.commit()
    return RedirectResponse("/",303)
@app.get("/job/{job_id}/{action}")
def action(job_id:int,action:str):
    with Session(engine) as s:
        j=s.get(Job,job_id)
        if j: j.status="saved" if action=="save" else "skipped"; s.add(j); s.commit()
    return RedirectResponse("/",303)
@app.get("/profile",response_class=HTMLResponse)
def profile():
    with Session(engine) as s: p=s.exec(select(Profile)).first()
    return page(f"<h1>Profile</h1><form method='post'><label>Roles<input name='roles' value='{p.roles}'></label><label>Stack<input name='stack' value='{p.stack}'></label><label>Culture<textarea name='culture'>{p.culture}</textarea></label><label>Industries<textarea name='industries'>{p.industries}</textarea></label><label>Company stage<input name='company_stage' value='{p.company_stage}'></label><label>Hard requirement<input name='hard_requirement' value='{p.hard_requirement}'></label><label>Resume<textarea name='resume_text'>{p.resume_text}</textarea></label><button class='button'>Save</button></form>")
@app.post("/profile")
def save(roles:str=Form(...),stack:str=Form(...),culture:str=Form(...),industries:str=Form(...),company_stage:str=Form(...),hard_requirement:str=Form(...),resume_text:str=Form("")):
    with Session(engine) as s:
        p=s.exec(select(Profile)).first(); p.roles=roles; p.stack=stack; p.culture=culture; p.industries=industries; p.company_stage=company_stage; p.hard_requirement=hard_requirement; p.resume_text=resume_text; s.add(p); s.commit()
    return RedirectResponse("/",303)
