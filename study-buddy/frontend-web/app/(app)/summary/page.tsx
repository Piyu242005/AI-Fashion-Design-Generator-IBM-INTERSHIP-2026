/**
 * app/(app)/summary/page.tsx — AI Summary Generator
 * ===================================================
 * Summarise documents as bullet points or paragraph with detail control.
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

export default function SummaryPage() {
  const { documents }           = useDocuments();
  const [docId, setDocId]       = useState(0);
  const [style, setStyle]       = useState<SummaryStyle>("bullet");
  const [detail, setDetail]     = useState("standard");
  const [summary, setSummary]   = useState("");
  const [wordCount, setWordCount] = useState(0);

  const mutation = useMutation({
    mutationFn: () => summaryApi.generate({ document_id: docId, style, detail }),
    onSuccess: (res) => {
      setSummary(res.data.summary);
      setWordCount(res.data.word_count);
    },
    onError: () => toast.error("Failed to generate summary. Please try again."),
  });

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="max-w-3xl mx-auto animate-fade-in-up">
      <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">📝 Summary</h1>

      {/* Config card */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          {/* Document */}
          <div>
            <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">Document</label>
            <select value={docId} onChange={(e) => setDocId(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value={0}>Select…</option>
              {documents.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
            </select>
          </div>

          {/* Style */}
          <div>
            <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">Style</label>
            <select value={style} onChange={(e) => setStyle(e.target.value as SummaryStyle)}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="bullet">Bullet Points</option>
              <option value="paragraph">Paragraph</option>
              <option value="detailed">Detailed</option>
            </select>
          </div>

          {/* Detail level */}
          <div>
            <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">Detail Level</label>
            <select value={detail} onChange={(e) => setDetail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="brief">Brief</option>
              <option value="standard">Standard</option>
              <option value="comprehensive">Comprehensive</option>
            </select>
          </div>
        </div>

        <button onClick={() => mutation.mutate()}
          disabled={!docId || mutation.isPending}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-colors">
          {mutation.isPending ? "Generating summary…" : "Generate Summary →"}
        </button>
      </div>

      {/* Summary output */}
      {summary && (
        <div className="card animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-700 dark:text-slate-200">Summary</h2>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">{wordCount} words</span>
              <button onClick={handleCopy}
                className="px-3 py-1 text-xs rounded-lg border border-slate-300 dark:border-slate-600 text-slate-500 hover:text-blue-500 hover:border-blue-400 transition-colors">
                Copy
              </button>
            </div>
          </div>
          <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose-study text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
            {summary}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}
