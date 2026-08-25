import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "link";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "rounded-md bg-black px-4 py-2 font-medium text-white disabled:opacity-50 dark:bg-white dark:text-black",
  secondary:
    "rounded-md border border-black/10 px-3 py-1.5 font-medium hover:bg-black/5 disabled:opacity-50 dark:border-white/10 dark:hover:bg-white/10",
  link: "underline disabled:opacity-50",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      className={`${variantClasses[variant]} ${className}`.trim()}
    />
  );
}
