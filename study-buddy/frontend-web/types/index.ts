/**
 * types/index.ts — AI-Powered Study Buddy
 * =========================================
 * Shared TypeScript type definitions for all API responses,
 * UI state, and domain models. Mirrors the Pydantic schemas
 * in backend/app/schemas/__init__.py exactly.
 */

// ── Auth ──────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  study_streak: number;
  document_count: number;
  created_at: string; // ISO 8601
}

export interface LoginRequest {
  username: string; // email address
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

// ── Documents ─────────────────────────────────────────────────────────────

export type DocumentStatus = "processing" | "ready" | "error";
export type DocumentType   = "pdf" | "docx" | "pptx" | "txt";

export interface Document {
  id: number;
  user_id: number;
  filename: string;
  file_type: DocumentType;
  chunk_count: number;
  status: DocumentStatus;
  uploaded_at: string; // ISO 8601
}

// ── Chat / RAG ────────────────────────────────────────────────────────────

export type ChatIntent = "ask" | "quiz" | "summary" | "flashcard" | "teach" | "blocked";

export interface ChatRequest {
  question: string;
  document_ids: number[];
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  intent: ChatIntent;
  intent_label: string;
  agent_name: string;
  latency_ms: number;
}

export interface ChatMessage {
  id: string; // client-side UUID
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  intent?: ChatIntent;
  timestamp: Date;
}

// ── Quiz ──────────────────────────────────────────────────────────────────

export type QuestionType = "mcq" | "true_false" | "short_answer" | "mixed";
export type Difficulty   = "easy" | "medium" | "hard";

export interface QuizQuestion {
  question: string;
  options: string[];       // empty for short_answer
  answer: string;
  explanation: string;
  type: QuestionType;
}

export interface QuizGenerateRequest {
  document_id: number;
  num_questions: number;
  question_type: QuestionType;
  difficulty: Difficulty;
  topic?: string;
}

export interface QuizGenerateResponse {
  document_id: number;
  questions: QuizQuestion[];
  num_questions: number;
  question_type: QuestionType;
  difficulty: Difficulty;
}

export interface QuizSubmitRequest {
  document_id: number;
  topic: string;
  score_pct: number;
  num_questions: number;
}

export interface QuizSubmitResponse {
  message: string;
  score_pct: number;
}

// ── Summary ───────────────────────────────────────────────────────────────

export type SummaryStyle = "bullet" | "paragraph" | "detailed";

export interface SummaryRequest {
  document_id: number;
  style: SummaryStyle;
  detail?: string;
}

export interface SummaryResponse {
  document_id: number;
  filename: string;
  summary: string;
  style: SummaryStyle;
  word_count: number;
}

// ── Flashcards ────────────────────────────────────────────────────────────

export interface Flashcard {
  front: string;
  back: string;
}

export interface FlashcardRequest {
  document_id: number;
  num_cards: number;
}

export interface FlashcardResponse {
  document_id: number;
  flashcards: Flashcard[];
  num_cards: number;
}

// ── Dashboard ─────────────────────────────────────────────────────────────

export interface TopicScore {
  topic: string;
  avg_score: number;
  attempts: number;
}

export interface Recommendation {
  topic: string;
  reason: string;
  priority: "high" | "medium" | "low";
}

export interface DashboardStats {
  document_count: number;
  quiz_count: number;
  avg_quiz_score: number;
  study_streak: number;
  total_chats: number;
  recent_chats: ChatMessage[];
  topic_scores: TopicScore[];
  recommendations: Recommendation[];
}

// ── UI State ──────────────────────────────────────────────────────────────

export interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
}

export type Theme = "dark" | "light" | "system";

export interface UserPreferences {
  theme: Theme;
  response_style: "concise" | "detailed";
  explain_level: "simple" | "intermediate" | "advanced";
  quiz_type: QuestionType;
  quiz_count: number;
  difficulty: Difficulty;
}
