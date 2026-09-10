# OMEN

**OMEN** is an institutional career intelligence and employability platform. It connects student profile signals, current market demand, learning progress, verified projects, placement opportunities, applications, outcomes, and institutional interventions.

> **Your career shouldn't be a guess.** OMEN is designed to show where a student stands in the market and what to do next—not to make unsupported hiring-probability claims.

## What is implemented

The repository contains a Next.js + TypeScript frontend, a FastAPI + Pydantic backend, version-controlled Supabase/PostgreSQL migrations with RLS policies, a seeded market fallback dataset, and a working end-to-end demo vertical slice:

- Student landing page and dashboard with market employability score, component breakdown, positive/negative factors, skill gaps, career explorer, what-if projection, opportunities, applications, notifications, and TPO analytics.
- FastAPI endpoints for profile, intelligence, careers, market, jobs, applications, notifications, TPO overview, status transitions, and CSV result preview.
- Market-driven scoring based on normalized demand, demonstrated proficiency, practical experience, assessment signals, and communication. This is explicitly labeled as a development fallback and readiness signal.
- Deterministic hard eligibility engine, separate role matching, application state history, and human-controlled TPO status updates.
- Supabase migration with core profiles, skills, roles, jobs, applications, learning, projects, notifications, bootcamps, polls, market snapshots, indexes, and RLS policies.

The API currently runs in a safe **demo mode** when Supabase credentials are absent so the application is locally demonstrable. Replace the repository-backed demo store with Supabase repository calls for production deployment; the schema and policy foundation are ready for that connection.

## Run locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example .env        # fill server-side values when using Supabase
uvicorn app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

Open <http://localhost:3000>. The frontend calls `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000/api/v1`).

## Supabase setup

1. Create a Supabase project and configure Google under **Authentication → Providers → Google**. The Google client secret remains in Supabase; it is never placed in this repo.
2. Run `supabase/migrations/202609100001_omen_core.sql` in the Supabase SQL editor or with the Supabase CLI.
3. Run `supabase/seed/seed.sql` for development catalog data. Seed data is clearly development-only.
4. Add server-only `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and optional `DATABASE_URL` to the backend environment. Never expose the service role key or database URL to the browser.
5. Create private storage buckets for `resumes`, `certificates`, `project-submissions`, `course-resources`, and `company-documents`, then add storage policies following the same `auth.uid()` ownership pattern.

## Architecture

```text
Next.js UI → typed API boundary → FastAPI routes/services → Supabase/PostgreSQL + Storage
                                      ↓
                  market normalization → skill graph → matching / gaps → learning / verification
                                      ↓
                            jobs → eligibility + match → application → TPO review → outcome intelligence
```

The `backend/app/intelligence/engine.py` module intentionally keeps market scoring, role matching, and deterministic eligibility separate. A future provider can replace the local snapshot without rewriting the scoring contract.

## Testing

```bash
cd backend
source .venv/bin/activate
pytest -q
```

For a smoke test after starting the API:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/students/me/intelligence
```

## Security

`.env`, secrets, keys, passwords, and credentials are ignored. Supabase RLS policies protect student-owned records and give TPOs controlled institutional access. Backend CORS is configured through `CORS_ORIGINS`. File uploads should be sent through a server-side signed upload flow in production with MIME and size validation.

## Product boundaries

OMEN is not a job board, ATS, external recruitment portal, scraping platform, generic chatbot, or unsupported hiring predictor. External application URLs are recorded and opened after OMEN records the application.


## Supabase integration status

The active OMEN Supabase project has been initialized from the repository migrations. Migrations `202609100001_omen_core.sql`, `202609100002` storage policies, and `202609100003_omen_profile_outcomes.sql` create the core profile, skill, market, learning, project, placement, notification, resume, outcome, analytics, poll, and bootcamp relationships. Private storage buckets are created for resumes, certificates, project submissions, course resources, and company documents.

When `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are configured in the backend, the API uses the authenticated Supabase user, persists onboarding profiles, uploads private resumes, persists course progress and projects, and reads jobs, applications, notifications, polls, and bootcamps from Supabase. Without those values, the API explicitly reports `demo_mode: true` and uses the controlled local fallback.

The frontend now includes `/login`, `/auth/callback`, and `/onboarding`. Login uses Supabase Auth’s Google provider; the Google credentials remain configured in Supabase and are not stored in this repository. The backend exposes `/api/v1/auth/config` and `/api/v1/auth/me` for session-aware clients.

## Current endpoint coverage

Implemented endpoint families include health and auth, student profile and intelligence, resume upload, careers and what-if projections, market data, jobs, applications, application state updates, course catalog and progress, project submission, notifications, TPO overview, polls, bootcamp creation, and CSV result preview. The existing migration provides the persistent state needed to extend assessment, verification, shortlist, and outcome-confirmation endpoints without changing the core data model.

## Production security follow-up

The initial migration enables RLS on private user-owned tables and installs ownership policies. Supabase inspection also identified public reference/workflow tables that should receive deliberate read/write policies before exposing them directly through a browser client: `skills`, `roles`, `role_skills`, `companies`, `jobs`, `job_requirements`, `application_status_history`, `courses`, `course_phases`, `learning_resources`, `assessments`, `assessment_questions`, `student_course_progress`, `student_assessment_attempts`, `skill_verifications`, `market_snapshots`, `bootcamps`, `student_polls`, `poll_options`, and `poll_responses`. The server-side service-role path remains protected from the browser, but production rollout should complete these table-specific policies based on whether each table is public-readable, student-owned, or TPO-managed.


## Phase 0 foundation

Phase 0 centralizes persistence through `OmenRepository`. When Supabase is configured, application creation, application status changes, status history, notifications, course progress, project submission, bootcamp creation, polls, jobs, courses, profiles, and intelligence reference data use the repository or its service boundary instead of the in-memory demo lists. The demo lists remain available only when Supabase is unavailable.

FastAPI authorization helpers now expose reusable authentication, student, TPO, and admin checks. The authenticated role is read from the server-side `profiles` record and is never trusted from the browser. TPO analytics, status changes, bootcamp creation, and result preview reject non-TPO users with HTTP 403 when production authentication is active.

Migration `202609100004_phase0_rls.sql` enables RLS across all current public tables. Public reference tables are authenticated-read/TPO-managed, student-owned records are restricted through `auth.uid()` ownership checks, workflow history and outcomes are visible to the relevant student or TPO, and institutional analytics is TPO-only. The migration has been applied to the active OMEN Supabase project.
