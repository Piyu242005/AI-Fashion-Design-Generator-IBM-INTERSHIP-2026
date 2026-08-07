/**
 * app/(app)/quiz/page.tsx — Quiz Generator
 * ==========================================
 * Select document, configure quiz, take it, and see your score.
 */

"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { quizApi } from "@/services/api";
import { useDocuments } from "@/hooks/useDocuments";
import type { QuizGenerateResponse, QuizQuestion, Difficulty, QuestionType } from "@/types";

type Screen = "config" | "quiz" | "results";

export default function QuizPage() {
  const { documents } = useDocuments();

  const [screen, setScreen]   = useState<Screen>("config");
  const [docId, setDocId]     = useState<number>(0);
  const [qType, setQType]     = useState<QuestionType>("mcq");
  const [diff, setDiff]       = useState<Difficulty>("medium");
  const [count, setCount]     = useState(5);
  const [topic, setTopic]     = useState("");
  const [quiz, setQuiz]       = useState<QuizGenerateResponse | null>(null);
  const [answers, setAnswers] = useState<string[]>([]);
  const [score, setScore]     = useState(0);

  const generateMutation = useMutation({
    mutationFn: () =>
      quizApi.generate({ document_id: docId, num_questions: count, question_type: qType, difficulty: diff, topic: topic || undefined }),
    onSuccess: (res) => {
      setQuiz(res.data);
      setAnswers(new Array(res.data.questions.length).fill(""));
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
    // Save to backend
    quizApi.submit({ document_id: docId, topic: topic || "General", score_pct: pct, num_questions: count });
    setScreen("results");
  };

  // ── Config screen ────────────────────────────────────────────────────────
  if (screen === "config") {
    return (
      <div className="max-w-xl mx-auto animate-fade-in-up">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">❓ Quiz Generator</h1>
        <div className="card space-y-5">
          <Select label="Document" value={String(docId)} onChange={(v) => setDocId(Number(v))}>
            <option value={0}>Select a document…</option>
            {documents.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
          </Select>
          <Select label="Question Type" value={qType} onChange={(v) => setQType(v as QuestionType)}>
            {["mcq", "true_false", "short_answer", "mixed"].map((t) => (
              <option key={t} value={t}>{t.replace("_", " ").toUpperCase()}</option>
            ))}
          </Select>
          <Select label="Difficulty" value={diff} onChange={(v) => setDiff(v as Difficulty)}>
            {["easy", "medium", "hard"].map((d) => (
              <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
            ))}
          </Select>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Number of Questions: {count}
            </label>
            <input type="range" min={3} max={20} value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full accent-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Topic (optional)
            </label>
            <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Photosynthesis"
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={!docId || generateMutation.isPending}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-colors"
          >
            {generateMutation.isPending ? "Generating…" : "Generate Quiz →"}
          </button>
        </div>
      </div>
    );
  }

  // ── Quiz screen ──────────────────────────────────────────────────────────
  if (screen === "quiz" && quiz) {
    return (
      <div className="max-w-2xl mx-auto animate-fade-in-up">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-slate-800 dark:text-white">❓ Quiz</h1>
          <span className="text-sm text-slate-400">{quiz.num_questions} questions · {quiz.difficulty}</span>
        </div>
        <div className="space-y-6">
          {quiz.questions.map((q: QuizQuestion, i: number) => (
            <div key={i} className="card">
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">
                {i + 1}. {q.question}
              </p>
              {q.options.length > 0 ? (
                <div className="space-y-2">
                  {q.options.map((opt) => (
                    <label key={opt} className="flex items-center gap-3 cursor-pointer group">
                      <input type="radio" name={`q-${i}`} value={opt}
                        checked={answers[i] === opt}
                        onChange={() => setAnswers(prev => { const a = [...prev]; a[i] = opt; return a; })}
                        className="accent-blue-500 w-4 h-4" />
                      <span className="text-sm text-slate-600 dark:text-slate-300 group-hover:text-blue-500 transition-colors">{opt}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <input type="text" value={answers[i] || ""} placeholder="Your answer…"
                  onChange={(e) => setAnswers(prev => { const a = [...prev]; a[i] = e.target.value; return a; })}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500" />
              )}
            </div>
          ))}
        </div>
        <button onClick={handleSubmit}
          className="mt-6 w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl text-sm transition-colors">
          Submit Answers
        </button>
      </div>
    );
  }

  // ── Results screen ───────────────────────────────────────────────────────
  return (
    <div className="max-w-xl mx-auto text-center animate-fade-in-up">
      <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Quiz Complete!</h1>
      <div className={`text-6xl font-extrabold my-6 ${score >= 80 ? "text-green-500" : score >= 60 ? "text-yellow-500" : "text-red-500"}`}>
        {score}%
      </div>
      <p className="text-slate-500 dark:text-slate-400 mb-8">
        {score >= 80 ? "Excellent work! 🎉" : score >= 60 ? "Good effort! Keep practicing. 💪" : "Review the material and try again. 📚"}
      </p>
      <button onClick={() => { setScreen("config"); setQuiz(null); }}
        className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-colors">
        Try Another Quiz
      </button>
    </div>
  );
}

function Select({ label, value, onChange, children }: {
  label: string; value: string;
  onChange: (v: string) => void; children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
        {children}
      </select>
    </div>
  );
}
