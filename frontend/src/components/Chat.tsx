"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { API_BASE_URL } from "@/lib/config";
import type { BackendAskResponse, ChatMessage } from "@/lib/types";

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);


  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const trimmed = input.trim();
    if (!trimmed) return;

    setError(null);
    setBusy(true);

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      createdAt: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch(`${API_BASE_URL}/ask-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: trimmed }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed (${res.status})`);
      }

      const data = (await res.json()) as BackendAskResponse;

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        createdAt: Date.now(),
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chatLayout">
      <div className="chatScroll" aria-label="chat messages">
        {messages.length === 0 ? (
          <div className="emptyState">
            <div className="emptyStateTitle">Ask a question</div>
            <div className="emptyStateBody">
              Ask something to get started.
            </div>
          </div>
        ) : (
          <div className="messageList">
            {messages.map((m) => (
              <div
                className={
                  m.role === "user" ? "messageRow user" : "messageRow assistant"
                }
                key={m.id}
              >
                <div className="messageBubble">
                  <div className="messageMeta">
                    <span className="messageRole">
                      {m.role === "user" ? "You" : "Assistant"}
                    </span>
                    <span className="messageTime">
                      {new Date(m.createdAt).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="messageText">{m.content}</div>
                  {m.role === "assistant" &&
                    m.sources &&
                    m.sources.length > 0 && (
                      <div className="sourcesSection">
                        <div className="sourcesTitle">Sources</div>
                        <div className="messageSources">
                          {m.sources.map((s, idx) => (
                            <span
                              className="sourcePill"
                              key={`${s.source}-${s.page_label}-${idx}`}
                              title={`${s.source} (page ${s.page_label})`}
                            >
                              <span className="sourceName">{s.source}</span>
                              <span className="sourcePage">
                                p{s.page_label}
                              </span>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="composer">
        {error && <div className="errorBanner">{error}</div>}

        <div className="composerRow">
          <input
            className="composerInput"
            type="text"
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />
          <button
            className="composerButton"
            disabled={input.trim().length === 0}
            onClick={send}
          >
            {busy ? "Sending" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
