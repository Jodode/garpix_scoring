from fastapi import FastAPI, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from db_config import SessionLocal, engine
from models import Base, Student, Course, Performance, StudentPerformance, StudentPerformanceRelease
from pydantic import BaseModel
import pandas as pd
import shutil
import random
import re
import joblib

import collections
import numpy as np
# Загрузка модели
loaded_model = joblib.load('final_cbc.pkl')

def custom_accuracy(y_true, y_pred):
    correct = 0
    for true, pred in zip(y_true, y_pred):
        if true == pred:
            correct += 1
    return correct / len(y_true)


app = FastAPI()

templates = Jinja2Templates(directory="templates/")

app.mount("/static", StaticFiles(directory="static/"), name="static")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StudentCreate(BaseModel):
    student_number: str

class CourseCreate(BaseModel):
    course_name: str

class PerformanceCreate(BaseModel):
    student_id: int
    course_id: int
    semester: str
    grade_without_resits: int
    grade_performance: int
    start_year: int
    start_semester_year: int
    semester_number: int

class StudentPerformanceCreate(BaseModel):
    student_id: int
    preparation_level: str
    study_group: str
    specialization: str
    academic_year: str
    semester: str
    course_id: int
    grade_without_resits: int
    grade_performance: int
    start_year: int
    start_semester_year: int
    semester_number: int


class StudentPerformanceReleaseCreate(BaseModel):
    student_id: int
    preparation_level: str
    study_group: str
    specialization: str
    academic_year: str
    semester: str
    course: str
    grade_without_resits: int
    grade_performance: int
    start_year: int
    start_semester_year: int
    semester_number: int


def parse_student_ids(text: str):
    student_ids = re.split(r'[;, \n]+', text)
    
    student_ids = [id for id in student_ids if id]
    return student_ids

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная"})

@app.get("/about")
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": "О проекте"})

@app.get("/database")
def read_database(request: Request):
    return templates.TemplateResponse("database.html", {"request": request, "title": "База данных", "student": None})


@app.post("/students/")
def create_student(student_number: str = Form(...), db: Session = Depends(get_db)):
    db_student = Student(student_number=student_number)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.post("/courses/")
def create_course(course_name: str = Form(...), db: Session = Depends(get_db)):
    db_course = Course(course_name=course_name)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.post("/performance/")
def create_performance(file: UploadFile = File(...), db: Session = Depends(get_db)):
    with open(f"backend/uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename}

@app.post("/students_performance/")
def create_student_performance(student_performance: StudentPerformanceCreate, db: Session = Depends(get_db)):
    db_student_performance = StudentPerformance(**student_performance.dict())
    db.add(db_student_performance)
    db.commit()
    db.refresh(db_student_performance)
    return db_student_performance

@app.get("/students/{student_id}")
def read_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(Student).filter(Student.id == student_id).first()

@app.get("/courses/{course_id}")
def read_course(course_id: int, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.id == course_id).first()

@app.get("/performance/{performance_id}")
def read_performance(performance_id: int, db: Session = Depends(get_db)):
    return db.query(Performance).filter(Performance.id == performance_id).first()

@app.get("/students_performance/{student_performance_id}")
def read_student_performance(student_performance_id: int, db: Session = Depends(get_db)):
    return db.query(StudentPerformance).filter(StudentPerformance.id == student_performance_id).first()

@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    db_student.student_number = student.student_number
    db.commit()
    db.refresh(db_student)
    return db_student

@app.put("/courses/{course_id}")
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    db_course.course_name = course.course_name
    db.commit()
    db.refresh(db_course)
    return db_course

@app.put("/performance/{performance_id}")
def update_performance(performance_id: int, performance: PerformanceCreate, db: Session = Depends(get_db)):
    db_performance = db.query(Performance).filter(Performance.id == performance_id).first()
    for key, value in performance.dict().items():
        setattr(db_performance, key, value)
    db.commit()
    db.refresh(db_performance)
    return db_performance

@app.put("/students_performance/{student_performance_id}")
def update_student_performance(student_performance_id: int, student_performance: StudentPerformanceCreate, db: Session = Depends(get_db)):
    db_student_performance = db.query(StudentPerformance).filter(StudentPerformance.id == student_performance_id).first()
    for key, value in student_performance.dict().items():
        setattr(db_student_performance, key, value)
    db.commit()
    db.refresh(db_student_performance)
    return db_student_performance

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted"}

@app.delete("/performance/{performance_id}")
def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    db_performance = db.query(Performance).filter(Performance.id == performance_id).first()
    db.delete(db_performance)
    db.commit()
    return {"message": "Performance deleted"}

@app.delete("/students_performance/{student_performance_id}")
def delete_student_performance(student_performance_id: int, db: Session = Depends(get_db)):
    db_student_performance = db.query(StudentPerformance).filter(StudentPerformance.id == student_performance_id).first()
    db.delete(db_student_performance)
    db.commit()
    return {"message": "Student performance deleted"}



"""
@app.post("/get_student_performance")
async def get_student_performance(request: Request, student_id: int = Form(...), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        performance = db.query(Performance).filter(Performance.student_id == student_id).all()
        student.performance = performance
        for p in student.performance:
            p.course = db.query(Course).filter(Course.id == p.course_id).first()
    return {"student": {"id": student.id, "performance": [{"course": {"course_name": p.course.course_name}, "grade_performance": p.grade_performance} for p in student.performance]}}
"""

@app.post("/get_student_performance")
async def get_student_performance(request: Request, student_id: int = Form(...), db: Session = Depends(get_db)):
    student = db.query(StudentPerformanceRelease).filter(StudentPerformanceRelease.student_id == student_id).all()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    df = pd.DataFrame([{
        "Номер ЛД": s.student_id,
        "Уровень подготовки": s.preparation_level,
        "Учебная группа": s.study_group,
        "Специальность/направление": s.specialization,
        "Учебный год": s.academic_year,
        "Полугодие": s.semester,
        "Дисциплина": s.course,
        "Оценка (без пересдач)": s.grade_without_resits,
        "Оценка (успеваемость)": s.grade_performance,
        "Год начала обучения": s.start_year,
        "Год начала семестра": s.start_semester_year,
        "Номер семестра": s.semester_number
    } for s in student])
    
    return templates.TemplateResponse("database.html", {"request": request, "title": "База данных", "student": df.to_html(classes="table table-striped table-bordered table-hover text-white", justify="left")})

"""
@app.post("/get_student_performance")
def get_student_performance(request: Request, student_id: int = Form(...), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        performance = db.query(Performance).filter(Performance.student_id == student_id).all()
        student.performance = performance
        for p in student.performance:
            p.course = db.query(Course).filter(Course.id == p.course_id).first()
    return templates.TemplateResponse("database.html", {"request": request, "title": "База данных", "student": student})
"""

#Для теста -------------------------------------------------------------



"""
@app.post("/submit_student_id")
async def submit_student_id(request: Request, student_id: str = Form(...)):
    student_ids = parse_student_ids(student_id)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids})
"""
"""
@app.post("/submit_student_id")
async def submit_student_id(request: Request, student_id: str = Form(...), db: Session = Depends(get_db)):
    student_ids = parse_student_ids(student_id)
    predictions = {}
    
    for sid in student_ids:
        student = db.query(StudentPerformanceRelease).filter(StudentPerformanceRelease.student_id == sid).all()
        if not student:
            continue
        
        data = [{
            "Номер ЛД": s.student_id,
            "Уровень подготовки": s.preparation_level,
            "Учебная группа": s.study_group,
            "Специальность/направление": s.specialization,
            "Учебный год": s.academic_year,
            "Полугодие": s.semester,
            "Дисциплина": s.course,
            "Оценка (без пересдач)": s.grade_without_resits,
            "Оценка (успеваемость)": s.grade_performance,
            "Год начала обучения": s.start_year,
            "Год начала семестра": s.start_semester_year,
            "Номер семестра": s.semester_number
        } for s in student]
        
        X_test = pd.DataFrame(data)
        student_predictions = loaded_model.predict(X_test)
        predictions[sid] = student_predictions.tolist()

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Student data not found")

    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids, "predictions": predictions})
"""

@app.post("/submit_student_id")
async def submit_student_id(request: Request, student_id: str = Form(...), db: Session = Depends(get_db)):
    student_ids = parse_student_ids(student_id)
    predictions = {}
    
    for sid in student_ids:
        student = db.query(StudentPerformanceRelease).filter((StudentPerformanceRelease.student_id == sid) & (StudentPerformanceRelease.semester == 'II полугодие') & (StudentPerformanceRelease.academic_year == "2022 - 2023")).all()
        if not student:
            continue
        print(student)
        
        data = []
        subjects = []
        semesters = []
        for s in student:
            data.append({
                "Номер ЛД": s.student_id,
                "Уровень подготовки": s.preparation_level,
                "Учебная группа": s.study_group,
                "Специальность/направление": s.specialization,
                "Учебный год": s.academic_year,
                "Полугодие": s.semester,
                "Дисциплина": s.course,
                # "Оценка (без пересдач)": s.grade_without_resits,
                "Оценка (успеваемость)": s.grade_performance,
                'Институт': s.university,
                "Год начала обучения": s.start_year,
                "Год начала семестра": s.start_semester_year,
                "Номер семестра": s.semester_number,
                'Дисциплина_encoded': s.course_encoded,
                '2': s.two_num,
                '3': s.three_num,
                '4': s.four_num,
                '5': s.five_num,
            })
            subjects.append(s.course)
            semesters.append(s.semester_number)

        X_test = pd.DataFrame(data).drop(columns=['Оценка (успеваемость)',])
        y_true = pd.DataFrame(data)['Оценка (успеваемость)']
        student_predictions = np.array(list(map(lambda x: x[0], loaded_model.predict(X_test))))
        acc_grades = round(custom_accuracy(y_true, student_predictions), 2)

        counter_true = collections.Counter(y_true)
        counter_predict = collections.Counter(student_predictions)

        c_in_true = 0
        c_in_predict = 0

        if 2 in counter_true:
            c_in_true = counter_true[2]
        if 2 in counter_predict:
            c_in_predict = counter_predict[2]
    
        predictions[sid] = [acc_grades, (c_in_true, c_in_predict)] + list(zip(subjects, semesters, student_predictions, y_true))

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Student data not found")


    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids, "predictions": predictions, })



"""
@app.post("/submit_file")
async def submit_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    contents = contents.decode('utf-8')
    student_ids = parse_student_ids(contents)
    predictions = {}

    for sid in student_ids:
        student = db.query(StudentPerformanceRelease).filter(StudentPerformanceRelease.student_id == sid).all()
        if not student:
            continue
        
        data = [{
            "Номер ЛД": s.student_id,
            "Уровень подготовки": s.preparation_level,
            "Учебная группа": s.study_group,
            "Специальность/направление": s.specialization,
            "Учебный год": s.academic_year,
            "Полугодие": s.semester,
            "Дисциплина": s.course,
            "Оценка (без пересдач)": s.grade_without_resits,
            "Оценка (успеваемость)": s.grade_performance,
            "Год начала обучения": s.start_year,
            "Год начала семестра": s.start_semester_year,
            "Номер семестра": s.semester_number
        } for s in student]
        
        X_test = pd.DataFrame(data)
        student_predictions = loaded_model.predict(X_test)
        predictions[sid] = student_predictions.tolist()

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Student data not found")

    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids, "predictions": predictions})

"""

@app.post("/submit_file")
async def submit_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    contents = contents.decode('utf-8')
    student_ids = parse_student_ids(contents)
    predictions = {}

    for sid in student_ids:
        student = db.query(StudentPerformanceRelease).filter((StudentPerformanceRelease.student_id == sid) & (StudentPerformanceRelease.semester == 'II полугодие') & (StudentPerformanceRelease.academic_year == "2022 - 2023")).all()
        if not student:
            continue
        print(student)
        
        data = []
        subjects = []
        semesters = []
        for s in student:
            data.append({
                "Номер ЛД": s.student_id,
                "Уровень подготовки": s.preparation_level,
                "Учебная группа": s.study_group,
                "Специальность/направление": s.specialization,
                "Учебный год": s.academic_year,
                "Полугодие": s.semester,
                "Дисциплина": s.course,
                # "Оценка (без пересдач)": s.grade_without_resits,
                "Оценка (успеваемость)": s.grade_performance,
                'Институт': s.university,
                "Год начала обучения": s.start_year,
                "Год начала семестра": s.start_semester_year,
                "Номер семестра": s.semester_number,
                'Дисциплина_encoded': s.course_encoded,
                '2': s.two_num,
                '3': s.three_num,
                '4': s.four_num,
                '5': s.five_num,
            })
            subjects.append(s.course)
            semesters.append(s.semester_number)

        X_test = pd.DataFrame(data).drop(columns=['Оценка (успеваемость)',])
        y_true = pd.DataFrame(data)['Оценка (успеваемость)']
        student_predictions = np.array(list(map(lambda x: x[0], loaded_model.predict(X_test))))
        acc_grades = round(custom_accuracy(y_true, student_predictions), 2)

        counter_true = collections.Counter(y_true)
        counter_predict = collections.Counter(student_predictions)

        c_in_true = 0
        c_in_predict = 0

        if 2 in counter_true:
            c_in_true = counter_true[2]
        if 2 in counter_predict:
            c_in_predict = counter_predict[2]
    
        predictions[sid] = [acc_grades, (c_in_true, c_in_predict)] + list(zip(subjects, semesters, student_predictions, y_true))

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Student data not found")

    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids, "predictions": predictions})


"""
@app.post("/submit_file")
async def submit_file(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    contents = contents.decode('utf-8')
    student_ids = parse_student_ids(contents)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная", "student_ids": student_ids})

"""
# Новые эндпоинты для бота
@app.post("/bot_submit_student_id")
async def bot_submit_student_id(student_id: str = Form(...)):
    student_ids = parse_student_ids(student_id)
    return {"student_ids": student_ids}

@app.post("/bot_submit_file")
async def bot_submit_file(file: UploadFile = File(...)):
    contents = await file.read()
    contents = contents.decode('utf-8')
    student_ids = parse_student_ids(contents)
    return {"student_ids": student_ids}

@app.post("/bot_get_student_performance")
async def bot_get_student_performance(student_id: int = Form(...), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        performance = db.query(Performance).filter(Performance.student_id == student_id).all()
        student.performance = performance
        for p in student.performance:
            p.course = db.query(Course).filter(Course.id == p.course_id).first()
    return {"student": {"id": student.id, "performance": [{"course": {"course_name": p.course.course_name}, "grade_performance": p.grade_performance} for p in student.performance]}}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)