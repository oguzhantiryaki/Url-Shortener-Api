from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config.db import get_db
from models.index import User as DBUser
from schemas.index import User, JWTtoken

SECRET_KEY = "this-is-a-secret-key"
ALGORITHM = "HS256"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def hash_password(password: str):
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)


def create_jwt_token(username: str, expire_time: int):
    encode = {
        "sub": username,
        "exp": datetime.now() + timedelta(minutes=expire_time)
    }
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


auth = APIRouter(prefix="/auth")


@auth.post("/token")
def login(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == login.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = JWTtoken(
        access_token=create_jwt_token(user.username, 60), 
        token_type="bearer"
    )
    return token


@auth.post("/")
def register(user: User, db: Session = Depends(get_db)):
    existing_user = db.query(DBUser).filter(DBUser.username == user.username).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    new_user = DBUser(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_username_from_token(token: str):
    try:
        jwt_decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = jwt_decode.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return username

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )