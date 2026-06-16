from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import Optional

from app.config.database import get_session
from app.models.schemas import StudentRecord, StudentUpdate, StudentProfileDetails, BranchAnalytics, Department

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/createStudent", response_model=StudentRecord, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentRecord, session: Session = Depends(get_session)):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.get("/getStudents", response_model=list[StudentRecord])
def get_students(name: Optional[str] = None, limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    statement = select(StudentRecord)
    if name:
        statement = statement.where(StudentRecord.name == name)
   
    statement = statement.offset(offset).limit(limit)
    students = session.exec(statement).all()

    if students:
        return students
    raise HTTPException(status_code=404, detail="student not found")

@router.get("/getStudent/{student_id}", response_model=StudentProfileDetails)
def get_student(student_id: int, session: Session = Depends(get_session)):
    statement = (
        select(StudentRecord, Department)
        .join(Department)
        .where(StudentRecord.id == student_id)
    )
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="student not found")
    
    stud, dept = result
    return {
        "student_id": stud.id,
        "student_name": stud.name,
        "cgpa": stud.cgpa,
        "department_name": dept.name,
        "hod_name": dept.hod
    }

@router.patch("/updateStudent/{student_id}", response_model=StudentRecord)
def update_student(student_id: int, student: StudentUpdate, session: Session = Depends(get_session)):
    db_student = session.get(StudentRecord, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="student not found")
    
    updated = student.model_dump(exclude_unset=True)
    for key, value in updated.items():
        setattr(db_student, key, value)
    
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student

@router.delete("/delete_student/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(StudentRecord, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    
    session.delete(student)
    session.commit()
    return None

@router.get("/analysis", response_model=list[BranchAnalytics])
def analysis(session: Session = Depends(get_session)):
    statement = ( 
        select(
            Department.name.label("branch"),
            func.avg(StudentRecord.cgpa).label("Average CGPA")
        )
        .join(Department)
        .group_by(Department.name)
    )
    result = session.exec(statement).all()

    analytics_data = []
    for branch_name, avg_score in result:
        analytics_data.append({
            "branch": branch_name,
            "average_cgpa": round(avg_score, 2) 
        })
    return analytics_data