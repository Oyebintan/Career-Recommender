# System Requirements

## Functional requirements

The system shall:

1. **FR-1** — Allow a user to register with name, email, and password, or sign in
   with a Google account.
2. **FR-2** — Authenticate users and maintain a login session; restrict protected
   pages to authenticated users.
3. **FR-3** — Capture a user profile (age, gender, education level, course of
   study).
4. **FR-4** — Present a structured interest assessment of 35 questions across 13
   categories, answered on a 5-point Likert scale, one category at a time, and
   prevent submission until every question is answered.
5. **FR-5** — Score every career using the weighted question-to-career mapping and
   rank them.
6. **FR-6** — Return the user's top 3 career matches with a percentage match
   score.
7. **FR-7** — Display career information: description, salary range, education
   requirement, domain, and required skills.
8. **FR-8** — Perform skill-gap analysis for a selected career: report possessed
   skills, missing skills, and a readiness percentage.
9. **FR-9** — Persist each assessment and its recommendations, and present the
   user's assessment history on a dashboard.

## Non-functional requirements

- **NFR-1 (Usability)** — Mobile-first, responsive UI with light/dark themes.
- **NFR-2 (Consistency)** — Deterministic recommendations: identical answers
  always yield identical results.
- **NFR-3 (Security)** — Passwords stored only as salted hashes; per-user data
  access enforced on every protected route.
- **NFR-4 (Maintainability)** — Business logic isolated in a service layer,
  independently testable; domain data kept in CSVs, decoupled from code.
- **NFR-5 (Portability)** — Runs locally or containerised (Docker) with
  configuration supplied entirely through environment variables.

---

## Software requirements

| Item | Requirement |
|------|-------------|
| Python | 3.11+ |
| Database | PostgreSQL 13+ (Neon.tech cloud or local) |
| OS | Any (Windows/macOS/Linux); container image is `python:3.11-slim` |
| Browser | Any modern browser (Chrome, Edge, Firefox, Safari) |

### Key Python dependencies

(see `Backend/requirements.txt` for exact pinned versions)

- **Flask** — web framework
- **Flask-SQLAlchemy / SQLAlchemy** — ORM
- **Flask-Login** — session/auth management
- **Werkzeug** — password hashing
- **Authlib** — Google OAuth
- **pandas** — CSV dataset loading and processing
- **psycopg2-binary** — PostgreSQL driver
- **python-dotenv** — environment configuration

---

## Hardware requirements (minimum, for local development)

| Resource | Minimum |
|----------|---------|
| CPU | Dual-core |
| RAM | 4 GB |
| Disk | ~500 MB (project + dependencies) |
| Network | Required (cloud PostgreSQL, CDN assets, optional OAuth) |

---

## Configuration

Set via a `.env` file in `Backend/` (see `.env.example`):

| Variable | Purpose | Required |
|----------|---------|----------|
| `SECRET_KEY` | Signs session cookies | Yes (production) |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `FLASK_DEBUG` | `True`/`False` debug mode | No (defaults on locally) |
| `GOOGLE_CLIENT_ID` | Google OAuth client id | No (button hidden if unset) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | No |
| `PORT` | Serving port (set by host platform) | No (defaults to 7860) |
