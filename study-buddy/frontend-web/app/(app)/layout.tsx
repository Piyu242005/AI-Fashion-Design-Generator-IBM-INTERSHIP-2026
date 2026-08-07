/**
 * app/(app)/layout.tsx — Authenticated App Layout
 * =================================================
 * Wraps all protected pages with sidebar navigation.
 * Redirects unauthenticated users to /login.
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { token } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard",  icon: "📊", label: "Dashboard"  },
  { href: "/chat",       icon: "💬", label: "Chat"        },
  { href: "/summary",    icon: "📝", label: "Summary"     },
  { href: "/quiz",       icon: "❓", label: "Quiz"        },
  { href: "/flashcards", icon: "🃏", label: "Flashcards"  },
  { href: "/profile",    icon: "👤", label: "Profile"     },
  { href: "/settings",   icon: "⚙️", label: "Settings"    },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading, logout } = useAuth();

  // Redirect to login if no token
  useEffect(() => {
    if (!isLoading && !token.isPresent()) {
      router.push("/login");
    }
  }, [isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f1117]">
        <div className="text-slate-400 text-sm animate-pulse">Loading…</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-[#0f1117]">

      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside className="w-60 shrink-0 bg-white dark:bg-[#1e2130] border-r border-slate-200 dark:border-slate-700 flex flex-col py-6 px-4">
        {/* Brand */}
        <div className="mb-8 px-2">
          <span className="text-lg font-bold text-blue-500">🎓 AI Study Buddy</span>
          {user && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 truncate">
              {user.name}
            </p>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map(({ href, icon, label }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/60 hover:text-blue-500 transition-colors"
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          ))}
        </nav>

        {/* Study Streak */}
        {user && (
          <div className="mt-4 px-3 py-2.5 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800">
            <p className="text-xs font-semibold text-orange-600 dark:text-orange-400">
              🔥 {user.study_streak} day streak
            </p>
          </div>
        )}

        {/* Logout */}
        <button
          onClick={logout}
          className="mt-4 flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors w-full"
        >
          <span>🚪</span> Logout
        </button>
      </aside>

      {/* ── Main content ────────────────────────────────────────────── */}
      <main className="flex-1 overflow-auto p-8">
        {children}
      </main>
    </div>
  );
}
