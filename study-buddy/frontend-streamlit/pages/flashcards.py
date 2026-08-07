"""
Flashcards Page — AI-Powered Study Buddy
==========================================
Interactive flashcard review interface:
  - Generate flashcards from a selected document
  - Flip card to reveal definition
  - Navigate forward / backward
  - Mark as known / needs review
  - Progress tracker
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import list_documents, generate_flashcards
from utils.session_state import init_session


def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>🃏 Flashcards</h1>
            <p>Review key terms and definitions generated from your study material.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch documents ────────────────────────────────────────────────────
    try:
        docs = list_documents(token)
    except Exception:
        docs = []

    if not docs:
        st.markdown(
            '<div class="custom-warning">📂 No documents found. Upload a document first.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Config ─────────────────────────────────────────────────────────────
    col_cfg, col_card = st.columns([1, 2])

    with col_cfg:
        st.markdown("#### ⚙️ Generate Cards")
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="fc_doc")
        chosen_id   = doc_map[chosen_name]
        count       = st.slider("Number of cards", 5, 30, 10, key="fc_count")

        if st.button("🃏  Generate Flashcards", use_container_width=True, key="gen_fc_btn"):
            with st.spinner("Generating flashcards…"):
                try:
                    result = generate_flashcards(token, chosen_id, count=count)
                    cards  = result.get("flashcards", [])
                    st.session_state["flashcards"]      = cards
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_flipped"] = False
                    st.session_state["fc_known"]        = set()
                    st.session_state["fc_review"]       = set()
                except RuntimeError as e:
                    st.error(f"Flashcard generation failed: {e}")
                    return

        # ── Progress ───────────────────────────────────────────────────────
        cards = st.session_state.get("flashcards", [])
        if cards:
            known  = len(st.session_state.get("fc_known",  set()))
            review = len(st.session_state.get("fc_review", set()))
            total  = len(cards)
            pct    = int((known / total) * 100)

            st.markdown(
                f"""
                <div class="content-card" style="margin-top:16px;">
                    <h4>📊 Progress</h4>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{pct}%;"></div>
                    </div>
                    <div style="font-size:12px;color:#64748b;margin-top:6px;">
                        ✅ Known: {known} &nbsp; ⚠️ Review: {review} &nbsp;
                        📋 Total: {total}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Flashcard display ──────────────────────────────────────────────────
    with col_card:
        cards = st.session_state.get("flashcards", [])

        if not cards:
            st.markdown(
                """
                <div style="text-align:center;padding:80px 20px;color:#475569;">
                    <div style="font-size:56px;margin-bottom:16px;">🃏</div>
                    <div style="font-size:15px;color:#64748b;">
                        Select a document and click<br>
                        <strong style="color:#3b82f6;">Generate Flashcards</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        idx     = st.session_state.get("flashcard_index", 0)
        flipped = st.session_state.get("flashcard_flipped", False)
        card    = cards[idx]
        term    = card.get("term", "")
        defn    = card.get("definition", "")

        # ── Card display ───────────────────────────────────────────────────
        if not flipped:
            st.markdown(
                f"""
                <div class="flashcard">
                    <div class="flashcard-term">{term}</div>
                    <div class="flashcard-hint">Click "Flip" to reveal definition</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="flashcard" style="border-color:#8b5cf6;">
                    <div style="font-size:12px;color:#64748b;text-transform:uppercase;
                                letter-spacing:.08em;margin-bottom:8px;">Definition</div>
                    <div class="flashcard-def">{defn}</div>
                    <div style="margin-top:16px;font-size:12px;color:#475569;">
                        Term: <strong style="color:#8b5cf6;">{term}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Card counter ───────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="text-align:center;color:#64748b;font-size:13px;margin:12px 0;">
                Card {idx + 1} of {len(cards)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation buttons ─────────────────────────────────────────────
        b1, b2, b3, b4, b5 = st.columns(5)

        with b1:
            if st.button("◀ Prev", use_container_width=True, disabled=(idx == 0)):
                st.session_state["flashcard_index"]   = idx - 1
                st.session_state["flashcard_flipped"] = False
                st.rerun()

        with b2:
            label = "Flip ↓" if not flipped else "Flip ↑"
            if st.button(label, use_container_width=True):
                st.session_state["flashcard_flipped"] = not flipped
                st.rerun()

        with b3:
            if st.button("✅ Known", use_container_width=True):
                st.session_state.setdefault("fc_known", set()).add(idx)
                st.session_state.setdefault("fc_review", set()).discard(idx)
                if idx < len(cards) - 1:
                    st.session_state["flashcard_index"]   = idx + 1
                    st.session_state["flashcard_flipped"] = False
                st.rerun()

        with b4:
            if st.button("⚠️ Review", use_container_width=True):
                st.session_state.setdefault("fc_review", set()).add(idx)
                st.session_state.setdefault("fc_known", set()).discard(idx)
                if idx < len(cards) - 1:
                    st.session_state["flashcard_index"]   = idx + 1
                    st.session_state["flashcard_flipped"] = False
                st.rerun()

        with b5:
            if st.button("Next ▶", use_container_width=True, disabled=(idx >= len(cards) - 1)):
                st.session_state["flashcard_index"]   = idx + 1
                st.session_state["flashcard_flipped"] = False
                st.rerun()

        # ── Completion screen ──────────────────────────────────────────────
        known = st.session_state.get("fc_known", set())
        if len(known) == len(cards):
            st.markdown(
                """
                <div class="custom-success" style="text-align:center;margin-top:16px;">
                    🎉 <strong>You've reviewed all flashcards!</strong>
                    Great work — check the Dashboard for progress updates.
                </div>
                """,
                unsafe_allow_html=True,
            )
