alter table public.resumes add column if not exists content_type text not null default 'application/pdf';
alter table public.resumes add column if not exists file_size bigint not null default 0;
