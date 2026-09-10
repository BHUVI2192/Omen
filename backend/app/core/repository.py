from __future__ import annotations
from typing import Any
from app.core.supabase import is_configured, client

class OmenRepository:
    def __init__(self, user_id: str): self.user_id = user_id

    def student_profile(self) -> dict[str, Any] | None:
        if not is_configured(): return None
        p = client().table('profiles').select('*').eq('id', self.user_id).limit(1).execute()
        if not p.data: return None
        s = client().table('student_profiles').select('*').eq('user_id', self.user_id).limit(1).execute()
        skills = client().table('student_skills').select('proficiency,skills(name)').eq('student_id', s.data[0]['id']).execute() if s.data else None
        row = {**p.data[0], **(s.data[0] if s.data else {})}
        row['skills'] = {x['skills']['name']: x['proficiency'] for x in (skills.data if skills else []) if x.get('skills')}
        return row

    def save_student_profile(self, profile: dict[str, Any], skills: dict[str, float]) -> dict[str, Any]:
        if not is_configured(): return profile
        public = {k: profile[k] for k in ('full_name','department') if k in profile}
        client().table('profiles').upsert({'id': self.user_id, **public}).execute()
        student = {k: profile[k] for k in ('student_id','branch','semester','cgpa','backlogs','tenth_percentage','twelfth_percentage','career_intent') if k in profile}
        student['user_id'] = self.user_id; student['onboarding_complete'] = True
        row = client().table('student_profiles').upsert(student, on_conflict='user_id').execute().data[0]
        for name, proficiency in skills.items():
            skill = client().table('skills').select('id').eq('name', name).limit(1).execute()
            if skill.data:
                client().table('student_skills').upsert({'student_id':row['id'],'skill_id':skill.data[0]['id'],'proficiency':proficiency,'source':'self_reported'}).execute()
        return {**profile, 'id': self.user_id}

    def jobs(self):
        if not is_configured(): return None
        return client().table('jobs').select('*,companies(name),roles(name)').order('deadline').execute().data

    def applications(self):
        if not is_configured(): return None
        student = client().table('student_profiles').select('id').eq('user_id', self.user_id).limit(1).execute()
        if not student.data: return []
        return client().table('applications').select('*,jobs(title,external_application_url,companies(name),roles(name))').eq('student_id', student.data[0]['id']).order('applied_at', desc=True).execute().data

    def notifications(self):
        if not is_configured(): return None
        return client().table('notifications').select('*').eq('user_id', self.user_id).order('created_at', desc=True).execute().data
