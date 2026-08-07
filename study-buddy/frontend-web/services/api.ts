/**
 * services/api.ts — AI-Powered Study Buddy
 * ==========================================
 * Centralised HTTP client for all FastAPI backend calls.
 *
 * Design decisions:
 *  - axios instance with base URL from env var
 *  - Request interceptor auto-attaches JWT from localStorage
 *  - Response interceptor handles 401 → redirect to /login
 *  - All functions are typed against the shared types/index.ts
 *
 * Usage:
 *   import { chatApi, quizApi } from '@/services/api'
 *   const res = await chatApi.ask({ question: '...', document_ids: [1] })
 */

import axios, { type AxiosInstance, type AxiosResponse } from "axios";
import type {
  ChatRequest,
  ChatResponse,
  DashboardStats,
  Document,
  FlashcardRequest,
  FlashcardResponse,
  LoginRequest,
  QuizGenerateRequest,
  QuizGenerateResponse,
  QuizSubmitRequest,
  QuizSubmitResponse,
  RegisterRequest,
  SummaryRequest,
  SummaryResponse,
  TokenResponse,
  User,
} from "@/types";

// ── Axios instance ─────────────────────────────────────────────────────────

const API_URL =
  typeof window !== "undefined"
    ? "/api" // client-side: use Next.js rewrite proxy
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000") + "/api/v1";

const http: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000, // 30s — Gemini can be slow on first call
});

// ── Request interceptor — attach JWT ──────────────────────────────────────

http.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ── Response interceptor — handle 401 globally ────────────────────────────

http.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// ── Auth API ──────────────────────────────────────────────────────────────

export const authApi = {
  register: (data: RegisterRequest): Promise<AxiosResponse<User>> =>
    http.post("/auth/register", data),

  login: (data: LoginRequest): Promise<AxiosResponse<TokenResponse>> => {
    // FastAPI OAuth2 expects form data, not JSON
    const form = new URLSearchParams();
    form.append("username", data.username);
    form.append("password", data.password);
    return http.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: (): Promise<AxiosResponse<User>> => http.get("/auth/me"),
};

// ── Documents API ─────────────────────────────────────────────────────────

export const documentsApi = {
  upload: (file: File): Promise<AxiosResponse<Document>> => {
    const form = new FormData();
    form.append("file", file);
    return http.post("/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  list: (): Promise<AxiosResponse<Document[]>> => http.get("/documents/"),

  delete: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    http.delete(`/documents/${id}`),
};

// ── Chat API ──────────────────────────────────────────────────────────────

export const chatApi = {
  ask: (data: ChatRequest): Promise<AxiosResponse<ChatResponse>> =>
    http.post("/chat/", data),

  history: (): Promise<AxiosResponse<ChatResponse[]>> =>
    http.get("/chat/history"),

  clearHistory: (): Promise<AxiosResponse<{ message: string }>> =>
    http.delete("/chat/history"),
};

// ── Quiz API ──────────────────────────────────────────────────────────────

export const quizApi = {
  generate: (
    data: QuizGenerateRequest,
  ): Promise<AxiosResponse<QuizGenerateResponse>> =>
    http.post("/quiz/generate", data),

  submit: (
    data: QuizSubmitRequest,
  ): Promise<AxiosResponse<QuizSubmitResponse>> =>
    http.post("/quiz/submit", data),
};

// ── Summary API ───────────────────────────────────────────────────────────

export const summaryApi = {
  generate: (
    data: SummaryRequest,
  ): Promise<AxiosResponse<SummaryResponse>> =>
    http.post("/summary/", data),
};

// ── Flashcards API ────────────────────────────────────────────────────────

export const flashcardsApi = {
  generate: (
    data: FlashcardRequest,
  ): Promise<AxiosResponse<FlashcardResponse>> =>
    http.post("/flashcards/generate", data),
};

// ── Dashboard API ─────────────────────────────────────────────────────────

export const dashboardApi = {
  stats: (): Promise<AxiosResponse<DashboardStats>> =>
    http.get("/dashboard/"),
};
