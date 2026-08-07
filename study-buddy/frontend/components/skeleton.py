"""Skeleton Loaders — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st

def _s(css: str = "") -> str:
    return f'<div class="skeleton" style="{css}"></div>'

def skeleton_kpi_row() -> None:
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;">'
        f'{_s("height:100px;border-radius:14px;")}'*4 + '</div>',
        unsafe_allow_html=True)

def skeleton_chat() -> None:
    st.markdown(
        f'<div style="margin-bottom:24px;">'
        f'<div style="display:flex;justify-content:flex-end;margin-bottom:12px;">'
        f'{_s("height:40px;width:55%;border-radius:18px 18px 4px 18px;")}</div>'
        f'{_s("height:72px;width:80%;border-radius:18px 18px 18px 4px;margin-bottom:12px;")}'
        f'</div>', unsafe_allow_html=True)

def skeleton_doc_list(count: int = 3) -> None:
    items = "".join(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
        f'{_s("height:40px;width:40px;border-radius:8px;flex-shrink:0;")}'
        f'<div style="flex:1;">{_s("height:14px;width:60%;margin-bottom:6px;")}'
        f'{_s("height:10px;width:35%;")}</div></div>'
        for _ in range(count))
    st.markdown(f'<div class="content-card">{items}</div>', unsafe_allow_html=True)

def skeleton_text_block(lines: int = 6) -> None:
    widths = ["100%","92%","97%","85%","95%","78%","100%","88%"]
    items = "".join(_s(f"height:13px;width:{widths[i%len(widths)]};margin-bottom:10px;")
                    for i in range(lines))
    st.markdown(f'<div class="content-card" style="padding:20px;">{items}</div>',
                unsafe_allow_html=True)
