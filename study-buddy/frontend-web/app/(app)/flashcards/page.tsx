/**
 * app/(app)/flashcards/page.tsx — Flashcard Study Interface
 * ===========================================================
 * Generate flip cards and track Known / Review status.
 */

"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { flashcardsApi } from "@/services/api";
import { useDocuments } from "@/hooks/useDocuments";
import type { Flashcard } from "@/types";

export default function FlashcardsPage() {
  const { documents } = useDocuments();

  const [docId, setDocId]       = useState(0);
  const [count, setCount]       = useState(10);
  const [cards, setCards]       = useState<Flashcard[]>([]);
  const [current, setCurrent]   = useState(0);
  const [flipped, setFlipped]   = useState(false);
  const [known, setKnown]       = useState<Set<number>>(new Set());
  const [review, setReview]     = useState<Set<number>>(new Set());
  const [generated, setGenerated] = useState(false);

  const genMutation = useMutation({
    mutationFn: () => flashcardsApi.generate({ document_id: docId, num_cards: count }),
    onSuccess: (res) => {
      setCards(res.data.flashcards);
      setCurrent(0);
      setFlipped(false);
      setKnown(new Set());
      setReview(new Set());
      setGenerated(true);
    },
    onError: () => toast.error("Failed to generate flashcards."),
  });

  const card = cards[current];

  const handleMark = (status: "known" | "review") => {
    if (status === "known") setKnown((s) => new Set([...s, current]));
    else setReview((s) => new Set([...s, current]));

    if (current < cards.length - 1) {
      setCurrent((n) => n + 1);
      setFlipped(false);
    }
  };

  if (!generated) {
    return (
      <div className="max-w-md mx-auto animate-fade-in-up">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">🃏 Flashcards</h1>
        <div className="card space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Document</label>
            <select value={docId} onChange={(e) => setDocId(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value={0}>Select a document…</option>
              {documents.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Number of Cards: {count}
            </label>
            <input type="range" min={5} max={30} value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full accent-blue-500" />
          </div>
          <button onClick={() => genMutation.mutate()}
            disabled={!docId || genMutation.isPending}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-colors">
            {genMutation.isPending ? "Generating…" : "Generate Flashcards →"}
          </button>
        </div>
      </div>
    );
  }

  // All cards reviewed
  if (current >= cards.length) {
    return (
      <div className="max-w-md mx-auto text-center animate-fade-in-up">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-2">Session Complete!</h2>
        <div className="flex justify-center gap-8 my-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-500">{known.size}</div>
            <div className="text-xs text-slate-400 mt-1">Known</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-500">{review.size}</div>
            <div className="text-xs text-slate-400 mt-1">To Review</div>
          </div>
        </div>
        <button onClick={() => setGenerated(false)}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-colors">
          Generate New Cards
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto animate-fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-slate-800 dark:text-white">🃏 Flashcards</h1>
        <span className="text-sm text-slate-400">{current + 1} / {cards.length}</span>
      </div>

      {/* Progress */}
      <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full mb-6 overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all"
          style={{ width: `${((current + 1) / cards.length) * 100}%` }} />
      </div>

      {/* Flip card */}
      <div
        onClick={() => setFlipped((f) => !f)}
        className="cursor-pointer rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#1e2130] p-8 min-h-[200px] flex flex-col items-center justify-center text-center select-none transition-all hover:border-blue-400"
      >
        <span className="text-xs text-slate-400 uppercase tracking-wider mb-4">
          {flipped ? "Answer" : "Question — click to reveal"}
        </span>
        <p className="text-lg font-semibold text-slate-800 dark:text-slate-100">
          {flipped ? card.back : card.front}
        </p>
      </div>

      {/* Actions — shown after flip */}
      {flipped && (
        <div className="flex gap-4 mt-6">
          <button onClick={() => handleMark("review")}
            className="flex-1 py-3 rounded-xl border-2 border-yellow-400 text-yellow-500 font-semibold text-sm hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors">
            🔁 Review
          </button>
          <button onClick={() => handleMark("known")}
            className="flex-1 py-3 rounded-xl bg-green-600 hover:bg-green-700 text-white font-semibold text-sm transition-colors">
            ✓ Known
          </button>
        </div>
      )}
    </div>
  );
}
