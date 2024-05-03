from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from schemas.schemas import TokenOut
from db import database
from models import model
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from utils.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def get_user_from_db(user_id: str, db: Session):
    examiner = db.query(model.Examiner).filter(model.Examiner.id == user_id).first()
    admin = db.query(model.Admin).filter(model.Admin.id == user_id).first()
    examinee = db.query(model.User).filter(model.User.id == user_id).first()

    return examiner or admin or examinee


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")
        if user_id is None or user_type is None:
            raise credentials_exception
        token_data = TokenOut(user_id=user_id, user_type=user_type)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could Not Validate Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = get_user_from_db(token_data.user_id, db)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_type(user_type: str):
    def _get_current_user_type(
        token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could Not Validate Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_data = verify_access_token(token, credentials_exception)
        # Fetch user_type from the JWT payload
        user_type_claim = token_data.user_type

        user = get_user_from_db(token_data.user_id, db)

        if user is None:
            raise credentials_exception
        if user_type_claim != user_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No permissions"
            )
        return user

    return _get_current_user_type
