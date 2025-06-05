
from fastapi import FastAPI, HTTPException, status, Depends
import uvicorn
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

# Инициализация FastAPI
app = FastAPI()

# Настройка и создание классов через SQLAlchemy
engine = create_engine("sqlite:///app/db/variant2.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модели данных
class Teacher(Base):
    __tablename__ = "teacher"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    courses = relationship("Course", back_populates="teacher", cascade="all, delete")

class Course(Base):
    __tablename__ = "course"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_count = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"), nullable=False)
    
    teacher = relationship("Teacher", back_populates="courses")

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Pydantic модели для работы с таблицами
class TeacherBase(BaseModel):
    name: str

class TeacherCreate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: int
    
    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    name: str
    student_count: int
    teacher_id: int

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    
    class Config:
        orm_mode = True

# Вспомогательная функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для получения объектов таблицы Teacher
@app.get("/teachers", response_model=List[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return teachers

# Эндпоинт для добавления объекта в Teacher
@app.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = Teacher(name=teacher.name)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

# Эндпоинт для получения объектов таблицы Course по заданному id объекта Teacher
@app.get("/teachers/{teacher_id}/courses", response_model=List[CourseResponse])
def get_teacher_courses(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher.courses

# Эндпоинт для удаления объекта Teacher по заданному id
@app.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db.delete(teacher)
    db.commit()
    return

# Эндпоинт для получения объектов таблицы Course
@app.get("/courses", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses

# Эндпоинт для добавления объектов в Course
@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # Проверяем существование преподавателя
    teacher = db.query(Teacher).filter(Teacher.id == course.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db_course = Course(
        name=course.name,
        student_count=course.student_count,
        teacher_id=course.teacher_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Эндпоинт для удаления объекта Course по заданному id
@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return

# Для инициализации с помощью команды "python main.py"
if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=10000)