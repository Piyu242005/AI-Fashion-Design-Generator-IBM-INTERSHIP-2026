"""Flashcards Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import list_documents, generate_flashcards
from utils.session_state import init_session

def render():
    init_session()
    token = st.session_state.get("token","")
    st.markdown('<div class="page-header"><h1>🃏 Flashcards</h1>'
                '<p>Review key terms and definitions generated from your study material.</p></div>',
                unsafe_allow_html=True)
    try: docs = list_documents(token)
    except Exception: docs = []
    if not docs:
        st.markdown('<div class="custom-warning">📂 No documents. Upload one first.</div>',
                    unsafe_allow_html=True); return

    col_cfg, col_card = st.columns([1,2])
    with col_cfg:
        st.markdown("#### ⚙️ Generate Cards")
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="fc_doc")
        chosen_id   = doc_map[chosen_name]
        count       = st.slider("Number of cards", 5, 30, 10, key="fc_count")
        if st.button("🃏  Generate Flashcards", use_container_width=True):
            with st.spinner("Generating flashcards…"):
                try:
                    r = generate_flashcards(token, chosen_id, count=count)
                    st.session_state.update({
                        "flashcards": r.get("flashcards",[]),
                        "flashcard_index": 0,
                        "flashcard_flipped": False,
                        "fc_known": set(), "fc_review": set(),
                    })
                except RuntimeError as e:
                    st.error(f"Failed: {e}"); return

        cards = st.session_state.get("flashcards",[])
        if cards:
            known  = len(st.session_state.get("fc_known",set()))
            total  = len(cards)
            review = len(st.session_state.get("fc_review",set()))
            pct    = int((known/total)*100)
            st.markdown(
                f'<div class="content-card" style="margin-top:16px;">'
                f'<h4>📊 Progress</h4>'
                f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;"></div></div>'
                f'<div style="font-size:12px;color:var(--text-faint);margin-top:6px;">'
                f'✅ Known: {known} &nbsp; ⚠️ Review: {review} &nbsp; 📋 Total: {total}</div></div>',
                unsafe_allow_html=True)

    with col_card:
        cards = st.session_state.get("flashcards",[])
        if not cards:
            st.markdown(
                '<div style="text-align:center;padding:80px 20px;color:var(--text-faint);">'
                '<div style="font-size:56px;">🃏</div>'
                '<div style="font-size:15px;margin-top:16px;">Select a document and click '
                '<strong style="color:var(--accent);">Generate Flashcards</strong></div></div>',
                unsafe_allow_html=True); return

        idx     = st.session_state.get("flashcard_index",0)
        flipped = st.session_state.get("flashcard_flipped",False)
        card    = cards[idx]
        term    = card.get("term",""); defn = card.get("definition","")

        if not flipped:
            st.markdown(
                f'<div class="flashcard"><div style="font-size:22px;font-weight:700;color:var(--text);">{term}</div>'
                f'<div style="font-size:12px;color:var(--text-faint);margin-top:16px;">Click Flip to reveal</div></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="flashcard" style="border-color:var(--secondary);">'
                f'<div style="font-size:12px;color:var(--text-faint);text-transform:uppercase;margin-bottom:8px;">Definition</div>'
                f'<div style="font-size:15px;color:var(--text-muted);">{defn}</div>'
                f'<div style="margin-top:16px;font-size:12px;color:var(--text-faint);">Term: <strong style="color:var(--secondary);">{term}</strong></div></div>',
                unsafe_allow_html=True)

        st.markdown(f'<div style="text-align:center;color:var(--text-faint);font-size:13px;margin:12px 0;">Card {idx+1} of {len(cards)}</div>',
                    unsafe_allow_html=True)
        b1,b2,b3,b4,b5 = st.columns(5)
        with b1:
            if st.button("◀ Prev", use_container_width=True, disabled=(idx==0)):
                st.session_state["flashcard_index"] = idx-1
                st.session_state["flashcard_flipped"] = False; st.rerun()
        with b2:
            if st.button("Flip ↓" if not flipped else "Flip ↑", use_container_width=True):
                st.session_state["flashcard_flipped"] = not flipped; st.rerun()
        with b3:
            if st.button("✅ Known", use_container_width=True):
                st.session_state.setdefault("fc_known",set()).add(idx)
                st.session_state.setdefault("fc_review",set()).discard(idx)
                if idx < len(cards)-1: st.session_state["flashcard_index"] = idx+1
                st.session_state["flashcard_flipped"] = False; st.rerun()
        with b4:
            if st.button("⚠️ Review", use_container_width=True):
                st.session_state.setdefault("fc_review",set()).add(idx)
                st.session_state.setdefault("fc_known",set()).discard(idx)
                if idx < len(cards)-1: st.session_state["flashcard_index"] = idx+1
                st.session_state["flashcard_flipped"] = False; st.rerun()
        with b5:
            if st.button("Next ▶", use_container_width=True, disabled=(idx>=len(cards)-1)):
                st.session_state["flashcard_index"] = idx+1
                st.session_state["flashcard_flipped"] = False; st.rerun()

        if len(st.session_state.get("fc_known",set())) == len(cards):
            st.markdown('<div class="custom-success" style="text-align:center;margin-top:16px;">'
                        '🎉 <strong>You\'ve reviewed all flashcards!</strong></div>', unsafe_allow_html=True)
