from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(StrEnum):
    STUDENT = 'student'
    TPO = 'tpo'
    ADMIN = 'admin'


class ApplicationStatus(StrEnum):
    APPLIED = 'applied'
    ELIGIBLE = 'eligible'
    INELIGIBLE = 'ineligible'
    SHORTLISTED = 'shortlisted'
    INTERVIEWED = 'interviewed'
    SELECTED = 'selected'
    REJECTED = 'rejected'


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(TimestampMixin, Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.STUDENT.value)
    student_profile: Mapped['StudentProfile | None'] = relationship(back_populates='user', uselist=False)


class StudentProfile(TimestampMixin, Base):
    __tablename__ = 'student_profiles'

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    student_id: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(150))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    cgpa: Mapped[float | None] = mapped_column(Float)
    backlogs: Mapped[int] = mapped_column(Integer, default=0)
    user: Mapped[User] = relationship(back_populates='student_profile')
    skills: Mapped[list['StudentSkill']] = relationship(back_populates='student', cascade='all, delete-orphan')
    applications: Mapped[list['Application']] = relationship(back_populates='student')


class Skill(Base):
    __tablename__ = 'skills'

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    student_skills: Mapped[list['StudentSkill']] = relationship(back_populates='skill')
    jobs: Mapped[list['JobSkill']] = relationship(back_populates='skill')


class StudentSkill(Base):
    __tablename__ = 'student_skills'
    __table_args__ = (UniqueConstraint('student_id', 'skill_id'),)

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    skill_id: Mapped[UUID] = mapped_column(ForeignKey('skills.id', ondelete='CASCADE'))
    proficiency: Mapped[float] = mapped_column(Float, default=0)
    verified: Mapped[bool] = mapped_column(default=False)
    student: Mapped[StudentProfile] = relationship(back_populates='skills')
    skill: Mapped[Skill] = relationship(back_populates='student_skills')


class Company(Base):
    __tablename__ = 'companies'

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(500))
    jobs: Mapped[list['Job']] = relationship(back_populates='company')


class Job(TimestampMixin, Base):
    __tablename__ = 'jobs'

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('companies.id'))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(150))
    minimum_cgpa: Mapped[float] = mapped_column(Float, default=0)
    maximum_backlogs: Mapped[int] = mapped_column(Integer, default=0)
    allowed_departments: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    company: Mapped[Company] = relationship(back_populates='jobs')
    skills: Mapped[list['JobSkill']] = relationship(back_populates='job', cascade='all, delete-orphan')
    applications: Mapped[list['Application']] = relationship(back_populates='job')


class JobSkill(Base):
    __tablename__ = 'job_skills'
    __table_args__ = (UniqueConstraint('job_id', 'skill_id'),)

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(ForeignKey('jobs.id', ondelete='CASCADE'))
    skill_id: Mapped[UUID] = mapped_column(ForeignKey('skills.id', ondelete='CASCADE'))
    required_level: Mapped[float] = mapped_column(Float, default=0)
    job: Mapped[Job] = relationship(back_populates='skills')
    skill: Mapped[Skill] = relationship(back_populates='jobs')


class Application(TimestampMixin, Base):
    __tablename__ = 'applications'
    __table_args__ = (UniqueConstraint('student_id', 'job_id'),)

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    job_id: Mapped[UUID] = mapped_column(ForeignKey('jobs.id', ondelete='CASCADE'))
    status: Mapped[str] = mapped_column(String(20), default=ApplicationStatus.APPLIED.value)
    student: Mapped[StudentProfile] = relationship(back_populates='applications')
    job: Mapped[Job] = relationship(back_populates='applications')