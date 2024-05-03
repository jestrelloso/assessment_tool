from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import examiner_model
from schemas.schemas import ExaminerOut, ExaminerCreate, ExaminerUpdate
from utils import password_utils
from db.database import get_db
from utils.file_utils import save_image
from pydantic import ValidationError
from typing import List, Optional


router = APIRouter(prefix="/examiner", tags=["Examiner"])


# GET All Examiner
@router.get("/", response_model=List[ExaminerOut])
def get_all_examiner(db: Session = Depends(get_db)):
    examiners = db.query(examiner_model.Examiner).all()
    return examiners


# GET Examiner
@router.get("/{id}", response_model=ExaminerOut)
def get_examiner(id: str, db: Session = Depends(get_db)):
    examiner = (
        db.query(examiner_model.Examiner)
        .filter(examiner_model.Examiner.id == id)
        .first()
    )
    if not examiner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Examiner with id {id} does not found",
        )
    return examiner


# POST Examiner
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExaminerOut)
async def create_examiner(
    examiner: str = Body(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        post_examiner = ExaminerCreate.parse_raw(examiner)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid format or missing fields.")
    # Check if a examiner with the same email already exists
    existing_examiner = (
        db.query(examiner_model.Examiner)
        .filter(examiner_model.Examiner.email == post_examiner.email)
        .first()
    )
    if existing_examiner is not None:
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

    hashed_password = password_utils.hash(post_examiner.password)
    post_examiner.password = hashed_password
    new_examiner_data = post_examiner.dict()
    new_examiner_data.pop("profile_image", None)
    new_examiner = examiner_model.Examiner(
        **new_examiner_data, profile_image=profile_image
    )
    db.add(new_examiner)
    db.commit()
    db.refresh(new_examiner)
    return new_examiner


# PUT Examiner
@router.put("/{id}", response_model=ExaminerOut)
async def update_examiner(
    id: str,
    post_examiner: Optional[str] = Body(None),
    profile_image: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    # Retrieve the examiner
    examiner = (
        db.query(examiner_model.Examiner)
        .filter(examiner_model.Examiner.id == id)
        .first()
    )

    # If the examiner doesn't exist, return an error
    if not examiner:
        raise HTTPException(status_code=404, detail="Examiner not found")

    # Convert the post_examiner string to a dictionary if it's not None
    if post_examiner is not None:
        post_examiner = ExaminerUpdate.parse_raw(post_examiner)
        examiner_data = post_examiner.dict(exclude_unset=True)
        if post_examiner.password:
            hashed_password = password_utils.hash(post_examiner.password)
            examiner_data["password"] = hashed_password
    else:
        examiner_data = {}

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
        examiner_data["profile_image"] = image_path

    for key, value in examiner_data.items():
        setattr(examiner, key, value)

    db.commit()
    db.refresh(examiner)
    return examiner


# Delete Examiner
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_examiner(id: str, db: Session = Depends(get_db)):
    # Retrieve the examiner
    examiner = (
        db.query(examiner_model.Examiner)
        .filter(examiner_model.Examiner.id == id)
        .first()
    )

    # If the examiner doesn't exist, return an error
    if not examiner:
        raise HTTPException(status_code=404, detail="Examiner not found")

    # Delete the examiner
    db.delete(examiner)
    db.commit()

    return
