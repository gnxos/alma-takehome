"use client";

import { type FormEvent, type ReactNode, useState } from "react";

import { Button } from "@/components/ui/Button";
import { FileUpload } from "@/components/ui/FileUpload";
import { createLead } from "@/features/leads/api";
import type { LeadCreateResult } from "@/features/leads/types";
import {
  EMAIL_MAX_LENGTH,
  NAME_MAX_LENGTH,
  normalizeEmail,
  normalizeName,
  validateEmail,
  validateName,
  validateResumeFile,
} from "../validation";

interface FieldErrors {
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  resume?: string | null;
}

export function LeadSubmissionForm() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LeadCreateResult | null>(null);

  function validateFirstName(value: string) {
    const validationError = validateName(normalizeName(value), "First name");
    setFieldErrors((current) => ({
      ...current,
      firstName: validationError,
    }));
    return validationError;
  }

  function validateLastName(value: string) {
    const validationError = validateName(normalizeName(value), "Last name");
    setFieldErrors((current) => ({
      ...current,
      lastName: validationError,
    }));
    return validationError;
  }

  function validateEmailField(value: string) {
    const validationError = validateEmail(normalizeEmail(value));
    setFieldErrors((current) => ({
      ...current,
      email: validationError,
    }));
    return validationError;
  }

  function validateResume(file: File | null) {
    const validationError = file
      ? validateResumeFile(file)
      : "Please attach your resume/CV.";
    setFieldErrors((current) => ({
      ...current,
      resume: validationError,
    }));
    return validationError;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const firstNameError = validateFirstName(firstName);
    const lastNameError = validateLastName(lastName);
    const emailError = validateEmailField(email);
    const resumeError = validateResume(resume);
    if (firstNameError || lastNameError || emailError || resumeError || !resume) {
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      setResult(
        await createLead({
          first_name: normalizeName(firstName),
          last_name: normalizeName(lastName),
          email: normalizeEmail(email),
          resume,
        })
      );
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
            <SubmissionResult result={result} />
          ) : (
            <div className="rounded-card bg-paper-0 p-5 shadow-card sm:p-8">
              {error && (
                <p className="mb-6 rounded-input bg-brick-50 px-4 py-3 text-body-sm text-brick-600">
                  {error}
                </p>
              )}

              <form
                onSubmit={handleSubmit}
                noValidate
                className="flex flex-col gap-5"
              >
                <Field label="First name" error={fieldErrors.firstName}>
                  <input
                    maxLength={NAME_MAX_LENGTH}
                    value={firstName}
                    onChange={(event) => {
                      setFirstName(event.target.value);
                      if (fieldErrors.firstName) {
                        setFieldErrors((current) => ({
                          ...current,
                          firstName: null,
                        }));
                      }
                    }}
                    onBlur={(event) => validateFirstName(event.target.value)}
                    className={`field-input ${
                      fieldErrors.firstName ? "field-input-error" : ""
                    }`}
                  />
                </Field>
                <Field label="Last name" error={fieldErrors.lastName}>
                  <input
                    maxLength={NAME_MAX_LENGTH}
                    value={lastName}
                    onChange={(event) => {
                      setLastName(event.target.value);
                      if (fieldErrors.lastName) {
                        setFieldErrors((current) => ({
                          ...current,
                          lastName: null,
                        }));
                      }
                    }}
                    onBlur={(event) => validateLastName(event.target.value)}
                    className={`field-input ${
                      fieldErrors.lastName ? "field-input-error" : ""
                    }`}
                  />
                </Field>
                <Field label="Email" error={fieldErrors.email}>
                  <input
                    type="email"
                    maxLength={EMAIL_MAX_LENGTH}
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      if (fieldErrors.email) {
                        setFieldErrors((current) => ({
                          ...current,
                          email: null,
                        }));
                      }
                    }}
                    onBlur={(event) => validateEmailField(event.target.value)}
                    className={`field-input ${
                      fieldErrors.email ? "field-input-error" : ""
                    }`}
                  />
                </Field>
                <Field label="Resume / CV">
                  <FileUpload
                    file={resume}
                    accept=".pdf,.doc,.docx"
                    error={fieldErrors.resume}
                    onFileChange={(file) => {
                      setResume(file);
                      validateResume(file);
                    }}
                  />
                </Field>

                <Button
                  type="submit"
                  fullWidth
                  loading={submitting}
                  className="mt-2"
                >
                  {submitting ? "Submitting..." : "Submit application"}
                </Button>

                <p className="text-center text-body-sm text-ink-400">
                  By submitting, you agree to our{" "}
                  <span className="text-ink-700 underline">Terms of Service</span>
                  {" "}and{" "}
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

function SubmissionResult({ result }: { result: LeadCreateResult }) {
  return (
    <div className="rounded-card bg-paper-0 p-8 shadow-card">
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
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string | null;
  children: ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-label-sm text-ink-700">{label}</span>
      {children}
      {error && <span className="text-body-sm text-brick-600">{error}</span>}
    </label>
  );
}
