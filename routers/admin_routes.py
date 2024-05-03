from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import admin_model
from schemas.schemas import AdminOut, AdminCreate, AdminUpdate
from utils import password_utils
from db.database import get_db
from utils.file_utils import save_image
from pydantic import ValidationError
from typing import List, Optional


router = APIRouter(prefix="/admin", tags=["Admin"])


# GET All Admin
@router.get("/", response_model=List[AdminOut])
def get_all_admin(db: Session = Depends(get_db)):
    admins = db.query(admin_model.Admin).all()
    return admins


# GET Admin
@router.get("/{id}", response_model=AdminOut)
def get_admin(id: str, db: Session = Depends(get_db)):
    admin = db.query(admin_model.Admin).filter(admin_model.Admin.id == id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with id {id} does not found",
        )
    return admin


# POST Admin
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AdminOut)
async def create_admin(
    admin: str = Body(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        post_admin = AdminCreate.parse_raw(admin)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid format or missing fields.")
    # Check if a admin with the same email already exists
    existing_admin = (
        db.query(admin_model.Admin)
        .filter(admin_model.Admin.email == post_admin.email)
        .first()
    )
    if existing_admin is not None:
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

    hashed_password = password_utils.hash(post_admin.password)
    post_admin.password = hashed_password
    new_admin_data = post_admin.dict()
    new_admin_data.pop("profile_image", None)
    new_admin = admin_model.Admin(**new_admin_data, profile_image=profile_image)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


# PUT Admin
@router.put("/{id}", response_model=AdminOut)
async def update_admin(
    id: str,
    post_admin: Optional[str] = Body(None),
    profile_image: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    # Retrieve the admin
    admin = db.query(admin_model.Admin).filter(admin_model.Admin.id == id).first()

    # If the admin doesn't exist, return an error
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Convert the post_admin string to a dictionary if it's not None
    if post_admin is not None:
        post_admin = AdminUpdate.parse_raw(post_admin)
        admin_data = post_admin.dict(exclude_unset=True)
        if post_admin.password:
            hashed_password = password_utils.hash(post_admin.password)
            admin_data["password"] = hashed_password
    else:
        admin_data = {}

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
        admin_data["profile_image"] = image_path

    for key, value in admin_data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin


# Delete Admin
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(id: str, db: Session = Depends(get_db)):
    # Retrieve the admin
    admin = db.query(admin_model.Admin).filter(admin_model.Admin.id == id).first()

    # If the admin doesn't exist, return an error
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Delete the admin
    db.delete(admin)
    db.commit()

    return
