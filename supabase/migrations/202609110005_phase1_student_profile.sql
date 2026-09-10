alter table public.student_profiles add column if not exists graduation_year int;
alter table public.student_profiles add column if not exists projects_count int not null default 0;
alter table public.student_profiles add column if not exists internships_count int not null default 0;
alter table public.student_profiles add column if not exists hackathons_count int not null default 0;
alter table public.student_profiles add column if not exists open_source_count int not null default 0;
alter table public.student_profiles add column if not exists freelance_count int not null default 0;
alter table public.student_profiles add column if not exists readiness_signals jsonb not null default '{}';
