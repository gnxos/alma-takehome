import io

import docx
from pypdf import PdfWriter

GARBAGE_BYTES = b"this is not a real office document, just filler text" * 5


def create_lead(client, **overrides):
    data = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        **overrides,
    }
    resume_bytes = data.pop("resume_bytes", make_pdf_bytes())
    resume_filename = data.pop("resume_filename", "resume.pdf")
    resume_content_type = data.pop("resume_content_type", "application/pdf")
    files = {
        "resume": (
            resume_filename,
            io.BytesIO(resume_bytes),
            resume_content_type,
        )
    }
    return client.post("/api/leads", data=data, files=files)


def make_pdf_bytes(*, pages: int = 1, password: str | None = None) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=72, height=72)
    if password:
        writer.encrypt(user_password=password)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def make_docx_bytes(text: str = "Resume content") -> bytes:
    buf = io.BytesIO()
    document = docx.Document()
    document.add_paragraph(text)
    document.save(buf)
    return buf.getvalue()
