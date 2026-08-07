/**
 * app/(app)/settings/page.tsx — User Settings
 * =============================================
 * Theme toggle, AI preferences, quiz defaults.
 */

"use client";

import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  return (
    <div className="max-w-2xl mx-auto animate-fade-in-up space-y-6">
      <h1 className="text-2xl font-bold text-slate-800 dark:text-white">⚙️ Settings</h1>

      {/* Appearance */}
      <div className="card">
        <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-4">🎨 Appearance</h2>
        <div className="flex gap-3">
          {(["dark", "light", "system"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`flex-1 py-2.5 rounded-xl border text-sm font-medium capitalize transition-colors ${
                theme === t
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-blue-400"
              }`}
            >
              {t === "dark" ? "🌙 Dark" : t === "light" ? "☀️ Light" : "💻 System"}
            </button>
          ))}
        </div>
      </div>

      {/* AI Preferences */}
      <div className="card">
        <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-4">🤖 AI Preferences</h2>
        <div className="space-y-4">
          <Pref label="Response Style" options={["concise", "detailed"]} />
          <Pref label="Explanation Level" options={["simple", "intermediate", "advanced"]} />
        </div>
      </div>

      {/* Quiz defaults */}
      <div className="card">
        <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-4">❓ Quiz Defaults</h2>
        <div className="space-y-4">
          <Pref label="Default Question Type" options={["mcq", "true_false", "short_answer", "mixed"]} />
          <Pref label="Default Difficulty" options={["easy", "medium", "hard"]} />
        </div>
      </div>

      {/* About */}
      <div className="card text-center py-6 text-slate-400 text-sm">
        <p className="text-2xl mb-2">🎓</p>
        <p className="font-semibold text-slate-600 dark:text-slate-300">AI-Powered Study Buddy v2.0</p>
        <p className="mt-1">IBM SkillsBuild Final Project 2025</p>
        <p className="mt-1">Next.js 14 · FastAPI · LangChain · Gemini 1.5 Pro · ChromaDB</p>
      </div>
    </div>
  );
}

function Pref({ label, options }: { label: string; options: string[] }) {
  const [value, setValue] = useState(options[0]);
  return (
    <div className="flex items-center justify-between">
      <label className="text-sm text-slate-600 dark:text-slate-300">{label}</label>
      <select value={value} onChange={(e) => setValue(e.target.value)}
        className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
        {options.map((o) => (
          <option key={o} value={o}>{o.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</option>
        ))}
      </select>
    </div>
  );
}
