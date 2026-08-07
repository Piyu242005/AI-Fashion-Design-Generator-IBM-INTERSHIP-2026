/**
 * lib/utils.ts — AI-Powered Study Buddy
 * =======================================
 * Shared utility functions used across components.
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// ── Class name helper ──────────────────────────────────────────────────────
// Combines clsx (conditional classes) with twMerge (deduplication).
// Usage: cn("text-sm", isActive && "font-bold", "text-blue-500")
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// ── Token storage ──────────────────────────────────────────────────────────

export const token = {
  get: (): string | null =>
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null,

  set: (value: string): void => {
    if (typeof window !== "undefined") localStorage.setItem("access_token", value);
  },

  clear: (): void => {
    if (typeof window !== "undefined") localStorage.removeItem("access_token");
  },

  isPresent: (): boolean => !!token.get(),
};

// ── Date formatting ────────────────────────────────────────────────────────

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatRelative(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1)  return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24)   return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ── File helpers ───────────────────────────────────────────────────────────

export const ACCEPTED_TYPES: Record<string, string[]> = {
  "application/pdf":                                               [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
  "text/plain":                                                    [".txt"],
};

export function formatFileSize(bytes: number): string {
  if (bytes < 1024)        return `${bytes} B`;
  if (bytes < 1_048_576)   return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1_048_576).toFixed(1)} MB`;
}

export function fileExtension(filename: string): string {
  return filename.split(".").pop()?.toLowerCase() ?? "";
}

// ── Score colour helper ────────────────────────────────────────────────────

export function scoreColor(score: number): string {
  if (score >= 80) return "text-green-500";
  if (score >= 60) return "text-yellow-500";
  return "text-red-500";
}

export function scoreBg(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

// ── String helpers ─────────────────────────────────────────────────────────

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + "...";
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ── Random ID (for client-side message IDs) ───────────────────────────────

export function uuid(): string {
  return crypto.randomUUID();
}
