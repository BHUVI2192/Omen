from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.local_auth import hash_password, verify_password
from app.intelligence.engine import calculate_score, role_match, ROLES
from app.models.core import Skill, StudentProfile, StudentSkill, User
from app.schemas.auth import RegisterRequest
from app.schemas.student import StudentProfileUpdate


def _profile_payload(student: StudentProfile) -> dict:
    skills = {item.skill.name: item.proficiency for item in student.skills}
    experience = {'projects': 0, 'internships': 0}
    readiness = calculate_score(skills, experience, {'problem_solving': 55, 'communication': 55})
    target_role = 'Software Engineer'
    match = role_match(target_role, skills)
    gaps = []
    for skill, required in ROLES[target_role]['skills'].items():
        current = round(skills.get(skill, 0))
        required_score = round(required * 100)
        if current < required_score:
            gaps.append({'skill': skill, 'current': current, 'required': required_score, 'gap': required_score - current, 'severity': 'high' if required_score - current >= 40 else 'medium'})
    completeness = round(sum(bool(value) for value in [student.name, student.department, student.graduation_year, student.cgpa, skills]) / 6 * 100)
    return {
        'profile': {'id': str(student.id), 'name': student.name, 'email': student.user.email, 'student_id': student.student_id, 'department': student.department, 'graduation_year': student.graduation_year, 'cgpa': student.cgpa, 'backlogs': student.backlogs, 'completeness': completeness},
        'skills': skills,
        'readiness': {'score': readiness.score, 'components': readiness.components, 'positives': readiness.positives, 'gaps': readiness.gaps, 'methodology': 'Deterministic market-derived readiness signal; not a hiring probability.'},
        'career': {'target_role': target_role, 'match': match['match'], 'matched_skills': match['matched_skills'], 'missing_skills': match['missing_skills']},
        'skill_gaps': sorted(gaps, key=lambda gap: gap['gap'], reverse=True),
    }


def register(db: Session, payload: RegisterRequest) -> User:
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(409, 'Email is already registered')
    if db.scalar(select(StudentProfile).where(StudentProfile.student_id == payload.student_id)):
        raise HTTPException(409, 'Student ID is already registered')
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    student = StudentProfile(user=user, student_id=payload.student_id, name=payload.name, department=payload.department, graduation_year=payload.graduation_year, cgpa=payload.cgpa)
    db.add_all([user, student])
    db.commit()
    return db.scalar(select(User).options(selectinload(User.student_profile)).where(User.id == user.id))


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()).options(selectinload(User.student_profile)))
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(401, 'Invalid email or password')
    return user


def get_student(db: Session, user_id: str) -> StudentProfile:
    student = db.scalar(select(StudentProfile).options(selectinload(StudentProfile.user), selectinload(StudentProfile.skills).selectinload(StudentSkill.skill)).where(StudentProfile.user_id == UUID(user_id)))
    if not student:
        raise HTTPException(404, 'Student profile not found')
    return student


def update_profile(db: Session, user_id: str, payload: StudentProfileUpdate) -> dict:
    student = get_student(db, user_id)
    student.name = payload.name
    student.department = payload.department
    student.graduation_year = payload.graduation_year
    student.cgpa = payload.cgpa
    student.backlogs = payload.backlogs
    existing = {item.skill.name: item for item in student.skills}
    for name, proficiency in payload.skills.items():
        item = existing.get(name)
        if item:
            item.proficiency = proficiency
        else:
            skill = db.scalar(select(Skill).where(Skill.name == name)) or Skill(name=name)
            db.add(skill)
            db.flush()
            db.add(StudentSkill(student=student, skill=skill, proficiency=proficiency))
    db.commit()
    return _profile_payload(get_student(db, user_id))


def dashboard(db: Session, user_id: str) -> dict:
    return _profile_payload(get_student(db, user_id))