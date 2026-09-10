from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    student_id: str = Field(min_length=2, max_length=50)
    department: str = Field(min_length=2, max_length=150)
    graduation_year: int = Field(ge=2000, le=2100)
    cgpa: float = Field(ge=0, le=10)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)