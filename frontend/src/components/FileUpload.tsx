"use client";

import { useRef, useState } from "react";
import { CloseIcon, FileIcon, UploadCloudIcon } from "./icons";

function truncateMiddle(name: string, max = 28): string {
  if (name.length <= max) return name;
  const half = Math.floor((max - 3) / 2);
  return `${name.slice(0, half)}...${name.slice(name.length - half)}`;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUpload({
  file,
  onFileChange,
  error,
  accept,
}: {
  file: File | null;
  onFileChange: (file: File | null) => void;
  error?: string | null;
  accept: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function openBrowser() {
    inputRef.current?.click();
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0] ?? null;
    if (dropped) onFileChange(dropped);
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
      />

      {!file ? (
        <div
          role="button"
          tabIndex={0}
          onClick={openBrowser}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              openBrowser();
            }
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`flex min-h-[44px] cursor-pointer flex-col items-center justify-center gap-2 rounded-card border-2 border-dashed px-6 py-10 text-center transition-colors ${
            dragging ? "border-navy-600 bg-paper-100" : "border-ink-200"
          } ${error ? "border-brick-600 bg-brick-50" : ""}`}
        >
          <UploadCloudIcon
            className={`size-6 ${error ? "text-brick-600" : "text-ink-400"}`}
          />
          <p className={`text-body-md ${error ? "text-brick-600" : "text-ink-900"}`}>
            Drag your r&eacute;sum&eacute; here, or click to browse
          </p>
          <p className={`text-body-sm ${error ? "text-brick-600" : "text-ink-400"}`}>
            PDF or Word, up to 10MB.
          </p>
        </div>
      ) : (
        <div
          className={`flex items-center gap-3 rounded-card border px-4 py-3 ${
            error ? "border-brick-600 bg-brick-50" : "border-ink-200 bg-paper-0"
          }`}
        >
          <FileIcon className={`size-5 shrink-0 ${error ? "text-brick-600" : "text-ink-400"}`} />
          <div className="min-w-0 flex-1">
            <p className={`text-body-md ${error ? "text-brick-600" : "text-ink-900"}`}>
              {truncateMiddle(file.name)}
            </p>
            <p className={`text-body-sm ${error ? "text-brick-600" : "text-ink-400"}`}>
              {formatFileSize(file.size)}
            </p>
          </div>
          <button
            type="button"
            onClick={openBrowser}
            className="shrink-0 text-body-sm font-medium text-navy-600 hover:underline"
          >
            Replace
          </button>
          <button
            type="button"
            onClick={() => onFileChange(null)}
            aria-label="Remove file"
            className="shrink-0 rounded-input p-1 text-ink-400 hover:bg-paper-100"
          >
            <CloseIcon className="size-4" />
          </button>
        </div>
      )}

      {error && <p className="mt-1.5 text-body-sm text-brick-600">{error}</p>}
    </div>
  );
}
