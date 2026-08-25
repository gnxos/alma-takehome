import type { ButtonHTMLAttributes } from "react";

import { SpinnerIcon } from "./icons";

type ButtonVariant = "primary" | "secondary";

const base =
  "inline-flex h-11 items-center justify-center rounded-input px-5 text-body-md font-medium transition-colors disabled:cursor-not-allowed";
const variants: Record<ButtonVariant, string> = {
  primary:
    "bg-navy-600 text-paper-0 hover:bg-navy-700 disabled:bg-ink-200 disabled:text-ink-400",
  secondary:
    "border border-ink-200 bg-paper-0 text-ink-900 hover:bg-paper-100 disabled:text-ink-400",
};

export function buttonClasses({
  variant = "primary",
  fullWidth = false,
  className = "",
}: {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  className?: string;
} = {}): string {
  return `${base} ${variants[variant]} ${fullWidth ? "w-full" : ""} ${className}`;
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  loading?: boolean;
}

export function Button({
  variant = "primary",
  fullWidth = false,
  loading = false,
  disabled,
  className = "",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={buttonClasses({ variant, fullWidth, className })}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <SpinnerIcon className="mr-2 size-4" />}
      {children}
    </button>
  );
}
