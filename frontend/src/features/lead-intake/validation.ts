export const NAME_MIN_LENGTH = 2;
export const NAME_MAX_LENGTH = 36;

const UNICODE_LETTERS_AND_SPACES = /^[\p{L}\s]+$/u;

export function normalizeName(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

export function validateName(value: string, label: string): string | null {
  const normalized = normalizeName(value);
  if (
    normalized.length < NAME_MIN_LENGTH ||
    normalized.length > NAME_MAX_LENGTH
  ) {
    return `${label} must be between ${NAME_MIN_LENGTH} and ${NAME_MAX_LENGTH} characters.`;
  }
  if (!UNICODE_LETTERS_AND_SPACES.test(normalized)) {
    return `${label} may only contain letters and spaces.`;
  }
  return null;
}

export const EMAIL_MAX_LENGTH = 100;
const EMAIL_STRUCTURE_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function normalizeEmail(value: string): string {
  return value.trim();
}

export function validateEmail(value: string): string | null {
  const trimmed = normalizeEmail(value);
  if (trimmed.length === 0) return "Email is required.";
  if (trimmed.length > EMAIL_MAX_LENGTH) {
    return `Email must be at most ${EMAIL_MAX_LENGTH} characters.`;
  }
  if (/\s/.test(trimmed)) {
    return "Email must not contain spaces or line breaks.";
  }
  if (!EMAIL_STRUCTURE_RE.test(trimmed)) {
    return "Enter a valid email address.";
  }
  return null;
}

export const RESUME_MIN_SIZE_BYTES = 100;
export const RESUME_MAX_SIZE_BYTES = 10 * 1024 * 1024;
export const ALLOWED_RESUME_EXTENSIONS = [".pdf", ".doc", ".docx"];

export function validateResumeFile(file: File): string | null {
  const lowerName = file.name.toLowerCase();
  if (!ALLOWED_RESUME_EXTENSIONS.some((extension) => lowerName.endsWith(extension))) {
    return "Resume must be a PDF, DOC, or DOCX file.";
  }
  if (file.size === 0) return "Resume file is empty.";
  if (file.size < RESUME_MIN_SIZE_BYTES) {
    return "Resume file is too small to be a real document.";
  }
  if (file.size > RESUME_MAX_SIZE_BYTES) {
    return "Resume must be smaller than 10MB.";
  }
  return null;
}
