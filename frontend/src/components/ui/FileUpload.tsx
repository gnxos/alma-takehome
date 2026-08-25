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

interface FileUploadProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  error?: string | null;
  accept: string;
}

export function FileUpload({
  file,
  onFileChange,
  error,
  accept,
}: FileUploadProps) {
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
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
      />

      {!file ? (
        <div
          role="button"
          tabIndex={0}
          onClick={openBrowser}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              openBrowser();
            }
          }}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`group flex min-h-[96px] cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed p-5 text-center transition-all ${
            dragging
              ? "border-[#132A13] bg-[#E8F0DC]/40 scale-[0.99]"
              : "border-ink-200 bg-paper-50/50 hover:border-ink-400 hover:bg-paper-100/60"
          } ${error ? "border-brick-600 bg-brick-50/60" : ""}`}
        >
          <div className="flex size-9 items-center justify-center rounded-full bg-paper-0 shadow-xs ring-1 ring-black/5 group-hover:scale-105 transition-transform">
            <UploadCloudIcon
              className={`size-4.5 ${error ? "text-brick-600" : "text-ink-700"}`}
            />
          </div>
          <p
            className={`text-sm font-medium ${error ? "text-brick-600" : "text-ink-900"}`}
          >
            Upload resume or CV
          </p>
          <p
            className={`text-xs ${error ? "text-brick-600" : "text-ink-400"}`}
          >
            PDF or Word, max file size 10MB
          </p>
        </div>
      ) : (
        <div
          className={`flex items-center gap-3 rounded-xl border p-3.5 transition-all ${
            error
              ? "border-brick-600 bg-brick-50"
              : "border-ink-200 bg-paper-0 shadow-xs"
          }`}
        >
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-paper-100 text-ink-700">
            <FileIcon className="size-4.5" />
          </div>
          <div className="min-w-0 flex-1">
            <p
              className={`truncate text-sm font-medium ${error ? "text-brick-600" : "text-ink-900"}`}
            >
              {file.name}
            </p>
            <p
              className={`text-xs ${error ? "text-brick-600" : "text-ink-400"}`}
            >
              {formatFileSize(file.size)}
            </p>
          </div>
          <button
            type="button"
            onClick={openBrowser}
            className="shrink-0 text-xs font-semibold text-ink-700 hover:text-ink-900 hover:underline px-2 py-1"
          >
            Replace
          </button>
          <button
            type="button"
            onClick={() => onFileChange(null)}
            aria-label="Remove file"
            className="shrink-0 rounded-lg p-1.5 text-ink-400 hover:bg-paper-100 hover:text-ink-700 transition-colors"
          >
            <CloseIcon className="size-4" />
          </button>
        </div>
      )}

      {error && <p className="mt-1.5 text-xs text-brick-600 font-medium">{error}</p>}
    </div>
  );
}
