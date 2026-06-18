from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime,timedelta,timezone
from app.config.database import get_session
from app.models.schemas import User, UserRegister, userOut


router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "mySecretKeyISSUperDupersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_pass(password: str) -> str:
    return pwd_context.hash(password)

def varify_pass(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)


def create_access_token(data : dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encode_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username : str = payload.get("sub")
        user_id : int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), session:Session=Depends(get_session)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    return verify_access_token(token, credentials_exception)


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

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(credentials:OAuth2PasswordRequestForm = Depends(), session : Session = Depends(get_session)):
    user = session.exec(
        select(User).where(
            (User.email == credentials.username) | (User.username == credentials.username)
        )
    ).first()

    if not user:
        raise HTTPException(status_code= 401 , detail="invalid credentials")
    
    if not varify_pass(credentials.password, user.password):
        raise HTTPException(status_code= 401 , detail="invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    
    token_payload = {
        "sub" : user.username,
        "user_id" : user.id
    }

    access_token = create_access_token(token_payload)
    return{
        "access_token" : access_token,
        "token_type" : "bearer"
    }
