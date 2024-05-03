from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import user_model
from schemas.schemas import UserOut, UserCreate, UserUpdate
from utils import password_utils
from db.database import get_db
from utils.file_utils import save_image
from pydantic import ValidationError
from typing import List, Optional


router = APIRouter(prefix="/users", tags=["Users"])


def get_examinee_by_id(db, id: str):
    return db.query(user_model.User).filter(user_model.User.id == id).first()


# GET All Users
@router.get("/", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(user_model.User).all()
    for user in users:
        user.exam_ids = [exam.id for exam in user.exams]
    return users


# GET User
@router.get("/{id}", response_model=UserOut)
def get_user(id: str, db: Session = Depends(get_db)):
    user = get_examinee_by_id(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not found",
        )
    user.exam_ids = [exam.id for exam in user.exams]
    return user


# POST User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(
    user: str = Body(...), image: UploadFile = File(None), db: Session = Depends(get_db)
):
    try:
        post_user = UserCreate.parse_raw(user)

    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid format in post field")
    # Check if a user with the same email already exists
    existing_user = (
        db.query(user_model.User)
        .filter(user_model.User.email == post_user.email)
        .first()
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
        # Use save_image util to upload image
        profile_image = await save_image(image)
    else:
        profile_image = None

    hashed_password = password_utils.hash(post_user.password)
    post_user.password = hashed_password
    new_user_data = post_user.dict()
    new_user_data.pop("profile_image", None)
    new_user = user_model.User(**new_user_data, profile_image=profile_image)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# PUT User
@router.put("/{id}", response_model=UserOut)
async def update_user(
    id: str,
    post_user: Optional[str] = Body(None),
    profile_image: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    # Retrieve the user
    user = db.query(user_model.User).filter(user_model.User.id == id).first()

    # If the user doesn't exist, return an error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert the post_user string to a dictionary if it's not None
    if post_user is not None:
        post_user = UserUpdate.parse_raw(post_user)
        user_data = post_user.dict(exclude_unset=True)
        if post_user.password:
            hashed_password = password_utils.hash(post_user.password)
            user_data["password"] = hashed_password
    else:
        user_data = {}

    # Handle the profile_image field
    if profile_image:
        # Check if the file is a .jpg or .png file
        if not (
            profile_image.filename.endswith(".jpg")
            or profile_image.filename.endswith(".png")
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg and .png files are accepted",
            )
        # Save the uploaded image to a file and store the file path in the database
        image_path = await save_image(profile_image)
        user_data["profile_image"] = image_path

    for key, value in user_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# Delete User
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str, db: Session = Depends(get_db)):
    # Retrieve the user
    user = db.query(user_model.User).filter(user_model.User.id == id).first()

    # If the user doesn't exist, return an error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()

    return
