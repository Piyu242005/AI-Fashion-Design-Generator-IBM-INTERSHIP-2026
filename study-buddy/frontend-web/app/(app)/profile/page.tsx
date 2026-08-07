/**
 * app/(app)/profile/page.tsx — User Profile & Document Management
 * =================================================================
 */

"use client";

import { useAuth } from "@/hooks/useAuth";
import { useDocuments } from "@/hooks/useDocuments";
import { formatDate, formatFileSize } from "@/lib/utils";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { ACCEPTED_TYPES } from "@/lib/utils";

export default function ProfilePage() {
  const { user }                      = useAuth();
  const { documents, upload, deleteDoc, isUploading } = useDocuments();

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

  return (
    <div className="max-w-3xl mx-auto animate-fade-in-up space-y-8">
      {/* Profile header */}
      <div className="card flex items-center gap-5">
        <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center text-white text-2xl font-bold shrink-0">
          {user?.name?.charAt(0).toUpperCase() ?? "?"}
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white">{user?.name}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
          <div className="flex gap-4 mt-2 text-xs text-slate-400">
            <span>📄 {user?.document_count} documents</span>
            <span>🔥 {user?.study_streak} day streak</span>
            <span>📅 Joined {user ? formatDate(user.created_at) : "—"}</span>
          </div>
        </div>
      </div>

      {/* Upload zone */}
      <div>
        <h2 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-3">Upload Documents</h2>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
              : "border-slate-300 dark:border-slate-600 hover:border-blue-400"
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-3xl mb-2">📂</div>
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
            {isDragActive ? "Drop your files here" : "Drag & drop or click to upload"}
          </p>
          <p className="text-xs text-slate-400 mt-1">PDF, DOCX, PPTX, TXT — up to 50 MB</p>
          {isUploading && (
            <p className="text-xs text-blue-500 mt-2 animate-pulse">Uploading…</p>
          )}
        </div>
      </div>

      {/* Documents list */}
      <div>
        <h2 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-3">
          My Documents ({documents.length})
        </h2>
        {documents.length === 0 ? (
          <div className="card text-center py-10 text-slate-400">
            <div className="text-3xl mb-2">📭</div>
            <p className="text-sm">No documents yet. Upload your first study material above.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((d) => (
              <div key={d.id} className="card flex items-center gap-4">
                <span className="text-2xl shrink-0">
                  {d.file_type === "pdf" ? "📕" : d.file_type === "docx" ? "📘" : d.file_type === "pptx" ? "📙" : "📄"}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{d.filename}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {d.chunk_count} chunks · {formatDate(d.uploaded_at)}
                  </p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  d.status === "ready"
                    ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400"
                    : d.status === "processing"
                    ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400"
                    : "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400"
                }`}>
                  {d.status}
                </span>
                <button
                  onClick={() => deleteDoc(d.id)}
                  className="text-slate-400 hover:text-red-500 transition-colors text-xs shrink-0"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
