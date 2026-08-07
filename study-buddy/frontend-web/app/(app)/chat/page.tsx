/**
 * app/(app)/chat/page.tsx — Premium AI Chat Interface
 * =====================================================
 * Streaming-ready chat with markdown, source citations,
 * document selector chips, and cinematic dark UI.
 */

"use client";

import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "@/hooks/useChat";
import { useDocuments } from "@/hooks/useDocuments";

const SUGGESTED_QUESTIONS = [
  "Summarize the key concepts in my documents",
  "What are the most important topics I should focus on?",
  "Explain the main argument in simple terms",
  "Generate 5 study questions from my notes",
];

export default function ChatPage() {
  const { documents }                               = useDocuments();
  const [selectedIds, setSelectedIds]               = useState<number[]>([]);
  const { messages, sendMessage, clearChat, isThinking } = useChat(selectedIds);
  const [input, setInput]                           = useState("");
  const bottomRef                                   = useRef<HTMLDivElement>(null);
  const inputRef                                    = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleSend = () => {
    if (!input.trim() || isThinking) return;
    sendMessage(input);
    setInput("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleDoc = (id: number) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id],
    );

  const isEmpty = messages.length === 0;

  return (
    <div className="max-w-4xl mx-auto flex flex-col" style={{ height: "calc(100vh - 8rem)" }}>

      {/* ── Header ───────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-5 shrink-0">
        <div>
          <h1 className="text-2xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
            AI Chat
          </h1>
          <p className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
            {selectedIds.length === 0
              ? "Select documents below to begin"
              : `Chatting with ${selectedIds.length} document${selectedIds.length > 1 ? "s" : ""}`
            }
          </p>
        </div>
        <button
          onClick={clearChat}
          className="text-xs px-3 py-1.5 rounded-lg transition-all"
          style={{ color: "#5C6070", border: "1px solid rgba(255,255,255,0.07)" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.color = "#EF4444";
            (e.currentTarget as HTMLElement).style.borderColor = "rgba(239,68,68,0.3)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.color = "#5C6070";
            (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.07)";
          }}
        >
          Clear
        </button>
      </div>

      {/* ── Document Selector ────────────────────────────────────────── */}
      {documents.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4 shrink-0">
          {documents.map((d) => {
            const isSelected = selectedIds.includes(d.id);
            return (
              <button
                key={d.id}
                onClick={() => toggleDoc(d.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all"
                style={{
                  background: isSelected ? "rgba(255,45,85,0.12)" : "rgba(255,255,255,0.04)",
                  border: isSelected ? "1px solid rgba(255,45,85,0.35)" : "1px solid rgba(255,255,255,0.08)",
                  color: isSelected ? "#FF2D55" : "#9CA3AF",
                }}
              >
                <svg viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3 opacity-70">
                  <path d="M5 3.5h6A1.5 1.5 0 0112.5 5v7.5A1.5 1.5 0 0111 14H5a1.5 1.5 0 01-1.5-1.5V5A1.5 1.5 0 015 3.5z" />
                </svg>
                {d.filename}
              </button>
            );
          })}
        </div>
      )}

      {/* ── Message Area ─────────────────────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto space-y-5 pr-1 mb-4"
        style={{ scrollBehavior: "smooth" }}
      >
        {/* Empty state */}
        {isEmpty && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: "rgba(255,45,85,0.10)", border: "1px solid rgba(255,45,85,0.2)" }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="#FF2D55" strokeWidth={1.5} className="w-7 h-7">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <h3 className="text-sm font-bold mb-2" style={{ color: "#F1F3F8" }}>
              Ask anything about your documents
            </h3>
            <p className="text-xs mb-6" style={{ color: "#5C6070" }}>
              Select documents above, then type your question or choose a suggestion.
            </p>

            {/* Suggested questions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-xl">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setInput(q);
                    inputRef.current?.focus();
                  }}
                  className="p-3 rounded-xl text-left text-xs transition-all"
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.07)",
                    color: "#9CA3AF",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,45,85,0.25)";
                    (e.currentTarget as HTMLElement).style.color = "#F1F3F8";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.07)";
                    (e.currentTarget as HTMLElement).style.color = "#9CA3AF";
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, idx) => (
          <div
            key={msg.id}
            className="flex"
            style={{
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              animation: "fade-in-up 0.3s ease forwards",
            }}
          >
            {/* AI avatar */}
            {msg.role === "assistant" && (
              <div
                className="w-7 h-7 rounded-full shrink-0 mr-3 mt-1 flex items-center justify-center text-xs font-bold"
                style={{ background: "rgba(255,45,85,0.15)", border: "1px solid rgba(255,45,85,0.25)", color: "#FF2D55" }}
              >
                AI
              </div>
            )}

            <div style={{ maxWidth: "80%" }}>
              <div
                className="rounded-2xl px-4 py-3 text-sm leading-relaxed"
                style={
                  msg.role === "user"
                    ? {
                        background: "#FF2D55",
                        color: "#fff",
                        borderRadius: "20px 20px 4px 20px",
                        boxShadow: "0 4px 14px rgba(255,45,85,0.3)",
                      }
                    : {
                        background: "#0F1115",
                        border: "1px solid rgba(255,255,255,0.08)",
                        color: "#F1F3F8",
                        borderRadius: "4px 20px 20px 20px",
                      }
                }
              >
                {msg.role === "assistant" ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose-study">
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <p>{msg.content}</p>
                )}

                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div
                    className="mt-3 pt-3 flex flex-wrap gap-1.5"
                    style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}
                  >
                    {msg.sources.map((src) => (
                      <span
                        key={src}
                        className="px-2 py-0.5 rounded text-2xs font-medium"
                        style={{ background: "rgba(255,45,85,0.12)", color: "#FF6B8A" }}
                      >
                        📎 {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Action buttons for AI messages */}
              {msg.role === "assistant" && (
                <div className="flex items-center gap-2 mt-1.5 ml-1">
                  <button
                    onClick={() => navigator.clipboard.writeText(msg.content)}
                    className="text-2xs px-2 py-0.5 rounded transition-all"
                    style={{ color: "#5C6070" }}
                    onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "#F1F3F8")}
                    onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#5C6070")}
                  >
                    Copy
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Thinking indicator */}
        {isThinking && (
          <div className="flex items-center gap-3" style={{ animation: "fade-in 0.2s ease forwards" }}>
            <div
              className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-xs font-bold"
              style={{ background: "rgba(255,45,85,0.15)", border: "1px solid rgba(255,45,85,0.25)", color: "#FF2D55" }}
            >
              AI
            </div>
            <div
              className="px-4 py-3 rounded-2xl flex items-center gap-1.5"
              style={{
                background: "#0F1115",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "4px 20px 20px 20px",
              }}
            >
              <div className="thinking-dot" />
              <div className="thinking-dot" />
              <div className="thinking-dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input Area ───────────────────────────────────────────────── */}
      <div
        className="shrink-0 rounded-2xl overflow-hidden"
        style={{
          background: "#0F1115",
          border: "1px solid rgba(255,255,255,0.08)",
        }}
        onFocusCapture={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,45,85,0.35)";
        }}
        onBlurCapture={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.08)";
        }}
      >
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            selectedIds.length === 0
              ? "Select a document above first…"
              : "Ask a question about your documents… (Enter to send)"
          }
          disabled={selectedIds.length === 0 || isThinking}
          rows={3}
          className="w-full px-4 pt-3 pb-1 text-sm resize-none bg-transparent outline-none"
          style={{
            color: "#F1F3F8",
            fontFamily: "inherit",
          }}
        />
        <div className="flex items-center justify-between px-3 pb-3">
          <p className="text-2xs" style={{ color: "#5C6070" }}>
            Shift+Enter for new line
          </p>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isThinking || selectedIds.length === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all"
            style={{
              background: input.trim() && !isThinking && selectedIds.length > 0 ? "#FF2D55" : "rgba(255,255,255,0.06)",
              color: input.trim() && !isThinking && selectedIds.length > 0 ? "#fff" : "#5C6070",
              boxShadow: input.trim() && !isThinking && selectedIds.length > 0
                ? "0 4px 12px rgba(255,45,85,0.35)"
                : "none",
            }}
          >
            Send
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
