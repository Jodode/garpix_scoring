from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from db_config import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String, nullable=False)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(String)
    grade_without_resits = Column(Integer)
    grade_performance = Column(Integer)
    start_year = Column(Integer)
    start_semester_year = Column(Integer)
    semester_number = Column(Integer)

    student = relationship("Student")
    course = relationship("Course")

class StudentPerformance(Base):
    __tablename__ = "students_performance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    preparation_level = Column(String)
    study_group = Column(String)
    specialization = Column(String)
    academic_year = Column(String)
    semester = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    grade_without_resits = Column(Integer)
    grade_performance = Column(Integer)
    start_year = Column(Integer)
    start_semester_year = Column(Integer)
    semester_number = Column(Integer)

    student = relationship("Student")
    course = relationship("Course")

class StudentPerformanceRelease(Base):
    __tablename__ = "students_performance_release"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    preparation_level = Column(String)
    study_group = Column(String)
    specialization = Column(String)
    academic_year = Column(String)
    semester = Column(String)
    course = Column(String)
    grade_without_resits = Column(Integer)
    grade_performance = Column(Integer)
    university = Column(String)
    start_year = Column(Integer)
    start_semester_year = Column(Integer)
    semester_number = Column(Integer)
    course_encoded = Column(Float)
    two_num = Column(Float)
    three_num = Column(Float)
    four_num = Column(Float)
    five_num = Column(Float)