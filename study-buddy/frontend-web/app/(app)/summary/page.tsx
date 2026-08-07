/**
 * app/(app)/summary/page.tsx — Premium AI Document Summarizer
 * =============================================================
 * Generate structured summaries in multiple formats:
 * Bullet Points, Paragraph, Executive Brief, or Detailed Breakdown.
 */

"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast from "react-hot-toast";
import { summaryApi } from "@/services/api";
import { useDocuments } from "@/hooks/useDocuments";
import type { SummaryStyle } from "@/types";

const STYLES: { key: SummaryStyle; label: string; icon: string }[] = [
  { key: "bullet",    label: "Bullet Points", icon: "📋" },
  { key: "paragraph", label: "Paragraph",     icon: "📄" },
  { key: "detailed",  label: "Deep Dive",     icon: "🔬" },
];

export default function SummaryPage() {
  const { documents }             = useDocuments();
  const [docId, setDocId]         = useState(0);
  const [style, setStyle]         = useState<SummaryStyle>("bullet");
  const [detail, setDetail]       = useState("standard");
  const [summary, setSummary]     = useState("");
  const [wordCount, setWordCount] = useState(0);

  const mutation = useMutation({
    mutationFn: () => summaryApi.generate({ document_id: docId, style, detail }),
    onSuccess: (res) => {
      setSummary(res.data.summary);
      setWordCount(res.data.word_count);
      toast.success("Summary generated successfully!");
    },
    onError: () => toast.error("Failed to generate summary. Please try again."),
  });

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    toast.success("Summary copied to clipboard!");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div>
        <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
          AI Summaries
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Condense complex chapters and papers into clear, verifiable insights
        </p>
      </div>

      {/* ── Configuration Panel ────────────────────────────────────────────── */}
      <div
        className="p-6 rounded-2xl space-y-5"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Document Picker */}
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Target Document
            </label>
            <select
              value={docId}
              onChange={(e) => setDocId(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value={0}>Select a document…</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename}
                </option>
              ))}
            </select>
          </div>

          {/* Format / Style */}
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Summary Style
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {STYLES.map((s) => {
                const isSelected = style === s.key;
                return (
                  <button
                    key={s.key}
                    type="button"
                    onClick={() => setStyle(s.key)}
                    className="py-2.5 rounded-xl text-2xs font-semibold transition-all flex flex-col items-center gap-1"
                    style={{
                      background: isSelected ? "rgba(255,45,85,0.12)" : "#161820",
                      border: isSelected ? "1px solid rgba(255,45,85,0.35)" : "1px solid rgba(255,255,255,0.06)",
                      color: isSelected ? "#FF2D55" : "#9CA3AF",
                    }}
                  >
                    <span>{s.icon}</span>
                    <span>{s.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Detail Depth */}
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Detail Level
            </label>
            <select
              value={detail}
              onChange={(e) => setDetail(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value="brief">⚡ Brief (Key Takeaways)</option>
              <option value="standard">📄 Standard (Balanced)</option>
              <option value="comprehensive">📚 Comprehensive (All Details)</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={!docId || mutation.isPending}
          className="w-full py-3.5 rounded-xl text-xs font-semibold transition-all"
          style={{
            background: !docId || mutation.isPending ? "rgba(255,255,255,0.06)" : "#FF2D55",
            color: !docId || mutation.isPending ? "#5C6070" : "#fff",
            boxShadow: docId && !mutation.isPending ? "0 4px 20px rgba(255,45,85,0.35)" : "none",
          }}
        >
          {mutation.isPending ? "Synthesizing Summary with Gemini…" : "Generate AI Summary →"}
        </button>
      </div>

      {/* ── Generated Output ────────────────────────────────────────────────── */}
      {summary && (
        <div
          className="p-6 rounded-2xl space-y-4"
          style={{
            background: "#0F1115",
            border: "1px solid rgba(255,255,255,0.06)",
            animation: "fade-in 0.3s ease forwards",
          }}
        >
          <div className="flex items-center justify-between pb-4" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold" style={{ color: "#F1F3F8" }}>
                Generated Output
              </span>
              <span
                className="text-2xs px-2 py-0.5 rounded-full font-mono"
                style={{ background: "rgba(255,45,85,0.12)", color: "#FF6B8A" }}
              >
                {wordCount} words
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: "#9CA3AF",
                }}
                onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "#F1F3F8")}
                onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#9CA3AF")}
              >
                Copy Text
              </button>
            </div>
          </div>

          <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose-study text-xs leading-relaxed">
            {summary}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}
