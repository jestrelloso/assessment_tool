from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import model
from schemas import schemas
from utils import password_utils
from db.database import get_db
from utils.file_utils import save_image
from pydantic import ValidationError
from typing import Optional


router = APIRouter(prefix="/users", tags=["Users"])


# GET User
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: str, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not found",
        )
    return user


# POST User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(
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
        # Use save_image util to upload image
        profile_image = await save_image(image)
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


# PUT User
@router.put("/{id}")
async def update_user(
    id: str,
    post_user: str = Body(None),
    profile_image: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    # Retrieve the user
    user = db.query(model.User).filter(model.User.id == id).first()
    # Convert the post_user string to a dictionary
    post_user = schemas.UserUpdate.parse_raw(post_user)

    # If the user doesn't exist, return an error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's data
    user_data = post_user.dict(exclude_unset=True)
    if post_user.password:
        hashed_password = password_utils.hash(post_user.password)
        user_data["password"] = hashed_password

    # Handle the profile_image field
    if profile_image:
        # Save the uploaded image to a file and store the file path in the database
        image_path = await save_image(profile_image)
        user_data["profile_image"] = image_path

    for key, value in user_data.items():
        setattr(user, key, value)

    db.commit()
    return user


# Delete User
@router.delete("/{id}")
async def delete_user(id: str, db: Session = Depends(get_db)):
    # Retrieve the user
    user = db.query(model.User).filter(model.User.id == id).first()

    # If the user doesn't exist, return an error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
