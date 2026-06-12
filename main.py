from fastapi import FastAPI,Depends,HTTPException,status
from contextlib import asynccontextmanager
from pydantic import  BaseModel
from sqlmodel import Session,select
from typing import Optional
from database import init_db, get_session
from models import StudentRecord, StudentUpdate

@asynccontextmanager
async def lifeSpan(app : FastAPI):
    print("Server starting......")

    init_db()
    yield
    print("Server shutting down.....")


app = FastAPI(
    title = "Student Profile tracker",
    lifespan = lifeSpan
)

#CRUD :(create - Read - Update - Delete)

@app.get("/")
def Welcome():
    return {"Message":"Welcome to student Profile" }

#create (C)
@app.post("/createStudent",response_model = StudentRecord,status_code = status.HTTP_201_CREATED)
def create_student(student : StudentRecord, session:Session = Depends(get_session)):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

#read (R)
@app.get("/getStudents",response_model = list[StudentRecord])
def get_students(session : Session = Depends(get_session)):

    statement = select(StudentRecord)
    students = session.exec(statement).all()
    if students:
        return students
    else:
        raise HTTPException(status_code= 404 ,detail="student not found")


@app.get("/getStudent/{student_id}",response_model = StudentRecord)
def get_student(student_id :int, session:Session = Depends(get_session)):
    student = session.get(StudentRecord,student_id)
    if student:
        return student
    else:
        raise HTTPException(status_code=404,detail="student not found")
    
#update(U)
@app.patch("/updateStudent/{student_id}",response_model = StudentRecord)
def update_student(student_id : int, student : StudentUpdate, session:Session=Depends(get_session)):
    db_student = session.get(StudentRecord,student_id)
    if not db_student:
        raise HTTPException(status_code=404,detail="student not found")
    else:
        updated = student.model_dump(exclude_unset = True)
        for key,value in updated.items():
            setattr(db_student,key,value)
        
        session.add(db_student)
        session.commit()
        session.refresh(db_student)
        return db_student

#delete (D)
@app.delete("/delete_student/{student_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id : int, session: Session = Depends(get_session)):
    student = session.get(StudentRecord,student_id)

    if not student:
        raise HTTPException(status_code=404,detail="student not found")
    else:
        session.delete(student)
        session.commit()
        return None