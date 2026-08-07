/**
 * lib/auth.ts — Auth helpers for Next.js
 * ========================================
 * Server + client auth utilities.
 */

import { token } from "@/lib/utils";
import type { User } from "@/types";

/** Decode JWT payload (no verification — verification happens on server) */
export function decodeJwt(jwt: string): Record<string, unknown> | null {
  try {
    const payload = jwt.split(".")[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

/** Check if a stored JWT token is expired */
export function isTokenExpired(): boolean {
  const t = token.get();
  if (!t) return true;
  const decoded = decodeJwt(t);
  if (!decoded?.exp) return true;
  return (decoded.exp as number) * 1000 < Date.now();
}

/** Store token and user in localStorage */
export function saveSession(accessToken: string, user: User): void {
  token.set(accessToken);
  localStorage.setItem("user", JSON.stringify(user));
}

/** Clear all auth data from localStorage */
export function clearSession(): void {
  token.clear();
  localStorage.removeItem("user");
}

/** Get cached user from localStorage (may be stale — refetch on mount) */
export function getCachedUser(): User | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}
