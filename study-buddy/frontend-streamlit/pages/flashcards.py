"""
Flashcards Page — AI-Powered Study Buddy (Luxury AI SaaS Edition)
==================================================================
Interactive 3D flip card experience with active recall tracking,
keyboard shortcuts (Space to flip), and completion retention scores.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import list_documents, generate_flashcards
from utils.session_state import init_session

def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Page Header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">🃏 Smart Flashcards</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Active recall and spaced repetition deck extracted from your study notes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        docs = list_documents(token)
    except Exception:
        docs = []

    if not docs:
        st.markdown(
            '<div class="animate-fade-in-up" style="background:rgba(255,193,7,0.1);border-left:4px solid var(--warning);'
            'border-radius:var(--radius-sm);padding:16px;color:var(--warning);font-size:14px;">'
            '📂 No documents found. Please upload study material to generate flashcards.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Settings Column ────────────────────────────────────────────────────
    col_cfg, col_card = st.columns([1, 2.5])

    with col_cfg:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">⚙️ Deck Settings</div>', unsafe_allow_html=True)
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="fc_doc")
        chosen_id   = doc_map[chosen_name]

        count = st.slider("Number of flashcards", 5, 25, 10, key="fc_count")

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        gen_btn = st.button("✨ Generate Deck", use_container_width=True, type="primary", key="gen_fc_btn")

    if gen_btn:
        st.session_state["flashcards"]      = []
        st.session_state["fc_index"]        = 0
        st.session_state["fc_flipped"]      = False
        st.session_state["fc_known"]        = set()
        st.session_state["fc_review"]       = set()
        st.session_state["fc_doc_name"]     = chosen_name

        with st.spinner(f"Extracting key concepts from {chosen_name}…"):
            try:
                result = generate_flashcards(token, chosen_id, count=count)
                st.session_state["flashcards"] = result.get("flashcards", [])
            except RuntimeError as e:
                st.error(f"Generation failed: {e}")
                return

    # ── Flashcard Viewer ───────────────────────────────────────────────────
    with col_card:
        cards = st.session_state.get("flashcards", [])

        if not cards:
            st.markdown(
                """
                <div class="animate-fade-in" style="text-align:center;padding:80px 20px;color:var(--text-secondary);">
                    <div style="font-size:56px;margin-bottom:16px;">🃏</div>
                    <div style="font-size:20px;font-weight:800;color:var(--text-primary);margin-bottom:8px;letter-spacing:-0.02em;">
                        No active deck loaded
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);max-width:400px;margin:0 auto;line-height:1.5;">
                        Select a document on the left and click <strong>Generate Deck</strong>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        idx       = st.session_state.get("fc_index", 0)
        flipped   = st.session_state.get("fc_flipped", False)
        known: set  = st.session_state.get("fc_known", set())
        review: set = st.session_state.get("fc_review", set())
        total     = len(cards)

        # ── Finished All Cards ─────────────────────────────────────────────
        if idx >= total:
            acc = round((len(known) / total) * 100) if total else 0
            st.markdown(
                f"""
                <div class="content-card animate-fade-in-up" style="text-align:center;padding:64px 24px;border:2px solid var(--success);background:linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,200,83,0.1) 100%);">
                    <div style="font-size:64px;margin-bottom:16px;filter:drop-shadow(0 0 20px var(--success));">🎉</div>
                    <div style="font-size:32px;font-weight:900;color:var(--text-primary);margin:0 0 12px;letter-spacing:-0.03em;">Deck Completed!</div>
                    <div style="font-size:42px;font-weight:900;color:var(--success);margin-bottom:32px;">{acc}% Mastered</div>
                    <div style="display:flex;justify-content:center;gap:48px;margin-bottom:32px;padding:24px;background:var(--secondary);border-radius:var(--radius);border:1px solid var(--border);">
                        <div>
                            <div style="font-size:32px;font-weight:800;color:var(--success);line-height:1;">{len(known)}</div>
                            <div style="font-size:12px;color:var(--text-disabled);text-transform:uppercase;font-weight:700;margin-top:8px;">Mastered</div>
                        </div>
                        <div>
                            <div style="font-size:32px;font-weight:800;color:var(--warning);line-height:1;">{len(review)}</div>
                            <div style="font-size:12px;color:var(--text-disabled);text-transform:uppercase;font-weight:700;margin-top:8px;">To Review</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Restart Deck", use_container_width=True, type="secondary"):
                st.session_state["fc_index"]   = 0
                st.session_state["fc_flipped"] = False
                st.session_state["fc_known"]   = set()
                st.session_state["fc_review"]  = set()
                st.rerun()
            return

        card = cards[idx]

        # ── Progress Bar ───────────────────────────────────────────────────
        pct = round(((idx + 1) / total) * 100)
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--text-secondary);font-weight:600;margin-bottom:8px;">
                <span>Card {idx + 1} of {total}</span>
                <span style="color:var(--accent);">{pct}%</span>
            </div>
            <div class="progress-bar-bg" style="margin-bottom:24px;">
                <div class="progress-bar-fill" style="width:{pct}%;background:var(--accent);"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Flip Card Display ──────────────────────────────────────────────
        front = card.get("front", "")
        back  = card.get("back", "")
        hint  = card.get("hint", "")

        if not flipped:
            st.markdown(
                f"""
                <div class="animate-fade-in-up" style="background:var(--secondary);border:2px solid var(--border);border-radius:var(--radius);padding:48px 32px;text-align:center;min-height:300px;display:flex;flex-direction:column;justify-content:center;position:relative;box-shadow:var(--shadow);cursor:pointer;transition:all var(--duration-med) var(--ease-out);"
                     onmouseover="this.style.borderColor='var(--accent)';" onmouseout="this.style.borderColor='var(--border)';">
                    <div style="position:absolute;top:20px;left:24px;font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.08em;">
                        Term / Question
                    </div>
                    <div style="font-size:28px;font-weight:800;color:var(--text-primary);line-height:1.4;margin-bottom:24px;">{front}</div>
                    {f'<div style="font-size:14px;color:var(--text-secondary);background:var(--surface);padding:8px 16px;border-radius:99px;display:inline-block;margin:0 auto;border:1px solid var(--border);">💡 {hint}</div>' if hint else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="animate-fade-in-up" style="background:var(--surface);border:2px solid var(--accent);border-radius:var(--radius);padding:48px 32px;text-align:center;min-height:300px;display:flex;flex-direction:column;justify-content:center;position:relative;box-shadow:0 8px 32px rgba(255,0,60,0.15);">
                    <div style="position:absolute;top:20px;left:24px;font-size:11px;font-weight:700;color:var(--success);text-transform:uppercase;letter-spacing:0.08em;">
                        Definition / Answer
                    </div>
                    <div style="font-size:22px;font-weight:600;color:var(--text-primary);line-height:1.6;">{back}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        # ── Flip & Action Buttons ──────────────────────────────────────────
        if not flipped:
            if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                st.session_state["fc_flipped"] = True
                st.rerun()
        else:
            c_rev, c_know = st.columns(2)
            with c_rev:
                if st.button("🔁 Need Review", use_container_width=True, type="secondary"):
                    review.add(idx)
                    st.session_state["fc_review"]  = review
                    st.session_state["fc_index"]   = idx + 1
                    st.session_state["fc_flipped"] = False
                    st.rerun()
            with c_know:
                if st.button("✅ Mastered", use_container_width=True, type="primary"):
                    known.add(idx)
                    st.session_state["fc_known"]   = known
                    st.session_state["fc_index"]   = idx + 1
                    st.session_state["fc_flipped"] = False
                    st.rerun()
