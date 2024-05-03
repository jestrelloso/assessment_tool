from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import update, and_
from models import request_exam_model, exam_model, user_model
from models.examinee_exam_table_model import examinee_exam_table
from schemas.schemas import RequestExamInDB, UserOut
from db.database import get_db
from auth import oauth2
from typing import List


router = APIRouter(prefix="/request_exam", tags=["request_exam"])


def get_request_exam_by_id(db, id: str):
    return (
        db.query(request_exam_model.RequestExam)
        .filter(request_exam_model.RequestExam.id == id)
        .first()
    )


def get_request_exam_by_exam_id(db, exam_id: str):
    return (
        db.query(request_exam_model.RequestExam)
        .filter(request_exam_model.RequestExam.exam_id == exam_id)
        .first()
    )


def get_exam_by_id(db, id: str):
    return db.query(exam_model.Exam).filter(exam_model.Exam.id == id).first()


def get_examinee_by_id(db, id: str):
    return db.query(user_model.User).filter(user_model.User.id == id).first()


def get_existing_request_by_id(db, exam_id: str, examinee_id: str):
    return (
        db.query(request_exam_model.RequestExam)
        .filter(
            request_exam_model.RequestExam.exam_id == exam_id,
            request_exam_model.RequestExam.examinee_id == examinee_id,
        )
        .first()
    )


# GET All request exam
@router.get("/", response_model=List[RequestExamInDB])
def get_all_request_exams(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user),
):
    request_exams = (
        db.query(request_exam_model.RequestExam)
        .join(exam_model.Exam)
        .filter(exam_model.Exam.created_by == current_user.id)
        .all()
    )
    return request_exams


# GET Single request exam
@router.get("/{id}", response_model=RequestExamInDB)
def get_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user),
):
    request_exam = get_request_exam_by_id(db, id)
    if not request_exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request exam with id {id} does not found",
        )
    if request_exam.exam.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this exam request",
        )
    return request_exam


# POST a new request exam
@router.post("/", response_model=RequestExamInDB, status_code=status.HTTP_201_CREATED)
def create_request_exam(
    request_exam: str,
    db: Session = Depends(get_db),
    current_user_type: user_model.User = Depends(
        oauth2.get_current_user_type("Examinee")
    ),
    current_user: user_model.User = Depends(oauth2.get_current_user),
):
    # Check if the exam exists
    exam = get_exam_by_id(db, request_exam)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {request_exam} does not found",
        )

    # Check if a request for the same exam by the same user already exists
    existing_request = get_existing_request_by_id(db, request_exam, current_user.id)

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already requested this exam.",
        )

    new_request_exam = request_exam_model.RequestExam(
        exam_id=request_exam, examinee_id=current_user.id
    )

    db.add(new_request_exam)
    db.commit()
    db.refresh(new_request_exam)
    return new_request_exam


@router.put("/{request_exam_id}", response_model=UserOut)
def approve_exam_request(
    request_exam_id: str,
    db: Session = Depends(get_db),
    current_user_type: user_model.User = Depends(
        oauth2.get_current_user_type("Examiner")
    ),
):
    # Get the exam request
    exam_request = get_request_exam_by_id(db, request_exam_id)
    if not exam_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam request with id {request_exam_id} does not found",
        )

    # Check if the exam request has already been approved
    if exam_request.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This exam request has already been approved.",
        )

    # Update the exam request status and approval
    exam_request.status = "Approved"
    exam_request.is_approved = True

    # Get the examinee
    examinee = exam_request.examinee

    # Associate the exam with the examinee
    examinee.exams.append(exam_request.exam)
    db.commit()
    # Update the is_approved field in the examinee_exam_table
    db.execute(
        update(examinee_exam_table)
        .where(examinee_exam_table.c.examinee_id == examinee.id)
        .where(examinee_exam_table.c.exam_id == exam_request.exam.id)
        .values(is_approved=True)
    )

    # Commit the changes to the database
    db.commit()

    # Refresh the examinee object to get the updated data from the database
    db.refresh(examinee)

    examinee.exam_ids = [exam.id for exam in examinee.exams]

    # Return the updated examinee
    return examinee


@router.delete("/{request_exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_request(
    request_exam_id: str,
    current_user: user_model.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    # Get the exam request
    exam_request = get_request_exam_by_id(db, request_exam_id)
    if not exam_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam request with id {request_exam_id} does not found",
        )

    # Check if the current user is the examiner who created the exam
    if exam_request.exam.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this exam request",
        )

    # Delete the exam request
    db.delete(exam_request)

    db.execute(
        examinee_exam_table.delete().where(
            and_(
                examinee_exam_table.c.examinee_id == exam_request.examinee_id,
                examinee_exam_table.c.exam_id == exam_request.exam.id,
            )
        )
    )

    # Commit the changes to the database
    db.commit()

    # Return a message indicating the exam request was deleted
    return
