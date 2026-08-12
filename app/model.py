from pydantic import BaseModel, Field
from typing import Optional, List


# ─────────────────────────────────────────────
# Shared Base
# ─────────────────────────────────────────────
class StudentBase(BaseModel):
    age: int
    gender: str
    attendance_rate: float
    study_hours_per_week: float
    previous_gpa: float
    extracurricular_score: int
    family_income: str


# ─────────────────────────────────────────────
# Student Schemas
# ─────────────────────────────────────────────
class StudentCreate(StudentBase):
    age: int = Field(..., ge=10, le=100, example=20)
    gender: str = Field(..., example="Male")
    attendance_rate: float = Field(..., ge=0.0, le=100.0, example=85.5)
    study_hours_per_week: float = Field(..., ge=0.0, example=12.0)
    previous_gpa: float = Field(..., ge=0.0, le=4.0, example=3.2)
    extracurricular_score: int = Field(..., ge=0, le=5, example=3)
    family_income: str = Field(..., example="Medium")


class StudentUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=10, le=100)
    gender: Optional[str] = None
    attendance_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    study_hours_per_week: Optional[float] = Field(None, ge=0.0)
    previous_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    extracurricular_score: Optional[int] = Field(None, ge=0, le=5)
    family_income: Optional[str] = None


class StudentResponse(StudentBase):
    student_id: int
    final_gpa: Optional[float] = None
    pass_fail: Optional[int] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Prediction Schemas
# ─────────────────────────────────────────────
class PredictionInput(BaseModel):
    age: int = Field(..., ge=10, le=100, example=20)
    gender: str = Field(..., example="Male")
    attendance_rate: float = Field(..., ge=0.0, le=100.0, example=85.5)
    study_hours_per_week: float = Field(..., ge=0.0, example=12.0)
    previous_gpa: float = Field(..., ge=0.0, le=4.0, example=3.2)
    extracurricular_score: int = Field(..., ge=0, le=5, example=3)
    family_income: str = Field(..., example="Medium")


class PredictionResponse(BaseModel):
    predicted_gpa: float
    pass_fail: str
    pass_probability: float
    fail_probability: float


# ─────────────────────────────────────────────
# Pagination Schema
# ─────────────────────────────────────────────
class PaginatedStudents(BaseModel):
    total: int
    page: int
    page_size: int
    students: List[StudentResponse]

 