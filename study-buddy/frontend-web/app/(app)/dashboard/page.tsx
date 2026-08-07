/**
 * app/(app)/dashboard/page.tsx — Dashboard
 * ==========================================
 * KPI cards, topic progress, AI recommendations, recent activity.
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/services/api";
import { scoreColor, scoreBg } from "@/lib/utils";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard"],
    queryFn:  async () => (await dashboardApi.stats()).data,
  });

  if (isLoading) return <DashboardSkeleton />;
  if (!stats)    return <p className="text-slate-400">Could not load dashboard.</p>;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in-up">
      <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Dashboard</h1>

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Documents",   value: stats.document_count, icon: "📄" },
          { label: "Quizzes",     value: stats.quiz_count,     icon: "❓" },
          { label: "Avg Score",   value: `${stats.avg_quiz_score.toFixed(0)}%`, icon: "🎯" },
          { label: "Study Streak",value: `${stats.study_streak}d`, icon: "🔥" },
        ].map((k) => (
          <div key={k.label} className="card text-center">
            <div className="text-2xl mb-1">{k.icon}</div>
            <div className="text-2xl font-bold text-blue-500">{k.value}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{k.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Topic Progress */}
        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-4">
            📈 Topic Progress
          </h2>
          {stats.topic_scores.length === 0 ? (
            <p className="text-sm text-slate-400">Take a quiz to see your topic scores.</p>
          ) : (
            <div className="space-y-3">
              {stats.topic_scores.map((t) => (
                <div key={t.topic}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-600 dark:text-slate-300">{t.topic}</span>
                    <span className={`font-semibold ${scoreColor(t.avg_score)}`}>
                      {t.avg_score.toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${scoreBg(t.avg_score)}`}
                      style={{ width: `${t.avg_score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Recommendations */}
        <div className="card">
          <h2 className="font-semibold text-slate-700 dark:text-slate-200 mb-4">
            🤖 AI Recommendations
          </h2>
          {stats.recommendations.length === 0 ? (
            <p className="text-sm text-slate-400">Upload documents and take quizzes to get personalised tips.</p>
          ) : (
            <div className="space-y-3">
              {stats.recommendations.map((r, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                >
                  <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1">
                    {r.priority === "high" ? "🔴" : r.priority === "medium" ? "🟡" : "🟢"}{" "}
                    {r.topic}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-300">{r.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="h-8 w-40 skeleton" />
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="card h-24 skeleton" />
        ))}
      </div>
    </div>
  );
}
