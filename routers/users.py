from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import model
from schemas import schemas
from utils import password_utils
from db.database import get_db
from pydantic import ValidationError
import shutil
import os

router = APIRouter(prefix="/users", tags=["Users"])


# POST User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(
    user: str = Body(...), image: UploadFile = File(None), db: Session = Depends(get_db)
):
    try:
        post_user = schemas.UserCreate.parse_raw(user)

    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid format in post field")
    # Check if a user with the same email already exists
    existing_user = (
        db.query(model.User).filter(model.User.email == post_user.email).first()
    )
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email is already in use")

    if image is not None:
        # Check if the file is a .jpg or .png file
        if not (image.filename.endswith(".jpg") or image.filename.endswith(".png")):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg and .png files are accepted",
            )

        os.makedirs("images", exist_ok=True)

        # Save the file locally
        with open(f"images/{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        profile_image = f"images/{image.filename}"
    else:
        profile_image = None

    hashed_password = password_utils.hash(post_user.password)
    post_user.password = hashed_password
    new_user_data = post_user.dict()
    new_user_data.pop("profile_image", None)
    new_user = model.User(**new_user_data, profile_image=profile_image)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
