"use client";

import { useMemo, useState } from "react";
import { Chat } from "@/components/Chat";
import { PdfProcessor } from "@/components/PdfProcessor";

export default function HomePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [processedFiles, setProcessedFiles] = useState<string[]>([]);
  const [processMessage, setProcessMessage] = useState<string | null>(null);

  const statusText = useMemo(() => {
    if (!sessionId) return "No PDFs processed yet.";
    if (processedFiles.length === 0) return "Ready.";
    return `Ready — ${processedFiles.length} file(s).`;
  }, [sessionId, processedFiles]);

  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="sidebarHeader">
          <div className="brand">
            <div className="brandDot" aria-hidden="true" />
            <div>
              <div className="brandTitle">Multi PDF RAG</div>
              <div className="brandSub">Dummy API frontend</div>
            </div>
          </div>
        </div>

        <div className="sidebarSection">
          <div className="sidebarSectionTitle">PDFs</div>
          <div className="sidebarSectionBody">
            <PdfProcessor
              onProcessed={(result) => {
                setSessionId(result.sessionId);
                setProcessedFiles(result.files);
                setProcessMessage(result.message ?? null);
              }}
            />

            <div className="sidebarMeta">
              <div className="sidebarMetaRow">
                <span className="muted">Status</span>
                <span className="sidebarMetaValue">{statusText}</span>
              </div>

              {processedFiles.length > 0 && (
                <div className="sidebarFiles">
                  <div className="muted">Processed</div>
                  <div className="sidebarFileList" aria-label="processed files">
                    {processedFiles.map((f) => (
                      <div className="sidebarFile" key={f} title={f}>
                        {f}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {processMessage && (
                <div className="sidebarHint" aria-label="process message">
                  {processMessage}
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      <section className="chatPane">
        <header className="chatTopBar">
          <div>
            <div className="chatTitle">Chat</div>
            <div className="chatSubtitle">
              {sessionId ? `Session: ${sessionId}` : "Process PDFs to start"}
            </div>
          </div>
        </header>

        <Chat sessionId={sessionId} processedFiles={processedFiles} />
      </section>
    </div>
  );
}
