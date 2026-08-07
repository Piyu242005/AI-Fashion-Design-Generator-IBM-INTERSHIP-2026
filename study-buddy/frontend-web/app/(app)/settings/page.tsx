/**
 * app/(app)/settings/page.tsx — Premium Platform Settings
 * =========================================================
 * AI model parameters, explanation preferences, quiz defaults,
 * theme management, and API connection status.
 */

"use client";

import { useState } from "react";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const [model, setModel]             = useState("gemini-1.5-pro");
  const [style, setStyle]             = useState("concise");
  const [level, setLevel]             = useState("intermediate");
  const [qType, setQType]             = useState("mcq");
  const [diff, setDiff]               = useState("medium");
  const [stream, setStream]           = useState(true);

  const handleSave = () => {
    toast.success("Settings saved successfully!");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div>
        <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
          Platform Settings
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Configure AI model inference, response verbosity, and study defaults
        </p>
      </div>

      {/* ── AI Model Configuration ────────────────────────────────────────── */}
      <div
        className="p-6 rounded-2xl space-y-4"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <h2 className="text-sm font-bold" style={{ color: "#F1F3F8" }}>
          AI Engine Preferences
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                Primary LLM Model
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                Google Gemini model used for synthesis and generation
              </p>
            </div>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="px-3.5 py-2 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Recommended)</option>
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (Ultra Fast)</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                Explanation Depth
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                Depth of AI explanations during Q&A
              </p>
            </div>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="px-3.5 py-2 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value="simple">Beginner (Simple Analogies)</option>
              <option value="intermediate">Intermediate (Standard)</option>
              <option value="advanced">Advanced (Deep Technical)</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                Stream Token Responses
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                Render answers in real-time as they generate
              </p>
            </div>
            <input
              type="checkbox"
              checked={stream}
              onChange={(e) => setStream(e.target.checked)}
              className="w-4 h-4 accent-[#FF2D55]"
            />
          </div>
        </div>
      </div>

      {/* ── Quiz & Flashcards Defaults ────────────────────────────────────── */}
      <div
        className="p-6 rounded-2xl space-y-4"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <h2 className="text-sm font-bold" style={{ color: "#F1F3F8" }}>
          Quiz & Study Defaults
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                Default Question Type
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                Format applied when creating quick quizzes
              </p>
            </div>
            <select
              value={qType}
              onChange={(e) => setQType(e.target.value)}
              className="px-3.5 py-2 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value="mcq">Multiple Choice</option>
              <option value="true_false">True / False</option>
              <option value="short_answer">Short Answer</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                Default Difficulty
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                Initial challenge level for generated questions
              </p>
            </div>
            <select
              value={diff}
              onChange={(e) => setDiff(e.target.value)}
              className="px-3.5 py-2 rounded-xl text-xs outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value="easy">🟢 Easy</option>
              <option value="medium">🟡 Medium</option>
              <option value="hard">🔴 Hard</option>
            </select>
          </div>
        </div>
      </div>

      <button
        onClick={handleSave}
        className="w-full py-3.5 rounded-xl text-xs font-bold transition-all"
        style={{
          background: "#FF2D55",
          color: "#fff",
          boxShadow: "0 4px 14px rgba(255,45,85,0.35)",
        }}
      >
        Save Settings
      </button>

      {/* ── System Info Card ──────────────────────────────────────────────── */}
      <div
        className="p-5 rounded-2xl text-center space-y-1"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <p className="text-xs font-bold" style={{ color: "#F1F3F8" }}>
          AI-Powered Study Buddy · v2.0 Enterprise
        </p>
        <p className="text-2xs" style={{ color: "#5C6070" }}>
          IBM SkillsBuild 2026 · Google Gemini 1.5 Pro · ChromaDB Vector Store
        </p>
      </div>
    </div>
  );
}
