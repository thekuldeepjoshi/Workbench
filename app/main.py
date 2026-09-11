from fastapi import FastAPI
from .database import init_db
app=FastAPI(title="Workbench")
@app.on_event("startup")
def startup(): init_db()
@app.get("/")
def home(): return {"name":"Workbench","status":"running"}
