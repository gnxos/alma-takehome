# Architecture & Design Decisions

A brief overview of the key design choices made in this application.

---

## 1. System Overview

```
Frontend (Next.js :3000)
       │
       ▼ (REST API)
Backend (FastAPI :8000)
  ├── Database : SQLite (Local) / MySQL RDS (Prod)
  ├── Storage  : Local Disk (Local) / AWS S3 (Prod)
  └── Email    : Mailpit (Local) / Resend (Prod)
```

---

## 2. Key Decisions & Rationale

### 📧 Email Service (Mailpit vs. Resend)
- **Local Dev**: Uses **Mailpit** (local SMTP on port `1025`, web UI on `http://localhost:8025`). Zero API keys required and no risk of emailing real users.
- **Production**: Uses **Resend** via API key and verified sending domain.
- **Async Execution**: Emails are sent via FastAPI background tasks so form submissions return instantly (<100ms) even if SMTP is slow.
- **Status Tracking**: Delivery outcomes (`SENT` or `FAILED`) are saved on the lead record.

### 🗄️ Database (SQLite vs. MySQL)
- **Local Dev**: **SQLite** (`leads.db`) for instant zero-configuration setup.
- **Production**: **MySQL** (AWS RDS / Aurora) with connection pooling for concurrent traffic and automated backups.

### 📁 File Storage (Local Disk vs. AWS S3)
- **Local Dev**: Uploads saved to `./uploads/` with UUID filenames.
- **Production**: Uploads stream to **AWS S3** private buckets, accessed via short-lived presigned URLs for attorney downloads.
- **File Validation**: Files are checked for real PDF/DOCX headers (rejects password-protected, corrupted, or empty files).

### 🏷️ Ticket IDs (`INT-YYYY-XXXXXX`)
- Changed from 4 random digits to a **6-character Crockford Base32** suffix using cryptographically secure `secrets`.
- **Why**: 4 digits had only 9,000 combinations (colliding at ~118 leads). The 6-character format provides over **1 billion** unique IDs per year and avoids confusing characters (`I`, `L`, `O`, `U`).
- Included in both the prospect confirmation email and attorney notification.

### 🔄 Lead Lifecycle & De-duplication
- If a prospect submits again while their lead is still **`PENDING`**, the API returns their existing ticket.
- Once marked **`REACHED_OUT`**, new submissions create a fresh ticket.

---

## 3. Local vs. Production Summary

| Component | Local Dev | Production |
| :--- | :--- | :--- |
| **Database** | SQLite (`leads.db`) | MySQL (AWS RDS / Aurora) |
| **Storage** | Local Disk (`./uploads`) | AWS S3 (Private Bucket + Presigned URLs) |
| **Email** | Mailpit (`localhost:1025` / `:8025`) | Resend API |
| **Frontend** | Next.js (`localhost:3000`) | Next.js on Vercel / AWS ECS |
| **Backend** | FastAPI (`localhost:8000`) | FastAPI on AWS ECS / Fargate |
