from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db import database
from models import user_model, examiner_model, admin_model
from auth import oauth2
from schemas.schemas import Token
from utils import password_utils

router = APIRouter(tags=["Authentication"])


def get_user_by_email(db: Session, model, email):
    return db.query(model).filter(model.email == email).first()


@router.post("/login", response_model=Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = get_user_by_email(db, user_model.User, user_credentials.username)
    examiner = get_user_by_email(db, examiner_model.Examiner, user_credentials.username)
    admin = get_user_by_email(db, admin_model.Admin, user_credentials.username)

    user = user or examiner or admin
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid credentials",
        )
    if not password_utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid credentials",
        )
    access_token = oauth2.create_access_token(
        data={"user_id": str(user.id), "user_type": str(user.user_type)}
    )
    return {"access_token": access_token, "token_type": "bearer"}
