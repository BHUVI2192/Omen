drop policy if exists attempts_own on public.student_assessment_attempts;
create policy attempts_read_own on public.student_assessment_attempts for select to authenticated using (student_id in (select id from public.student_profiles where user_id=auth.uid()) or public.is_tpo());
create policy attempts_insert_own on public.student_assessment_attempts for insert to authenticated with check (student_id in (select id from public.student_profiles where user_id=auth.uid()));
create policy attempts_tpo_manage on public.student_assessment_attempts for update to authenticated using (public.is_tpo()) with check (public.is_tpo());
create or replace function public.prevent_student_project_verification_change() returns trigger language plpgsql security definer set search_path=public as $$ begin if not public.is_tpo() and (new.status <> old.status or new.feedback is distinct from old.feedback or new.verification_status <> old.verification_status or new.verified_by is distinct from old.verified_by or new.verified_at is distinct from old.verified_at) then raise exception 'Only TPO/admin can change project review fields'; end if; return new; end; $$;
drop trigger if exists protect_project_review_fields on public.projects;
create trigger protect_project_review_fields before update on public.projects for each row execute function public.prevent_student_project_verification_change();
