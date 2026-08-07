/**
 * app/(app)/profile/page.tsx — Premium User Profile & Achievements
 * ==================================================================
 * User avatar, study streaks, achievements, certificates, and learning stats.
 */

"use client";

import { useAuth } from "@/hooks/useAuth";
import { formatDate } from "@/lib/utils";

const ACHIEVEMENTS = [
  { icon: "🔥", title: "7-Day Streak", desc: "Studied 7 days in a row", unlocked: true },
  { icon: "🧠", title: "Master Mind", desc: "Scored 100% on 5 quizzes", unlocked: true },
  { icon: "📚", title: "Bookworm", desc: "Uploaded 10+ documents", unlocked: true },
  { icon: "⚡", title: "Speed Learner", desc: "Generated 50+ flashcards", unlocked: false },
];

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto space-y-8" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div>
        <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
          Profile & Badges
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Your academic identity, achievements, and learning milestones
        </p>
      </div>

      {/* ── Profile Header Card ─────────────────────────────────────────────── */}
      <div
        className="p-6 rounded-3xl flex items-center gap-6"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center text-3xl font-black shrink-0"
          style={{
            background: "linear-gradient(135deg, #FF2D55 0%, #FF6B8A 100%)",
            color: "#fff",
            boxShadow: "0 8px 32px rgba(255,45,85,0.35)",
          }}
        >
          {user?.name?.charAt(0).toUpperCase() ?? "U"}
        </div>
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold" style={{ color: "#F1F3F8" }}>
              {user?.name}
            </h2>
            <span
              className="text-2xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ background: "rgba(255,45,85,0.12)", color: "#FF2D55" }}
            >
              Pro Learner
            </span>
          </div>
          <p className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
            {user?.email}
          </p>

          <div className="flex items-center gap-4 mt-3 text-xs" style={{ color: "#9CA3AF" }}>
            <span>🔥 {user?.study_streak ?? 0} day streak</span>
            <span>·</span>
            <span>📄 {user?.document_count ?? 0} documents</span>
            <span>·</span>
            <span>📅 Joined {user ? formatDate(user.created_at) : "—"}</span>
          </div>
        </div>
      </div>

      {/* ── Achievements Grid ────────────────────────────────────────────────── */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-wider mb-4" style={{ color: "#9CA3AF" }}>
          Earned Badges & Achievements
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {ACHIEVEMENTS.map((a) => (
            <div
              key={a.title}
              className="p-5 rounded-2xl transition-all"
              style={{
                background: "#0F1115",
                border: a.unlocked ? "1px solid rgba(255,45,85,0.2)" : "1px solid rgba(255,255,255,0.06)",
                opacity: a.unlocked ? 1 : 0.45,
              }}
            >
              <span className="text-3xl mb-2 block">{a.icon}</span>
              <p className="text-sm font-bold" style={{ color: a.unlocked ? "#F1F3F8" : "#5C6070" }}>
                {a.title}
              </p>
              <p className="text-2xs mt-1 leading-relaxed" style={{ color: "#5C6070" }}>
                {a.desc}
              </p>
              <span
                className="inline-block mt-3 text-2xs font-bold uppercase tracking-wider"
                style={{ color: a.unlocked ? "#10B981" : "#5C6070" }}
              >
                {a.unlocked ? "✓ Unlocked" : "🔒 In Progress"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
