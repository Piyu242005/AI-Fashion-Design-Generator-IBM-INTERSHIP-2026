/**
 * app/(auth)/login/page.tsx — Premium Sign In Form
 * ==================================================
 * Luxury dark styling, email/password inputs with focus glow,
 * and loading states.
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isLoginPending } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(form);
  };

  return (
    <div
      className="p-8 rounded-3xl space-y-6"
      style={{
        background: "#0F1115",
        border: "1px solid rgba(255,255,255,0.08)",
        boxShadow: "0 20px 60px rgba(0,0,0,0.8)",
      }}
    >
      <div>
        <h1 className="text-2xl font-black tracking-tight" style={{ color: "#F1F3F8" }}>
          Welcome back
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Sign in to access your study materials and chat history
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
            Email Address
          </label>
          <input
            type="email"
            required
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            placeholder="you@university.edu"
            className="w-full px-4 py-3 rounded-xl text-xs outline-none transition-all"
            style={{
              background: "#161820",
              border: "1px solid rgba(255,255,255,0.08)",
              color: "#F1F3F8",
            }}
          />
        </div>

        <div>
          <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
            Password
          </label>
          <input
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••••••"
            className="w-full px-4 py-3 rounded-xl text-xs outline-none transition-all"
            style={{
              background: "#161820",
              border: "1px solid rgba(255,255,255,0.08)",
              color: "#F1F3F8",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoginPending}
          className="w-full py-3.5 rounded-xl font-bold text-xs transition-all mt-2"
          style={{
            background: "#FF2D55",
            color: "#fff",
            boxShadow: "0 4px 20px rgba(255,45,85,0.35)",
          }}
        >
          {isLoginPending ? "Authenticating…" : "Sign In to Workspace →"}
        </button>
      </form>

      <div
        className="pt-4 text-center text-xs"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)", color: "#5C6070" }}
      >
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-bold hover:underline" style={{ color: "#FF2D55" }}>
          Create one now
        </Link>
      </div>
    </div>
  );
}
