import uuid
import json

# GET TESTING


def test_get_all_exams(authorized_examiner):
    res = authorized_examiner.get("/exams")
    assert res.status_code == 200
    exams = res.json()
    assert isinstance(exams, list)


def test_get_all_exams_not_authorized(client):
    res = client.get("/exams")
    assert res.status_code == 401


def test_get_exam_by_id(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    res = authorized_examiner.get(f"/exams/{exam_id}")
    assert res.status_code == 200
    exam = res.json()
    assert exam["id"] == exam_id


def test_get_by_id_exams_not_authorized(client, test_exam):
    exam_id = str(test_exam["id"])
    res = client.get(f"/exams/{exam_id}")
    assert res.status_code == 401


def test_get_post_not_exist(authorized_examiner):
    non_existent_uuid = uuid.uuid4()
    res = authorized_examiner.get(f"/exams/{non_existent_uuid}")
    assert res.status_code == 404


# POST TESTING
def test_create_exam(authorized_examiner, mock_exam):
    mock_exam_str = json.dumps(mock_exam)
    data = {"exam": mock_exam_str}
    with open("images/frieren.jpg", "rb") as img_file:
        res = authorized_examiner.post(
            "/exams/", data=data, files={"cover_photo": img_file}
        )

    assert res.status_code == 200
    exam = res.json()
    assert exam["title"] == mock_exam["title"]
    assert exam["description"] == mock_exam["description"]
    assert exam["time_duration"] == mock_exam["time_duration"]
    assert "cover_photo" in exam
    assert exam["topics"][0]["name"] == mock_exam["topics"][0]["name"]
    assert (
        exam["topics"][0]["questions"][0]["question"]
        == mock_exam["topics"][0]["questions"][0]["question"]
    )
    assert [
        choice["option"] for choice in exam["topics"][0]["questions"][0]["choices"]
    ] == [
        choice["option"] for choice in mock_exam["topics"][0]["questions"][0]["choices"]
    ]


def test_create_exam_non_authorized(client, mock_exam):
    mock_exam_str = json.dumps(mock_exam)
    data = {"exam": mock_exam_str}
    with open("images/frieren.jpg", "rb") as img_file:
        res = client.post("/exams/", data=data, files={"cover_photo": img_file})

    assert res.status_code == 401


# # Partial UPDATE TESTING
def test_update_exam_partial(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    total_questions = {"total_questions": 50}
    res = authorized_examiner.patch(
        f"/exams/{exam_id}", data={"exam": json.dumps(total_questions)}
    )
    assert res.status_code == 200
    updated_exam_response = res.json()
    expected_total_questions = total_questions["total_questions"]
    actual_total_questions = updated_exam_response.get("total_questions")
    assert (
        actual_total_questions == expected_total_questions
    ), "Total questions not updated as expected"


def test_update_exam_topics(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    topic_id = str(test_exam["topics"][0]["id"])
    new_topic_data = {"id": topic_id, "name": "New Topic Title"}
    exam_update_data = {"topics": [new_topic_data]}
    res = authorized_examiner.patch(
        f"/exams/{exam_id}", data={"exam": json.dumps(exam_update_data)}
    )
    assert res.status_code == 200
    updated_exam_response = res.json()
    updated_topic_title = next(
        (
            topic["name"]
            for topic in updated_exam_response["topics"]
            if topic["id"] == topic_id
        ),
        None,
    )
    assert (
        updated_topic_title == new_topic_data["name"]
    ), "Topic title not updated as expected"


def test_update_exam_questions(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    topic_id = str(test_exam["topics"][0]["id"])
    question_id = str(test_exam["topics"][0]["questions"][0]["id"])
    new_question_data = {"id": question_id, "question": "New Question Text"}
    new_topic_data = {"id": topic_id, "questions": [new_question_data]}
    exam_update_data = {"topics": [new_topic_data]}
    res = authorized_examiner.patch(
        f"/exams/{exam_id}", data={"exam": json.dumps(exam_update_data)}
    )
    assert res.status_code == 200
    updated_exam_response = res.json()
    updated_question_text = next(
        (
            question["question"]
            for topic in updated_exam_response["topics"]
            for question in topic["questions"]
            if question["id"] == question_id
        ),
        None,
    )
    assert (
        updated_question_text == new_question_data["question"]
    ), "Question text not updated as expected"


def test_update_exam_choices(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    topic_id = str(test_exam["topics"][0]["id"])
    question_id = str(test_exam["topics"][0]["questions"][0]["id"])
    choice_id = str(test_exam["topics"][0]["questions"][0]["choices"][0]["id"])
    new_choice_data = {"id": choice_id, "option": "New Choice Text"}
    new_question_data = {"id": question_id, "choices": [new_choice_data]}
    new_topic_data = {"id": topic_id, "questions": [new_question_data]}
    exam_update_data = {"topics": [new_topic_data]}
    res = authorized_examiner.patch(
        f"/exams/{exam_id}", data={"exam": json.dumps(exam_update_data)}
    )
    assert res.status_code == 200
    updated_exam_response = res.json()
    updated_choice_text = next(
        (
            choice["option"]
            for topic in updated_exam_response["topics"]
            for question in topic["questions"]
            for choice in question["choices"]
            if choice["id"] == choice_id
        ),
        None,
    )
    assert (
        updated_choice_text == new_choice_data["option"]
    ), "Choice text not updated as expected"


def test_delete_topic(authorized_examiner, test_exam):
    topic_id = str(test_exam["topics"][0]["id"])
    res = authorized_examiner.delete(f"exams/topics/{topic_id}")
    assert res.status_code == 204


def test_delete_question(authorized_examiner, test_exam):
    question_id = str(test_exam["topics"][0]["questions"][0]["id"])
    res = authorized_examiner.delete(f"exams/question/{question_id}")
    assert res.status_code == 204


def test_delete_choice(authorized_examiner, test_exam):
    choice_id = str(test_exam["topics"][0]["questions"][0]["choices"][0]["id"])
    res = authorized_examiner.delete(f"exams/choice/{choice_id}")
    assert res.status_code == 204


def test_delete_exam(authorized_examiner, test_exam):
    exam_id = str(test_exam["id"])
    res = authorized_examiner.delete(f"/exams/{exam_id}")
    assert res.status_code == 204
    res = authorized_examiner.get(f"/exams/{exam_id}")
    assert res.status_code == 404
