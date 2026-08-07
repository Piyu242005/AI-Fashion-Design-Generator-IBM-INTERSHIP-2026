/**
 * app/(app)/layout.tsx — Premium Authenticated App Layout
 * =========================================================
 * Sidebar navigation with collapsed mode, active indicators,
 * notification badges, streak widget, and smooth animations.
 */

"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { token } from "@/lib/utils";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
      </svg>
    ),
    badge: null,
  },
  {
    href: "/chat",
    label: "AI Chat",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
      </svg>
    ),
    badge: null,
  },
  {
    href: "/documents",
    label: "Documents",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
      </svg>
    ),
    badge: null,
  },
  {
    href: "/summary",
    label: "Summary",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
      </svg>
    ),
    badge: null,
  },
  {
    href: "/quiz",
    label: "Quiz",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
      </svg>
    ),
    badge: null,
  },
  {
    href: "/flashcards",
    label: "Flashcards",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
      </svg>
    ),
    badge: null,
  },
];

const BOTTOM_NAV = [
  {
    href: "/profile",
    label: "Profile",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
      </svg>
    ),
  },
  {
    href: "/settings",
    label: "Settings",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
      </svg>
    ),
  },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router   = useRouter();
  const pathname = usePathname();
  const { user, isLoading, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!isLoading && !token.isPresent()) {
      router.push("/login");
    }
  }, [isLoading, router]);

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: "#050505" }}
      >
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-10 h-10 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: "#FF2D55", borderTopColor: "transparent" }}
          />
          <p className="text-xs" style={{ color: "#5C6070" }}>Loading your workspace…</p>
        </div>
      </div>
    );
  }

  const sidebarW = collapsed ? "72px" : "220px";

  return (
    <div
      className="flex min-h-screen"
      style={{ background: "#050505" }}
    >
      {/* ── Sidebar ──────────────────────────────────────────────────── */}
      <aside
        className="shrink-0 flex flex-col py-5 transition-all duration-300 relative"
        style={{
          width: sidebarW,
          background: "#0F1115",
          borderRight: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        {/* Brand */}
        <div
          className="flex items-center gap-3 px-4 mb-6"
          style={{ overflow: "hidden" }}
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-sm"
            style={{ background: "#FF2D55" }}
          >
            🧠
          </div>
          {!collapsed && (
            <div>
              <p className="text-xs font-bold tracking-tight" style={{ color: "#F1F3F8" }}>
                Study Buddy
              </p>
              <p className="text-2xs" style={{ color: "#5C6070" }}>
                AI Platform
              </p>
            </div>
          )}
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="absolute -right-3 top-7 w-6 h-6 rounded-full flex items-center justify-center transition-all"
          style={{
            background: "#0F1115",
            border: "1px solid rgba(255,255,255,0.10)",
            color: "#5C6070",
          }}
        >
          <svg
            viewBox="0 0 16 16"
            fill="currentColor"
            className="w-3 h-3 transition-transform"
            style={{ transform: collapsed ? "rotate(180deg)" : "rotate(0deg)" }}
          >
            <path d="M9.78 12.78a.75.75 0 01-1.06 0L4.47 8.53a.75.75 0 010-1.06l4.25-4.25a.75.75 0 011.06 1.06L6.06 8l3.72 3.72a.75.75 0 010 1.06z" />
          </svg>
        </button>

        {/* Divider */}
        <div className="mx-4 mb-3" style={{ height: "1px", background: "rgba(255,255,255,0.06)" }} />

        {/* Main Nav */}
        <nav className="flex-1 space-y-0.5 px-2">
          {NAV_ITEMS.map(({ href, label, icon, badge }) => {
            const isActive = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                title={collapsed ? label : undefined}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 relative group"
                style={{
                  background: isActive ? "rgba(255,45,85,0.10)" : "transparent",
                  color: isActive ? "#FF2D55" : "#9CA3AF",
                  border: isActive ? "1px solid rgba(255,45,85,0.2)" : "1px solid transparent",
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)";
                    (e.currentTarget as HTMLElement).style.color = "#F1F3F8";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                    (e.currentTarget as HTMLElement).style.color = "#9CA3AF";
                  }
                }}
              >
                {/* Active indicator bar */}
                {isActive && (
                  <div
                    className="absolute left-0 top-1/4 bottom-1/4 w-0.5 rounded-r"
                    style={{ background: "#FF2D55" }}
                  />
                )}
                <span className="shrink-0">{icon}</span>
                {!collapsed && <span className="truncate">{label}</span>}
                {!collapsed && badge && (
                  <span
                    className="ml-auto text-2xs font-bold px-1.5 py-0.5 rounded-full"
                    style={{ background: "rgba(255,45,85,0.15)", color: "#FF2D55" }}
                  >
                    {badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Study Streak */}
        {!collapsed && user && (
          <div
            className="mx-3 my-2 px-3 py-2.5 rounded-xl"
            style={{ background: "rgba(255,45,85,0.06)", border: "1px solid rgba(255,45,85,0.15)" }}
          >
            <div className="flex items-center gap-2">
              <span className="text-base">🔥</span>
              <div>
                <p className="text-xs font-bold" style={{ color: "#FF6B8A" }}>
                  {user.study_streak} Day Streak
                </p>
                <p className="text-2xs" style={{ color: "#5C6070" }}>
                  Keep it going!
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="mx-4 my-2" style={{ height: "1px", background: "rgba(255,255,255,0.06)" }} />

        {/* Bottom Nav */}
        <nav className="px-2 space-y-0.5">
          {BOTTOM_NAV.map(({ href, label, icon }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                title={collapsed ? label : undefined}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150"
                style={{
                  background: isActive ? "rgba(255,45,85,0.10)" : "transparent",
                  color: isActive ? "#FF2D55" : "#9CA3AF",
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)";
                    (e.currentTarget as HTMLElement).style.color = "#F1F3F8";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                    (e.currentTarget as HTMLElement).style.color = "#9CA3AF";
                  }
                }}
              >
                <span className="shrink-0">{icon}</span>
                {!collapsed && <span>{label}</span>}
              </Link>
            );
          })}

          {/* Logout */}
          <button
            onClick={logout}
            title={collapsed ? "Logout" : undefined}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150"
            style={{ color: "#5C6070" }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.color = "#EF4444";
              (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.08)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.color = "#5C6070";
              (e.currentTarget as HTMLElement).style.background = "transparent";
            }}
          >
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 shrink-0">
              <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
            </svg>
            {!collapsed && <span>Logout</span>}
          </button>
        </nav>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <main className="flex-1 overflow-auto">
        {/* Top bar */}
        <header
          className="sticky top-0 z-30 flex items-center justify-between px-8 py-4"
          style={{
            background: "rgba(5,5,5,0.8)",
            borderBottom: "1px solid rgba(255,255,255,0.05)",
            backdropFilter: "blur(16px)",
          }}
        >
          <div />
          {/* Right side: user chip */}
          {user && (
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl"
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                style={{ background: "#FF2D55", color: "#fff" }}
              >
                {user.name?.charAt(0).toUpperCase() ?? "U"}
              </div>
              <span className="text-xs font-medium" style={{ color: "#9CA3AF" }}>
                {user.name}
              </span>
            </div>
          )}
        </header>

        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
