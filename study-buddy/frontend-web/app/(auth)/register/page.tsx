/**
 * app/(auth)/register/page.tsx — Premium Account Creation
 * =========================================================
 * Full name, email, password registration with instant token setting.
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const { register, isRegisterPending } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register({
      username: form.email,
      email:    form.email,
      name:     form.name,
      password: form.password,
    });
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
          Create an Account
        </h1>
        <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
          Get instant access to AI tutoring, quizzes, and flashcards
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
            Full Name
          </label>
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Alex Johnson"
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
            Email Address
          </label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="alex@university.edu"
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
            Create Password
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
          disabled={isRegisterPending}
          className="w-full py-3.5 rounded-xl font-bold text-xs transition-all mt-2"
          style={{
            background: "#FF2D55",
            color: "#fff",
            boxShadow: "0 4px 20px rgba(255,45,85,0.35)",
          }}
        >
          {isRegisterPending ? "Creating Account…" : "Create Free Account →"}
        </button>
      </form>

      <div
        className="pt-4 text-center text-xs"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)", color: "#5C6070" }}
      >
        Already have an account?{" "}
        <Link href="/login" className="font-bold hover:underline" style={{ color: "#FF2D55" }}>
          Sign In
        </Link>
      </div>
    </div>
  );
}
