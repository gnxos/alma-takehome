# Coding Agent Usage & Attribution

A summary of how AI coding agents were leveraged during the development of this project.

---

## 1. Tools & Setup
- **Coding Assistant**: Antigravity / Claude 3.7 & Gemini Coding Agent.
- **Workflow**: Iterative pair programming with human architectural oversight, code review, automated testing (`pytest`), and Docker verification.

---

## 2. Delegation Strategy

### What was delegated to the Agent:
- Scaffolded FastAPI endpoint boilerplate and SQLAlchemy session dependencies.
- Next.js UI component layouts, Tailwind styling, and form state hooks.
- Test suites (`backend/tests`) for API routes, email mocking, and validators.
- Docker Compose configuration for Mailpit, FastAPI, and Next.js.

### What was human-guided & reviewed:
- **Collision Resistance**: Identifying the vulnerability in 4-digit random IDs (`random.randint(1000, 9999)`) and directing the migration to **Crockford Base32 CSPRNG** (`INT-YYYY-XXXXXX`).
- **Template Architecture**: Refactoring verbose Python template modules into clean, human-editable **JSON templates** (`prospect.json` and `attorney.json`).
- **Database Hygiene**: Removing redundant legacy fields from migration scripts to keep the schema strictly aligned with the domain model.
- **Production Readiness**: Defining clear separation between local dev (SQLite, Local Disk, Mailpit) and production cloud services (MySQL RDS, AWS S3, Resend).

---

## 3. Caught & Fixed: Subtly Bad Code Example

### The Issue: Fragile Ticket ID Generation
- **What the agent initially had**:
  ```python
  def generate_reference_number() -> str:
      year = datetime.now(timezone.utc).year
      digits = random.randint(1000, 9999)
      return f"INT-{year}-{digits}"
  ```
- **Why it was flawed**:
  With only 9,000 possible IDs per year, the Birthday Paradox causes a **50% collision probability after just 118 leads**. Under real traffic, the database retry loop would exhaust its attempts and throw 500 errors.
- **How it was caught & fixed**:
  During human code review of `reference_numbers.py`, the entropy was analyzed. It was rewritten to use Python's cryptographically secure `secrets` module and Crockford's Base32 alphabet (32^6 = 1,073,741,824 combinations/year), eliminating visual confusion (`I`, `L`, `O`, `U`) and reducing collision probability to near zero.

---

## 4. Representative Prompt Excerpts

```text
Human: "review the email service and give me steps to run it in local."
Agent: [Analyzed smtplib transport, Mailpit integration, and created step-by-step local test instructions]

Human: "this is very vague way of generating Id that can create duplicates, make it better"
Agent: [Refactored to 6-char Crockford Base32 CSPRNG with 1.07B combinations/year and updated test suites]

Human: "and also its lot of code i was expecting kind of json template instead of .py"
Agent: [Replaced 4 python template files with clean JSON templates in templates/ directory and updated renderer]
```

---

## 5. Attribution Summary (NOTES)
- **Agent-Generated**: UI component scaffolding, standard CRUD routes, initial test definitions, Dockerfile templates.
- **Human-Directed / Refactored**: Security and sanitization (`html.escape`), CSPRNG ID generation, JSON template structure, schema migrations, and documentation.
