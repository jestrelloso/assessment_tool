from fastapi import status, HTTPException, Depends, APIRouter, UploadFile, File, Body
from sqlalchemy.orm import Session
from models import (
    exam_model,
    question_model,
    topic_model,
    choices_model,
    examiner_model,
)
from schemas.schemas import ExamInDB, ExamCreate, ExamUpdate
from db.database import get_db
from auth import oauth2
from typing import List
from pydantic import ValidationError
from utils.file_utils import save_image


router = APIRouter(prefix="/exams", tags=["Exam"])


def get_exam_by_id(db, id: str):
    return db.query(exam_model.Exam).filter(exam_model.Exam.id == id).first()


def get_question_by_id(db, question_id: str):
    return (
        db.query(question_model.Question)
        .filter(question_model.Question.id == question_id)
        .first()
    )


def get_topic_by_id(db, topic_id):
    return db.query(topic_model.Topic).filter(topic_model.Topic.id == topic_id).first()


def get_choice_by_id(db, choice_id):
    return (
        db.query(choices_model.Choice)
        .filter(choices_model.Choice.id == choice_id)
        .first()
    )


# GET All exams
@router.get("/", response_model=List[ExamInDB])
def get_all_exams(
    db: Session = Depends(get_db),
    current_user: examiner_model.Examiner = Depends(oauth2.get_current_user),
):
    exams = (
        db.query(exam_model.Exam)
        .filter(exam_model.Exam.created_by == current_user.id)
        .all()
    )
    return exams


# GET exams by ID
@router.get("/{id}", response_model=ExamInDB)
def get_exam(
    id: str,
    db: Session = Depends(get_db),
    current_user: examiner_model.Examiner = Depends(oauth2.get_current_user),
):
    exam = get_exam_by_id(db, id)
    if not exam or exam.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {id} not found",
        )
    return exam


# # POST exam
@router.post("/", response_model=ExamInDB)
async def create_exam(
    exam: str = Body(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user_type: examiner_model.Examiner = Depends(
        oauth2.get_current_user_type("Examiner")
    ),
):
    try:
        post_exam = ExamCreate.parse_raw(exam)

    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid format in post field")
    # Create the new exam
    new_exam = exam_model.Exam(
        **post_exam.dict(exclude={"topics"}), created_by=current_user_type.id
    )

    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    # Create the topics and questions for the exam
    for topic_data in post_exam.topics:
        new_topic = topic_model.Topic(
            **topic_data.dict(exclude={"questions"}), exam_id=new_exam.id
        )
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)

        for question_data in topic_data.questions:
            new_question = question_model.Question(
                **question_data.dict(exclude={"choices"}), topic_id=new_topic.id
            )
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            for choice_data in question_data.choices:
                new_choice = choices_model.Choice(
                    **choice_data.dict(), question_id=new_question.id
                )
                db.add(new_choice)
                db.commit()
                db.refresh(new_choice)

    if image is not None:
        # Check if the file is a .jpg or .png file
        if not (image.filename.endswith(".jpg") or image.filename.endswith(".png")):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg and .png files are accepted",
            )
        # Use save_image util to upload image
        cover_photo = await save_image(image)
        new_exam.cover_photo = cover_photo

    db.commit()
    db.refresh(new_exam)
    return new_exam


def update_exam(db, db_exam, update_exam):
    for attr, value in update_exam.dict(exclude_unset=True).items():
        if attr != "topics":
            setattr(db_exam, attr, value)


def update_topic(db, db_topic, topic_data):
    for attr, value in topic_data.dict(exclude_unset=True).items():
        if attr != "questions":
            setattr(db_topic, attr, value)


def update_question(db, db_question, question_data):
    for attr, value in question_data.dict(exclude_unset=True).items():
        if attr != "choices":
            setattr(db_question, attr, value)


def update_choice(db, db_choice, choice_data):
    for attr, value in choice_data.dict(exclude_unset=True).items():
        setattr(db_choice, attr, value)


@router.patch("/{exam_id}", response_model=ExamInDB)
async def update_exam_partial(
    exam_id: str,
    exam: str = Body(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user_type: examiner_model.Examiner = Depends(
        oauth2.get_current_user_type("Examiner")
    ),
):

    db_exam = get_exam_by_id(db, exam_id)
    if db_exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam is not None:
        try:
            update_exam_data = ExamUpdate.parse_raw(exam)
            update_exam(db, db_exam, update_exam_data)
            if update_exam_data.topics is not None:
                for topic_data in update_exam_data.topics:
                    db_topic = get_topic_by_id(db, topic_data.id)

                    if db_topic is not None:
                        update_topic(db, db_topic, topic_data)
                        if topic_data.questions is not None:
                            for question_data in topic_data.questions:
                                db_question = get_question_by_id(db, question_data.id)

                                if db_question is not None:
                                    update_question(db, db_question, question_data)
                                    if question_data.choices is not None:
                                        for choice_data in question_data.choices:
                                            db_choice = get_choice_by_id(
                                                db, choice_data.id
                                            )

                                            if db_choice is None:
                                                raise HTTPException(
                                                    status_code=404,
                                                    detail=f"Choice not found: {choice_data.id}",
                                                )
                                            db_question.choices.append(db_choice)
                                            update_choice(db, db_choice, choice_data)

            db.commit()
        except ValidationError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid format in post field")

    if image is not None:
        if not (image.filename.endswith(".jpg") or image.filename.endswith(".png")):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg and .png files are accepted",
            )
        cover_photo = await save_image(image)
        db_exam.cover_photo = cover_photo
        db.commit()

    db.refresh(db_exam)
    return db_exam


# DELETE exam
@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: str, db: Session = Depends(get_db)):
    db_exam = get_exam_by_id(db, exam_id)
    if db_exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    db.delete(db_exam)
    db.commit()
    return


# DELETE topic
@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: str, db: Session = Depends(get_db)):
    db_topic = get_topic_by_id(db, topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(db_topic)
    db.commit()
    return


# DELETE Question
@router.delete("/question/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: str, db: Session = Depends(get_db)):
    db_question = get_question_by_id(db, question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(db_question)
    db.commit()
    return


# Delete Choice
@router.delete("/choice/{choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_choice(choice_id: str, db: Session = Depends(get_db)):
    db_choice = get_choice_by_id(db, choice_id)
    if db_choice is None:
        raise HTTPException(status_code=404, detail="Choice not found")

    db.delete(db_choice)
    db.commit()
    return
