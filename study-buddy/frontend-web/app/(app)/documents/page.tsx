/**
 * app/(app)/documents/page.tsx — Premium Document Management
 * ============================================================
 * Drag and drop upload, vector processing status, document cards,
 * chunk counts, file format badges, and delete actions.
 */

"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useDocuments } from "@/hooks/useDocuments";
import { formatDate, ACCEPTED_TYPES } from "@/lib/utils";

export default function DocumentsPage() {
  const { documents, upload, deleteDoc, isUploading } = useDocuments();
  const [search, setSearch]                           = useState("");

  const onDrop = useCallback(
    (files: File[]) => {
      files.forEach((f) => upload(f));
    },
    [upload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: 50 * 1024 * 1024,
  });

  const filtered = documents.filter((d) =>
    d.filename.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div>
        <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
          Document Vault
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Upload study materials to index them into your private ChromaDB vector store
        </p>
      </div>

      {/* ── Drag and Drop Zone ──────────────────────────────────────────────── */}
      <div
        {...getRootProps()}
        className="p-10 rounded-3xl text-center cursor-pointer transition-all duration-300 relative group"
        style={{
          background: isDragActive ? "rgba(255,45,85,0.06)" : "#0F1115",
          border: isDragActive ? "2px dashed #FF2D55" : "1px dashed rgba(255,255,255,0.12)",
          boxShadow: isDragActive ? "0 0 40px rgba(255,45,85,0.15)" : "none",
        }}
      >
        <input {...getInputProps()} />
        <div
          className="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center text-2xl transition-transform group-hover:scale-110"
          style={{ background: "rgba(255,45,85,0.10)", color: "#FF2D55" }}
        >
          📄
        </div>
        <p className="text-sm font-bold" style={{ color: "#F1F3F8" }}>
          {isDragActive ? "Drop documents here" : "Drag & drop files or browse"}
        </p>
        <p className="text-2xs mt-1" style={{ color: "#5C6070" }}>
          PDF, DOCX, PPTX, TXT · Up to 50 MB per file
        </p>

        {isUploading && (
          <div className="mt-4 flex items-center justify-center gap-2">
            <div className="w-2 h-2 rounded-full bg-brand animate-ping" style={{ background: "#FF2D55" }} />
            <p className="text-xs font-semibold" style={{ color: "#FF6B8A" }}>
              Extracting and indexing chunks into ChromaDB…
            </p>
          </div>
        )}
      </div>

      {/* ── Search & Filter ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between gap-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search documents by name…"
          className="px-4 py-2.5 rounded-xl text-xs outline-none w-72"
          style={{
            background: "#0F1115",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "#F1F3F8",
          }}
        />
        <span className="text-xs" style={{ color: "#5C6070" }}>
          {filtered.length} indexed {filtered.length === 1 ? "document" : "documents"}
        </span>
      </div>

      {/* ── Document Cards Grid ─────────────────────────────────────────────── */}
      {filtered.length === 0 ? (
        <div
          className="p-12 rounded-3xl text-center space-y-2"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <span className="text-3xl">📭</span>
          <p className="text-sm font-semibold" style={{ color: "#F1F3F8" }}>
            No documents found
          </p>
          <p className="text-xs" style={{ color: "#5C6070" }}>
            Upload your lecture slides, notes, or textbooks to begin chatting with them
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <div
              key={d.id}
              className="p-5 rounded-2xl transition-all duration-200 flex flex-col justify-between"
              style={{
                background: "#0F1115",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,45,85,0.25)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
              }}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span
                    className="text-2xs font-bold uppercase tracking-wider px-2 py-0.5 rounded"
                    style={{
                      background: "rgba(255,45,85,0.10)",
                      color: "#FF2D55",
                      border: "1px solid rgba(255,45,85,0.25)",
                    }}
                  >
                    {d.file_type.toUpperCase()}
                  </span>
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{
                      background: d.status === "ready" ? "#10B981" : "#F59E0B",
                      boxShadow: d.status === "ready" ? "0 0 8px #10B981" : "none",
                    }}
                  />
                </div>

                <p className="text-sm font-bold truncate" style={{ color: "#F1F3F8" }}>
                  {d.filename}
                </p>

                <div className="flex items-center gap-3 mt-2 text-2xs" style={{ color: "#5C6070" }}>
                  <span>{d.chunk_count} vector chunks</span>
                  <span>·</span>
                  <span>{formatDate(d.uploaded_at)}</span>
                </div>
              </div>

              <div
                className="mt-4 pt-3 flex items-center justify-between"
                style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
              >
                <span className="text-2xs font-medium" style={{ color: "#10B981" }}>
                  ✓ Ready for RAG
                </span>
                <button
                  onClick={() => deleteDoc(d.id)}
                  className="text-2xs transition-colors"
                  style={{ color: "#5C6070" }}
                  onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "#EF4444")}
                  onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#5C6070")}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
