/**
 * app/page.tsx — Landing Page (root route "/")
 * ==============================================
 * Hero section with CTA, features grid, how-it-works, and tech stack.
 * Server Component — no "use client" needed here.
 */

import Link from "next/link";

const FEATURES = [
  {
    icon: "🔍",
    title: "RAG-Powered Q&A",
    description:
      "Ask questions about your own documents. Answers are grounded in your uploaded content — no hallucinations.",
  },
  {
    icon: "❓",
    title: "Quiz Generator",
    description:
      "Auto-generate MCQ, True/False, and Short Answer quizzes at easy, medium, or hard difficulty.",
  },
  {
    icon: "🃏",
    title: "Smart Flashcards",
    description:
      "Automatically extract key terms and definitions. Flip cards, mark as Known or Review.",
  },
  {
    icon: "📝",
    title: "AI Summaries",
    description:
      "Condense long documents into bullet points or paragraphs at your chosen detail level.",
  },
  {
    icon: "💡",
    title: "Concept Explainer",
    description:
      "Ask the Teaching Agent to explain any concept in plain language with real-world analogies.",
  },
  {
    icon: "📊",
    title: "Smart Dashboard",
    description:
      "Track study streaks, quiz scores per topic, and get AI-generated personalised recommendations.",
  },
];

const STEPS = [
  { step: "1", title: "Upload your notes", desc: "PDF, DOCX, PPTX, or TXT — up to 50 MB." },
  { step: "2", title: "Ask anything", desc: "Type a question, pick a quiz, or request a summary." },
  { step: "3", title: "Learn smarter", desc: "Get grounded, accurate answers and track your progress." },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-[#0f1117]">

      {/* ── Nav ───────────────────────────────────────────────────────── */}
      <nav className="border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <span className="text-xl font-bold text-blue-500">🎓 AI Study Buddy</span>
        <div className="flex gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors font-semibold"
          >
            Get Started Free
          </Link>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-6 pt-24 pb-16 text-center">
        <div className="inline-block px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider mb-6">
          IBM SkillsBuild Final Project 2025
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white mb-6 leading-tight">
          Your AI-Powered
          <span className="text-blue-500"> Study Buddy</span>
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400 mb-10 max-w-2xl mx-auto">
          Upload your study materials. Ask questions. Get grounded answers,
          quizzes, flashcards, and summaries — all powered by{" "}
          <strong className="text-slate-800 dark:text-slate-200">Google Gemini 1.5 Pro</strong>{" "}
          and{" "}
          <strong className="text-slate-800 dark:text-slate-200">Retrieval-Augmented Generation</strong>.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/register"
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-base transition-colors shadow-lg"
          >
            Start Studying Free →
          </Link>
          <Link
            href="https://github.com/your-username/ai-study-buddy"
            target="_blank"
            className="px-8 py-3 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-semibold text-base hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            View on GitHub
          </Link>
        </div>
      </section>

      {/* ── Features Grid ─────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-center text-slate-800 dark:text-white mb-12">
          Everything you need to study smarter
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="p-6 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#1e2130] hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
            >
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section className="bg-slate-50 dark:bg-[#161b27] py-16 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-12">How it works</h2>
          <div className="flex flex-col sm:flex-row gap-8 justify-center">
            {STEPS.map((s) => (
              <div key={s.step} className="flex-1">
                <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">
                  {s.step}
                </div>
                <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">{s.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-200 dark:border-slate-800 py-8 px-6 text-center text-sm text-slate-500 dark:text-slate-500">
        <p>AI-Powered Study Buddy · IBM SkillsBuild Final Project 2025 · MIT License</p>
        <p className="mt-1">
          Built with Next.js 14 · FastAPI · LangChain · Google Gemini 1.5 Pro · ChromaDB
        </p>
      </footer>
    </main>
  );
}
