from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config.database import get_session
from app.models.schemas import Department

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/createDepartment", response_model=Department)
def create_department(dept_data: Department, session: Session = Depends(get_session)):
    existing_dept = session.exec(
        select(Department).where(Department.name == dept_data.name)
    ).first()
    
    if existing_dept:
        raise HTTPException(status_code=400, detail="Department already exists")
        
    session.add(dept_data)
    session.commit()
    session.refresh(dept_data)
    return dept_data

@router.patch("/updateDepartment/{department_id}", response_model=Department)
def update_department(department_id: int, department: Department, session: Session = Depends(get_session)):
    db_dept = session.get(Department, department_id)
    if not db_dept:
        raise HTTPException(status_code=404, detail="department not found")
    
    updated = department.model_dump(exclude_unset=True)
    for key, value in updated.items():
        setattr(db_dept, key, value)
    
    session.add(db_dept)
    session.commit()
    session.refresh(db_dept)
    return db_dept

@router.delete("/delete/{dept_id}",status_code = 204)
def delete_dept(dept_id : int, session:Session=Depends(get_session)):
    dept = session.get(Department, dept_id)
    if not dept:
        raise HTTPException(status_code = 404, detail="Department not found")
    
    session.delete(dept)
    session.commit()
    return None
                