-- OMEN Storage Buckets & Access Control Policies
-- Buckets are private by default; access is enforced through storage.objects RLS policies.

-- 1. Create Private Storage Buckets
insert into storage.buckets (id, name, public)
values
  ('resumes', 'resumes', false),
  ('certificates', 'certificates', false),
  ('project-submissions', 'project-submissions', false),
  ('course-resources', 'course-resources', false),
  ('company-documents', 'company-documents', false)
on conflict (id) do update set public = false;

-- 2. Ensure RLS is enabled on storage.objects
alter table storage.objects enable row level security;

-- ============================================================================
-- RESUMES: Student can manage their own files (scoped by user ID); TPO has read access
-- ============================================================================
create policy "storage_resumes_student_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'resumes'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_resumes_student_insert"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'resumes'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_resumes_student_update"
on storage.objects for update
to authenticated
using (
  bucket_id = 'resumes'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'resumes'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_resumes_student_delete"
on storage.objects for delete
to authenticated
using (
  bucket_id = 'resumes'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_resumes_tpo_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'resumes'
  and public.is_tpo()
);

-- ============================================================================
-- CERTIFICATES: Student can manage their own certificates; TPO has read access
-- ============================================================================
create policy "storage_certificates_student_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'certificates'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_certificates_student_insert"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'certificates'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_certificates_student_update"
on storage.objects for update
to authenticated
using (
  bucket_id = 'certificates'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'certificates'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_certificates_student_delete"
on storage.objects for delete
to authenticated
using (
  bucket_id = 'certificates'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_certificates_tpo_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'certificates'
  and public.is_tpo()
);

-- ============================================================================
-- PROJECT SUBMISSIONS: Student manages submissions; TPO has read access
-- ============================================================================
create policy "storage_projects_student_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'project-submissions'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_projects_student_insert"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'project-submissions'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_projects_student_update"
on storage.objects for update
to authenticated
using (
  bucket_id = 'project-submissions'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'project-submissions'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_projects_student_delete"
on storage.objects for delete
to authenticated
using (
  bucket_id = 'project-submissions'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "storage_projects_tpo_select"
on storage.objects for select
to authenticated
using (
  bucket_id = 'project-submissions'
  and public.is_tpo()
);

-- ============================================================================
-- COURSE RESOURCES: Authenticated users can read; TPO can manage
-- ============================================================================
create policy "storage_course_resources_auth_select"
on storage.objects for select
to authenticated
using (bucket_id = 'course-resources');

create policy "storage_course_resources_tpo_all"
on storage.objects for all
to authenticated
using (bucket_id = 'course-resources' and public.is_tpo())
with check (bucket_id = 'course-resources' and public.is_tpo());

-- ============================================================================
-- COMPANY DOCUMENTS: Authenticated users can read; TPO can manage
-- ============================================================================
create policy "storage_company_docs_auth_select"
on storage.objects for select
to authenticated
using (bucket_id = 'company-documents');

create policy "storage_company_docs_tpo_all"
on storage.objects for all
to authenticated
using (bucket_id = 'company-documents' and public.is_tpo())
with check (bucket_id = 'company-documents' and public.is_tpo());
