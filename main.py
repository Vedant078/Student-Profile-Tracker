from fastapi import FastAPI,Depends,HTTPException,status
from contextlib import asynccontextmanager
from pydantic import  BaseModel
from sqlmodel import Session,select,func
from typing import Optional,List
from database import init_db, get_session
from models import StudentRecord, StudentUpdate, Department

class BranchAnalytics(BaseModel):
    branch: str
    average_cgpa: float


class StudentProfileDetails(BaseModel):
    student_id : int
    student_name : str
    cgpa : float
    department_name : str
    hod_name : str


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

@app.post("/createDepartment", response_model=Department)
def create_department(dept_data: Department, session: Session = Depends(get_session)):
    # 1. Check if a department with this name already exists
    existing_dept = session.exec(
        select(Department).where(Department.name == dept_data.name)
    ).first()
    
    if existing_dept:
        raise HTTPException(status_code=400, detail="Department already exists")
        
    # 2. Add the new department to the session and save
    session.add(dept_data)
    session.commit()
    session.refresh(dept_data) # This populates the generated id column
    
    return dept_data

@app.post("/createStudent",response_model = StudentRecord,status_code = status.HTTP_201_CREATED)
def create_student(student : StudentRecord, session:Session = Depends(get_session)):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

#read (R)
@app.get("/getStudents",response_model = list[StudentRecord])
def get_students(name : Optional[str] = None,limit: int = 10,offset : int = 0,session : Session = Depends(get_session)):

    statement = select(StudentRecord)

    if name:
        statement = statement.where(StudentRecord.name==name)
   
    statement = statement.offset(offset).limit(limit)
    students = session.exec(statement).all()

    if students:
        return students
    else:
        raise HTTPException(status_code= 404 ,detail="student not found")

# read specific (R)
@app.get("/getStudent/{student_id}",response_model = StudentProfileDetails)
def get_student(student_id :int, session:Session = Depends(get_session)):
   statement = (
       select(StudentRecord, Department)
       .join(Department)
       .where(StudentRecord.id ==student_id)
   )
   result = session.exec(statement).first()
   if not result:
       raise HTTPException(status_code=404, detail = "student not found")
   else:
       stud,dept = result #result is tupples (2 types of tupples as input)

       return {
           "student_id": stud.id,
           "student_name": stud.name,
           "cgpa": stud.cgpa,
           "department_name": dept.name,
           "hod_name" : dept.hod
       }
    
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
    
@app.patch("/updateDepartment/{department_id}",response_model = Department)
def update_department(department_id : int, department:Department,session:Session = Depends(get_session)):
    db_dept = session.get(Department,department_id)
    if not db_dept:
        raise HTTPException(status_code=404,detail="department not found")
    else:
        updated = department.model_dump(exclude_unset = True)
        for key,value in updated.items():
            setattr(db_dept,key,value)
        
        session.add(db_dept)
        session.commit()
        session.refresh(db_dept)
        return db_dept


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
    

@app.get("/analysis",response_model = list[BranchAnalytics])
def analysis(session:Session = Depends(get_session)):
    statement = select(
        StudentRecord.branch,
        func.avg(StudentRecord.cgpa).label("Average CGPA")
    ).group_by(StudentRecord.branch)

    result = session.exec(statement).all()

    analytics_data = []
    for branch_name, avg_score in result:
        analytics_data.append({
            "branch": branch_name,
            "average_cgpa": round(avg_score, 2) 
        })
    return analytics_data