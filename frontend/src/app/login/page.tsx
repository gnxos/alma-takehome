"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { Button } from "@/components/Button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      router.push("/leads");
    } catch {
      setError("That email or password isn't right.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-paper-50 font-sans lg:bg-paper-0">
      <div className="flex w-full flex-col justify-center px-6 py-16 sm:px-10 lg:w-[480px] lg:shrink-0 lg:px-16">
        <span className="text-heading-md font-bold tracking-tight text-ink-900">
          alma
        </span>

        <h1 className="mt-10 text-heading-lg text-ink-900">Welcome back</h1>
        <p className="mt-2 text-body-md text-ink-700">
          Sign in to manage leads.
        </p>

        <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
          <label className="flex flex-col gap-1.5">
            <span className="text-label-sm text-ink-700">Email</span>
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="field-input"
            />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-label-sm text-ink-700">Password</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="field-input"
            />
          </label>

          {error && <p className="text-body-sm text-brick-600">{error}</p>}

          <Button type="submit" fullWidth loading={submitting} className="mt-2">
            {submitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>

        <p className="mt-10 text-body-sm text-ink-400">
          Internal tool for Alma attorneys. Accounts are provisioned by your
          administrator.
        </p>
      </div>

      <div className="relative hidden flex-1 overflow-hidden bg-gradient-to-br from-navy-700 via-navy-600 to-navy-700 lg:block">
        <div
          className="absolute inset-0 -translate-y-1/4 rotate-[-8deg] bg-gradient-to-r from-sage-600/0 via-sage-600/70 to-sage-600/0"
          style={{ height: "22%" }}
        />
        <div
          className="absolute inset-0 translate-y-1/3 rotate-[-8deg] bg-gradient-to-r from-brass-500/0 via-brass-500/50 to-brass-500/0"
          style={{ height: "14%" }}
        />
        <p className="absolute bottom-16 left-16 max-w-xs text-display-md font-serif text-paper-0">
          A clear path from lead to case.
        </p>
      </div>
    </div>
  );
}
