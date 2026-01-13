from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # юзаем BigInteger т.к айдишники в тг бывают огромными
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    # связь с таблицей баллов (чтобы можно было делать student.scores)
    scores: Mapped[list["Score"]] = relationship(back_populates="student", cascade="all, delete-orphan")

class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String(50))
    score: Mapped[int]
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    student: Mapped["Student"] = relationship(back_populates="scores")