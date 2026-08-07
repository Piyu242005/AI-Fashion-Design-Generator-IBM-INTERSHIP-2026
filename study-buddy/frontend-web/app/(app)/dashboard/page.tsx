/**
 * app/(app)/dashboard/page.tsx — Premium Executive Dashboard
 * ============================================================
 * KPI stat cards, topic progress, AI recommendations, activity feed.
 * Luxury dark red aesthetic — no generic charts.
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/services/api";
import type { DashboardStats } from "@/types";

function scoreColor(s: number): string {
  if (s >= 80) return "#10B981";
  if (s >= 60) return "#F59E0B";
  return "#EF4444";
}

const QUICK_ACTIONS = [
  { label: "Start Chat", icon: "💬", href: "/chat", desc: "Ask AI a question" },
  { label: "New Quiz",   icon: "🎯", href: "/quiz",  desc: "Test your knowledge" },
  { label: "Flashcards", icon: "🃏", href: "/flashcards", desc: "Review key concepts" },
  { label: "Summarize",  icon: "📝", href: "/summary", desc: "Generate summary" },
];

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey:  ["dashboard"],
    queryFn:   async () => (await dashboardApi.stats()).data,
    staleTime: 30_000,
  });

  if (isLoading) return <DashboardSkeleton />;
  if (!stats)    return (
    <div className="flex items-center justify-center h-64">
      <p className="text-sm" style={{ color: "#5C6070" }}>Could not load dashboard.</p>
    </div>
  );

  const KPI_CARDS = [
    {
      label: "Study Streak",
      value: `${stats.study_streak}`,
      unit: "days",
      icon: "🔥",
      trend: "+2 this week",
      trendUp: true,
      accent: "#FF2D55",
      accentDim: "rgba(255,45,85,0.10)",
    },
    {
      label: "Documents",
      value: `${stats.document_count}`,
      unit: "files",
      icon: "📄",
      trend: "Ready to query",
      trendUp: true,
      accent: "#6366F1",
      accentDim: "rgba(99,102,241,0.10)",
    },
    {
      label: "Quiz Accuracy",
      value: `${stats.avg_quiz_score?.toFixed(0) ?? 0}`,
      unit: "%",
      icon: "🎯",
      trend: `${stats.quiz_count} quizzes taken`,
      trendUp: stats.avg_quiz_score >= 70,
      accent: "#10B981",
      accentDim: "rgba(16,185,129,0.10)",
    },
    {
      label: "AI Sessions",
      value: `${stats.total_chat_sessions ?? 0}`,
      unit: "chats",
      icon: "🤖",
      trend: "Gemini powered",
      trendUp: true,
      accent: "#F59E0B",
      accentDim: "rgba(245,158,11,0.10)",
    },
  ];

  return (
    <div
      className="max-w-6xl mx-auto space-y-8"
      style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}
    >
      {/* Page header */}
      <div>
        <h1
          className="text-3xl font-black tracking-tighter"
          style={{ color: "#F1F3F8" }}
        >
          Dashboard
        </h1>
        <p className="text-sm mt-1" style={{ color: "#5C6070" }}>
          Your learning command center
        </p>
      </div>

      {/* ── KPI Cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {KPI_CARDS.map((card) => (
          <div
            key={card.label}
            className="p-5 rounded-2xl transition-all duration-200 cursor-default group"
            style={{
              background: "#0F1115",
              border: "1px solid rgba(255,255,255,0.06)",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = card.accent + "40";
              (e.currentTarget as HTMLElement).style.transform = "translateY(-2px)";
              (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 32px ${card.accent}15`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)";
              (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
              (e.currentTarget as HTMLElement).style.boxShadow = "none";
            }}
          >
            <div className="flex items-start justify-between mb-3">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center text-base"
                style={{ background: card.accentDim }}
              >
                {card.icon}
              </div>
            </div>
            <div className="flex items-baseline gap-1">
              <span
                className="text-3xl font-black tracking-tighter"
                style={{ color: card.accent }}
              >
                {card.value}
              </span>
              <span className="text-xs font-medium" style={{ color: "#5C6070" }}>
                {card.unit}
              </span>
            </div>
            <p className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
              {card.label}
            </p>
            <p
              className="text-2xs mt-2 font-medium"
              style={{ color: card.trendUp ? "#10B981" : "#EF4444" }}
            >
              {card.trendUp ? "↑" : "↓"} {card.trend}
            </p>
          </div>
        ))}
      </div>

      {/* ── Main grid ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Topic Progress */}
        <div
          className="lg:col-span-2 p-6 rounded-2xl"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-sm font-bold" style={{ color: "#F1F3F8" }}>
              Topic Progress
            </h2>
            <span
              className="text-2xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ background: "rgba(255,45,85,0.10)", color: "#FF2D55" }}
            >
              Live
            </span>
          </div>

          {stats.topic_scores.length === 0 ? (
            <div
              className="flex flex-col items-center justify-center py-10 rounded-xl"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px dashed rgba(255,255,255,0.08)" }}
            >
              <p className="text-2xl mb-2">📊</p>
              <p className="text-xs" style={{ color: "#5C6070" }}>
                Take a quiz to see your topic scores
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {stats.topic_scores.map((t) => {
                const color = scoreColor(t.avg_score);
                return (
                  <div key={t.topic}>
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-xs font-medium" style={{ color: "#9CA3AF" }}>
                        {t.topic}
                      </span>
                      <span className="text-xs font-bold" style={{ color }}>
                        {t.avg_score.toFixed(0)}%
                      </span>
                    </div>
                    <div
                      className="h-1.5 rounded-full overflow-hidden"
                      style={{ background: "rgba(255,255,255,0.06)" }}
                    >
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${t.avg_score}%`, background: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* AI Recommendations */}
        <div
          className="p-6 rounded-2xl"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <h2 className="text-sm font-bold mb-5" style={{ color: "#F1F3F8" }}>
            AI Recommendations
          </h2>

          {stats.recommendations.length === 0 ? (
            <div
              className="flex flex-col items-center justify-center py-8 rounded-xl text-center"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px dashed rgba(255,255,255,0.08)" }}
            >
              <p className="text-2xl mb-2">🤖</p>
              <p className="text-xs" style={{ color: "#5C6070" }}>
                Upload documents and take quizzes to unlock personalised tips
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {stats.recommendations.map((r, i) => {
                const pColor = r.priority === "high" ? "#EF4444"
                             : r.priority === "medium" ? "#F59E0B"
                             : "#10B981";
                return (
                  <div
                    key={i}
                    className="p-3.5 rounded-xl"
                    style={{
                      background: "rgba(255,255,255,0.02)",
                      border: "1px solid rgba(255,255,255,0.06)",
                    }}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div
                        className="w-1.5 h-1.5 rounded-full shrink-0"
                        style={{ background: pColor }}
                      />
                      <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                        {r.topic}
                      </p>
                    </div>
                    <p className="text-xs leading-relaxed" style={{ color: "#5C6070" }}>
                      {r.reason}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Quick Actions ──────────────────────────────────────────── */}
      <div>
        <h2 className="text-sm font-bold mb-4" style={{ color: "#9CA3AF" }}>
          Quick Actions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {QUICK_ACTIONS.map((a) => (
            <a
              key={a.label}
              href={a.href}
              className="group flex flex-col gap-2 p-4 rounded-2xl transition-all duration-200"
              style={{
                background: "#0F1115",
                border: "1px solid rgba(255,255,255,0.06)",
                textDecoration: "none",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,45,85,0.25)";
                (e.currentTarget as HTMLElement).style.background = "rgba(255,45,85,0.04)";
                (e.currentTarget as HTMLElement).style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)";
                (e.currentTarget as HTMLElement).style.background = "#0F1115";
                (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
              }}
            >
              <span className="text-xl">{a.icon}</span>
              <div>
                <p className="text-xs font-semibold" style={{ color: "#F1F3F8" }}>
                  {a.label}
                </p>
                <p className="text-2xs" style={{ color: "#5C6070" }}>
                  {a.desc}
                </p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Skeleton ─────────────────────────────────────────────────────────────── */
function DashboardSkeleton() {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="h-8 w-48 rounded-xl" style={{ background: "#161820" }} />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-28 rounded-2xl"
            style={{
              background: "linear-gradient(90deg, #0F1115 25%, #161820 50%, #0F1115 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.6s infinite linear",
            }}
          />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div
          className="lg:col-span-2 h-64 rounded-2xl"
          style={{
            background: "linear-gradient(90deg, #0F1115 25%, #161820 50%, #0F1115 75%)",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.6s infinite linear",
          }}
        />
        <div
          className="h-64 rounded-2xl"
          style={{
            background: "linear-gradient(90deg, #0F1115 25%, #161820 50%, #0F1115 75%)",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.6s infinite linear",
          }}
        />
      </div>
    </div>
  );
}
