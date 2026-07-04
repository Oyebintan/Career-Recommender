# CareerRecommender

A smart web-based career recommendation system that helps users identify
suitable career paths based on their interests, strengths, and
preferences — and bridges their skill gaps.

---

## Project Overview

CareerRecommender is a Flask-powered web application that guides users
through a structured assessment and returns personalised career
recommendations using a weighted scoring engine.

### Key Features

- User registration, login, and Google OAuth sign-in
- Profile setup (age, education, field of study)
- 35-question Likert-scale career assessment across 13 life categories
- Weighted scoring engine — normalised fairly per career
- Top 3 career matches with match percentage
- Skill gap analysis — shows required, existing, and missing skills
- Assessment history on personal dashboard
- Light and dark mode UI
- Fully responsive (mobile + desktop)

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.x |
| Database ORM | SQLAlchemy + Flask-SQLAlchemy |
| Authentication | Flask-Login + Authlib (Google OAuth) |
| Database | PostgreSQL (Neon.tech in production) |
| Data Processing | Pandas, NumPy |
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Deployment | Hugging Face Spaces (Docker) |

---

## Project Structure

career-recommender/
│
├── Backend/
│   ├── app.py                  # Flask app factory, blueprint registration
│   ├── config.py               # Environment-based configuration
│   ├── extensions.py           # db, login_manager, oauth instances
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── models/
│   │   ├── user.py             # User model (supports email + Google OAuth)
│   │   ├── profile.py          # User profile (age, education, etc.)
│   │   ├── assessment.py       # Assessment + AssessmentAnswer models
│   │   └── recommendation.py   # Recommendation model
│   │
│   ├── routes/
│   │   ├── auth_routes.py      # Register, login, logout, Google OAuth
│   │   ├── profile_routes.py   # Profile setup
│   │   ├── assessment_routes.py
│   │   ├── recommendation_routes.py
│   │   └── dashboard_routes.py
│   │
│   ├── services/
│   │   ├── dataset_loader.py       # Loads all 5 CSV datasets
│   │   ├── recommendation_service.py  # Scoring engine
│   │   └── skill_gap_service.py    # Skill gap analysis
│   │
│   └── tests/
│       ├── test_loader.py
│       ├── test_recommendation.py
│       ├── test_skill_gap.py
│       └── test_db_connection.py
│
├── Frontend/
│   ├── static/
│   │   ├── css/main.css        # Full design system (light + dark mode)
│   │   └── js/
│   │       ├── main.js         # Theme toggle, flash messages, animations
│   │       └── assessment.js   # Multi-step wizard logic
│   │
│   └── templates/
│       ├── base.html           # Shared navbar, flash messages, footer
│       ├── landing.html
│       ├── login.html
│       ├── register.html
│       ├── profile_setup.html
│       ├── assessment.html
│       ├── assessment_review.html
│       ├── career_results.html
│       ├── career_details.html
│       ├── skill_gap.html
│       ├── dashboard.html
│       └── error.html
│
├── datasets/
│   └── custom/
│       ├── career_profiles.csv         # 42 careers with domain
│       ├── career_descriptions.csv     # Descriptions, salary, education
│       ├── career_skills.csv           # Skills per career
│       ├── assessment_questions.csv    # 35 questions across 13 categories
│       └── career_question_mapping.csv # Question-career weights
│
├── docs/
│   ├── README.md
│   └── architecture.md
│
├── Dockerfile
└── requirements.txt

---

## Recommendation Engine

### How It Works

1. User answers 35 questions on a 1–5 Likert scale
2. Each answer is matched to careers via `career_question_mapping.csv`
3. Raw score is calculated: `score += answer_value × weight`
4. Each career is normalised against its **own theoretical maximum**
   (sum of mapped weights × 5) — not the global maximum
5. Careers are ranked by normalised percentage
6. Top 3 are returned and stored

### Why Per-Career Normalisation Matters

The normalization formula is:
career_score% = (raw_score / career_own_max) × 100

This is critical. Using a global maximum (dividing by the single
highest scorer) would structurally favour careers that happen to
have more questions mapped to them — causing bias toward any
over-represented domain. Per-career normalisation ensures fair
comparison regardless of how many questions are mapped per career.

---

## Skill Gap Analysis

After a career is recommended:
1. Required skills are retrieved from `career_skills.csv`
2. User inputs their existing skills
3. System identifies missing skills
4. Readiness score = (skills_owned / skills_required) × 100

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Oyebintan/Career-Recommender.git
cd Career-Recommender

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp Backend/.env.example Backend/.env
# Edit Backend/.env — fill in SECRET_KEY and DATABASE_URL

# Run the app
cd Backend
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

### Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session signing key |
| `DATABASE_URL` | PostgreSQL connection string |
| `GOOGLE_CLIENT_ID` | (Optional) Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | (Optional) Google OAuth client secret |
| `DATASETS_DIR` | (Optional) Absolute path override for datasets folder |

---

## Database Schema

| Table | Description |
|---|---|
| `users` | Registered users (email + Google OAuth) |
| `profiles` | User background info (age, education) |
| `assessments` | Each assessment attempt |
| `assessment_answers` | Individual question responses |
| `recommendations` | Top 3 career results per assessment |

---

## Deployment

The application is deployed on **Hugging Face Spaces** using Docker,
with a **Neon.tech** hosted PostgreSQL database.

The `Dockerfile` at the project root handles the full build. The
`requirements.txt` at root level is what Docker installs.

---

## Testing

Run from the `Backend/` directory with the virtual environment active:

```bash
python tests/test_loader.py
python tests/test_recommendation.py
python tests/test_skill_gap.py
python tests/test_db_connection.py
```

---

## Author

Developed by **Olamide** as an academic project submission.
