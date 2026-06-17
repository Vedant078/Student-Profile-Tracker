from typing import List,Optional
from pydantic import BaseModel, EmailStr
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


class User(SQLModel, table=True):
    id : Optional[int] = Field(default = None, primary_key = True)
    username : str = Field(index = True, unique = True)
    email : str = Field(unique = True)
    password : str

class UserRegister(BaseModel):
    username : str
    email : EmailStr
    password : str

class userOut(BaseModel):
    id : int
    username : str
    email : str

class BranchAnalytics(BaseModel):
    branch: str
    average_cgpa: float


class StudentProfileDetails(BaseModel):
    student_id : int
    student_name : str
    cgpa : float
    department_name : str
    hod_name : str


class Userlogin(BaseModel):
    email : EmailStr
    password : str