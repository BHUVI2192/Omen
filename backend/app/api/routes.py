from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.intelligence.engine import calculate_score, role_match, eligibility, ROLES, MARKET_SKILLS
from app.core.config import settings
from app.core.supabase import current_user, is_configured, client
from app.core.repository import OmenRepository

router = APIRouter()

DEMO_STUDENT = {'id':'demo-student','name':'Aarav Mehta','student_id':'OMEN-1024','department':'Computer Science','branch':'CSE','semester':7,'cgpa':8.1,'backlogs':0,'skills':{'Python':82,'Git':76,'SQL':43,'React':61,'Statistics':58,'Cloud':34,'Communication':47,'DSA':64,'Excel':55},'experience':{'projects':2,'internships':1},'assessments':{'problem_solving':72,'communication':47}}
JOBS = [{'id':'job-1','company':'Northstar Labs','role':'Data Analyst','ctc':'₹12–16 LPA','location':'Bengaluru · Hybrid','minimum_cgpa':7.0,'allowed_branches':['CSE','IT','ECE'],'max_backlogs':0,'deadline':'2026-10-18','skills':['SQL','Python','Power BI','Statistics'],'description':'Own dashboards and analysis that help product teams make faster decisions.','external_url':'https://example.com/apply/northstar'}]
APPLICATIONS=[]
NOTIFICATIONS=[{'id':'n1','title':'Welcome to OMEN','body':'Your market intelligence workspace is ready. Start with your skill gaps.','type':'system','read':False}]

class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2)
    department: str
    branch: str
    semester: int = Field(ge=1, le=12)
    cgpa: float = Field(ge=0, le=10)
    backlogs: int = Field(ge=0)
    skills: dict[str,float]
    projects: int = Field(ge=0, le=20)
    internships: int = Field(ge=0, le=10)

class ApplicationCreate(BaseModel):
    job_id: str
    apply_anyway: bool = False

class StatusUpdate(BaseModel):
    status: str

@router.get('/health')
def health(): return {'status':'ok','service':'omen-api','timestamp':datetime.now(timezone.utc).isoformat()}

@router.get('/auth/config')
def auth_config():
    return {'supabase_configured': is_configured(), 'demo_mode': not is_configured(), 'google_provider': 'Configure Google in Supabase Auth'}

@router.get('/auth/me')
def auth_me(authorization: str | None = Header(default=None)):
    user = current_user(authorization)
    return {'user': user, 'profile': OmenRepository(user['id']).student_profile() if is_configured() else DEMO_STUDENT}

@router.get('/courses')
def courses():
    if is_configured():
        return {'courses': client().table('courses').select('*,skills(name),course_phases(*)').order('title').execute().data}
    return {'courses': [
        {'id':'course-sql','title':'SQL for Decision Makers','description':'Query thinking, joins, aggregation, and analytical storytelling.','skill':'SQL','estimated_hours':24,'phases':['Foundation','Skill development','Practice','Project','Verification']},
        {'id':'course-python','title':'Python for Analytics','description':'Build a practical analysis workflow from raw data to insight.','skill':'Python','estimated_hours':32,'phases':['Foundation','Data workflows','Practice','Project','Verification']}
    ]}

@router.post('/students/me/courses/{course_id}/progress')
def update_course_progress(course_id: str, progress: float = 0, authorization: str | None = Header(default=None)):
    if not 0 <= progress <= 100: raise HTTPException(422, 'Progress must be between 0 and 100')
    if is_configured():
        user=current_user(authorization); student=client().table('student_profiles').select('id').eq('user_id',user['id']).limit(1).execute()
        course=client().table('courses').select('id').eq('id',course_id).limit(1).execute()
        if not student.data or not course.data: raise HTTPException(404,'Course or student not found')
        row=client().table('student_course_progress').upsert({'student_id':student.data[0]['id'],'course_id':course_id,'progress':progress}).execute().data
        return {'progress': row[0] if row else {'course_id':course_id,'progress':progress}}
    return {'progress': {'course_id':course_id, 'progress':progress, 'mode':'demo'}}

class ProjectSubmission(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(min_length=20)
    github_url: str
    live_demo_url: str | None = None

@router.post('/projects')
def submit_project(payload: ProjectSubmission, authorization: str | None = Header(default=None)):
    if is_configured():
        user=current_user(authorization); student=client().table('student_profiles').select('id').eq('user_id',user['id']).limit(1).execute()
        if not student.data: raise HTTPException(400,'Complete onboarding first')
        row=client().table('projects').insert({**payload.model_dump(),'student_id':student.data[0]['id'],'status':'Submitted'}).execute().data
        return {'project':row[0]}
    return {'project': {'id':'demo-project','status':'Submitted', **payload.model_dump()}}

@router.post('/resumes')
async def upload_resume(file: UploadFile = File(...), authorization: str | None = Header(default=None)):
    if file.content_type != 'application/pdf': raise HTTPException(415,'Only PDF resumes are accepted')
    content=await file.read()
    if len(content)>5*1024*1024: raise HTTPException(413,'Resume must be smaller than 5 MB')
    if is_configured():
        user=current_user(authorization); path=f"{user['id']}/{file.filename}"
        client().storage.from_('resumes').upload(path,content,{'content-type':'application/pdf','upsert':'true'})
        return {'stored':True,'bucket':'resumes','path':path}
    return {'stored':True,'bucket':'resumes','path':f'demo/{file.filename}','mode':'demo'}

@router.get('/tpo/polls')
def polls():
    if is_configured(): return {'polls':client().table('student_polls').select('*,poll_options(*)').eq('active',True).execute().data}
    return {'polls':[{'id':'poll-1','question':'What skill would you like to learn next?','options':['AI/ML','Graphic Design','UI/UX','Cloud','Cybersecurity'],'responses':128}]}

@router.post('/tpo/bootcamps')
def create_bootcamp(title: str, target_skill: str, source: str = 'outcome-driven', authorization: str | None = Header(default=None)):
    if not title.strip() or not target_skill.strip(): raise HTTPException(422,'Title and target skill are required')
    if is_configured():
        user=current_user(authorization); skill=client().table('skills').select('id').eq('name',target_skill).limit(1).execute()
        row=client().table('bootcamps').insert({'title':title,'target_skill_id':skill.data[0]['id'] if skill.data else None,'source':source,'created_by':user['id']}).execute().data
        return {'bootcamp':row[0]}
    return {'bootcamp':{'id':'demo-bootcamp','title':title,'target_skill':target_skill,'source':source,'notifications_created':True}}

@router.get('/me')
def me(): return {'user':DEMO_STUDENT,'role':'student','demo_mode':True}

@router.get('/students/me/intelligence')
def intelligence():
    result=calculate_score(DEMO_STUDENT['skills'],DEMO_STUDENT['experience'],DEMO_STUDENT['assessments'])
    return {'score':result.score,'components':result.components,'positives':result.positives,'negatives':result.negatives,'gaps':result.gaps,'methodology':'Market-derived heuristic using normalized development-only demand snapshot; not a hiring probability.'}

@router.put('/students/me/profile')
def update_profile(payload: ProfileUpdate, authorization: str | None = Header(default=None)):
    DEMO_STUDENT.update(payload.model_dump(exclude={'projects','internships'})); DEMO_STUDENT['experience']={'projects':payload.projects,'internships':payload.internships}
    if is_configured():
        user=current_user(authorization)
        saved=OmenRepository(user['id']).save_student_profile({
            'full_name':payload.name,'department':payload.department,'branch':payload.branch,
            'semester':payload.semester,'cgpa':payload.cgpa,'backlogs':payload.backlogs,
        }, payload.skills)
        return {'ok':True,'profile':saved,'mode':'supabase'}
    return {'ok':True,'profile':DEMO_STUDENT,'mode':'demo'}

@router.get('/careers')
def careers(): return {'roles':[role_match(name,DEMO_STUDENT['skills']) | {'market_skills':req['skills']} for name,req in ROLES.items()]}

@router.get('/careers/{role}/what-if')
def what_if(role:str, skill:str, target:float):
    if role not in ROLES: raise HTTPException(404,'Unknown role')
    current=calculate_score(DEMO_STUDENT['skills'],DEMO_STUDENT['experience'],DEMO_STUDENT['assessments']).score
    simulated={**DEMO_STUDENT['skills'],skill:target}; projected=calculate_score(simulated,DEMO_STUDENT['experience'],DEMO_STUDENT['assessments']).score
    return {'label':'Projected impact','current_score':current,'projected_score':projected,'role_match':role_match(role,simulated),'disclaimer':'This is a scenario, not a guaranteed outcome.'}

@router.get('/market')
def market(): return {'source':'Development fallback snapshot','skills':[{'name':k,'demand':round(v*100),'trend':'rising' if v>.7 else 'steady'} for k,v in MARKET_SKILLS.items()]}

@router.get('/jobs')
def jobs():
    result=[]
    for job in JOBS:
        elig=eligibility(DEMO_STUDENT,job); match=role_match(job['role'],DEMO_STUDENT['skills'])
        result.append({**job,'eligibility':elig,'match':match['match'],'missing_skills':[s for s in job['skills'] if DEMO_STUDENT['skills'].get(s,0)<65]})
    return {'jobs':result}

@router.post('/applications')
def apply(payload: ApplicationCreate):
    job=next((j for j in JOBS if j['id']==payload.job_id),None)
    if not job: raise HTTPException(404,'Opportunity not found')
    elig=eligibility(DEMO_STUDENT,job)
    if not elig['eligible']: raise HTTPException(400,{'message':'Hard eligibility rules must be satisfied','reasons':elig['reasons']})
    if any(a['job_id']==payload.job_id for a in APPLICATIONS): return {'application':next(a for a in APPLICATIONS if a['job_id']==payload.job_id)}
    app={'id':f'app-{len(APPLICATIONS)+1}','job_id':job['id'],'company':job['company'],'role':job['role'],'status':'Applied','applied_at':datetime.now(timezone.utc).isoformat(),'status_history':[{'status':'Applied','at':datetime.now(timezone.utc).isoformat()}]}; APPLICATIONS.append(app); NOTIFICATIONS.insert(0,{'id':f'n{len(NOTIFICATIONS)+1}','title':'Application recorded','body':f"Your application for {job['role']} at {job['company']} is Applied.",'type':'application','read':False}); return {'application':app,'redirect_url':job['external_url']}

@router.get('/applications')
def applications(): return {'applications':APPLICATIONS}

@router.get('/notifications')
def notifications(): return {'notifications':NOTIFICATIONS}

@router.get('/tpo/overview')
def tpo_overview():
    result=calculate_score(DEMO_STUDENT['skills'],DEMO_STUDENT['experience'],DEMO_STUDENT['assessments'])
    return {'total_students':128,'average_market_employability':74,'students_needing_intervention':23,'top_skill_deficits':[{'skill':'Power BI','coverage':39},{'skill':'Cloud','coverage':44},{'skill':'Communication','coverage':48}], 'role_demand':[{'role':'Data Analyst','demand':84},{'role':'Software Engineer','demand':78},{'role':'AI/ML Engineer','demand':61}], 'applications':len(APPLICATIONS),'demo_student_score':result.score}

@router.post('/tpo/applications/{application_id}/status')
def update_status(application_id:str,payload:StatusUpdate):
    valid={'Under Review','Shortlisted','Interview','Selected','Not Shortlisted','Rejected'}
    if payload.status not in valid: raise HTTPException(400,'Invalid state transition')
    app=next((a for a in APPLICATIONS if a['id']==application_id),None)
    if not app: raise HTTPException(404,'Application not found')
    app['status']=payload.status; app['status_history'].append({'status':payload.status,'at':datetime.now(timezone.utc).isoformat()}); NOTIFICATIONS.insert(0,{'id':f'n{len(NOTIFICATIONS)+1}','title':f'Application status: {payload.status}','body':f"Your {app['role']} application has moved to {payload.status}.",'type':'status','read':False}); return {'application':app}

@router.post('/tpo/results/preview')
async def preview_results(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'): raise HTTPException(400,'Upload a CSV file')
    raw=(await file.read()).decode('utf-8-sig'); lines=[l.strip() for l in raw.splitlines() if l.strip()]
    if not lines or lines[0].lower()!='student_id,status': raise HTTPException(400,'CSV header must be student_id,status')
    rows=[]; errors=[]
    for i,line in enumerate(lines[1:],2):
        parts=[p.strip() for p in line.split(',')]
        if len(parts)!=2 or parts[1] not in {'Selected','Rejected'}: errors.append(f'Row {i}: invalid format or status')
        else: rows.append({'student_id':parts[0],'status':parts[1]})
    return {'rows':rows,'errors':errors,'requires_confirmation':bool(rows) and not errors}
