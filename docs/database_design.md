# Database Design

Persistent application data is stored in **PostgreSQL** and accessed through the
**SQLAlchemy ORM**. The schema is defined by the models in `Backend/models/` and
created automatically via `db.create_all()` on first run.

The database is organised around **five tables**. The static domain data
(careers, skills, questions, weights) is **not** stored here — it lives in the
CSV datasets and is loaded at runtime.

See `Backend/erd_output/Figure_3_3_ERD.png` (and `.pdf`) for the entity
relationship diagram, generated live from the models.

---

## Tables

### `users`
Registered accounts.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK |
| `name` | String(120) | NOT NULL |
| `email` | String(120) | NOT NULL, UNIQUE, indexed |
| `password_hash` | String(255) | nullable (null for OAuth-only users) |
| `google_id` | String(120) | nullable, UNIQUE, indexed |
| `created_at` | DateTime | default: now (UTC) |

### `profiles`
Demographic profile, one per user.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK |
| `user_id` | Integer | FK → `users.id`, NOT NULL, UNIQUE |
| `age` | Integer | NOT NULL |
| `gender` | String(30) | NOT NULL |
| `education_level` | String(80) | NOT NULL |
| `course_of_study` | String(120) | NOT NULL |

### `assessments`
One row per assessment attempt.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK |
| `user_id` | Integer | FK → `users.id`, NOT NULL |
| `created_at` | DateTime | default: now (UTC) |

### `assessment_answers`
The individual answers within an attempt.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK |
| `assessment_id` | Integer | FK → `assessments.id`, NOT NULL |
| `question_id` | Integer | NOT NULL (refers to a question in `assessment_questions.csv`) |
| `answer` | Integer | NOT NULL (Likert value 1–5) |

### `recommendations`
The top-ranked careers stored for each attempt.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK |
| `assessment_id` | Integer | FK → `assessments.id`, NOT NULL |
| `career_name` | String(120) | NOT NULL |
| `score` | Float | NOT NULL (percentage match) |
| `rank` | Integer | NOT NULL (1 = best match) |

---

## Relationships

| From | To | Cardinality | Cascade |
|------|----|-------------|---------|
| `users` | `profiles` | one-to-one | all, delete-orphan |
| `users` | `assessments` | one-to-many | all, delete-orphan |
| `assessments` | `assessment_answers` | one-to-many | all, delete-orphan |
| `assessments` | `recommendations` | one-to-many | all, delete-orphan |

Deleting a user cascades to their profile, assessments, answers, and
recommendations, so no orphaned records remain.

```
users ─1:1─ profiles
  │
  └─1:N─ assessments ─1:N─ assessment_answers
                     └─1:N─ recommendations
```

---

## Notes

- `question_id` in `assessment_answers` is an integer reference into the
  question bank CSV rather than a foreign key, because the question catalogue is
  managed as data (CSV), not as a database table.
- `recommendations.career_name` similarly stores the career by name, matching the
  career identifiers used across the CSV datasets.
- Timezone-aware UTC timestamps are used for `created_at` columns.
