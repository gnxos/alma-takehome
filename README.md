# Lead Management

A small application for managing prospect leads: a public form for prospects to submit
their information and resume/CV, and an internal view for listing, viewing, and updating
leads.

- `backend/` — FastAPI + SQLAlchemy (SQLite) API
- `frontend/` — Next.js (App Router, TypeScript, Tailwind) web app

## Project structure

The application is organized by responsibility so framework entry points stay
small and domain code remains independently testable.

```text
backend/app/
├── api/             # FastAPI router composition and HTTP route handlers
├── core/            # Environment configuration and authentication primitives
├── database/        # SQLAlchemy base, engine, sessions, and dependencies
├── models/          # Database entities and enums
├── repositories/    # Persistence queries and mutations
├── schemas/         # Pydantic request and response contracts
├── services/        # Email, upload storage, and content validation
├── templates/       # Prospect and attorney email rendering
└── main.py          # Application factory and middleware setup

backend/tests/
├── api/             # Auth and lead endpoint integration tests
├── database/        # Schema initialization and compatibility migration tests
├── repositories/    # Persistence and reference-collision integration tests
└── services/        # Email and resume validation unit tests

frontend/src/
├── app/             # Next.js route entry points and root layout only
├── components/      # Shared layout and UI primitives
├── features/        # Auth, intake, and lead-management feature modules
└── lib/             # Feature-agnostic infrastructure such as the API client
```

Backend dependencies flow from routes to repositories/services, then to models
and database infrastructure. Frontend routes compose feature components; each
feature owns its API adapter, types, hooks, validation, and UI where applicable.

## Docker

The fastest way to run everything:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000` (docs at `/docs`)
- Mailpit: `http://localhost:8025` (local email inbox; SMTP on port `1025`)

The backend's SQLite database and uploaded resumes persist in named Docker
volumes (`backend_data`, `backend_uploads`) across restarts.

`NEXT_PUBLIC_API_URL` is baked into the frontend at build time (it runs in the
browser, so it must be a host-reachable URL, not a Docker-internal hostname).
If you change the backend's host/port, rebuild the frontend with that value:

```bash
docker compose build --build-arg NEXT_PUBLIC_API_URL=http://your-host:8000 frontend
```

## Backend (without Docker)

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

Config is read from environment variables (see `.env.example`): `DATABASE_URL`,
`UPLOAD_DIR`, `CORS_ORIGINS`, `RESEND_API_KEY`, `EMAIL_FROM`, `ATTORNEY_EMAIL`,
`FRONTEND_URL`, `EMAIL_BACKEND`, `SMTP_HOST`, `SMTP_PORT`,
`ATTORNEY_PASSWORD`, and `JWT_SECRET`.

Run tests:

```bash
./venv/bin/pytest
```

### API

| Method | Path                     | Auth      | Description                                   |
| ------ | ------------------------ | --------- | ---------------------------------------------- |
| POST   | `/api/leads`              | Public    | Create a lead (multipart form + resume file)  |
| GET    | `/api/leads`               | Attorney  | List leads (`status_filter`, `skip`, `limit`) |
| GET    | `/api/leads/{identifier}`   | Attorney  | Get a lead by ID or reference number          |
| PATCH  | `/api/leads/{identifier}`   | Attorney  | Update a lead's fields/status                 |
| GET    | `/api/leads/{identifier}/resume` | Attorney | Download the lead's resume                 |
| POST   | `/login`                    | Public    | Log in, sets an httpOnly session cookie       |
| POST   | `/logout`                   | Public    | Clears the session cookie                     |
| GET    | `/auth/me`                   | Attorney  | Current attorney's email                      |

A lead requires `first_name`, `last_name`, `email`, and a single `resume` file
(`.pdf`, `.doc`, or `.docx`, 100 bytes–10MB). New leads start with status
`PENDING`, receive an `INT-YYYY-NNNN` reference number, and can be transitioned
to `REACHED_OUT`. A repeat submission for the same normalized email returns the
existing lead instead of creating a duplicate ticket.

**Name fields** are trimmed, collapse repeated inner whitespace to a single
space, must be 2–36 characters, support unicode letters, and reject digits
and symbols.

**Email** is trimmed, structurally validated, capped at 100 characters,
rejects embedded spaces/line breaks, has its domain (but not local part)
lowercased, and must resolve to a domain with an MX (or fallback A) DNS
record — so this endpoint depends on outbound DNS access.

**Resume files** are checked for real content, not just their extension:
PDFs and DOCX files are opened and rejected if password-protected or
unreadable/corrupted; legacy DOC/DOCX encryption is detected via its OLE
container structure. Only one file may be uploaded per submission.

### Email notifications

After a lead and its resume have been validated, stored, and committed, a
FastAPI `BackgroundTask` attempts two independent messages:

1. `We received your information` goes to the validated prospect address.
2. `New lead: {first_name} {last_name}` goes to `ATTORNEY_EMAIL` and links to
   `FRONTEND_URL/admin/leads/{lead_id}`.

Neither email attaches the resume. The attorney downloads it from the
authenticated dashboard. If either delivery fails, the other is still
attempted and the committed lead remains `PENDING`; provider errors are logged
without logging the API key.

Set `EMAIL_BACKEND=resend` and configure `RESEND_API_KEY` plus a verified
`EMAIL_FROM` address for production. The implementation uses Resend's Python
SDK. If the Resend key is missing, the service logs a safe
`DEV EMAIL - NOT DELIVERED` preview instead of crashing.

#### Local email testing with Mailpit

Mailpit captures both messages locally and never sends them to the internet.
It is included in `docker-compose.yml` and uses the standard SMTP port `1025`
and web UI port `8025`.

For the full Docker stack:

```bash
docker compose up --build
```

For a backend running directly on port `8001`, start only Mailpit and place
these non-secret values in the ignored `backend/.env` file:

```bash
docker compose up -d --wait mailpit

EMAIL_BACKEND=smtp
SMTP_HOST=localhost
SMTP_PORT=1025
EMAIL_FROM=Lead Team <leads@example.test>
ATTORNEY_EMAIL=attorney@example.com
FRONTEND_URL=http://localhost:3000
RESEND_API_KEY=
```

Then run:

```bash
cd backend
./.venv/bin/uvicorn app.main:app --reload --port 8001
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8001` in `frontend/.env.local`, run
the frontend on port `3000`, submit a valid lead, and inspect both captured
messages at `http://localhost:8025`. The attorney link should redirect an
unauthenticated browser to `/login`; after sign-in it opens that lead in the
internal dashboard. Incorrect SMTP/Resend settings must not change or duplicate
the stored lead.

### Attorney authentication

The internal dashboard (`GET`/`PATCH` on `/api/leads*`) requires a logged-in
attorney session. There's a single hardcoded attorney account, configured via
`ATTORNEY_EMAIL` / `ATTORNEY_PASSWORD` (defaults: `attorney@alma.example.com`
/ `Alma123!` — override both for anything beyond local dev).

`POST /login` checks the submitted credentials with a timing-safe comparison
and, on success, sets a JWT (`JWT_SECRET`, `HS256`, `JWT_EXPIRE_MINUTES`) as
an httpOnly cookie — invalid credentials return `401`. `POST /logout` clears
that cookie. `GET /auth/me` returns the current attorney's email, or `401` if
the cookie is missing, invalid, or expired.

## Frontend (without Docker)

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Runs at `http://localhost:3000`.

- `/` — public lead submission form
- `/login` — attorney sign-in
- `/leads` — internal dashboard with status filters and a lead detail drawer (redirects to `/login` if not authenticated)
- `/leads?ref=INT-YYYY-NNNN` — opens the matching lead directly in the dashboard
- `/admin/leads/{lead_id}` — protected email entry point for a specific lead
