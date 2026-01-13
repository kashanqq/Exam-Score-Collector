from pydantic import BaseModel, Field, field_validator, ConfigDict

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
    score: int = Field(..., ge=0, le=100)

class ScoreResponse(ScoreBase):
    model_config = ConfigDict(from_attributes=True) 

class StudentResponse(StudentBase):
    telegram_id: int
    scores: list[ScoreResponse] = []
    model_config = ConfigDict(from_attributes=True)