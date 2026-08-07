/**
 * app/(app)/flashcards/page.tsx — Premium 3D Flashcard Study Interface
 * ======================================================================
 * Interactive 3D flip cards with active recall tracking, progress bar,
 * keyboard shortcut support (Space to flip, 1 for Review, 2 for Known).
 */

"use client";

import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { flashcardsApi } from "@/services/api";
import { useDocuments } from "@/hooks/useDocuments";
import type { Flashcard } from "@/types";

export default function FlashcardsPage() {
  const { documents } = useDocuments();

  const [docId, setDocId]         = useState(0);
  const [count, setCount]         = useState(10);
  const [cards, setCards]         = useState<Flashcard[]>([]);
  const [current, setCurrent]     = useState(0);
  const [flipped, setFlipped]     = useState(false);
  const [known, setKnown]         = useState<Set<number>>(new Set());
  const [review, setReview]       = useState<Set<number>>(new Set());
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
    } else {
      setCurrent(cards.length);
    }
  };

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!generated || current >= cards.length) return;
      if (e.code === "Space") {
        e.preventDefault();
        setFlipped((f) => !f);
      } else if (e.key === "1" && flipped) {
        handleMark("review");
      } else if (e.key === "2" && flipped) {
        handleMark("known");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [generated, current, flipped, cards.length]);

  // ── Generation Form ────────────────────────────────────────────────────────
  if (!generated) {
    return (
      <div className="max-w-md mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
        <div>
          <h1 className="text-3xl font-black tracking-tighter" style={{ color: "#F1F3F8" }}>
            Smart Flashcards
          </h1>
          <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
            AI-extracted key concepts with active recall spaced repetition
          </p>
        </div>

        <div
          className="p-6 rounded-2xl space-y-5"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div>
            <label className="block text-2xs font-semibold uppercase tracking-wider mb-2" style={{ color: "#9CA3AF" }}>
              Source Document
            </label>
            <select
              value={docId}
              onChange={(e) => setDocId(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none"
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

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-2xs font-semibold uppercase tracking-wider" style={{ color: "#9CA3AF" }}>
                Number of Cards
              </label>
              <span className="text-xs font-bold" style={{ color: "#FF2D55" }}>
                {count} cards
              </span>
            </div>
            <input
              type="range"
              min={5}
              max={25}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full accent-[#FF2D55]"
            />
          </div>

          <button
            onClick={() => genMutation.mutate()}
            disabled={!docId || genMutation.isPending}
            className="w-full py-3.5 rounded-xl text-sm font-semibold transition-all"
            style={{
              background: !docId || genMutation.isPending ? "rgba(255,255,255,0.06)" : "#FF2D55",
              color: !docId || genMutation.isPending ? "#5C6070" : "#fff",
              boxShadow: docId && !genMutation.isPending ? "0 4px 20px rgba(255,45,85,0.35)" : "none",
            }}
          >
            {genMutation.isPending ? "Extracting Concepts with AI…" : "Generate Deck →"}
          </button>
        </div>
      </div>
    );
  }

  // ── Session Finished Screen ────────────────────────────────────────────────
  if (current >= cards.length) {
    const accuracy = Math.round((known.size / cards.length) * 100);
    return (
      <div className="max-w-md mx-auto text-center space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
        <div
          className="p-8 rounded-3xl space-y-6"
          style={{ background: "#0F1115", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <span className="text-5xl">🎉</span>
          <div>
            <h1 className="text-2xl font-black tracking-tight" style={{ color: "#F1F3F8" }}>
              Deck Completed!
            </h1>
            <p className="text-xs mt-1" style={{ color: "#5C6070" }}>
              Retention Score: {accuracy}%
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div
              className="p-4 rounded-2xl"
              style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)" }}
            >
              <span className="text-2xl font-black text-emerald-400">{known.size}</span>
              <p className="text-2xs font-semibold text-emerald-500 uppercase mt-1">Known</p>
            </div>
            <div
              className="p-4 rounded-2xl"
              style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)" }}
            >
              <span className="text-2xl font-black text-amber-400">{review.size}</span>
              <p className="text-2xs font-semibold text-amber-500 uppercase mt-1">To Review</p>
            </div>
          </div>

          <button
            onClick={() => setGenerated(false)}
            className="w-full py-3.5 rounded-xl font-bold text-xs transition-all"
            style={{
              background: "#FF2D55",
              color: "#fff",
              boxShadow: "0 4px 14px rgba(255,45,85,0.35)",
            }}
          >
            Study Another Deck
          </button>
        </div>
      </div>
    );
  }

  // ── Flashcard Study Screen ─────────────────────────────────────────────────
  return (
    <div className="max-w-xl mx-auto space-y-6" style={{ animation: "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards" }}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: "#F1F3F8" }}>
            Flashcards
          </h1>
          <p className="text-xs mt-0.5" style={{ color: "#5C6070" }}>
            Space: Flip · 1: Review · 2: Known
          </p>
        </div>
        <span
          className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg"
          style={{ background: "rgba(255,45,85,0.12)", color: "#FF2D55" }}
        >
          {current + 1} / {cards.length}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${((current + 1) / cards.length) * 100}%`, background: "#FF2D55" }}
        />
      </div>

      {/* 3D Flip Card Container */}
      <div
        onClick={() => setFlipped((f) => !f)}
        className="cursor-pointer select-none rounded-3xl min-h-[260px] flex flex-col items-center justify-center p-8 text-center transition-all duration-300 relative group"
        style={{
          background: flipped ? "rgba(255,45,85,0.06)" : "#0F1115",
          border: flipped ? "1px solid rgba(255,45,85,0.35)" : "1px solid rgba(255,255,255,0.08)",
          boxShadow: flipped ? "0 0 30px rgba(255,45,85,0.15)" : "0 4px 20px rgba(0,0,0,0.5)",
        }}
      >
        <span
          className="text-2xs font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full mb-4"
          style={{
            background: flipped ? "rgba(255,45,85,0.15)" : "rgba(255,255,255,0.06)",
            color: flipped ? "#FF2D55" : "#9CA3AF",
          }}
        >
          {flipped ? "Definition & Answer" : "Term / Question · Click to Reveal"}
        </span>

        <p
          className="text-base font-semibold leading-relaxed max-w-md"
          style={{ color: flipped ? "#F1F3F8" : "#F1F3F8" }}
        >
          {flipped ? card.back : card.front}
        </p>

        <span className="text-2xs mt-4" style={{ color: "#5C6070" }}>
          (Tap anywhere or press Space to flip)
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => handleMark("review")}
          className="flex-1 py-3.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
          style={{
            background: "rgba(245,158,11,0.08)",
            border: "1px solid rgba(245,158,11,0.25)",
            color: "#F59E0B",
          }}
        >
          <span>🔁</span> Review Again [1]
        </button>
        <button
          onClick={() => handleMark("known")}
          className="flex-1 py-3.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
          style={{
            background: "rgba(16,185,129,0.10)",
            border: "1px solid rgba(16,185,129,0.3)",
            color: "#10B981",
          }}
        >
          <span>✓</span> Mastered [2]
        </button>
      </div>
    </div>
  );
}
