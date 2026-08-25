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
import { Button } from "@/components/Button";
import { FileUpload } from "@/components/FileUpload";
import type { LeadCreateResult } from "@/lib/types";

interface FieldErrors {
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  resume?: string | null;
}

export default function SubmitLeadPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LeadCreateResult | null>(null);

  function validateFirstNameField(value: string) {
    const err = validateName(normalizeName(value), "First name");
    setFieldErrors((prev) => ({ ...prev, firstName: err }));
    return err;
  }

  function validateLastNameField(value: string) {
    const err = validateName(normalizeName(value), "Last name");
    setFieldErrors((prev) => ({ ...prev, lastName: err }));
    return err;
  }

  function validateEmailField(value: string) {
    const err = validateEmail(normalizeEmail(value));
    setFieldErrors((prev) => ({ ...prev, email: err }));
    return err;
  }

  function validateResumeField(file: File | null) {
    const err = file ? validateResumeFile(file) : "Please attach your resume/CV.";
    setFieldErrors((prev) => ({ ...prev, resume: err }));
    return err;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const firstNameError = validateFirstNameField(firstName);
    const lastNameError = validateLastNameField(lastName);
    const emailError = validateEmailField(email);
    const resumeError = validateResumeField(resume);
    if (firstNameError || lastNameError || emailError || resumeError || !resume) {
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const created = await createLead({
        first_name: normalizeName(firstName),
        last_name: normalizeName(lastName),
        email: normalizeEmail(email),
        resume,
      });
      setResult(created);
    } catch {
      setError(
        "Something went wrong on our end — your information hasn't been sent yet. Try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-paper-50 font-sans lg:flex-row">
      <div className="flex flex-col justify-center px-6 py-12 sm:px-10 lg:w-[440px] lg:shrink-0 lg:bg-paper-100 lg:px-16 lg:py-16">
        <span className="text-heading-md font-bold tracking-tight text-ink-900">
          alma
        </span>

        <span className="mt-10 text-label-sm text-brass-500">Get started</span>
        <h1 className="mt-2 text-display-lg font-serif text-ink-900">
          Tell us about your case.
        </h1>
        <p className="mt-4 text-body-md text-ink-700">
          An attorney will review your information and follow up by email.
        </p>
      </div>

      <div className="flex flex-1 items-start justify-center px-6 py-10 sm:px-10 lg:items-center lg:py-16">
        <div className="w-full max-w-[480px]">
          {result ? (
            <div className="rounded-card bg-paper-0 p-8 shadow-card sm:p-8">
              <h2 className="text-display-md font-serif text-ink-900">
                {result.already_exists
                  ? "You already have an application in progress."
                  : "Your application is in."}
              </h2>
              <p className="mt-3 text-mono-sm font-mono-alma text-brass-500">
                Reference {result.reference_number}
              </p>
              <p className="mt-4 text-body-md text-ink-700">
                {result.already_exists
                  ? `We found an existing application for ${result.email}. An attorney will reach out from here — no need to submit again.`
                  : `We've sent a copy to ${result.email}. An attorney will reach out from here.`}
              </p>
            </div>
          ) : (
            <div className="rounded-card bg-paper-0 p-5 shadow-card sm:p-8">
              {error && (
                <p className="mb-6 rounded-input bg-brick-50 px-4 py-3 text-body-sm text-brick-600">
                  {error}
                </p>
              )}

              <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
                <Field label="First name" error={fieldErrors.firstName}>
                  <input
                    maxLength={NAME_MAX_LENGTH}
                    value={firstName}
                    onChange={(e) => {
                      setFirstName(e.target.value);
                      if (fieldErrors.firstName)
                        setFieldErrors((p) => ({ ...p, firstName: null }));
                    }}
                    onBlur={(e) => validateFirstNameField(e.target.value)}
                    className={`field-input ${fieldErrors.firstName ? "field-input-error" : ""}`}
                  />
                </Field>
                <Field label="Last name" error={fieldErrors.lastName}>
                  <input
                    maxLength={NAME_MAX_LENGTH}
                    value={lastName}
                    onChange={(e) => {
                      setLastName(e.target.value);
                      if (fieldErrors.lastName)
                        setFieldErrors((p) => ({ ...p, lastName: null }));
                    }}
                    onBlur={(e) => validateLastNameField(e.target.value)}
                    className={`field-input ${fieldErrors.lastName ? "field-input-error" : ""}`}
                  />
                </Field>
                <Field label="Email" error={fieldErrors.email}>
                  <input
                    type="email"
                    maxLength={EMAIL_MAX_LENGTH}
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (fieldErrors.email) setFieldErrors((p) => ({ ...p, email: null }));
                    }}
                    onBlur={(e) => validateEmailField(e.target.value)}
                    className={`field-input ${fieldErrors.email ? "field-input-error" : ""}`}
                  />
                </Field>
                <Field label="Resume / CV">
                  <FileUpload
                    file={resume}
                    accept=".pdf,.doc,.docx"
                    error={fieldErrors.resume}
                    onFileChange={(file) => {
                      setResume(file);
                      validateResumeField(file);
                    }}
                  />
                </Field>

                <Button type="submit" fullWidth loading={submitting} className="mt-2">
                  {submitting ? "Submitting..." : "Submit application"}
                </Button>

                <p className="text-center text-body-sm text-ink-400">
                  By submitting, you agree to our{" "}
                  <span className="text-ink-700 underline">Terms of Service</span> and{" "}
                  <span className="text-ink-700 underline">Privacy Policy</span>.
                </p>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string | null;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-label-sm text-ink-700">{label}</span>
      {children}
      {error && <span className="text-body-sm text-brick-600">{error}</span>}
    </label>
  );
}
