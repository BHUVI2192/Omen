from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.intelligence.engine import calculate_score, role_match, eligibility, ROLES, MARKET_SKILLS

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

@router.get('/me')
def me(): return {'user':DEMO_STUDENT,'role':'student','demo_mode':True}

@router.get('/students/me/intelligence')
def intelligence():
    result=calculate_score(DEMO_STUDENT['skills'],DEMO_STUDENT['experience'],DEMO_STUDENT['assessments'])
    return {'score':result.score,'components':result.components,'positives':result.positives,'negatives':result.negatives,'gaps':result.gaps,'methodology':'Market-derived heuristic using normalized development-only demand snapshot; not a hiring probability.'}

@router.put('/students/me/profile')
def update_profile(payload: ProfileUpdate):
    DEMO_STUDENT.update(payload.model_dump(exclude={'projects','internships'})); DEMO_STUDENT['experience']={'projects':payload.projects,'internships':payload.internships}
    return {'ok':True,'profile':DEMO_STUDENT}

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
