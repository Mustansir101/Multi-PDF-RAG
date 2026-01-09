"use client";

import { useMemo, useState } from "react";
import { API_BASE_URL } from "@/lib/config";
import type { BackendProcessResponse, ProcessResult } from "@/lib/types";

type PdfProcessorProps = {
  onProcessed: (result: ProcessResult) => void;
};

export function PdfProcessor({ onProcessed }: PdfProcessorProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileNames = useMemo(() => files.map((f) => f.name), [files]);

  async function onProcess() {
    setError(null);
    setBusy(true);
    try {
      const form = new FormData();
      // FastAPI endpoint expects the field name "files"
      for (const f of files) form.append("files", f);

      const res = await fetch(`${API_BASE_URL}/process-pdfs`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed (${res.status})`);
      }

      const data = (await res.json()) as BackendProcessResponse;
      onProcessed({
        files: data.files,
        sessionId: data.session_id,
        message: data.message,
      });
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="pdfBox">
      <label className="filePicker">
        <input
          type="file"
          accept="application/pdf"
          multiple
          onChange={(e) => {
            const picked = Array.from(e.target.files ?? []);
            setFiles(picked);
          }}
        />
        <span className="filePickerText">
          {files.length === 0
            ? "Choose PDF files"
            : `${files.length} file(s) selected`}
        </span>
      </label>

      <button
        className="primaryButton"
        disabled={busy || files.length === 0}
        onClick={onProcess}
      >
        {busy ? "Processing…" : "Process"}
      </button>

      {fileNames.length > 0 && (
        <div className="fileChips" aria-label="selected files">
          {fileNames.map((n) => (
            <span key={n} className="chip" title={n}>
              {n}
            </span>
          ))}
        </div>
      )}

      {error && <div className="errorText">{error}</div>}
    </div>
  );
}
