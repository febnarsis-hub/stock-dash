from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("홈", "⌂"),
    ("시장 현황", "▥"),
    ("종목 분석", "◫"),
    ("공시 분석", "▤"),
    ("테마 & 섹터", "◇"),
    ("포트폴리오", "▣"),
    ("관심 종목", "☆"),
    ("AI 인사이트", "✦"),
    ("데이터 연결 관리", "⚙"),
]


def apply_theme():
    """Light, information-dense investment workspace inspired by the supplied reference."""
    st.markdown(
        """
<style>
:root {
  --bg: #F4F8FB;
  --surface: #FFFFFF;
  --surface-soft: #F8FBFD;
  --sidebar: #EDF4F8;
  --line: #DCE6ED;
  --line-soft: #E9F0F4;
  --text: #18324D;
  --muted: #71859A;
  --blue: #2F6FDB;
  --blue-soft: #EAF2FF;
  --green: #16A37D;
  --green-soft: #EAF8F3;
  --red: #DE6271;
  --red-soft: #FFF0F2;
  --gold: #C5A24A;
}

html, body, [class*="css"] {
  font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
.stApp {
  background: var(--bg);
  color: var(--text);
}
.block-container {
  max-width: 1520px;
  padding: 1.05rem 1.7rem 3.5rem;
}
header[data-testid="stHeader"] {
  background: rgba(244,248,251,.94);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(220,230,237,.7);
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--sidebar);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div {
  padding: 1.1rem .8rem 1rem;
}
[data-testid="stSidebar"] .stRadio > label { display:none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: .35rem; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  min-height: 42px;
  padding: .62rem .75rem;
  border-radius: 10px;
  color: #47647F;
  transition: all .15s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background: #E3EDF4;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background: #DDEBFF;
  color: #245FBD;
  font-weight: 750;
  box-shadow: inset 3px 0 #4B83E6;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
  font-size: 14px;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCaptionContainer,
[data-testid="stSidebar"] p { color: #668099; }

/* Typography */
h1, h2, h3, h4 {
  color: var(--text);
  letter-spacing: -.035em;
}
h1 { font-size: 2rem !important; font-weight: 800; }
h2 { font-size: 1.35rem !important; font-weight: 780; }
h3 { font-size: 1.05rem !important; font-weight: 760; }
p, li { line-height: 1.55; }
[data-testid="stCaptionContainer"] { color: var(--muted); }

/* Cards / metrics */
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 15px 17px;
  box-shadow: 0 4px 16px rgba(49,79,105,.045);
}
[data-testid="stMetricLabel"] { color: var(--muted); font-size: 12px; }
[data-testid="stMetricValue"] { color: var(--text); font-weight: 800; }
[data-testid="stMetricDelta"] { font-weight: 700; }
[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  background: var(--surface);
  box-shadow: 0 4px 18px rgba(49,79,105,.04);
}

.stButton > button, .stFormSubmitButton > button, .stLinkButton > a {
  border-radius: 9px;
  min-height: 2.55rem;
  font-weight: 700;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--blue);
  border-color: var(--blue);
}
.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
  border-radius: 10px !important;
  border-color: var(--line) !important;
  background: #fff !important;
}
.stTextInput input { min-height: 44px; }

/* Tabs / tables */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
  border-radius: 8px 8px 0 0;
  padding: 9px 13px;
  color: #637A91;
}
.stTabs [aria-selected="true"] { color: var(--blue) !important; font-weight: 750; }
.stDataFrame {
  border: 1px solid var(--line);
  border-radius: 11px;
  overflow: hidden;
}
hr { border-color: var(--line) !important; }

/* Brand */
.planx-brand {
  display:flex;
  align-items:center;
  gap:10px;
  margin: 3px 7px 25px;
}
.planx-brand-mark {
  width:38px;
  height:38px;
  border-radius:10px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: linear-gradient(145deg,#2F6FDB,#67A0F0);
  color:#fff;
  font-size:21px;
  font-weight:800;
  box-shadow: 0 5px 12px rgba(47,111,219,.18);
}
.planx-brand-title {
  font-size:19px;
  line-height:1.1;
  font-weight:820;
  color:#173653;
  letter-spacing:-.035em;
}
.planx-brand-sub {
  font-size:10px;
  color:#7C91A5;
  margin-top:4px;
}

/* Hero */
.planx-hero {
  background: linear-gradient(135deg,#FFFFFF 0%,#F8FBFD 62%,#EEF5FC 100%);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 22px 25px;
  margin: 0 0 14px;
  box-shadow: 0 5px 18px rgba(49,79,105,.04);
}
.planx-eyebrow {
  color:#5D7EA1;
  font-size:10px;
  font-weight:800;
  letter-spacing:.11em;
  margin-bottom:6px;
}
.planx-hero h1 {
  margin:0;
  font-size:29px !important;
  line-height:1.2;
}
.planx-hero p {
  margin:7px 0 0;
  color:#6B8195;
  font-size:13px;
}

/* Reusable cards */
.planx-card {
  background:#fff;
  border:1px solid var(--line);
  border-radius:13px;
  padding:17px 18px;
  min-height:108px;
  box-shadow:0 4px 16px rgba(49,79,105,.035);
}
.planx-card-title {
  font-size:12px;
  color:#72879A;
  margin-bottom:8px;
  font-weight:650;
}
.planx-card-value {
  font-size:24px;
  color:#19344F;
  font-weight:820;
  letter-spacing:-.035em;
  font-variant-numeric: tabular-nums;
}
.planx-card-note {
  margin-top:6px;
  font-size:11px;
  color:#8799AA;
}
.planx-empty {
  background:#fff;
  border:1px dashed #C9D8E3;
  border-radius:13px;
  padding:20px;
  color:#70869A;
}
.planx-source {
  display:inline-flex;
  align-items:center;
  gap:5px;
  color:#657C91;
  background:#F7FAFC;
  border:1px solid var(--line);
  padding:4px 8px;
  border-radius:999px;
  font-size:10px;
}
.planx-status-ok { color:#087B5C; background:var(--green-soft); border-color:#B8E8D8; }
.planx-status-wait { color:#966D19; background:#FFF8E8; border-color:#F1DCA1; }
.planx-status-bad { color:#B44755; background:var(--red-soft); border-color:#F0C3C9; }

/* Reference dashboard rhythm */
[data-testid="stHorizontalBlock"] { align-items: stretch; }
[data-testid="stHorizontalBlock"] > div { min-width: 0; }
[data-testid="stVerticalBlockBorderWrapper"] h3 { margin-bottom: .35rem; }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
  box-shadow: none;
  border-color: var(--line-soft);
}
[data-testid="stDataFrame"] { background:#fff; }
.stPlotlyChart, [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
  border-radius: 12px;
}

@media (max-width: 900px) {
  .block-container { padding:1rem 1rem 3rem; }
  .planx-hero { padding:19px 18px; }
  .planx-hero h1 { font-size:25px !important; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def brand():
    st.markdown(
        """
<div class="planx-brand">
  <div class="planx-brand-mark">↗</div>
  <div>
    <div class="planx-brand-title">Stock Dash</div>
    <div class="planx-brand-sub">데이터로 보는 나만의 투자</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "PLANX INVESTMENT OS"):
    st.markdown(
        f"""
<div class="planx-hero">
  <div class="planx-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def card(title: str, value: str, note: str = "", status: str = ""):
    status_html = f'<div class="planx-card-note">{html.escape(status)}</div>' if status else ""
    st.markdown(
        f"""
<div class="planx-card">
  <div class="planx-card-title">{html.escape(title)}</div>
  <div class="planx-card-value">{html.escape(value)}</div>
  <div class="planx-card-note">{html.escape(note)}</div>
  {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str):
    st.markdown(
        f"""
<div class="planx-empty">
  <strong style="color:#294763">{html.escape(title)}</strong><br>
  <span>{html.escape(message)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def source_badge(label: str, state: str = "wait"):
    cls = {"ok": "planx-status-ok", "bad": "planx-status-bad"}.get(state, "planx-status-wait")
    st.markdown(
        f'<span class="planx-source {cls}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )
