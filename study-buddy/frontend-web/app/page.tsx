/**
 * app/page.tsx — Premium Landing Page
 * =====================================
 * Cinematic hero, feature showcase, social proof, and animated CTAs.
 * Inspired by Vercel, Linear, and OpenAI's marketing sites.
 */

import Link from "next/link";

const FEATURES = [
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
      </svg>
    ),
    title: "RAG-Powered Chat",
    description: "Ask anything about your study materials. Answers are grounded in your documents — every response is verifiable and cited.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
      </svg>
    ),
    title: "Instant Summaries",
    description: "Condense 100-page PDFs into focused bullet points or executive briefs in seconds. Multiple formats, one click.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
      </svg>
    ),
    title: "Smart Flashcards",
    description: "AI extracts key terms, definitions and concepts automatically. Flip, mark known, and track retention with spaced repetition.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
      </svg>
    ),
    title: "Adaptive Quizzes",
    description: "MCQ, True/False, and short-answer quizzes auto-generated from your content. Difficulty adapts to your performance over time.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
      </svg>
    ),
    title: "Study Analytics",
    description: "Track streaks, quiz accuracy by topic, learning time, and weak areas. Get AI-generated personalized study plans.",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
      </svg>
    ),
    title: "AI Recommendations",
    description: "Intelligent study recommendations based on your quiz performance, history, and identified knowledge gaps.",
  },
];

const STATS = [
  { value: "50+", label: "File Formats" },
  { value: "< 2s", label: "Average Latency" },
  { value: "RAG", label: "Architecture" },
  { value: "99.9%", label: "Uptime SLA" },
];

const STEPS = [
  {
    step: "01",
    title: "Upload Your Materials",
    desc: "Drop in PDF, DOCX, PPTX, or TXT files. Our AI instantly extracts, chunks, and indexes your content into a private vector store.",
    color: "from-brand-500 to-brand-400",
  },
  {
    step: "02",
    title: "Interact with Your Content",
    desc: "Ask questions, request summaries, take quizzes, or generate flashcards. Everything is grounded in your specific documents.",
    color: "from-violet-500 to-violet-400",
  },
  {
    step: "03",
    title: "Learn Smarter, Not Harder",
    desc: "Your analytics dashboard tracks progress, surfaces weak topics, and continuously personalizes your learning path.",
    color: "from-emerald-500 to-emerald-400",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen" style={{ background: "#050505", color: "#F1F3F8" }}>

      {/* ── Ambient background ──────────────────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute -top-[30%] left-[50%] -translate-x-1/2 w-[900px] h-[600px] rounded-full"
          style={{
            background: "radial-gradient(ellipse, rgba(255,45,85,0.08) 0%, transparent 70%)",
            filter: "blur(60px)",
          }}
        />
        <div
          className="absolute top-[60%] right-[-10%] w-[500px] h-[400px] rounded-full"
          style={{
            background: "radial-gradient(ellipse, rgba(124,58,237,0.05) 0%, transparent 70%)",
            filter: "blur(80px)",
          }}
        />
      </div>

      {/* ── Navigation ──────────────────────────────────────────────────── */}
      <nav
        className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-6 py-4"
        style={{
          background: "rgba(5,5,5,0.8)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          backdropFilter: "blur(20px)",
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
            style={{ background: "#FF2D55" }}
          >
            🧠
          </div>
          <span className="text-sm font-bold tracking-tight" style={{ color: "#F1F3F8" }}>
            Study Buddy
          </span>
          <span
            className="px-2 py-0.5 rounded text-2xs font-semibold uppercase tracking-widest"
            style={{ background: "rgba(255,45,85,0.12)", color: "#FF2D55", border: "1px solid rgba(255,45,85,0.3)" }}
          >
            AI
          </span>
        </div>

        <div className="hidden md:flex items-center gap-6">
          {["Features", "How it works", "Docs"].map((item) => (
            <a
              key={item}
              href="#"
              className="text-sm transition-colors"
              style={{ color: "#9CA3AF" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#F1F3F8")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#9CA3AF")}
            >
              {item}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-sm font-medium rounded-lg transition-all"
            style={{
              color: "#9CA3AF",
              border: "1px solid rgba(255,255,255,0.08)",
              background: "transparent",
            }}
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm font-semibold rounded-lg transition-all"
            style={{
              background: "#FF2D55",
              color: "#fff",
              boxShadow: "0 4px 14px rgba(255,45,85,0.4)",
            }}
          >
            Get Started →
          </Link>
        </div>
      </nav>

      {/* ── Hero Section ─────────────────────────────────────────────────── */}
      <section className="relative pt-40 pb-28 px-6 text-center max-w-5xl mx-auto">
        {/* Announcement badge */}
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold mb-8"
          style={{
            background: "rgba(255,45,85,0.08)",
            border: "1px solid rgba(255,45,85,0.25)",
            color: "#FF6B8A",
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
          IBM SkillsBuild Final Project 2026 · Powered by Google Gemini
        </div>

        <h1
          className="text-5xl sm:text-7xl font-black tracking-tighter text-balance mb-6 leading-none"
          style={{ color: "#F1F3F8" }}
        >
          Study Smarter With{" "}
          <span
            style={{
              background: "linear-gradient(135deg, #FF2D55 0%, #FF6B8A 60%, #FF9AAF 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            AI
          </span>
          {" "}That
          <br />
          Knows Your Material
        </h1>

        <p
          className="text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
          style={{ color: "#9CA3AF" }}
        >
          Upload your notes. Ask questions. Get grounded, cited answers, quizzes,
          flashcards, and personalized study plans — all powered by{" "}
          <strong style={{ color: "#F1F3F8" }}>Retrieval-Augmented Generation</strong>.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
          <Link
            href="/register"
            className="px-8 py-3.5 font-semibold rounded-xl text-sm transition-all inline-flex items-center gap-2"
            style={{
              background: "#FF2D55",
              color: "#fff",
              boxShadow: "0 0 30px rgba(255,45,85,0.4), 0 4px 14px rgba(255,45,85,0.3)",
            }}
          >
            Start for Free
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
            </svg>
          </Link>
          <Link
            href="https://github.com/Piyu242005/IBM-INTERSHIP-2026"
            target="_blank"
            className="px-8 py-3.5 font-semibold rounded-xl text-sm transition-all inline-flex items-center gap-2"
            style={{
              color: "#9CA3AF",
              border: "1px solid rgba(255,255,255,0.10)",
              background: "rgba(255,255,255,0.03)",
            }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            View Source
          </Link>
        </div>

        {/* Stats strip */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-px max-w-2xl mx-auto overflow-hidden rounded-2xl"
          style={{ background: "rgba(255,255,255,0.06)" }}
        >
          {STATS.map((s) => (
            <div
              key={s.label}
              className="flex flex-col items-center py-4 px-6"
              style={{ background: "rgba(15,17,21,0.95)" }}
            >
              <span
                className="text-2xl font-black tracking-tighter"
                style={{ color: "#FF2D55" }}
              >
                {s.value}
              </span>
              <span className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features Grid ────────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <p
            className="text-xs font-semibold uppercase tracking-widest mb-3"
            style={{ color: "#FF2D55" }}
          >
            Capabilities
          </p>
          <h2
            className="text-3xl sm:text-4xl font-black tracking-tighter"
            style={{ color: "#F1F3F8" }}
          >
            Everything your brain needs
          </h2>
          <p className="text-sm mt-3 max-w-xl mx-auto" style={{ color: "#9CA3AF" }}>
            A complete AI-powered learning environment built on RAG, purpose-built for deep study.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className="group p-6 rounded-2xl transition-all duration-300 cursor-default"
              style={{
                background: "rgba(15,17,21,0.8)",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,45,85,0.25)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
                (e.currentTarget as HTMLElement).style.boxShadow = "0 8px 32px rgba(255,45,85,0.12)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
                (e.currentTarget as HTMLElement).style.boxShadow = "none";
              }}
            >
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                style={{ background: "rgba(255,45,85,0.12)", color: "#FF2D55" }}
              >
                {f.icon}
              </div>
              <h3
                className="font-bold text-sm mb-2"
                style={{ color: "#F1F3F8" }}
              >
                {f.title}
              </h3>
              <p className="text-sm leading-relaxed" style={{ color: "#5C6070" }}>
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────────────────── */}
      <section className="py-20 px-6" style={{ background: "rgba(15,17,21,0.5)" }}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <p
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: "#FF2D55" }}
            >
              Process
            </p>
            <h2
              className="text-3xl sm:text-4xl font-black tracking-tighter"
              style={{ color: "#F1F3F8" }}
            >
              How it works
            </h2>
          </div>

          <div className="space-y-4">
            {STEPS.map((s) => (
              <div
                key={s.step}
                className="flex gap-5 p-6 rounded-2xl"
                style={{
                  background: "rgba(22,24,32,0.8)",
                  border: "1px solid rgba(255,255,255,0.06)",
                }}
              >
                <div
                  className="text-2xl font-black tracking-tighter shrink-0 w-10"
                  style={{ color: "#FF2D55" }}
                >
                  {s.step}
                </div>
                <div>
                  <h3
                    className="font-bold text-sm mb-1"
                    style={{ color: "#F1F3F8" }}
                  >
                    {s.title}
                  </h3>
                  <p className="text-sm leading-relaxed" style={{ color: "#9CA3AF" }}>
                    {s.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Section ──────────────────────────────────────────────────── */}
      <section className="py-24 px-6 text-center max-w-3xl mx-auto">
        <h2
          className="text-4xl sm:text-5xl font-black tracking-tighter mb-5"
          style={{ color: "#F1F3F8" }}
        >
          Ready to ace your exams?
        </h2>
        <p className="text-base mb-10" style={{ color: "#9CA3AF" }}>
          Join students already using AI Study Buddy to learn smarter.
        </p>
        <Link
          href="/register"
          className="px-10 py-4 font-bold rounded-xl text-sm inline-flex items-center gap-2"
          style={{
            background: "#FF2D55",
            color: "#fff",
            boxShadow: "0 0 50px rgba(255,45,85,0.35)",
          }}
        >
          Start Studying — It&apos;s Free
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
          </svg>
        </Link>
      </section>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer
        className="py-8 px-6 text-center text-xs"
        style={{
          borderTop: "1px solid rgba(255,255,255,0.06)",
          color: "#5C6070",
        }}
      >
        <p>
          AI-Powered Study Buddy · IBM SkillsBuild 2026 · MIT License
        </p>
        <p className="mt-1">
          Built with Next.js · FastAPI · LangChain · Google Gemini · ChromaDB
        </p>
      </footer>
    </div>
  );
}
