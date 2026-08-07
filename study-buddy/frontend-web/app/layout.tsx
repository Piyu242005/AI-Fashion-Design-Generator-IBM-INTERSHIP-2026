/**
 * app/layout.tsx — Root Layout
 * ==============================
 * Wraps every page with:
 *  - ThemeProvider (next-themes — class-based dark mode)
 *  - ReactQueryProvider (TanStack Query)
 *  - react-hot-toast container
 *  - Global fonts and styles
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "./providers";
import "@/styles/globals.css";

// ── Font ──────────────────────────────────────────────────────────────────
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

// ── SEO metadata ──────────────────────────────────────────────────────────
export const metadata: Metadata = {
  title: {
    default:  "AI Study Buddy",
    template: "%s | AI Study Buddy",
  },
  description:
    "AI-Powered Study Assistant — Upload documents, ask questions, generate quizzes and flashcards using RAG + Google Gemini.",
  keywords: [
    "AI", "study", "RAG", "flashcards", "quiz", "LangChain", "Gemini",
    "education", "learning", "IBM SkillsBuild",
  ],
  authors: [{ name: "AI Study Buddy Team" }],
  openGraph: {
    type:        "website",
    title:       "AI-Powered Study Buddy",
    description: "Personalised AI study assistant powered by Google Gemini + RAG",
    siteName:    "AI Study Buddy",
  },
};

// ── Root layout ───────────────────────────────────────────────────────────
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <body className="min-h-screen bg-white dark:bg-[#0f1117] antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
