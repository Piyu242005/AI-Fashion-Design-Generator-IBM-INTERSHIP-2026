/**
 * app/(app)/chat/page.tsx — RAG Chat Interface
 * ==============================================
 * Multi-turn conversation with document-grounded AI answers.
 */

"use client";

import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "@/hooks/useChat";
import { useDocuments } from "@/hooks/useDocuments";
import { formatRelative } from "@/lib/utils";

export default function ChatPage() {
  const { documents }                       = useDocuments();
  const [selectedIds, setSelectedIds]       = useState<number[]>([]);
  const { messages, sendMessage, clearChat, isThinking } = useChat(selectedIds);
  const [input, setInput]                   = useState("");
  const bottomRef                           = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  const toggleDoc = (id: number) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id],
    );

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">💬 Chat</h1>
        <button
          onClick={clearChat}
          className="text-xs text-slate-400 hover:text-red-400 transition-colors"
        >
          Clear chat
        </button>
      </div>

      {/* Document selector */}
      {documents.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {documents.map((d) => (
            <button
              key={d.id}
              onClick={() => toggleDoc(d.id)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                selectedIds.includes(d.id)
                  ? "bg-blue-600 text-white border-blue-600"
                  : "border-slate-300 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:border-blue-400"
              }`}
            >
              📄 {d.filename}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <span className="text-5xl mb-4">💬</span>
            <p className="text-slate-500 dark:text-slate-400">
              Select documents above and ask anything about them.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-white dark:bg-[#1e2130] border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-bl-sm"
              }`}
            >
              {msg.role === "assistant" ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  className="prose-study text-sm"
                >
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <p>{msg.content}</p>
              )}

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-600">
                  <p className="text-xs text-slate-400">
                    📎 Sources: {msg.sources.join(", ")}
                  </p>
                </div>
              )}

              <p className={`text-xs mt-1 ${msg.role === "user" ? "text-blue-200" : "text-slate-400"}`}>
                {formatRelative(msg.timestamp.toISOString())}
              </p>
            </div>
          </div>
        ))}

        {/* Thinking indicator */}
        {isThinking && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-[#1e2130] border border-slate-200 dark:border-slate-700 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="mt-4 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder={
            selectedIds.length === 0
              ? "Select a document above first…"
              : "Ask a question about your documents…"
          }
          disabled={selectedIds.length === 0 || isThinking}
          className="flex-1 px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-[#1e2130] text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isThinking}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
