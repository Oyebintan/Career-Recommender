# System Architecture

## Overview

CareerRecommender follows a classic three-tier web architecture:
**Frontend (HTML/CSS/JS) → Flask Backend → PostgreSQL Database**,
with CSV-based datasets powering the recommendation logic.

---

## Architecture Diagram
User (Browser)
│
▼
┌─────────────────────────────────────────────────┐
│              FLASK APPLICATION                  │
│                                                 │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐  │
│  │  Routes  │──▶│ Services │──▶│  Models    │  │
│  │ (5 BPs)  │   │          │   │ (ORM)      │  │
│  └──────────┘   │ Rec.Svc  │   └─────┬──────┘  │
│                 │ Gap.Svc  │         │          │
│  ┌──────────┐   │ Loader   │         │          │
│  │Templates │   └────┬─────┘         │          │
│  │(Jinja2)  │        │               │          │
│  └──────────┘        ▼               ▼          │
│                ┌──────────┐   ┌──────────────┐  │
│                │  CSVs    │   │  PostgreSQL  │  │
│                │(datasets)│   │  (Neon.tech) │  │
│                └──────────┘   └──────────────┘  │
└─────────────────────────────────────────────────┘

---

## Component Breakdown

### Routes (Blueprints)

| Blueprint | Prefix | Responsibility |
|---|---|---|
| `auth_bp` | `/` | Register, login, logout, Google OAuth |
| `profile_bp` | `/profile` | Create and update user profile |
| `assessment_bp` | `/assessment` | Serve questions, submit answers |
| `recommendation_bp` | `/results` | Career results, details, skill gap |
| `dashboard_bp` | `/dashboard` | Assessment history |

### Services

**DatasetLoader** — Locates and loads all 5 CSVs. Uses a walk-up
directory search so it works on any hosting layout.

**RecommendationService** — Implements the weighted scoring engine.
Scores are normalised per-career against each career's own maximum
possible score, ensuring fairness across careers with different
question coverage.

**SkillGapService** — Compares user-supplied skills against the
required skills for a given career and returns a readiness percentage.

### Data Flow
User answers 35 questions
│
▼
assessment_routes.py → RecommendationService.get_top_careers()
│
├── calculate_scores()   — raw weighted scores per career
├── normalize_scores()   — % against each career's own max
└── rank + return top 3
│
▼
Recommendations saved to DB → Review page → Results page

---

## Security

- Passwords hashed with Werkzeug `generate_password_hash`
- Sessions signed with `SECRET_KEY`
- `@login_required` on all authenticated routes
- Environment variables for all secrets (never committed)
- PostgreSQL credentials kept in `.env` (excluded from git)

---

## Deployment Architecture
GitHub ──push──▶ Hugging Face Spaces
│
Docker build
(Dockerfile at root)
│
python Backend/app.py
│
Flask on port 7860
│
Connects to Neon.tech
PostgreSQL via DATABASE_URL

