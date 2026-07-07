# CareerRecommender

A smart web-based recommender system for **career path identification and skill
recommendation**. Users complete a short interest assessment and receive their
top-matching careers, detailed career information, and a personalised skill-gap
analysis showing which skills they still need to acquire.

Version 1 is **rule-based** (weighted scoring + skill comparison), not machine
learning. The recommendation logic is deliberately transparent and reproducible:
two users with identical answers always receive identical recommendations.

---

## What it does

1. Collects user assessment responses on a 5-point Likert scale.
2. Scores and ranks **42 careers** across **6 domains** using a curated
   question-to-career weight mapping (**35 questions**, **13 interest categories**).
3. Returns the user's **top 3 career matches** with a percentage match score.
4. Shows career details — description, salary range, education requirement, and
   required skills.
5. Runs a **skill-gap analysis**: compares required skills against the user's
   skills and reports a readiness score plus the specific skills still missing.
6. Persists every assessment so users can review their history from a dashboard.

---

## Technology stack

| Layer | Technology |
|-------|-----------|
| Presentation | HTML5, Bootstrap 5, vanilla JavaScript, Jinja2 templates |
| Application | Python, Flask (5 route blueprints) |
| Service | Python + pandas (dataset loader, recommendation, skill-gap) |
| Data | PostgreSQL (hosted on Neon.tech) via SQLAlchemy ORM |
| Auth | Flask-Login + Werkzeug password hashing; optional Google OAuth (Authlib) |
| Deployment | Docker, Hugging Face Spaces (port 7860) |

---

## Project structure

```
career-recommender-project/
├── Backend/
│   ├── app.py                     # Flask entry point / app factory
│   ├── config.py                  # Config (reads .env)
│   ├── extensions.py              # db, login_manager, oauth singletons
│   ├── models/                    # SQLAlchemy models (5 tables)
│   ├── routes/                    # 5 blueprints: auth, profile, assessment,
│   │                              #   recommendation, dashboard
│   ├── services/                  # dataset_loader, recommendation, skill_gap
│   ├── tests/                     # standalone verification scripts
│   ├── generate_*.py              # Chapter 3 diagram/code-image generators
│   └── requirements.txt
├── Frontend/
│   ├── templates/                 # Jinja2 pages
│   └── static/{css,js}/           # styles + client scripts
├── datasets/
│   ├── custom/                    # 5 primary CSV datasets
│   └── onet/                      # supplementary O*NET data (not yet used)
├── docs/                          # this documentation
└── Dockerfile
```

---

## Running locally

> The application entry point lives in `Backend/` and its imports assume that is
> the working directory. Always run it from inside `Backend/`.

1. **Create the environment file**

   ```bash
   cd Backend
   cp .env.example .env
   ```

   Then edit `.env` and set at minimum:
   - `SECRET_KEY` — a random value (`python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_URL` — e.g. `postgresql://<user>:<password>@<host>:5432/career_recommender`
   - (optional) `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` to enable Google sign-in

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run**

   ```bash
   python app.py
   ```

   Tables are created automatically on first run (`db.create_all()`).
   The app is served at `http://127.0.0.1:7860` (or the port in `$PORT`).

---

## How it works (summary)

- **Recommendation** — for each answered question, every mapped career gains
  `answer × weight`. Raw scores are then expressed as a percentage of the
  highest-scoring career in that response (so the best match reads as 100%),
  sorted, and the top three are stored.
- **Skill gap** — required skills for the chosen career are compared with the
  user's supplied skills; readiness = `possessed ÷ required × 100`.

See [architecture.md](architecture.md), [database_design.md](database_design.md),
and [system_requirements.md](system_requirements.md) for detail.

---

## Datasets

**Primary (custom):** `career_profiles.csv`, `career_descriptions.csv`,
`assessment_questions.csv`, `career_question_mapping.csv`, `career_skills.csv`.

**Supplementary (O*NET):** occupation data, essential skills, knowledge,
abilities, and software skills. These are **retained for future enhancement**
and are not consumed by the Version 1 recommendation logic.

---

## Limitations & future work

- Skill matching is currently an exact, case-sensitive string comparison.
- The O*NET datasets require an occupation-matching layer before they can enrich
  the 42 modelled careers.
- Datasets are re-read from disk per request (fine at current scale; a cache is
  a straightforward future optimisation).
