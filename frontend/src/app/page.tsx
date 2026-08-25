"use client";

import { FormEvent, useState } from "react";
import { createLead } from "@/lib/api";
import {
  EMAIL_MAX_LENGTH,
  NAME_MAX_LENGTH,
  normalizeEmail,
  normalizeName,
  validateEmail,
  validateName,
  validateResumeFile,
} from "@/lib/validation";

export default function SubmitLeadPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!resume) {
      setError("Please attach your resume/CV.");
      return;
    }

    const normalizedFirstName = normalizeName(firstName);
    const normalizedLastName = normalizeName(lastName);
    const normalizedEmail = normalizeEmail(email);
    const validationError =
      validateName(normalizedFirstName, "First name") ??
      validateName(normalizedLastName, "Last name") ??
      validateEmail(normalizedEmail) ??
      validateResumeFile(resume);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await createLead({
        first_name: normalizedFirstName,
        last_name: normalizedLastName,
        email: normalizedEmail,
        resume,
      });
      setSuccess(true);
      setFirstName("");
      setLastName("");
      setEmail("");
      setResume(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className="mx-auto max-w-md px-6 py-16 text-center">
        <h1 className="text-2xl font-semibold">Thanks for applying!</h1>
        <p className="mt-2 text-sm text-black/60 dark:text-white/60">
          We&apos;ve received your information and will be in touch soon.
        </p>
        <button
          className="mt-6 text-sm underline"
          onClick={() => setSuccess(false)}
        >
          Submit another response
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-2xl font-semibold">Get Started</h1>
      <p className="mt-2 text-sm text-black/60 dark:text-white/60">
        Tell us about yourself and attach your resume/CV.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
        <Field label="First name">
          <input
            required
            maxLength={NAME_MAX_LENGTH}
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Last name">
          <input
            required
            maxLength={NAME_MAX_LENGTH}
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Email">
          <input
            required
            type="email"
            maxLength={EMAIL_MAX_LENGTH}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Resume / CV (PDF or Word, max 10MB)">
          <input
            required
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setResume(e.target.files?.[0] ?? null)}
            className="input file:mr-3 file:rounded-md file:border-0 file:bg-black/5 file:px-3 file:py-1.5 file:text-sm dark:file:bg-white/10"
          />
        </Field>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 rounded-md bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          {submitting ? "Submitting..." : "Submit"}
        </button>
      </form>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium">{label}</span>
      {children}
    </label>
  );
}
