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


## Phase 1 student workspace

The public root route is now landing-only. It no longer renders a student dashboard. The explicit demo experience is available at `/demo`. Authenticated students use `/student/dashboard`, `/student/career-dna`, `/student/market-score`, `/student/careers`, `/student/skill-gaps`, and `/student/profile`.

The OAuth callback checks the authenticated Supabase user, server-backed profile role, and student profile existence. Existing students go to `/student/dashboard`; users without a student profile go to `/onboarding`; TPO/admin users are directed to the TPO route boundary.

Phase 1 student APIs include `/api/v1/students/me/profile`, `/api/v1/students/me/intelligence`, `/api/v1/students/me/skill-gaps`, `/api/v1/careers`, `/api/v1/careers/{role}/what-if`, and `/api/v1/resumes`. Student workspace screens consume these APIs rather than duplicating intelligence calculations in React. Resume uploads remain PDF-only, private, and limited to 5 MB.

Onboarding profile fields now persist graduation year, academics, experience counts, readiness signals, career intent-compatible profile data, and skills through the Phase 0 repository boundary. The Phase 1 schema addition is `202609110005_phase1_student_profile.sql`.


## Phase 2 learning-to-verification loop

Phase 2 adds database-backed learning and evidence workflows. Student routes are `/student/learning`, `/student/learning/[course_id]`, `/student/learning/[course_id]/assessment/[assessment_id]`, `/student/projects`, and `/student/projects/[project_id]`. TPO review is available at `/tpo/projects`.

The learning flow is: course catalog → course phases and linked resources → persisted course progress → deterministic assessment attempt → persisted score and retry history → project submission → TPO verification or rework → verified skill evidence. Assessment grading is deterministic: MCQ answers use exact normalized comparison and fill-in-the-blank answers use case/whitespace-normalized comparison. Attempts are append-only for students; each retry receives a new attempt number.

Project verification is TPO/admin controlled. Students can submit GitHub URLs, view their own projects and feedback, and resubmit after `Rework Required`. Students cannot set `Verified`, change TPO feedback, or alter assessment results. Verified project evidence is stored in `skill_verifications` and also updates the corresponding `student_skills` record with `source = verified_project` using the transparent rule `max(existing proficiency, verified project level)`; verification never arbitrarily inflates a skill. Subsequent intelligence and skill-gap reads consume the updated student skill evidence.

Phase 2 schema migrations are `202609110006_phase2_learning_verification.sql`, `202609110007_phase2_security.sql`, and `202609110008_phase2_rework_security.sql`. RLS remains enabled on courses, resources, assessments, attempts, projects, and verification records. The intended course completion rule is: all required phases completed, a passing assessment, and a final project verified; course progress alone is not treated as verified skill.


## Phase 1.5 onboarding and Career DNA UX

The onboarding flow now uses eight progressive steps: Welcome, Academics, Technical Profile, Projects & Experience, Resume, Career Intent, Readiness, and Career DNA Created. The UI uses controlled department, degree, skill, role, industry, proficiency, readiness, and practice-frequency catalogs from `GET /api/v1/catalogs/onboarding`; it does not duplicate department labels across components.

Onboarding drafts autosave through `GET/PUT /api/v1/students/me/onboarding` and preserve the current step, draft data, and meaningful profile completeness. Final submission continues to use `PUT /api/v1/students/me/profile`, preserving the existing repository and Supabase ownership architecture. Structured profile fields include career intents, preferred industries, work environment, target CTC, readiness signals, practice frequency, and project metadata.

Resume upload remains private PDF storage with a 5 MB limit. No resume parser exists in the current backend, so the redesigned UI intentionally does not display fabricated extracted entities. It shows secure upload state and clearly indicates that extracted entities will appear only when a real parser returns them. Skill cards retain source-aware labels such as `Self-reported`; later assessed, resume-extracted, project-evidence, and TPO-verified sources remain distinct.


## Phase 1.5 stabilization

The stabilization pass fixed the onboarding runtime path without changing the completed authentication, RBAC, RLS, dashboard, or Phase 2 architecture. Student profile, onboarding draft, and resume APIs now require an Authorization header; in local tests, `Bearer demo-token` is accepted only as an explicit development token. The real frontend onboarding no longer invents or silently falls back to that token. Missing sessions show a sign-in state instead of silently using demo data.

FastAPI CORS explicitly allows `http://localhost:3000`, authenticated requests, `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, and `OPTIONS`. The reported browser CORS message was secondary to failed authentication/server requests; direct verification now returns `401` for unauthenticated profile access and `2xx` for explicit authenticated development requests, with correct preflight headers.

Resume uploads now require an authenticated student, non-empty valid PDF bytes beginning with the PDF signature, and a maximum size of 5 MB. Production uploads use the private Supabase Storage bucket `resumes` at a unique path `{authenticated_user_id}/{uuid}.pdf`, then persist storage path, original filename, content type, file size, and timestamp metadata in `public.resumes`. The service-role key remains backend-only. Storage policies scope object access to the authenticated user folder, and no public URL is returned.

Hydration investigation found no OMEN onboarding-level `AudioContext`, random ID, browser-only render branch, or remaining onboarding date expression after stabilization. Production and development browser loads showed no hydration or AudioContext console errors. The only remaining date formatting is in the isolated `/demo` application-history view after data is loaded; it does not participate in onboarding render hydration.


## Phase 3 student career operating system

Phase 3 adds a student command-center aggregation endpoint at `GET /api/v1/students/me/dashboard`. It returns the current profile summary, profile completeness, market-derived score and contributors, Career DNA summary, prioritized skill gaps, next-best action, learning recommendations, opportunities, application summary, and notifications in one request. The frontend uses this aggregation to avoid a long sequential dashboard waterfall.

The student workspace navigation now includes Overview, Career DNA, Market, Learn, Skill Gaps, Projects, Placements, Applications, and Profile. Compatibility routes such as `/student/career-dna`, `/student/market-score`, `/student/careers`, and `/student/learning` remain available. Polls are not a primary navigation module; institutional actions belong in notifications.

Supabase Auth remains the only authentication system. Login supports Google OAuth and email/password through `signInWithPassword`; signup at `/signup` uses `signUp` with Supabase Auth and supports confirmation-required responses. No custom password table or password hashing was introduced.

Phase 3 APIs include:

```text
GET  /api/v1/students/me/dashboard
GET  /api/v1/students/me/notifications
POST /api/v1/students/me/notifications/{id}/read
GET  /api/v1/students/me/recommendations
GET  /api/v1/students/me/learning/recommendations
GET  /api/v1/students/me/opportunities
GET  /api/v1/students/me/opportunities/{id}/match
GET  /api/v1/students/me/applications
GET  /api/v1/students/me/applications/{id}/intelligence
POST /api/v1/students/me/polls/{poll_id}/responses
```

Market Employability remains the existing deterministic market-demand heuristic. The dashboard calls its output a market-derived readiness signal, not a hiring probability. Opportunity matching uses transparent role/skill alignment and eligibility rules. Application intelligence never fabricates employer rejection reasons; when none exists it explicitly says the company reason was not provided and labels improvement areas as OMEN inference.

Application-time historical fields are supported by the new `application_intelligence_snapshots` table. The existing application, notification, project, course, assessment, and skill entities are reused rather than duplicated.

### Isolated ML development pipeline

The `ml/` package is independent from web startup and production database writes. It uses `data/synthetic/students.csv`, explicitly labeled **SYNTHETIC — DEVELOPMENT ONLY**, and writes small artifacts to `ml/artifacts/`. The current development-only artifact is a deterministic weighted market-readiness baseline with a reproducible seed and MAE evaluation on a held-out split. It is not used as a production placement probability and is not presented in the student UI.

Run the independent training command with:

```bash
PYTHONPATH=. python -m ml.training.train_all
```

The generated registry metadata records model name, version, dataset, feature version, metrics, synthetic flag, and weights. Synthetic metrics are labeled `synthetic_development_evaluation`. No model trains during API startup or request handling.


## Phase 4 course catalog and development stabilization

The learning catalog now contains **15 connected implementation courses** in both the Supabase migration and local demo fallback. Each course includes a difficulty, estimated effort, a three-phase implementation plan, a concrete build outcome, and a free authoritative source. The catalog reuses the existing Phase 2 `courses`, `course_phases`, and `learning_resources` entities; it does not create a competing course system.

The free-source catalog includes Python, HTML/CSS, JavaScript, React, Git, SQL, FastAPI, REST/HTTP, Docker, data structures, statistics, machine learning, cloud fundamentals, Python testing, and system design/interviews. Sources include [freeCodeCamp](https://www.freecodecamp.org/), [MDN Learn](https://developer.mozilla.org/en-US/docs/Learn), [React Learn](https://react.dev/learn), [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/), [Docker Get Started](https://docs.docker.com/get-started/), [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course), [Khan Academy Statistics](https://www.khanacademy.org/math/statistics-probability), [AWS Digital Training](https://aws.amazon.com/training/digital/), and [pytest documentation](https://docs.pytest.org/en/stable/getting-started.html). Source claims are intentionally limited to publicly accessible learning material; OMEN does not copy or redistribute third-party course content.

### Development error fix

The recurring blank dashboard and `globalError` were reproduced in Next.js development logs. The actual failure was the Next.js 15.5 development Segment Explorer attempting to load a missing React Client Manifest module:

```text
Could not find the module ... next-devtools/userspace/app/segment-explorer-node.js#SegmentViewNode in the React Client Manifest
```

This was a framework development-tool crash, not an OMEN student-data exception. `frontend/next.config.mjs` now disables `devIndicators`, which removes the broken devtools path while retaining normal compile/runtime error reporting. The root layout also uses `suppressHydrationWarning` on the framework-owned HTML/body boundaries. Production builds remain unaffected. Manual development verification now renders the expected authentication gate without the blank page or hydration/devtools error.

### Resume upload UX

Onboarding resume upload now has explicit state feedback: `Uploading securely…`, selected filename, animated progress, `Resume uploaded successfully`, private-storage confirmation, and visible error messages. The frontend accepts the production `storage_path` response as well as the local demo `path`, fixing the prior case where a successful upload was stored but not shown in the profile form.
