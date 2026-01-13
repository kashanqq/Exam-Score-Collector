from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db, engine, Base
from models import Student, Score
from pydantic import BaseModel
from schemas import StudentCreate, ScoreCreate, ScoreResponse

app = FastAPI()

# Pydantic схемы для валидации
class StudentCreate(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str

class ScoreCreate(BaseModel):
    telegram_id: int
    subject: str
    score: int

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/register/")
async def register_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли уже такой
    result = await db.execute(select(Student).where(Student.telegram_id == student.telegram_id))
    if result.scalars().first():
        return {"msg": "Already registered"}
    
    new_student = Student(telegram_id=student.telegram_id, first_name=student.first_name, last_name=student.last_name)
    db.add(new_student)
    await db.commit()
    return {"msg": "Success"}

@app.post("/scores/", response_model=ScoreResponse)
async def add_score(score_data: ScoreCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Student).where(Student.telegram_id == score_data.telegram_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    query = select(Score).where(
        (Score.student_id == student.id) & 
        (Score.subject == score_data.subject)
    )

    existing_score_result = await db.execute(query)
    existing_score = existing_score_result.scalars().first()

    if existing_score:
        existing_score.score = score_data.score
        final_score = existing_score
    else:
        new_score = Score(
            student_id=student.id, 
            subject=score_data.subject, 
            score=score_data.score
        )
        db.add(new_score)
        final_score = new_score

    await db.commit()
    await db.refresh(final_score)
    return final_score

@app.get("/scores/{telegram_id}")
async def get_scores(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    student = result.scalars().first()
    if not student:
        return []
    
    scores_res = await db.execute(select(Score).where(Score.student_id == student.id))
    return [{"subject": s.subject, "score": s.score} for s in scores_res.scalars().all()]