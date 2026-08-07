"""Search Component — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st

def search_bar(placeholder: str = "Search…", key: str = "search_bar") -> str:
    query = st.text_input("🔍", placeholder=placeholder, key=key, label_visibility="collapsed")
    return query.strip().lower()

def filter_documents(docs: list[dict], query: str) -> list[dict]:
    if not query: return docs
    return [d for d in docs if query in d.get("filename", "").lower()]

def filter_chat_history(history: list[dict], query: str) -> list[dict]:
    if not query: return history
    return [m for m in history if query in m.get("content", "").lower()]

def filter_flashcards(cards: list[dict], query: str) -> list[dict]:
    if not query: return cards
    return [c for c in cards if query in c.get("term","").lower() or query in c.get("definition","").lower()]
