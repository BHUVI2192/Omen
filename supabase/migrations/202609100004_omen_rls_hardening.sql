-- OMEN Database Security & Row Level Security (RLS) Hardening
-- Enforces student isolation, TPO/Admin governance, and catalog read/write boundaries.

-- ============================================================================
-- 1. SUPPLEMENT CORE TABLES (from migration 202609100001)
-- ============================================================================

-- profiles: allow authenticated users to insert/update their own profile
create policy "profiles_self_insert"
on public.profiles for insert
to authenticated
with check (id = auth.uid());

create policy "profiles_self_update"
on public.profiles for update
to authenticated
using (id = auth.uid())
with check (id = auth.uid());

create policy "profiles_tpo_update"
on public.profiles for update
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- student_profiles: allow TPO to update student profiles
create policy "student_profiles_tpo_update"
on public.student_profiles for update
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- student_skills: allow TPO full access to read and verify skills
create policy "student_skills_tpo_all"
on public.student_skills for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- ============================================================================
-- 2. HARDEN UNPROTECTED CORE WORKFLOW TABLES
-- ============================================================================

-- application_status_history
alter table public.application_status_history enable row level security;

create policy "status_history_student_select"
on public.application_status_history for select
to authenticated
using (
  application_id in (
    select a.id from public.applications a
    join public.student_profiles sp on sp.id = a.student_id
    where sp.user_id = auth.uid()
  )
);

create policy "status_history_tpo_all"
on public.application_status_history for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- student_course_progress
alter table public.student_course_progress enable row level security;

create policy "course_progress_student_all"
on public.student_course_progress for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "course_progress_tpo_select"
on public.student_course_progress for select
to authenticated
using (public.is_tpo());

-- student_assessment_attempts
alter table public.student_assessment_attempts enable row level security;

create policy "assessment_attempts_student_all"
on public.student_assessment_attempts for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "assessment_attempts_tpo_select"
on public.student_assessment_attempts for select
to authenticated
using (public.is_tpo());

-- skill_verifications
alter table public.skill_verifications enable row level security;

create policy "skill_verifications_student_select"
on public.skill_verifications for select
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "skill_verifications_tpo_all"
on public.skill_verifications for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- poll_responses
alter table public.poll_responses enable row level security;

create policy "poll_responses_student_all"
on public.poll_responses for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "poll_responses_tpo_select"
on public.poll_responses for select
to authenticated
using (public.is_tpo());

-- ============================================================================
-- 3. HARDEN PROFILE OUTCOMES TABLES (from migration 202609100003)
-- ============================================================================

-- resumes
alter table public.resumes enable row level security;

create policy "resumes_student_all"
on public.resumes for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "resumes_tpo_select"
on public.resumes for select
to authenticated
using (public.is_tpo());

-- certifications
alter table public.certifications enable row level security;

create policy "certifications_student_all"
on public.certifications for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "certifications_tpo_select"
on public.certifications for select
to authenticated
using (public.is_tpo());

-- experiences
alter table public.experiences enable row level security;

create policy "experiences_student_all"
on public.experiences for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "experiences_tpo_select"
on public.experiences for select
to authenticated
using (public.is_tpo());

-- career_role_matches
alter table public.career_role_matches enable row level security;

create policy "role_matches_student_select"
on public.career_role_matches for select
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "role_matches_tpo_all"
on public.career_role_matches for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- student_skill_gaps
alter table public.student_skill_gaps enable row level security;

create policy "skill_gaps_student_select"
on public.student_skill_gaps for select
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "skill_gaps_tpo_all"
on public.student_skill_gaps for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- student_job_matches
alter table public.student_job_matches enable row level security;

create policy "job_matches_student_select"
on public.student_job_matches for select
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "job_matches_tpo_all"
on public.student_job_matches for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- placement_results
alter table public.placement_results enable row level security;

create policy "placement_results_student_select"
on public.placement_results for select
to authenticated
using (
  application_id in (
    select a.id from public.applications a
    join public.student_profiles sp on sp.id = a.student_id
    where sp.user_id = auth.uid()
  )
);

create policy "placement_results_tpo_all"
on public.placement_results for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- bootcamp_enrollments
alter table public.bootcamp_enrollments enable row level security;

create policy "bootcamp_enrollments_student_all"
on public.bootcamp_enrollments for all
to authenticated
using (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
)
with check (
  student_id in (
    select id from public.student_profiles where user_id = auth.uid()
  )
);

create policy "bootcamp_enrollments_tpo_all"
on public.bootcamp_enrollments for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- institutional_metrics
alter table public.institutional_metrics enable row level security;

create policy "metrics_auth_select"
on public.institutional_metrics for select
to authenticated
using (true);

create policy "metrics_tpo_all"
on public.institutional_metrics for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- skill_gap_snapshots
alter table public.skill_gap_snapshots enable row level security;

create policy "snapshots_auth_select"
on public.skill_gap_snapshots for select
to authenticated
using (true);

create policy "snapshots_tpo_all"
on public.skill_gap_snapshots for all
to authenticated
using (public.is_tpo())
with check (public.is_tpo());

-- ============================================================================
-- 4. HARDEN CATALOG & REFERENCE TABLES
-- (Authenticated read access, TPO/Admin write access)
-- ============================================================================

-- skills
alter table public.skills enable row level security;
create policy "skills_auth_select" on public.skills for select to authenticated using (true);
create policy "skills_tpo_all" on public.skills for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- roles
alter table public.roles enable row level security;
create policy "roles_auth_select" on public.roles for select to authenticated using (true);
create policy "roles_tpo_all" on public.roles for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- role_skills
alter table public.role_skills enable row level security;
create policy "role_skills_auth_select" on public.role_skills for select to authenticated using (true);
create policy "role_skills_tpo_all" on public.role_skills for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- companies
alter table public.companies enable row level security;
create policy "companies_auth_select" on public.companies for select to authenticated using (true);
create policy "companies_tpo_all" on public.companies for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- jobs
alter table public.jobs enable row level security;
create policy "jobs_auth_select" on public.jobs for select to authenticated using (true);
create policy "jobs_tpo_all" on public.jobs for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- job_requirements
alter table public.job_requirements enable row level security;
create policy "job_requirements_auth_select" on public.job_requirements for select to authenticated using (true);
create policy "job_requirements_tpo_all" on public.job_requirements for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- courses
alter table public.courses enable row level security;
create policy "courses_auth_select" on public.courses for select to authenticated using (true);
create policy "courses_tpo_all" on public.courses for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- course_phases
alter table public.course_phases enable row level security;
create policy "course_phases_auth_select" on public.course_phases for select to authenticated using (true);
create policy "course_phases_tpo_all" on public.course_phases for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- learning_resources
alter table public.learning_resources enable row level security;
create policy "learning_resources_auth_select" on public.learning_resources for select to authenticated using (true);
create policy "learning_resources_tpo_all" on public.learning_resources for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- assessments
alter table public.assessments enable row level security;
create policy "assessments_auth_select" on public.assessments for select to authenticated using (true);
create policy "assessments_tpo_all" on public.assessments for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- assessment_questions
alter table public.assessment_questions enable row level security;
create policy "assessment_questions_auth_select" on public.assessment_questions for select to authenticated using (true);
create policy "assessment_questions_tpo_all" on public.assessment_questions for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- market_snapshots
alter table public.market_snapshots enable row level security;
create policy "market_snapshots_auth_select" on public.market_snapshots for select to authenticated using (true);
create policy "market_snapshots_tpo_all" on public.market_snapshots for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- bootcamps
alter table public.bootcamps enable row level security;
create policy "bootcamps_auth_select" on public.bootcamps for select to authenticated using (true);
create policy "bootcamps_tpo_all" on public.bootcamps for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- student_polls
alter table public.student_polls enable row level security;
create policy "student_polls_auth_select" on public.student_polls for select to authenticated using (true);
create policy "student_polls_tpo_all" on public.student_polls for all to authenticated using (public.is_tpo()) with check (public.is_tpo());

-- poll_options
alter table public.poll_options enable row level security;
create policy "poll_options_auth_select" on public.poll_options for select to authenticated using (true);
create policy "poll_options_tpo_all" on public.poll_options for all to authenticated using (public.is_tpo()) with check (public.is_tpo());
