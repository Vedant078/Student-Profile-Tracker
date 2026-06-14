from typing import List,Optional
from sqlmodel import SQLModel,Field,Relationship

class Department(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key = True)
    name : str = Field(index=True, unique=True)
    hod : str

    students : List["StudentRecord"] = Relationship(back_populates = "department")




class StudentRecord(SQLModel,table=True):
    id : Optional[int] = Field(default = None, primary_key = True)
    name : str
    cgpa : float
    department_id : Optional[int] = Field(default=None, foreign_key="department.id", ondelete = "SET NULL")
    department : Optional[Department] = Relationship(back_populates = "students")


class StudentUpdate(SQLModel):
    name :Optional[str] = None
    branch : Optional[str] = None
    cgpa : Optional[float] = None
