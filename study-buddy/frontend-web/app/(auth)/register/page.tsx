/**
 * app/(auth)/register/page.tsx — Registration Page
 * ==================================================
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const { register, isRegisterPending } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    register({ name: form.name, email: form.email, password: form.password });
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-6 text-center">
        Create Account
      </h2>

      {error && (
        <div className="mb-4 px-4 py-2.5 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {[
          { label: "Full Name",        key: "name",     type: "text",     placeholder: "Jane Smith" },
          { label: "Email",            key: "email",    type: "email",    placeholder: "jane@example.com" },
          { label: "Password",         key: "password", type: "password", placeholder: "Minimum 8 characters" },
          { label: "Confirm Password", key: "confirm",  type: "password", placeholder: "Repeat password" },
        ].map(({ label, key, type, placeholder }) => (
          <div key={key}>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {label}
            </label>
            <input
              type={type}
              required
              value={form[key as keyof typeof form]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              placeholder={placeholder}
              className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        ))}

        <button
          type="submit"
          disabled={isRegisterPending}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-lg text-sm transition-colors"
        >
          {isRegisterPending ? "Creating account…" : "Create Account"}
        </button>
      </form>

      <p className="text-center text-sm text-slate-500 dark:text-slate-400 mt-5">
        Already have an account?{" "}
        <Link href="/login" className="text-blue-500 hover:underline font-medium">
          Sign In
        </Link>
      </p>
    </div>
  );
}
