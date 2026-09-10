from __future__ import annotations
from datetime import datetime, timezone
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
    def save_student_profile(self, profile: dict[str, Any], skills: dict[str,float]) -> dict[str, Any]:
        if not is_configured(): return profile
        db=client(); db.table('profiles').upsert({'id':self.user_id,'full_name':profile.get('full_name'),'department':profile.get('department')}).execute()
        student={k:profile[k] for k in ('student_id','branch','semester','graduation_year','cgpa','backlogs','tenth_percentage','twelfth_percentage','career_intent','projects_count','internships_count','hackathons_count','open_source_count','freelance_count','readiness_signals') if k in profile}; student.update({'user_id':self.user_id,'onboarding_complete':True})
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
    def save_course_progress(self, course_id: str, progress: float) -> dict:
        sid=self._student_id(); rows=client().table('student_course_progress').upsert({'student_id':sid,'course_id':course_id,'progress':progress}).execute().data; return rows[0] if rows else {'course_id':course_id,'progress':progress}
    def submit_project(self, payload: dict) -> dict:
        sid=self._student_id(); rows=client().table('projects').insert({**payload,'student_id':sid,'status':'Submitted'}).execute().data; return rows[0]
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
