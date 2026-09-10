from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
from app.core.supabase import is_configured, client

class OmenRepository:
    def __init__(self, user_id: str): self.user_id = user_id
    def _student_id(self) -> str | None:
        if not is_configured(): return None
        rows=client().table('student_profiles').select('id').eq('user_id',self.user_id).limit(1).execute().data
        return rows[0]['id'] if rows else None
    def role(self) -> str | None:
        if not is_configured(): return 'student' if self.user_id == 'demo-student' else None
        rows=client().table('profiles').select('role').eq('id',self.user_id).limit(1).execute().data
        return rows[0]['role'] if rows else None
    def student_profile(self) -> dict[str, Any] | None:
        if not is_configured(): return None
        p=client().table('profiles').select('*').eq('id',self.user_id).limit(1).execute().data
        if not p: return None
        s=client().table('student_profiles').select('*').eq('user_id',self.user_id).limit(1).execute().data
        skills=client().table('student_skills').select('proficiency,skills(name)').eq('student_id',s[0]['id']).execute().data if s else []
        row={**p[0],**(s[0] if s else {})}; row['skills']={x['skills']['name']:x['proficiency'] for x in skills if x.get('skills')}; return row
    def onboarding_draft(self) -> dict[str, Any] | None:
        if not is_configured(): return None
        rows=client().table('student_profiles').select('onboarding_draft,onboarding_step,profile_completeness,onboarding_complete').eq('user_id',self.user_id).limit(1).execute().data
        return rows[0] if rows else {'onboarding_draft':{},'onboarding_step':1,'profile_completeness':0,'onboarding_complete':False}
    def save_onboarding_draft(self, draft: dict[str, Any], step: int, completeness: float) -> dict[str, Any]:
        if not is_configured(): return {'onboarding_draft':draft,'onboarding_step':step,'profile_completeness':completeness}
        client().table('profiles').upsert({'id':self.user_id}).execute()
        row=client().table('student_profiles').upsert({'user_id':self.user_id,'onboarding_draft':draft,'onboarding_step':step,'profile_completeness':completeness},on_conflict='user_id').execute().data
        return row[0] if row else {'onboarding_draft':draft,'onboarding_step':step,'profile_completeness':completeness}
    def save_resume_metadata(self, original_filename: str, storage_path: str, content_type: str, file_size: int) -> dict[str, Any]:
        sid=self._student_id()
        if not sid: raise ValueError('Complete academic profile before uploading a resume')
        rows=client().table('resumes').insert({'student_id':sid,'storage_path':storage_path,'original_filename':original_filename,'content_type':content_type,'file_size':file_size}).execute().data
        return {'id':rows[0]['id'] if rows else str(uuid4()),'student_id':sid,'bucket':'resumes','storage_path':storage_path,'original_filename':original_filename,'content_type':content_type,'file_size':file_size,'uploaded_at':datetime.now(timezone.utc).isoformat()}
    def save_student_profile(self, profile: dict[str, Any], skills: dict[str,float]) -> dict[str, Any]:
        if not is_configured(): return profile
        db=client(); db.table('profiles').upsert({'id':self.user_id,'full_name':profile.get('full_name'),'department':profile.get('department')}).execute()
        student={k:profile[k] for k in ('student_id','branch','semester','degree','graduation_year','cgpa','backlogs','tenth_percentage','twelfth_percentage','career_intent','career_intents','preferred_industries','work_environment','target_ctc','projects_count','internships_count','hackathons_count','open_source_count','freelance_count','readiness_signals','practice_frequency','onboarding_step','profile_completeness') if k in profile}; student.update({'user_id':self.user_id,'onboarding_complete':True})
        row=db.table('student_profiles').upsert(student,on_conflict='user_id').execute().data[0]
        for name,proficiency in skills.items():
            found=db.table('skills').select('id').eq('name',name).limit(1).execute().data
            if found: db.table('student_skills').upsert({'student_id':row['id'],'skill_id':found[0]['id'],'proficiency':proficiency,'source':'self_reported'}).execute()
        return {**profile,'id':self.user_id}
    def jobs(self):
        if not is_configured(): return None
        return client().table('jobs').select('*,companies(name),roles(name),job_requirements(*)').order('deadline').execute().data
    def job(self, job_id: str):
        if not is_configured(): return None
        rows=client().table('jobs').select('*,companies(name),roles(name),job_requirements(*)').eq('id',job_id).limit(1).execute().data
        return rows[0] if rows else None
    def applications(self):
        if not is_configured(): return None
        sid=self._student_id()
        if not sid: return []
        return client().table('applications').select('*,jobs(title,external_application_url,companies(name),roles(name))').eq('student_id',sid).order('applied_at',desc=True).execute().data
    def create_application(self, job_id: str, match_score: float, eligible: bool) -> dict:
        sid=self._student_id()
        if not sid: raise ValueError('Complete onboarding first')
        db=client(); existing=db.table('applications').select('*').eq('job_id',job_id).eq('student_id',sid).limit(1).execute().data
        if existing: return existing[0]
        row=db.table('applications').insert({'job_id':job_id,'student_id':sid,'match_score':match_score,'eligibility':eligible,'status':'Applied'}).execute().data[0]
        db.table('application_status_history').insert({'application_id':row['id'],'status':'Applied','changed_by':self.user_id}).execute()
        db.table('notifications').insert({'user_id':self.user_id,'title':'Application recorded','body':'Your application has been recorded as Applied.','type':'application'}).execute()
        return row
    def update_application_status(self, application_id: str, status: str) -> dict:
        db=client(); row=db.table('applications').update({'status':status}).eq('id',application_id).execute().data
        if not row: raise ValueError('Application not found')
        db.table('application_status_history').insert({'application_id':application_id,'status':status,'changed_by':self.user_id}).execute()
        student=db.table('applications').select('student_id').eq('id',application_id).limit(1).execute().data
        if student:
            profile=db.table('student_profiles').select('user_id').eq('id',student[0]['student_id']).limit(1).execute().data
            if profile: db.table('notifications').insert({'user_id':profile[0]['user_id'],'title':f'Application status: {status}','body':f'Your application moved to {status}.','type':'status'}).execute()
        return row[0]
    def notifications(self):
        if not is_configured(): return None
        return client().table('notifications').select('*').eq('user_id',self.user_id).order('created_at',desc=True).execute().data
    def courses(self):
        if not is_configured(): return None
        return client().table('courses').select('*,skills(name),course_phases(*)').order('title').execute().data
    def course(self, course_id: str):
        if not is_configured(): return None
        rows=client().table('courses').select('*,skills(name),course_phases(*,learning_resources(*))').eq('id',course_id).limit(1).execute().data
        if not rows: return None
        assessments=client().table('assessments').select('*,assessment_questions(*)').eq('course_id',course_id).execute().data
        rows[0]['assessments']=assessments
        rows[0]['assessment']=assessments[0] if assessments else None
        return rows[0]
    def course_progress(self, course_id: str):
        sid=self._student_id()
        if not sid: return None
        rows=client().table('student_course_progress').select('*').eq('student_id',sid).eq('course_id',course_id).limit(1).execute().data
        return rows[0] if rows else {'student_id':sid,'course_id':course_id,'progress':0}
    def save_course_progress(self, course_id: str, progress: float) -> dict:
        sid=self._student_id(); rows=client().table('student_course_progress').upsert({'student_id':sid,'course_id':course_id,'progress':progress}).execute().data; return rows[0] if rows else {'course_id':course_id,'progress':progress}
    def submit_project(self, payload: dict) -> dict:
        sid=self._student_id(); rows=client().table('projects').insert({**payload,'student_id':sid,'status':'Submitted'}).execute().data; return rows[0]
    def projects(self):
        sid=self._student_id()
        if not sid: return []
        return client().table('projects').select('*,courses(title),profiles:verified_by(full_name)').eq('student_id',sid).order('created_at',desc=True).execute().data
    def project(self, project_id: str):
        rows=client().table('projects').select('*,courses(title),profiles:verified_by(full_name)').eq('id',project_id).limit(1).execute().data
        if not rows: return None
        row=rows[0]
        sid=self._student_id()
        if sid and row.get('student_id') != sid and self.role() not in {'tpo','admin'}: raise PermissionError('Project is not owned by this student')
        return row
    def submit_existing_project(self, project_id: str, payload: dict) -> dict:
        sid=self._student_id(); rows=client().table('projects').update({**payload,'student_id':sid,'status':'Submitted','verification_status':'Under Review','submitted_at':datetime.now(timezone.utc).isoformat()}).eq('id',project_id).eq('student_id',sid).execute().data
        if not rows: raise ValueError('Project not found or not owned by student')
        return rows[0]
    def tpo_projects(self, status: str | None = None):
        query=client().table('projects').select('*,courses(title),student_profiles(student_id,user_id),profiles:verified_by(full_name)').order('submitted_at',desc=True)
        if status: query=query.eq('verification_status',status)
        return query.execute().data
    def review_project(self, project_id: str, verification_status: str, feedback: str | None = None) -> dict:
        if verification_status not in {'Verified','Rework Required'}: raise ValueError('Invalid review state')
        row=client().table('projects').update({'verification_status':verification_status,'status':'Verified' if verification_status=='Verified' else 'Rework Required','feedback':feedback,'verified_by':self.user_id,'verified_at':datetime.now(timezone.utc).isoformat()}).eq('id',project_id).execute().data
        if not row: raise ValueError('Project not found')
        project=row[0]
        if verification_status=='Verified':
            for item in project.get('required_skills') or []:
                skill_id=item.get('skill_id') if isinstance(item,dict) else None
                skill_name=item.get('skill') if isinstance(item,dict) else None
                level=float(item.get('level',70)) if isinstance(item,dict) else 70
                if not skill_id and skill_name:
                    found=client().table('skills').select('id').eq('name',skill_name).limit(1).execute().data
                    skill_id=found[0]['id'] if found else None
                if skill_id:
                    client().table('skill_verifications').upsert({'student_id':project['student_id'],'skill_id':skill_id,'project_id':project_id,'verified_by':self.user_id,'level':level}).execute()
                    existing=client().table('student_skills').select('proficiency').eq('student_id',project['student_id']).eq('skill_id',skill_id).limit(1).execute().data
                    new_level=max(float(existing[0]['proficiency']) if existing else 0,level)
                    client().table('student_skills').upsert({'student_id':project['student_id'],'skill_id':skill_id,'proficiency':new_level,'source':'verified_project','verified':True}).execute()
            student=client().table('student_profiles').select('user_id').eq('id',project['student_id']).limit(1).execute().data
            if student: client().table('notifications').insert({'user_id':student[0]['user_id'],'title':'Project verified','body':'Your project evidence has been verified by TPO.','type':'skill_verification'}).execute()
        return project
    def assessment(self, assessment_id: str):
        rows=client().table('assessments').select('*,assessment_questions(*)').eq('id',assessment_id).limit(1).execute().data
        return rows[0] if rows else None
    def attempts(self, assessment_id: str):
        sid=self._student_id(); return client().table('student_assessment_attempts').select('*').eq('assessment_id',assessment_id).eq('student_id',sid).order('attempt_number').execute().data
    def save_attempt(self, assessment_id: str, payload: dict):
        sid=self._student_id(); previous=self.attempts(assessment_id); payload.update({'student_id':sid,'assessment_id':assessment_id,'attempt_number':len(previous)+1})
        rows=client().table('student_assessment_attempts').insert(payload).execute().data; return rows[0]
    def jobs_for_tpo(self):
        if not is_configured(): return None
        return client().table('jobs').select('*,companies(name),roles(name)').order('created_at',desc=True).execute().data
    def create_bootcamp(self, payload: dict) -> dict:
        rows=client().table('bootcamps').insert({**payload,'created_by':self.user_id}).execute().data; return rows[0]
    def polls(self):
        if not is_configured(): return None
        return client().table('student_polls').select('*,poll_options(*)').eq('active',True).execute().data
    def market_snapshot(self):
        if not is_configured(): return None
        return client().table('market_snapshots').select('*').order('captured_at',desc=True).limit(1).execute().data
    def skills(self):
        if not is_configured(): return None
        return client().table('skills').select('id,name,market_demand,demand_trend').order('name').execute().data
    def roles(self):
        if not is_configured(): return None
        return client().table('roles').select('id,name,description,market_demand,role_skills(*)').order('name').execute().data
