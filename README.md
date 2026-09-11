# Workbench

Workbench is a personal productivity workspace built in Python. It provides a foundation for building focused tools and workflows in one place.

## Current Project

The first tool in Workbench is a **remote software engineering opportunity finder**.

It helps identify and rank potential engineering roles based on a configurable personal profile, with an emphasis on:

* Remote opportunities
* Software Engineering, Senior Software Engineering, and Fullstack roles
* Python and React experience
* Full-stack roles
* Company culture and working style
* Mission-driven companies
* Smaller and earlier-stage companies
* IoT, hardware, and hard-tech companies

Culture is treated as the strongest preference, while technical fit, role fit, mission, company stage, and hard-tech relevance contribute to the overall ranking.

## Features

* Personal candidate profile
* Configurable role and technology preferences
* Culture preference configuration
* Remote-only filtering
* Weighted opportunity scoring
* Job match explanations
* Save and skip workflow
* Job history
* Daily search workflow
* SQLite for local development
* PostgreSQL support through `DATABASE_URL`
* Render deployment configuration

## Architecture

```text
Workbench
├── app/
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # Database models
│   ├── database.py      # Database configuration
│   ├── scoring.py       # Opportunity scoring
│   └── static/
│       └── style.css    # UI styles
├── requirements.txt
├── pyproject.toml
├── render.yaml
└── README.md
```

## Running Locally

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Configuration

The application can use SQLite by default:

```text
sqlite:///jobs.db
```

For production, set:

```text
DATABASE_URL=postgresql://...
```

## Deployment

The repository includes a `render.yaml` configuration for deployment to Render.

The production application should use PostgreSQL rather than relying on the local SQLite filesystem.

## Job Search

The current implementation includes demo jobs so that the application can be developed and tested without external integrations.

The intended production workflow is:

1. Search for newly posted roles.
2. Apply the remote requirement as a hard filter.
3. Prioritize jobs posted within the last 24 hours.
4. Evaluate technical and role fit.
5. Evaluate company culture using available evidence.
6. Rank the strongest opportunities.
7. Return up to five high-quality matches.
8. Clearly indicate when fewer than five strong matches are available rather than automatically lowering the criteria.

External job-search integrations can be added independently of the scoring and profile components.

## Development

Workbench is intentionally structured so that additional tools can be added without turning the repository into a single-purpose application.

Potential future modules include:

* Job discovery integrations
* Resume analysis
* Application tracking
* Company research
* Interview preparation
* Personal workflow automation
* Additional productivity tools

## Status

This project is currently an MVP and is intended to evolve into a broader personal workspace.

External job-source integrations are not yet enabled in the current MVP.

