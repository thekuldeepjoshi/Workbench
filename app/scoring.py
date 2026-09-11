import re
from datetime import datetime, timezone

# Role and location now dominate the ranking, followed by technical fit.
WEIGHTS = {"role": 35, "location": 30, "seniority": 15, "stack": 10, "industry": 5, "culture": 5}

def terms(text):
    return [x.strip().lower() for x in re.split(r"[,;]", text or "") if x.strip()]

def hit(text, words):
    if not words:
        return 0
    return min(100, round(100 * sum(w in text for w in words) / len(words)))

def location_score(job, profile):
    loc = (job.location or "").lower()
    model = (job.work_model or "").lower()
    if "dublin" in loc:
        return 100
    if "ireland" in loc:
        return 90
    if any(x in loc for x in ["london", "berlin", "amsterdam", "paris", "barcelona", "lisbon", "madrid", "cork", "galway"]):
        return 75
    if "europe" in loc or "remote worldwide" in model or "worldwide" in loc:
        return 60
    if "remote" in model or "remote" in loc:
        return 45
    return 25

def seniority_score(job, profile):
    text = f"{job.title} {job.description}".lower()
    if any(x in text for x in ["director", "head of", "senior manager", "manager", "lead"]):
        return 100
    if any(x in text for x in ["principal", "staff", "senior"]):
        return 85
    if "associate" in text:
        return 55
    return 45

def score_job(job, profile):
    text = f"{job.title} {job.company} {job.description}".lower()
    role_words = terms(profile.roles)
    role = hit(text, role_words)
    # Stronger exact role-family signals for the requested ordering.
    if "technical account manager" in text or "tam" in text:
        role = max(role, 100)
    elif "technical support engineer" in text or "tse" in text:
        role = max(role, 90)
    elif "customer success" in text or "csm" in text:
        role = max(role, 80)
    elif "solutions architect" in text or "solutions engineer" in text:
        role = max(role, 70)

    scores = {
        "role": role,
        "location": location_score(job, profile),
        "seniority": seniority_score(job, profile),
        "stack": hit(text, terms(profile.stack)),
        "industry": hit(text, terms(profile.industries)),
        "culture": hit(text, terms(profile.culture)),
    }
    job.role_score = scores["role"]
    job.location_score = scores["location"]
    job.seniority_score = scores["seniority"]
    job.stack_score = scores["stack"]
    job.mission_score = scores["industry"]
    job.culture_score = scores["culture"]
    job.stage_score = 0
    job.hardtech_score = 0
    job.score = round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS) / 100)
    age_hours = max(0, (datetime.now(timezone.utc) - job.posted_at).total_seconds() / 3600)
    freshness = "Last 24h" if age_hours <= 24 else "Last 7d" if age_hours <= 168 else "Last 30d"
    salary = f" · {job.salary}" if job.salary else ""
    job.rationale = f"{freshness} · Role {scores['role']}/100 · Location {scores['location']}/100 · Seniority {scores['seniority']}/100 · Technical fit {scores['stack']}/100{salary}"
    return job
