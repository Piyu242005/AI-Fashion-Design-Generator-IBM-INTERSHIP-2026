/**
 * app/(app)/quiz/page.tsx — Premium AI Quiz Generator
 * =====================================================
 * Interactive MCQ, True/False, and Short Answer quizzes with timer,
 * progress bar, live feedback, and animated score screen.
 */

"use client";

import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { quizApi } from "@/services/api";
import { useDocuments } from "@/hooks/useDocuments";
import type { QuizGenerateResponse, QuizQuestion, Difficulty, QuestionType } from "@/types";

type Screen = "config" | "quiz" | "results";

export default function QuizPage() {
  const { documents } = useDocuments();

  const [screen, setScreen]     = useState<Screen>("config");
  const [docId, setDocId]       = useState<number>(0);
  const [qType, setQType]       = useState<QuestionType>("mcq");
  const [diff, setDiff]         = useState<Difficulty>("medium");
  const [count, setCount]       = useState(5);
  const [topic, setTopic]       = useState("");
  const [quiz, setQuiz]         = useState<QuizGenerateResponse | null>(null);
  const [answers, setAnswers]   = useState<string[]>([]);
  const [score, setScore]       = useState(0);
  const [timerSec, setTimerSec] = useState(0);

  // Timer while taking quiz
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (screen === "quiz") {
      interval = setInterval(() => setTimerSec((s) => s + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [screen]);

  const generateMutation = useMutation({
    mutationFn: () =>
      quizApi.generate({
        document_id: docId,
        num_questions: count,
        question_type: qType,
        difficulty: diff,
        topic: topic || undefined,
      }),
    onSuccess: (res) => {
      setQuiz(res.data);
      setAnswers(new Array(res.data.questions.length).fill(""));
      setTimerSec(0);
      setScreen("quiz");
    },
    onError: () => toast.error("Failed to generate quiz. Please try again."),
  });

  const handleSubmit = () => {
    if (!quiz) return;
    let correct = 0;
    quiz.questions.forEach((q, i) => {
      if (answers[i]?.trim().toLowerCase() === q.answer.trim().toLowerCase()) correct++;
    });
    const pct = Math.round((correct / quiz.questions.length) * 100);
    setScore(pct);
    quizApi.submit({
      document_id: docId,
      topic: topic || "General",
      score_pct: pct,
      num_questions: count,
    });
    setScreen("results");
  };

  const formatTimer = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  // ── Config Screen ──────────────────────────────────────────────────────────
  if (screen === "config") {
    return (
      <div className="max-w-xl mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
        <div>
          <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
            Quiz Generator
          </h1>
          <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
            Generate adaptive, multi-format quizzes from your materials
          </p>
        </div>

        <div
          className="p-6 rounded-2xl space-y-5"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          {/* Document selection */}
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Target Document
            </label>
            <select
              value={docId}
              onChange={(e) => setDocId(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none transition-all"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            >
              <option value={0}>Select a document…</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename}
                </option>
              ))}
            </select>
          </div>

          {/* Question Type & Difficulty grid */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
                Question Type
              </label>
              <select
                value={qType}
                onChange={(e) => setQType(e.target.value as QuestionType)}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none"
                style={{
                  background: "#161820",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: "#F1F3F8",
                }}
              >
                <option value="mcq">Multiple Choice</option>
                <option value="true_false">True / False</option>
                <option value="short_answer">Short Answer</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div>
              <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
                Difficulty
              </label>
              <select
                value={diff}
                onChange={(e) => setDiff(e.target.value as Difficulty)}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none"
                style={{
                  background: "#161820",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: "#F1F3F8",
                }}
              >
                <option value="easy">🟢 Easy</option>
                <option value="medium">🟡 Medium</option>
                <option value="hard">🔴 Hard</option>
              </select>
            </div>
          </div>

          {/* Question count */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-2xs font-semibold uppercase tracking-wider" style={{ color: "#9CA3AF" }}>
                Number of Questions
              </label>
              <span className="text-xs font-bold" style={{ color: "#FF2D55" }}>
                {count} questions
              </span>
            </div>
            <input
              type="range"
              min={3}
              max={15}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full accent-[#FF2D55]"
            />
          </div>

          {/* Topic */}
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Focus Topic (Optional)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Chapter 4 Neural Networks"
              className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none"
              style={{
                background: "#161820",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#F1F3F8",
              }}
            />
          </div>

          <button
            onClick={() => generateMutation.mutate()}
            disabled={!docId || generateMutation.isPending}
            className="w-full py-3.5 rounded-xl text-sm font-semibold transition-all"
            style={{
              background: !docId || generateMutation.isPending ? "rgba(255,255,255,0.06)" : "#FF2D55",
              color: !docId || generateMutation.isPending ? "#5C6070" : "#fff",
              boxShadow: docId && !generateMutation.isPending ? "0 4px 20px rgba(255,45,85,0.35)" : "none",
            }}
          >
            {generateMutation.isPending ? "Generating Quiz with AI…" : "Generate Quiz →"}
          </button>
        </div>
      </div>
    );
  }

  // ── Quiz Taking Screen ─────────────────────────────────────────────────────
  if (screen === "quiz" && quiz) {
    const answeredCount = answers.filter((a) => a.trim() !== "").length;
    const progressPct = (answeredCount / quiz.questions.length) * 100;

    return (
      <div className="max-w-2xl mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
        {/* Progress & timer bar */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold" style={{ color: "#F1F3F8" }}>
              Quiz in Progress
            </h1>
            <p className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
              {answeredCount} of {quiz.questions.length} answered
            </p>
          </div>
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl"
            style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <span className="text-xs">⏱️</span>
            <span className="text-xs font-mono font-bold" style={{ color: "#FF2D55" }}>
              {formatTimer(timerSec)}
            </span>
          </div>
        </div>

        {/* Progress track */}
        <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{ width: `${progressPct}%`, background: "#FF2D55" }}
          />
        </div>

        {/* Questions list */}
        <div className="space-y-4">
          {quiz.questions.map((q: QuizQuestion, i: number) => (
            <div
              key={i}
              className="p-5 rounded-2xl space-y-4"
              style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div className="flex items-start gap-3">
                <span
                  className="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                  style={{ background: "rgba(255,45,85,0.12)", color: "#FF2D55" }}
                >
                  {i + 1}
                </span>
                <p className="text-sm font-semibold leading-relaxed" style={{ color: "#F1F3F8" }}>
                  {q.question}
                </p>
              </div>

              {q.options && q.options.length > 0 ? (
                <div className="space-y-2 pt-1 pl-9">
                  {q.options.map((opt) => {
                    const isSelected = answers[i] === opt;
                    return (
                      <button
                        key={opt}
                        onClick={() =>
                          setAnswers((prev) => {
                            const a = [...prev];
                            a[i] = opt;
                            return a;
                          })
                        }
                        className="w-full p-3 rounded-xl text-left text-xs font-medium transition-all flex items-center gap-3"
                        style={{
                          background: isSelected ? "rgba(255,45,85,0.10)" : "rgba(255,255,255,0.02)",
                          border: isSelected ? "1px solid rgba(255,45,85,0.35)" : "1px solid rgba(255,255,255,0.06)",
                          color: isSelected ? "#FF2D55" : "#9CA3AF",
                        }}
                      >
                        <div
                          className="w-4 h-4 rounded-full border flex items-center justify-center shrink-0"
                          style={{
                            borderColor: isSelected ? "#FF2D55" : "rgba(255,255,255,0.2)",
                            background: isSelected ? "#FF2D55" : "transparent",
                          }}
                        >
                          {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                        <span>{opt}</span>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="pt-1 pl-9">
                  <input
                    type="text"
                    value={answers[i] || ""}
                    placeholder="Type your answer here…"
                    onChange={(e) =>
                      setAnswers((prev) => {
                        const a = [...prev];
                        a[i] = e.target.value;
                        return a;
                      })
                    }
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs outline-none"
                    style={{
                      background: "#161820",
                      border: "1px solid rgba(255,255,255,0.08)",
                      color: "#F1F3F8",
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          className="w-full py-4 rounded-xl font-bold text-sm transition-all"
          style={{
            background: "#10B981",
            color: "#fff",
            boxShadow: "0 4px 20px rgba(16,185,129,0.35)",
          }}
        >
          Submit Quiz for Grading →
        </button>
      </div>
    );
  }

  // ── Results Screen ─────────────────────────────────────────────────────────
  const isHigh = score >= 80;
  const isMed = score >= 60;
  const scoreColor = isHigh ? "#10B981" : isMed ? "#F59E0B" : "#EF4444";

  return (
    <div className="max-w-lg mx-auto text-center space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div
        className="p-8 rounded-3xl space-y-6"
        style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
      >
        <span className="text-5xl">{isHigh ? "🏆" : isMed ? "⚡" : "💡"}</span>

        <div>
          <h1 className="text-2xl font-black tracking-tight" style={{ color: "#F1F3F8" }}>
            Quiz Completed!
          </h1>
          <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
            Completed in {formatTimer(timerSec)}
          </p>
        </div>

        {/* Score Ring / Display */}
        <div
          className="w-32 h-32 rounded-full mx-auto flex flex-col items-center justify-center"
          style={{
            background: `radial-gradient(circle, ${scoreColor}15 0%, transparent 70%)`,
            border: `2px solid ${scoreColor}`,
            boxShadow: `0 0 30px ${scoreColor}30`,
          }}
        >
          <span className="text-4xl font-black tracking-tighter" style={{ color: scoreColor }}>
            {score}%
          </span>
          <span className="text-2xs font-semibold uppercase" style={{ color: "#5C6070" }}>
            Score
          </span>
        </div>

        <p className="text-xs leading-relaxed max-w-sm mx-auto" style={{ color: "#9CA3AF" }}>
          {isHigh
            ? "Outstanding performance! You have mastered this study material."
            : isMed
            ? "Solid understanding. Review the weak topics and try again for mastery."
            : "Keep practicing! Use AI Summaries and Chat to reinforce key concepts."}
        </p>

        <div className="flex gap-3 pt-2">
          <button
            onClick={() => {
              setScreen("config");
              setQuiz(null);
            }}
            className="flex-1 py-3 rounded-xl text-xs font-semibold transition-all"
            style={{
              background: "#FF2D55",
              color: "#fff",
              boxShadow: "0 4px 14px rgba(255,45,85,0.3)",
            }}
          >
            Take Another Quiz
          </button>
        </div>
      </div>
    </div>
  );
}
