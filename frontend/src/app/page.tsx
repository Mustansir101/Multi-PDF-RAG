"use client";

import { useMemo, useState } from "react";
import { Chat } from "@/components/Chat";

export default function HomePage() {
  const [processMessage, setProcessMessage] = useState<string | null>(null);

  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="sidebarHeader">
          <div className="brand">
            <div className="brandDot" aria-hidden="true" />
            <div>
              <div className="brandTitle">AI Question Generator</div>
            </div>
          </div>
        </div>

        <div className="sidebarSection">
          <div className="sidebarSectionTitle">PDFs</div>
          <div className="sidebarSectionBody">
            <div className="sidebarMeta">
              <div className="sidebarMetaRow">
                <span className="muted">This project transforms a simple Python script into a focused AI-driven question generation engine powered by Google’s Gemini API, where a carefully engineered system prompt ensures the model produces only high-quality, context-aware questions instead of generic responses. By combining strict prompt control with example-driven guidance, it consistently delivers precise and structured outputs, making it highly effective for use cases like interview preparation, study material creation, and idea generation, while also demonstrating practical mastery of prompt engineering and scalable AI integration.</span>
              </div>

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
          </div>
        </header>

        <Chat />
      </section>
    </div>
  );
}
