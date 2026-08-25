# How to Run Locally

A simple guide to running and testing the application on your computer.

---

## ⚡ Option 1: Using Docker (Recommended)

Run everything (Frontend, Backend, and Email Server) with one command:

```bash
docker compose up --build
```

### Where to go:
- **Public Form**: [http://localhost:3000](http://localhost:3000) (submit a new lead)
- **Attorney Login**: [http://localhost:3000/login](http://localhost:3000/login)
  - **Email**: `attorney@alma.example.com`
  - **Password**: `Alma123!`
- **Email Inbox (Mailpit)**: [http://localhost:8025](http://localhost:8025) (see all sent emails)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Option 2: Running Without Docker

If you prefer to run services manually, open 3 terminal windows:

### Terminal 1: Email Server (Mailpit)
```bash
docker run -d -p 1025:1025 -p 8025:8025 axllent/mailpit
```
*(Or on macOS with Homebrew: `brew install mailpit && mailpit`)*

### Terminal 2: Backend (Python FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 3: Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 How to Test the Flow

1. **Submit a Lead**:
   - Go to [http://localhost:3000](http://localhost:3000).
   - Fill in the form with a name, email (e.g. `yourname@gmail.com`), and upload a `.pdf` or `.docx` resume.
   - Click **Submit**. You will see your ticket reference number (e.g., `INT-2026-XXXXXX`).

2. **Check the Emails**:
   - Go to [http://localhost:8025](http://localhost:8025) (Mailpit).
   - You will see two emails:
     1. **Prospect Confirmation** (contains the ticket reference number).
     2. **Attorney Notification** (contains full lead details).

3. **Check the Attorney Dashboard**:
   - Go to [http://localhost:3000/login](http://localhost:3000/login).
   - Log in with `attorney@alma.example.com` / `Alma123!`.
   - View submitted leads, download uploaded resumes, and update lead status to **Reached Out**.

---

## 🧪 Running Automated Tests

To run the backend test suite:

```bash
cd backend
./venv/bin/pytest
```
