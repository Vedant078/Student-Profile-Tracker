from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext

from app.config.database import get_session
from app.models.schemas import User, UserRegister, userOut

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register", response_model=userOut, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, session: Session = Depends(get_session)):
    user_repeated = session.exec(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ).first()
    
    if user_repeated:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    secured_hash = hash_pass(user.password)
    
    db_user = User(
        id=None,
        username=user.username,
        email=user.email,
        password=secured_hash
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/user/{id}", response_model=userOut)
def get_user(id: int, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user