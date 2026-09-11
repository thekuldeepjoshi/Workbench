import re
WEIGHTS = {"culture":30,"stack":20,"role":15,"mission":12,"stage":10,"hardtech":13}
def terms(text): return [x.strip().lower() for x in re.split(r"[,;]", text) if x.strip()]
def score_job(job, profile):
    text=f"{job.title} {job.company} {job.description}".lower()
    def hit(words): return min(100, round(100*sum(w in text for w in words)/max(1,len(words))))
    scores={"culture":hit(terms(profile.culture)),"stack":hit(terms(profile.stack)),"role":hit(terms(profile.roles)),"mission":hit(terms(profile.industries)),"stage":hit(["series a","series b","series c","startup","early stage","small team"]),"hardtech":hit(["iot","hardware","robotics","embedded","edge computing","sensors"])}
    job.culture_score=scores["culture"]; job.stack_score=scores["stack"]; job.role_score=scores["role"]; job.mission_score=scores["mission"]; job.stage_score=scores["stage"]; job.hardtech_score=scores["hardtech"]
    job.score=round(sum(scores[k]*WEIGHTS[k] for k in WEIGHTS)/100)
    job.rationale=f"Culture {job.culture_score}/100, stack {job.stack_score}/100, role {job.role_score}/100, mission {job.mission_score}/100. Remote is the hard requirement."
    return job
