import uuid


def test_get_all_request_exams(authorized_examiner):
    res = authorized_examiner.get("/request_exam")
    assert res.status_code == 200
    request_exam = res.json()
    assert isinstance(request_exam, list)


def test_get_all_request_exams_not_authorized(client):
    res = client.get("/request_exam")
    assert res.status_code == 401


def test_get_request_exam_by_id(authorized_examiner, test_request_exam):
    id = str(test_request_exam["id"])
    res = authorized_examiner.get(f"/request_exam/{id}")
    assert res.status_code == 200
    request_exam = res.json()
    assert request_exam["id"] == id


def test_get_request_exam_by_id_not_authorized(client, test_request_exam):
    id = str(test_request_exam["id"])
    res = client.get(f"/request_exam/{id}")
    assert res.status_code == 401


def test_get_request_exam_not_exist(authorized_examiner):
    non_existent_uuid = uuid.uuid4()
    res = authorized_examiner.get(f"/request_exam/{non_existent_uuid}")
    assert res.status_code == 404


def test_create_request_exam(authorized_examinee, test_exam):
    request_exam = str(test_exam["id"])
    res = authorized_examinee.post(f"/request_exam/?request_exam={request_exam}")
    assert res.status_code == 201
    new_request_exam = res.json()
    assert new_request_exam["exam_id"] == request_exam
    user_id = new_request_exam["examinee"]["id"]
    authorized_examinee.user_id = user_id
    assert new_request_exam["examinee"]["id"] == authorized_examinee.user_id


def test_create_request_exam_unauthorized(client, test_exam):
    request_exam = str(test_exam["id"])
    res = client.post(f"/request_exam/?request_exam={request_exam}")
    assert res.status_code == 401


def test_create_request_exam_nonexistent_exam(authorized_examinee):
    non_existent_uuid = uuid.uuid4()
    res = authorized_examinee.post(f"/request_exam/?request_exam={non_existent_uuid}")
    assert res.status_code == 404
    assert res.json() == {"detail": f"Exam with id {non_existent_uuid} does not found"}


def test_create_request_exam_duplicate_request(authorized_examinee, test_exam):
    request_exam = str(test_exam["id"])
    res = authorized_examinee.post(f"/request_exam/?request_exam={request_exam}")
    assert res.status_code == 201
    res = authorized_examinee.post(f"/request_exam/?request_exam={request_exam}")
    assert res.status_code == 400
    assert res.json() == {"detail": "You have already requested this exam."}


def test_approve_exam_request(authorized_examiner, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = authorized_examiner.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 200
    updated_examinee = res.json()
    assert updated_examinee["exam_ids"] == [test_request_exam["exam_id"]]


def test_approve_exam_request_not_authorized(client, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = client.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 401


def test_approve_exam_request_no_permission(authorized_examinee, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = authorized_examinee.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 403


def test_approve_nonexistent_exam_request(authorized_examiner):
    non_existent_uuid = uuid.uuid4()
    res = authorized_examiner.put(f"/request_exam/{non_existent_uuid}")
    assert res.status_code == 404
    assert res.json() == {
        "detail": f"Exam request with id {non_existent_uuid} does not found"
    }


def test_approve_already_approved_exam_request(authorized_examiner, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = authorized_examiner.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 200
    res = authorized_examiner.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 400
    assert res.json() == {"detail": "This exam request has already been approved."}


def test_delete_exam_request(authorized_examiner, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = authorized_examiner.delete(f"/request_exam/{request_exam_id}")
    assert res.status_code == 204


def test_delete_exam_request_not_authorized(client, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = client.put(f"/request_exam/{request_exam_id}")
    assert res.status_code == 401


def test_delete_nonexistent_exam_request(authorized_examiner):
    non_existent_uuid = uuid.uuid4()
    res = authorized_examiner.delete(f"/request_exam/{non_existent_uuid}")
    assert res.status_code == 404
    assert res.json() == {
        "detail": f"Exam request with id {non_existent_uuid} does not found"
    }


def test_delete_exam_request_not_owned_by_user(authorized_examinee, test_request_exam):
    request_exam_id = str(test_request_exam["id"])
    res = authorized_examinee.delete(f"/request_exam/{request_exam_id}")
    assert res.status_code == 403
    assert res.json() == {
        "detail": "You do not have permission to delete this exam request"
    }
