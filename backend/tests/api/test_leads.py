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


def test_create_lead_triggers_email_notifications(client, monkeypatch):
    from app.services import email_notifications

    notified = []
    monkeypatch.setattr(
        email_notifications,
        "send_lead_notifications",
        notified.append,
    )

    response = create_lead(client)

    assert response.status_code == 201
    assert len(notified) == 1
    assert notified[0].email == "ada@example.com"


def test_create_lead_accepts_docx(client):
    response = create_lead(
        client,
        resume_bytes=make_docx_bytes(),
        resume_filename="resume.docx",
        resume_content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert response.status_code == 201


def test_create_lead_rejects_bad_extension(client):
    files = {"resume": ("resume.exe", io.BytesIO(b"nope"), "application/octet-stream")}
    response = client.post(
        "/api/leads",
        data={"first_name": "Bad", "last_name": "File", "email": "bad@example.com"},
        files=files,
    )
    assert response.status_code == 400


def test_create_lead_rejects_invalid_email(client):
    response = create_lead(client, email="not-an-email")
    assert response.status_code == 422


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
