from pydantic import BaseModel, Field


class StudentProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    department: str = Field(min_length=2, max_length=150)
    graduation_year: int = Field(ge=2000, le=2100)
    cgpa: float = Field(ge=0, le=10)
    backlogs: int = Field(ge=0)
    skills: dict[str, float] = Field(default_factory=dict)


class StudentSkillInput(BaseModel):
    skill: str = Field(min_length=1, max_length=100)
    proficiency: float = Field(ge=0, le=100)