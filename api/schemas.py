from pydantic import BaseModel, Field, field_validator

class StudentBase(BaseModel):
    first_name: str
    last_name: str

class ScoreBase(BaseModel):
    subject: str
    score: int = Field(..., ge=0, le=100)


class StudentCreate(StudentBase):
    telegram_id: int

class ScoreCreate(ScoreBase):
    telegram_id: int

class ScoreResponse(ScoreBase):
    class Config:
        from_attributes = True 

class StudentResponse(StudentBase):
    telegram_id: int
    scores: list[ScoreResponse] = []

    class Config:
        from_attributes = True