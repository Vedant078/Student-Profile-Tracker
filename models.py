from typing import Optional
from sqlmodel import SQLModel,Field

class StudentRecord(SQLModel,table=True):
    id : Optional[int] = Field(default = None, primary_key = True)
    name : str
    branch : str
    cgpa : float


class StudentUpdate(SQLModel):
    name :Optional[str] = None
    branch : Optional[str] = None
    cgpa : Optional[float] = None
