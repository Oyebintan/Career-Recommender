# System Architecture

CareerRecommender follows a **layered web architecture** with a clean separation
of concerns. Business logic lives in an isolated service layer, not inside the
web routes, which makes it independently testable and easy to reason about.

See `Backend/diagram_output/Figure_3_1_Architecture.png` for the visual diagram
(generated live from the codebase).

---

## Layers

### 1. Presentation Layer
HTML5, Bootstrap 5, and vanilla JavaScript rendered through **Jinja2 templates**
(`Frontend/templates/`). Mobile-first, responsive, with a light/dark theme toggle
persisted in `localStorage`. Client scripts (`Frontend/static/js/`) handle the
theme, flash messages, and the stepped assessment wizard.

### 2. Application Layer
Python + **Flask**, organised into **five route blueprints** under
`Backend/routes/`:

| Blueprint | Responsibility |
|-----------|----------------|
| `auth` | Landing, register, login, logout, Google OAuth |
| `profile` | Profile creation / editing |
| `assessment` | Serving the assessment, submitting answers, generating recommendations |
| `recommendation` | Career results, career detail, skill-gap analysis |
| `dashboard` | Assessment history overview |

Application-wide extensions (`db`, `login_manager`, `oauth`) are defined once in
`extensions.py` and initialised by the app factory `create_app()` in `app.py`.

### 3. Service Layer
Three framework-agnostic modules under `Backend/services/`:

- **`DatasetLoader`** — locates and reads the five custom CSV datasets with
  pandas, exposing a simple interface so other modules never touch file paths.
- **`RecommendationService`** — weighted scoring, percentage scaling, and ranking.
- **`SkillGapService`** — compares required vs. possessed skills and computes a
  readiness score.

Keeping this logic out of the routes means it can be verified in isolation
(`Backend/tests/`) without a running web server or database.

### 4. Data Layer
**PostgreSQL** (hosted on Neon.tech), accessed through the **SQLAlchemy ORM**.
Persists users, profiles, assessments, individual answers, and recommendation
history. See [database_design.md](database_design.md).

---

## Request flow (typical assessment journey)

```
Browser
  │  HTTP request
  ▼
Route blueprint (application layer)
  │  function call
  ▼
Service (recommendation / skill-gap)   ──reads──▶  CSV datasets (pandas)
  │  results
  ▼
SQLAlchemy models  ──ORM──▶  PostgreSQL
  │
  ▼
Jinja2 template  ──HTML──▶  Browser
```

End-to-end user journey:

```
Landing → Register → Login → Profile Setup → Assessment
        → Submit → Career Results → Skill-Gap Analysis → Dashboard
```

On submission, answers are persisted, the recommendation engine runs, the top
three careers are stored, and the user is taken **directly to the results page**.

---

## Authentication

- Session management via **Flask-Login**.
- Passwords hashed with **Werkzeug** (`generate_password_hash` /
  `check_password_hash`); the hash column is nullable to support OAuth-only users.
- Optional **Google OAuth** via Authlib — the sign-in button is shown only when
  `GOOGLE_CLIENT_ID` is configured, so the app runs fine without it.
- Protected routes use `@login_required`, and record lookups are always scoped to
  `current_user` (`first_or_404`) so users can only access their own data.

---

## Design rationale

- **Separation of concerns** keeps the scoring logic testable and swappable
  without touching the web or database layers.
- **App factory pattern** (`create_app()`) allows the same application to be
  configured differently for local development, testing (e.g. SQLite), and
  production (PostgreSQL) via environment variables.
- **Data decoupled from code** — careers, skills, questions, and weights live in
  CSVs, so the domain can be extended without changing Python.

## Deployment

Containerised with Docker (`python:3.11-slim`) and deployed to Hugging Face
Spaces. The app binds to `0.0.0.0` on the `PORT` provided by the platform
(7860 by default) with debug disabled in that environment.
