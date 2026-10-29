#!/usr/bin/env python3
"""
streamlit_app.py  —  OMNI-AI Interactive Web App
=================================================
Styled to match the existing futuristic purple-neon UI (ui/styles.css).

Run with:
    .venv\\Scripts\\streamlit.exe run streamlit_app.py
"""

import streamlit as st
from datetime import datetime
import logging

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="OMNI-AI - Futuristic Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS matching ui/styles.css exactly ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* ── Variables (from styles.css :root) ───── */
:root {
    --primary-purple: #8b5cf6;
    --dark-bg: #0f0f2e;
    --darker-bg: #0a0a1a;
    --surface-dark: #1a1a3e;
    --neon-purple: #d946ef;
    --neon-cyan: #06b6d4;
    --neon-pink: #ec4899;
    --neon-blue: #3b82f6;
    --neon-green: #10b981;
    --morph-shadow: 0 8px 32px rgba(0,0,0,0.3);
    --glow-shadow: 0 0 20px rgba(217,70,239,0.5);
    --transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}

/* ── App background ─────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0f0f2e 0%, #1a0a2e 50%, #16003b 100%);
    color: #e0e0ff;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
}

/* ── Stars animation ────────────────────── */
.stars-layer {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
    background-image:
        radial-gradient(2px 2px at 20px 30px, #d946ef, rgba(217,70,239,0)),
        radial-gradient(2px 2px at 60px 70px, #06b6d4, rgba(6,182,212,0)),
        radial-gradient(1px 1px at 50px 50px, #ec4899, rgba(236,72,153,0)),
        radial-gradient(1px 1px at 130px 80px, #10b981, rgba(16,185,129,0));
    background-repeat: repeat;
    background-size: 400px 400px;
    animation: twinkle 5s linear infinite;
}
@keyframes twinkle {
    0%, 100% { opacity: 0.3; }
    50%       { opacity: 1; }
}

/* ── Purple grid overlay ────────────────── */
.bg-grid {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(139,92,246,0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139,92,246,0.1) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none; z-index: 1;
}

/* ── Floating tech words ────────────────── */
.tech-word {
    position: fixed; font-size: 80px; font-weight: bold;
    opacity: 0.03; color: var(--neon-purple);
    animation: float-word 20s infinite linear;
    pointer-events: none; z-index: 1;
}
.tw1 { top:10%; left:5%;  animation-delay:0s; }
.tw2 { top:20%; right:10%; animation-delay:2s; }
.tw3 { top:40%; left:15%; animation-delay:4s; }
.tw4 { bottom:20%; right:5%; animation-delay:6s; }
.tw5 { bottom:30%; left:20%; animation-delay:8s; }
.tw6 { top:60%; right:20%; animation-delay:10s; }
@keyframes float-word {
    0%   { transform: translateY(-100vh) rotate(0deg);   }
    100% { transform: translateY(100vh)  rotate(360deg); }
}

/* ── Header bar ─────────────────────────── */
.omni-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 18px 30px;
    background: rgba(26,26,62,0.85);
    border-bottom: 2px solid var(--neon-purple);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(217,70,239,0.2);
    margin-bottom: 0;
    position: relative; z-index: 10;
}
.logo-section { display:flex; align-items:center; gap:20px; }
.logo-glow {
    width:50px; height:50px;
    display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg, var(--primary-purple), var(--neon-purple));
    border-radius: 50%;
    box-shadow: 0 0 20px var(--neon-purple), inset 0 0 20px rgba(255,255,255,0.2);
    font-size: 24px; color: white;
    animation: pulse-glow 2s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 20px var(--neon-purple), inset 0 0 20px rgba(255,255,255,0.2); }
    50%      { box-shadow: 0 0 40px var(--neon-purple), inset 0 0 20px rgba(255,255,255,0.4); }
}
.logo-title { font-size: 28px; font-weight: bold; margin:0; color:#e0e0ff; }
.logo-title span { color: var(--neon-purple); text-shadow: 0 0 10px var(--neon-purple); }
.logo-tagline { font-size: 12px; color: var(--neon-cyan); margin: 4px 0 0; }
.header-status-dot {
    display:inline-block; width:10px; height:10px; border-radius:50%;
    background:var(--neon-green); box-shadow: 0 0 10px var(--neon-green);
    animation: pulse-dot 2s infinite;
    margin-right:6px;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(26,26,62,0.6) !important;
    border-right: 2px solid var(--primary-purple) !important;
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.nav-item-btn {
    display: flex; align-items: center; gap: 14px;
    width: 100%; padding: 14px 18px; margin-bottom: 6px;
    background: rgba(139,92,246,0.05);
    border: 2px solid transparent;
    color: #a0a0ff;
    border-radius: 15px; cursor: pointer;
    transition: var(--transition);
    font-size: 14px; font-weight: 500;
    text-align: left;
}
.nav-item-btn:hover, .nav-item-btn.active {
    background: linear-gradient(135deg, rgba(217,70,239,0.3), rgba(6,182,212,0.1));
    border-color: var(--neon-purple);
    color: var(--neon-purple);
    box-shadow: 0 0 15px rgba(217,70,239,0.4);
}

/* Override streamlit button styles for sidebar nav */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: rgba(139,92,246,0.05) !important;
    border: 2px solid transparent !important;
    color: #a0a0ff !important;
    border-radius: 15px !important;
    padding: 14px 18px !important;
    margin-bottom: 4px !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(139,92,246,0.15) !important;
    border-color: var(--primary-purple) !important;
    color: var(--neon-purple) !important;
}

/* ── Status indicator (sidebar footer) ──── */
.status-indicator {
    display:flex; align-items:center; gap:10px;
    padding:10px 15px;
    background: rgba(16,185,129,0.1);
    border: 2px solid var(--neon-green);
    border-radius: 10px; color: var(--neon-green);
    font-size: 13px;
}
.pulse-dot {
    width:8px; height:8px; background: var(--neon-green);
    border-radius:50%; animation: pulse-dot 2s infinite;
    flex-shrink:0;
}

/* ── Content panel ───────────────────────── */
.content-panel {
    background: rgba(26,26,62,0.6);
    border: 2px solid var(--primary-purple);
    border-radius: 20px;
    padding: 28px 30px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(139,92,246,0.2);
    position: relative; z-index: 2;
}
.section-title {
    font-size: 26px; color: var(--neon-purple);
    text-shadow: 0 0 10px var(--neon-purple);
    border-bottom: 2px solid var(--neon-purple);
    padding-bottom: 14px; margin-bottom: 22px;
}

/* ── Stat cards ─────────────────────────── */
.stat-card {
    background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.05));
    border: 2px solid var(--primary-purple);
    border-radius: 15px; padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(139,92,246,0.2);
    transition: var(--transition);
    display: flex; gap: 16px; align-items: flex-start;
    margin-bottom: 8px;
}
.stat-card:hover {
    border-color: var(--neon-purple);
    box-shadow: 0 0 30px var(--neon-purple);
    transform: translateY(-4px);
}
.stat-icon {
    width:56px; height:56px; border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    font-size:22px; flex-shrink:0;
}
.stat-icon.cpu    { background:rgba(236,72,153,0.2); color:var(--neon-pink);   box-shadow:0 0 15px rgba(236,72,153,0.4); }
.stat-icon.memory { background:rgba(59,130,246,0.2); color:var(--neon-blue);   box-shadow:0 0 15px rgba(59,130,246,0.4); }
.stat-icon.disk   { background:rgba(217,70,239,0.2); color:var(--neon-purple); box-shadow:0 0 15px rgba(217,70,239,0.4); }
.stat-icon.net    { background:rgba(6,182,212,0.2);  color:var(--neon-cyan);   box-shadow:0 0 15px rgba(6,182,212,0.4); }
.stat-label { font-size:12px; color:#a0a0ff; margin-bottom:6px; }
.stat-value { font-size:22px; font-weight:bold; color:white; }
.stat-bar { width:100%; height:6px; background:rgba(0,0,0,0.3); border-radius:3px; margin-top:8px; overflow:hidden; }
.stat-fill { height:100%; background:linear-gradient(90deg,var(--neon-purple),var(--neon-cyan)); border-radius:3px; }

/* ── Chat bubbles ───────────────────────── */
.chat-wrap { display:flex; flex-direction:column; gap:14px; padding:10px 0; }
.row-user { display:flex; flex-direction:row-reverse; align-items:flex-end; gap:10px; }
.row-ai   { display:flex; flex-direction:row; align-items:flex-end; gap:10px; }
.av {
    width:40px; height:40px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:18px; flex-shrink:0;
}
.av-ai   { background:linear-gradient(135deg,var(--primary-purple),var(--neon-purple));
           box-shadow:0 0 15px rgba(217,70,239,0.5); }
.av-user { background:linear-gradient(135deg,#2c5282,#1a365d); }
.bub {
    max-width:72%; padding:12px 18px; border-radius:18px;
    font-size:14px; line-height:1.6; word-break:break-word;
}
.bub-ai {
    background: rgba(26,26,62,0.8);
    border: 2px solid var(--primary-purple);
    color: #e0e0ff;
    border-bottom-left-radius: 4px;
    box-shadow: 0 0 15px rgba(139,92,246,0.2);
}
.bub-user {
    background: linear-gradient(135deg, rgba(217,70,239,0.25), rgba(139,92,246,0.2));
    border: 2px solid var(--neon-purple);
    color: #e0e0ff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 0 15px rgba(217,70,239,0.3);
}
.bub-meta { font-size:11px; color:rgba(160,160,255,0.4); margin-top:4px; text-align:right; }

/* ── Input ──────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(0,0,0,0.3) !important;
    border: 2px solid var(--primary-purple) !important;
    border-radius: 12px !important;
    color: #e0e0ff !important;
    padding: 12px 18px !important;
    font-size: 14px !important;
    font-family: 'Segoe UI', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--neon-purple) !important;
    box-shadow: 0 0 15px rgba(217,70,239,0.4) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #6a6a88 !important; }

/* ── Buttons ────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-purple), var(--neon-purple)) !important;
    border: 2px solid var(--neon-purple) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 0 15px rgba(217,70,239,0.4) !important;
    transition: var(--transition) !important;
    font-size: 14px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--neon-purple), var(--neon-pink)) !important;
    box-shadow: 0 0 30px var(--neon-purple) !important;
    transform: scale(1.04) !important;
}

/* ── Action buttons row ─────────────────── */
.action-btn-row { display:flex; gap:12px; flex-wrap:wrap; margin-top:8px; }

/* ── Right panel cards ──────────────────── */
.panel-card {
    background: rgba(26,26,62,0.6);
    border: 2px solid var(--primary-purple);
    border-radius: 15px; padding: 18px 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(139,92,246,0.2);
    margin-bottom: 16px;
}
.panel-card h4 { color:var(--neon-purple); margin-bottom:12px; font-size:15px; }

/* ── Status row items ───────────────────── */
.status-row { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(139,92,246,0.2); }
.status-row:last-child { border-bottom:none; }
.status-row .slabel { color:#a0a0ff; font-size:13px; }
.sbadge-green { background:rgba(16,185,129,0.15); color:var(--neon-green); border:1px solid var(--neon-green); border-radius:12px; padding:2px 10px; font-size:11px; }

/* ── Activity log ───────────────────────── */
.activity-item { padding:6px 0; border-bottom:1px solid rgba(139,92,246,0.15); font-size:12px; }
.activity-item:last-child { border-bottom:none; }
.atime { color:var(--neon-cyan); margin-right:8px; }
.aaction { color:#a0a0ff; }

/* ── Quick info grid ────────────────────── */
.info-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.info-item { display:flex; flex-direction:column; gap:2px; }
.ilabel { font-size:11px; color:#6a6a88; }
.ivalue { font-size:15px; color:var(--neon-cyan); font-weight:600; }

/* ── Scrollbar ──────────────────────────── */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background:rgba(139,92,246,0.5); border-radius:3px; }

/* ── Hide Streamlit chrome ──────────────── */
#MainMenu { visibility:hidden; }
footer    { visibility:hidden; }
header    { visibility:hidden; }
</style>

<!-- Background layers (stars + grid + tech words) -->
<div class="stars-layer"></div>
<div class="bg-grid"></div>
<div class="tech-word tw1">AI</div>
<div class="tech-word tw2">NEURAL</div>
<div class="tech-word tw3">DATA</div>
<div class="tech-word tw4">QUANTUM</div>
<div class="tech-word tw5">CYBER</div>
<div class="tech-word tw6">SYNC</div>
""", unsafe_allow_html=True)

# ── Header bar ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="omni-header">
    <div class="logo-section">
        <div class="logo-glow">🤖</div>
        <div>
            <div class="logo-title">OMNI<span>-AI</span></div>
            <div class="logo-tagline">Futuristic Assistant Platform</div>
        </div>
    </div>
    <div>
        <span class="header-status-dot"></span>
        <span style="color:var(--neon-green);font-size:13px;font-weight:600">System Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("omni-streamlit")


# ── Brain loader ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔧 Initialising OMNI-AI brain…")
def _load_brain():
    try:
        from main import create_omnisystem
        return create_omnisystem(), True
    except Exception as exc:
        logger.warning("Brain unavailable: %s", exc)
        return None, False


def _query(brain, message: str) -> dict:
    if brain is None:
        return {
            "response": (
                f"[Mock mode] You said: \"{message}\"\n\n"
                "The AI brain is not loaded — install optional dependencies to enable it."
            ),
            "intent": "mock", "confidence": 0.0,
            "entities": [], "action_plan": [],
        }
    try:
        if hasattr(brain, "chat_detailed"):
            return brain.chat_detailed(message)
        return {"response": brain.chat(message), "intent": None,
                "confidence": None, "entities": [], "action_plan": []}
    except Exception as exc:
        return {"response": f"⚠️ Error: {exc}", "intent": "error",
                "confidence": 0.0, "entities": [], "action_plan": []}


# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "total_queries" not in st.session_state: st.session_state.total_queries = 0
if "section"       not in st.session_state: st.session_state.section       = "chat"
if "uptime_start"  not in st.session_state: st.session_state.uptime_start  = datetime.now()

brain, brain_ok = _load_brain()

# =============================================================================
# SIDEBAR  (nav menu matching index.html)
# =============================================================================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    nav_items = [
        ("💬", "Chat"),
        ("📊", "Dashboard"),
        ("🎙️", "Voice"),
        ("🛡️", "Security"),
        ("📡", "Monitor"),
        ("🧠", "AI Models"),
    ]
    for icon, label in nav_items:
        key = label.lower()
        if st.button(f"{icon}  {label}", key=f"nav_{key}"):
            st.session_state.section = key

    st.markdown("<hr style='border-color:rgba(139,92,246,0.4);margin:16px 0'>",
                unsafe_allow_html=True)

    # Status indicator
    status_label = "Brain Online" if brain_ok else "Mock Mode"
    status_color = "var(--neon-green)" if brain_ok else "var(--neon-pink)"
    st.markdown(f"""
    <div class="status-indicator" style="border-color:{status_color};background:rgba(16,185,129,0.08)">
        <div class="pulse-dot" style="background:{status_color}"></div>
        <span style="color:{status_color}">{status_label}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:11px;color:#6a6a88;text-align:center'>"
        f"Queries: <b style='color:var(--neon-cyan)'>{st.session_state.total_queries}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

# =============================================================================
# MAIN LAYOUT  (content + right panel)
# =============================================================================
main_col, right_col = st.columns([3, 1])

# ── Right panel ───────────────────────────────────────────────────────────────
with right_col:
    # System status
    st.markdown("""
    <div class="panel-card">
        <h4>System Status</h4>
        <div class="status-row"><span class="slabel">AI System</span>   <span class="sbadge-green">Online</span></div>
        <div class="status-row"><span class="slabel">Voice Engine</span><span class="sbadge-green">Ready</span></div>
        <div class="status-row"><span class="slabel">Encryption</span>  <span class="sbadge-green">Secure</span></div>
        <div class="status-row"><span class="slabel">Monitor</span>     <span class="sbadge-green">Active</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Recent activity
    activity_html = "<div class='panel-card'><h4>Recent Activity</h4>"
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages[-5:]):
            ts   = msg.get("ts", "")
            role = "You" if msg["role"] == "user" else "OMNI-AI"
            snippet = msg["content"][:40] + "…" if len(msg["content"]) > 40 else msg["content"]
            activity_html += (
                f"<div class='activity-item'>"
                f"<span class='atime'>{ts}</span>"
                f"<span class='aaction'>{role}: {snippet}</span>"
                f"</div>"
            )
    else:
        activity_html += "<div class='activity-item'><span class='aaction' style='color:#6a6a88'>No activity yet</span></div>"
    activity_html += "</div>"
    st.markdown(activity_html, unsafe_allow_html=True)

    # Quick info
    uptime = datetime.now() - st.session_state.uptime_start
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s   = divmod(rem, 60)
    st.markdown(f"""
    <div class="panel-card">
        <h4>Quick Info</h4>
        <div class="info-grid">
            <div class="info-item">
                <span class="ilabel">Uptime</span>
                <span class="ivalue">{h}:{m:02d}:{s:02d}</span>
            </div>
            <div class="info-item">
                <span class="ilabel">Version</span>
                <span class="ivalue">2.0</span>
            </div>
            <div class="info-item">
                <span class="ilabel">Messages</span>
                <span class="ivalue">{len(st.session_state.messages)}</span>
            </div>
            <div class="info-item">
                <span class="ilabel">Mode</span>
                <span class="ivalue" style="color:{'var(--neon-green)' if brain_ok else 'var(--neon-pink)'}">
                    {'Live' if brain_ok else 'Mock'}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.total_queries = 0
        st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────
with main_col:
    section = st.session_state.section

    # ── CHAT section (default) ────────────────────────────────────────────────
    if section == "chat":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>💬 AI Chat</div>", unsafe_allow_html=True)

        # Chat history
        if not st.session_state.messages:
            st.markdown("""
            <div style='text-align:center;color:#6a6a88;padding:3rem 0'>
                <div style='font-size:3rem'>🤖</div>
                <div style='margin-top:.5rem;font-size:15px;color:#a0a0ff'>
                    OMNI-AI is ready — ask me anything!
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            parts = ["<div class='chat-wrap'>"]
            for msg in st.session_state.messages:
                content = msg["content"]
                ts      = msg.get("ts", "")
                if msg["role"] == "user":
                    parts.append(f"""
                    <div class='row-user'>
                        <div><div class='bub bub-user'>{content}</div>
                        <div class='bub-meta'>{ts}</div></div>
                        <div class='av av-user'>👤</div>
                    </div>""")
                else:
                    parts.append(f"""
                    <div class='row-ai'>
                        <div class='av av-ai'>🤖</div>
                        <div><div class='bub bub-ai'>{content}</div>
                        <div class='bub-meta'>{ts}</div></div>
                    </div>""")
            parts.append("</div>")
            st.markdown("\n".join(parts), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Input row
        ic, bc = st.columns([8, 1])
        with ic:
            user_input = st.text_input(
                label="msg", label_visibility="collapsed",
                placeholder="Type your command to OMNI-AI...",
                key="chat_input")
        with bc:
            send = st.button("➤ Send", use_container_width=True)

        # Quick prompts
        st.markdown(
            "<div style='font-size:12px;color:#6a6a88;margin:8px 0 4px'>⚡ Quick prompts:</div>",
            unsafe_allow_html=True)
        q_cols = st.columns(4)
        quick_list = ["What can you do?", "System status", "Tell me a joke", "Run security audit"]
        sel = None
        for i, qp in enumerate(quick_list):
            if q_cols[i].button(qp, key=f"qp_{i}", use_container_width=True):
                sel = qp

        # Send logic
        msg_to_send = user_input.strip() if (send and user_input.strip()) else sel
        if msg_to_send:
            ts_now = datetime.now().strftime("%H:%M")
            st.session_state.messages.append(
                {"role": "user", "content": msg_to_send, "ts": ts_now})
            st.session_state.total_queries += 1
            with st.spinner("🤖 Processing..."):
                result = _query(brain, msg_to_send)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": result.get("response", "No response."),
                "ts":      datetime.now().strftime("%H:%M"),
                "meta":    result,
            })
            st.rerun()

    # ── DASHBOARD section ─────────────────────────────────────────────────────
    elif section == "dashboard":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📊 System Dashboard</div>",
                    unsafe_allow_html=True)

        # Fetch health data
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=0.1)
            mem  = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except ImportError:
            cpu = mem = disk = 0

        c1, c2, c3, c4 = st.columns(4)
        for col, icon_cls, label, val, unit in [
            (c1, "cpu",    "CPU Usage",   cpu,  "%"),
            (c2, "memory", "Memory",      mem,  "%"),
            (c3, "disk",   "Disk Usage",  disk, "%"),
            (c4, "net",    "Network",     100,  ""),
        ]:
            with col:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-icon {icon_cls}'>
                        {'💻' if icon_cls=='cpu' else '🧠' if icon_cls=='memory' else '💾' if icon_cls=='disk' else '🌐'}
                    </div>
                    <div>
                        <div class='stat-label'>{label}</div>
                        <div class='stat-value'>{val if val else 'Active'}{unit if val else ''}</div>
                        {'<div class="stat-bar"><div class="stat-fill" style="width:'+str(val)+'%"></div></div>' if val else ''}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(139,92,246,0.05);border:2px solid var(--primary-purple);
                    border-radius:15px;padding:20px;'>
            <div style='color:var(--neon-purple);font-weight:600;margin-bottom:12px'>⚡ Quick Actions</div>
        """, unsafe_allow_html=True)
        qa1, qa2, qa3 = st.columns(3)
        if qa1.button("❤️ System Health",   use_container_width=True): st.session_state.section = "monitor"
        if qa2.button("🛡️ Security Audit",  use_container_width=True): st.session_state.section = "security"
        if qa3.button("🔄 Refresh",          use_container_width=True): st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── VOICE section ─────────────────────────────────────────────────────────
    elif section == "voice":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎙️ Voice Assistant</div>",
                    unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center;padding:30px 20px;background:rgba(6,182,212,0.05);
                    border:2px solid var(--neon-cyan);border-radius:20px;
                    box-shadow:0 0 30px rgba(6,182,212,0.2);margin-bottom:20px'>
            <div style='display:flex;justify-content:center;gap:5px;align-items:flex-end;height:60px;margin-bottom:16px'>
                <div style='width:4px;background:linear-gradient(180deg,var(--neon-cyan),var(--neon-purple));
                            border-radius:2px;height:30px;animation:bar1 0.5s ease-in-out infinite'></div>
                <div style='width:4px;background:linear-gradient(180deg,var(--neon-cyan),var(--neon-purple));
                            border-radius:2px;height:50px;animation:bar1 0.5s ease-in-out infinite;animation-delay:.1s'></div>
                <div style='width:4px;background:linear-gradient(180deg,var(--neon-cyan),var(--neon-purple));
                            border-radius:2px;height:60px;animation:bar1 0.5s ease-in-out infinite;animation-delay:.2s'></div>
                <div style='width:4px;background:linear-gradient(180deg,var(--neon-cyan),var(--neon-purple));
                            border-radius:2px;height:50px;animation:bar1 0.5s ease-in-out infinite;animation-delay:.1s'></div>
                <div style='width:4px;background:linear-gradient(180deg,var(--neon-cyan),var(--neon-purple));
                            border-radius:2px;height:30px;animation:bar1 0.5s ease-in-out infinite'></div>
            </div>
            <p style='color:var(--neon-cyan);font-size:16px'>Ready to listen</p>
        </div>
        <style>
        @keyframes bar1 { 0%,100%{height:20px} 50%{height:55px} }
        </style>
        """, unsafe_allow_html=True)
        st.info("🎙️ Voice input requires `speech_recognition` and `pyttsx3`. "
                "Use the Chat tab for text interaction.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── SECURITY section ──────────────────────────────────────────────────────
    elif section == "security":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🛡️ Security & Encryption</div>",
                    unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("<div class='panel-card'><h4>🔒 Data Encryption</h4>", unsafe_allow_html=True)
            to_encrypt = st.text_input("Data to encrypt", placeholder="Enter data to encrypt...", key="enc_in")
            if st.button("Encrypt", key="enc_btn"):
                if to_encrypt:
                    try:
                        from cryptography.fernet import Fernet
                        key = Fernet.generate_key()
                        f   = Fernet(key)
                        tok = f.encrypt(to_encrypt.encode()).decode()
                        st.code(tok[:80] + "…", language=None)
                    except ImportError:
                        st.warning("Install `cryptography`: pip install cryptography")
            st.markdown("</div>", unsafe_allow_html=True)
        with sc2:
            st.markdown("<div class='panel-card'><h4>🛡️ Security Audit</h4>", unsafe_allow_html=True)
            if st.button("Run Audit", key="audit_btn", use_container_width=True):
                result = _query(brain, "security audit")
                st.success(result.get("response", "Audit complete."))
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── MONITOR section ───────────────────────────────────────────────────────
    elif section == "monitor":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📡 System Monitoring</div>",
                    unsafe_allow_html=True)
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=0.2)
            mem  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            st.markdown(f"""
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px'>
                <div class='panel-card'>
                    <h4>🖥️ CPU</h4>
                    <div class='stat-value' style='color:var(--neon-pink)'>{cpu}%</div>
                    <div class='stat-bar' style='margin-top:10px'>
                        <div class='stat-fill' style='width:{cpu}%'></div>
                    </div>
                </div>
                <div class='panel-card'>
                    <h4>🧠 Memory</h4>
                    <div class='stat-value' style='color:var(--neon-blue)'>{mem.percent}%</div>
                    <div class='stat-bar' style='margin-top:10px'>
                        <div class='stat-fill' style='width:{mem.percent}%'></div>
                    </div>
                </div>
                <div class='panel-card'>
                    <h4>💾 Disk</h4>
                    <div class='stat-value' style='color:var(--neon-purple)'>{disk.percent}%</div>
                    <div class='stat-bar' style='margin-top:10px'>
                        <div class='stat-fill' style='width:{disk.percent}%'></div>
                    </div>
                </div>
                <div class='panel-card'>
                    <h4>🌐 Network</h4>
                    <div class='stat-value' style='color:var(--neon-cyan)'>Active</div>
                    <div style='color:#a0a0ff;font-size:12px;margin-top:6px'>Connection OK</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        except ImportError:
            st.warning("Install `psutil` to enable system monitoring: pip install psutil")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI MODELS section ──────────────────────────────────────────────────────
    elif section == "ai models":
        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🧠 AI Models & Analysis</div>",
                    unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        models = [
            ("TensorFlow", "tensorflow", "🧬", "Intent classification & entity extraction"),
            ("PyTorch",    "torch",      "🔗", "Advanced NLP & transformers"),
            ("Speech Rec.","speech_recognition","🎙️","Voice-to-text engine"),
            ("psutil",     "psutil",     "📡", "System monitoring"),
        ]
        for i, (name, mod, icon, desc) in enumerate(models):
            col = m1 if i % 2 == 0 else m2
            try:
                __import__(mod)
                status = f"<span style='color:var(--neon-green)'>● Available</span>"
            except ImportError:
                status = f"<span style='color:#6a6a88'>○ Not installed</span>"
            col.markdown(f"""
            <div class='panel-card'>
                <h4>{icon} {name}</h4>
                <div style='color:#a0a0ff;font-size:12px;margin-bottom:8px'>{desc}</div>
                {status}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
