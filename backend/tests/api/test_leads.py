import io
import re

from app.core import config
from tests.factories import GARBAGE_BYTES, create_lead, make_docx_bytes, make_pdf_bytes

REFERENCE_NUMBER_RE = re.compile(r"^INT-\d{4}-\d{4}$")


def test_create_lead_success(client):
    response = create_lead(client)
    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Ada"
    assert body["email"] == "ada@example.com"
    assert body["status"] == "PENDING"
    assert body["resume_filename"] == "resume.pdf"
    assert REFERENCE_NUMBER_RE.match(body["reference_number"])
    assert body["already_exists"] is False


def test_create_lead_returns_existing_ticket_for_duplicate_email(client):
    first = create_lead(client, email="dupe@example.com").json()

    second_response = create_lead(
        client, email="dupe@example.com", first_name="Someone", last_name="Else"
    )

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["already_exists"] is True
    assert second["id"] == first["id"]
    assert second["reference_number"] == first["reference_number"]
    # The original record is untouched — not overwritten by the second submission.
    assert second["first_name"] == "Ada"


def test_create_lead_allows_new_submission_when_previous_status_is_reached_out(client):
    # 1. First submission (PENDING)
    first_response = create_lead(client, email="candidate@example.com")
    assert first_response.status_code == 201
    first = first_response.json()
    assert first["status"] == "PENDING"
    assert first["already_exists"] is False

    # 2. Re-submitting while PENDING should return existing ticket
    dupe_response = create_lead(client, email="candidate@example.com")
    assert dupe_response.status_code == 200
    assert dupe_response.json()["id"] == first["id"]
    assert dupe_response.json()["already_exists"] is True

    # 3. Attorney reaches out (status updated to REACHED_OUT)
    update_response = client.patch(
        f"/api/leads/{first['id']}", json={"status": "REACHED_OUT"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "REACHED_OUT"

    # 4. Now the user should be able to submit a new ticket again
    new_response = create_lead(
        client,
        email="candidate@example.com",
        first_name="Ada",
        last_name="Byron",
    )
    assert new_response.status_code == 201
    new_ticket = new_response.json()
    assert new_ticket["already_exists"] is False
    assert new_ticket["id"] != first["id"]
    assert new_ticket["reference_number"] != first["reference_number"]
    assert new_ticket["status"] == "PENDING"
    assert new_ticket["last_name"] == "Byron"


def test_get_lead_by_reference_number(client):
    created = create_lead(client).json()
    response = client.get(f"/api/leads/{created['reference_number']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_lead_by_reference_number(client):
    created = create_lead(client).json()
    response = client.patch(
        f"/api/leads/{created['reference_number']}", json={"status": "REACHED_OUT"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REACHED_OUT"


def test_download_resume_by_reference_number(client):
    resume_bytes = make_pdf_bytes()
    created = create_lead(client, resume_bytes=resume_bytes).json()
    response = client.get(f"/api/leads/{created['reference_number']}/resume")
    assert response.status_code == 200
    assert response.content == resume_bytes


def test_create_lead_triggers_both_email_methods(client, email_service):
    response = create_lead(client)

    assert response.status_code == 201
    email_service.send_prospect_confirmation.assert_called_once()
    email_service.send_attorney_notification.assert_called_once()
    prospect_lead = email_service.send_prospect_confirmation.call_args.args[0]
    attorney_lead = email_service.send_attorney_notification.call_args.args[0]
    assert prospect_lead.id == response.json()["id"]
    assert prospect_lead.email == "ada@example.com"
    assert attorney_lead.id == prospect_lead.id


def test_create_lead_accepts_docx(client):
    response = create_lead(
        client,
        resume_bytes=make_docx_bytes(),
        resume_filename="resume.docx",
        resume_content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert response.status_code == 201


def test_create_lead_rejects_bad_extension(client, email_service):
    files = {"resume": ("resume.exe", io.BytesIO(b"nope"), "application/octet-stream")}
    response = client.post(
        "/api/leads",
        data={"first_name": "Bad", "last_name": "File", "email": "bad@example.com"},
        files=files,
    )
    assert response.status_code == 400
    email_service.send_prospect_confirmation.assert_not_called()
    email_service.send_attorney_notification.assert_not_called()


def test_create_lead_rejects_invalid_email(client, email_service):
    response = create_lead(client, email="not-an-email")
    assert response.status_code == 422
    email_service.send_prospect_confirmation.assert_not_called()
    email_service.send_attorney_notification.assert_not_called()


def test_create_lead_rejects_missing_resume_without_sending_email(
    client, email_service
):
    response = client.post(
        "/api/leads",
        data={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
        },
    )

    assert response.status_code == 422
    email_service.send_prospect_confirmation.assert_not_called()
    email_service.send_attorney_notification.assert_not_called()


def test_database_failure_cleans_upload_and_does_not_send_email(
    client, email_service, monkeypatch
):
    from app.repositories import leads as lead_repository

    def fail_to_create(*args, **kwargs):
        raise RuntimeError("db failed")

    monkeypatch.setattr(lead_repository, "create", fail_to_create)

    response = create_lead(client)

    assert response.status_code == 500
    assert response.json()["detail"] == "Could not save lead"
    assert list(config.UPLOAD_DIR.iterdir()) == []
    email_service.send_prospect_confirmation.assert_not_called()
    email_service.send_attorney_notification.assert_not_called()


def test_email_failure_keeps_single_pending_lead_and_attempts_second_email(
    client, email_service, caplog
):
    api_key = "re_must_not_appear_in_logs"
    email_service.send_prospect_confirmation.side_effect = RuntimeError(api_key)

    with caplog.at_level("ERROR"):
        response = create_lead(client, email="delivery-failure@example.com")

    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "PENDING"
    email_service.send_prospect_confirmation.assert_called_once()
    email_service.send_attorney_notification.assert_called_once()
    assert api_key not in caplog.text

    duplicate = create_lead(client, email="delivery-failure@example.com")
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == created["id"]
    listing = client.get("/api/leads").json()
    assert listing["total"] == 1


def test_create_lead_rejects_name_too_short(client):
    response = create_lead(client, first_name="A")
    assert response.status_code == 422


def test_create_lead_rejects_name_too_long(client):
    response = create_lead(client, first_name="A" * 37)
    assert response.status_code == 422


def test_create_lead_allows_name_at_length_boundaries(client):
    response = create_lead(client, first_name="Al", last_name="B" * 36)
    assert response.status_code == 201


def test_create_lead_rejects_digits_in_name(client):
    response = create_lead(client, first_name="Jane3")
    assert response.status_code == 422


def test_create_lead_rejects_blank_name(client):
    response = create_lead(client, first_name="   ")
    assert response.status_code == 422


def test_create_lead_trims_and_collapses_name_spacing(client):
    response = create_lead(
        client, first_name="  gn   teja  ", last_name="  van   Der  Berg "
    )
    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "gn teja"
    assert body["last_name"] == "van Der Berg"


def test_create_lead_supports_unicode_names(client):
    response = create_lead(client, first_name="Müller", last_name="日本語")
    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Müller"
    assert body["last_name"] == "日本語"


def test_create_lead_trims_and_lowercases_email_domain(client):
    response = create_lead(client, email="  Ada.Lovelace@EXAMPLE.COM  ")
    assert response.status_code == 201
    assert response.json()["email"] == "Ada.Lovelace@example.com"


def test_create_lead_rejects_email_too_long(client):
    long_local_part = "a" * 90
    response = create_lead(client, email=f"{long_local_part}@example.com")
    assert response.status_code == 422


def test_create_lead_rejects_email_with_internal_space(client):
    response = create_lead(client, email="ada lovelace@example.com")
    assert response.status_code == 422


def test_create_lead_rejects_domain_without_mx_or_a_record(client, monkeypatch):
    from app.services import email_validation

    monkeypatch.setattr(email_validation, "domain_has_mail_exchanger", lambda domain: False)
    response = create_lead(client, email="ada@no-mail-domain.example")
    assert response.status_code == 422


def test_create_lead_rejects_empty_resume(client):
    response = create_lead(client, resume_bytes=b"")
    assert response.status_code == 400


def test_create_lead_rejects_resume_below_min_size(client):
    response = create_lead(client, resume_bytes=b"%PDF-1.4", resume_filename="tiny.pdf")
    assert response.status_code == 400


def test_create_lead_rejects_resume_above_max_size(client):
    oversized = b"0" * (config.MAX_RESUME_SIZE_BYTES + 1)
    response = create_lead(client, resume_bytes=oversized, resume_filename="huge.pdf")
    assert response.status_code == 400


def test_create_lead_rejects_corrupted_pdf(client):
    response = create_lead(client, resume_bytes=GARBAGE_BYTES, resume_filename="fake.pdf")
    assert response.status_code == 400


def test_create_lead_rejects_password_protected_pdf(client):
    response = create_lead(
        client,
        resume_bytes=make_pdf_bytes(password="secret"),
        resume_filename="protected.pdf",
    )
    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()


def test_create_lead_rejects_corrupted_docx(client):
    response = create_lead(client, resume_bytes=GARBAGE_BYTES, resume_filename="fake.docx")
    assert response.status_code == 400


def test_create_lead_rejects_password_protected_docx(client, monkeypatch):
    from app.services import resume_validation

    monkeypatch.setattr(resume_validation, "is_office_file_encrypted", lambda f: True)
    response = create_lead(
        client,
        resume_bytes=make_docx_bytes(),
        resume_filename="protected.docx",
    )
    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()


def test_create_lead_rejects_multiple_resume_files(client):
    data = {"first_name": "Two", "last_name": "Files", "email": "two@example.com"}
    pdf_bytes = make_pdf_bytes()
    files = [
        ("resume", ("resume1.pdf", io.BytesIO(pdf_bytes), "application/pdf")),
        ("resume", ("resume2.pdf", io.BytesIO(pdf_bytes), "application/pdf")),
    ]
    response = client.post("/api/leads", data=data, files=files)
    assert response.status_code == 400


def test_get_lead(client):
    created = create_lead(client).json()
    response = client.get(f"/api/leads/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_lead_not_found(client):
    response = client.get("/api/leads/does-not-exist")
    assert response.status_code == 404


def test_list_leads_sorted_newest_first(client):
    first = create_lead(client, email="first@example.com").json()
    second = create_lead(client, email="second@example.com").json()
    response = client.get("/api/leads")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["id"] for item in body["items"]] == [second["id"], first["id"]]


def test_list_leads_by_email_returns_all_matching_tickets(client):
    first = create_lead(client, email="shared@example.com").json()
    second = create_lead(client, email="temporary@example.com").json()
    create_lead(client, email="different@example.com")
    updated_second = client.patch(
        f"/api/leads/{second['id']}",
        json={"email": "Shared@example.com"},
    )
    assert updated_second.status_code == 200

    response = client.get(
        "/api/leads/by-email",
        params={"email": " SHARED@EXAMPLE.COM "},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["id"] for item in body["items"]] == [second["id"], first["id"]]


def test_update_lead_status(client):
    created = create_lead(client).json()
    response = client.patch(f"/api/leads/{created['id']}", json={"status": "REACHED_OUT"})
    assert response.status_code == 200
    assert response.json()["status"] == "REACHED_OUT"


def test_update_lead_fields(client):
    created = create_lead(client).json()
    response = client.patch(
        f"/api/leads/{created['id']}",
        json={"first_name": "Augusta", "email": "augusta@example.com"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Augusta"
    assert body["email"] == "augusta@example.com"
    assert body["last_name"] == "Lovelace"


def test_update_lead_normalizes_name_spacing(client):
    created = create_lead(client).json()
    response = client.patch(
        f"/api/leads/{created['id']}", json={"first_name": "  gn   teja  "}
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "gn teja"


def test_update_lead_rejects_invalid_name(client):
    created = create_lead(client).json()
    response = client.patch(f"/api/leads/{created['id']}", json={"first_name": "A"})
    assert response.status_code == 422


def test_update_lead_rejects_invalid_email(client):
    created = create_lead(client).json()
    response = client.patch(f"/api/leads/{created['id']}", json={"email": "not-an-email"})
    assert response.status_code == 422


def test_download_resume(client):
    resume_bytes = make_pdf_bytes()
    created = create_lead(client, resume_bytes=resume_bytes).json()
    response = client.get(f"/api/leads/{created['id']}/resume")
    assert response.status_code == 200
    assert response.content == resume_bytes
