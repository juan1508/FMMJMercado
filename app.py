import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
import io

# ── Import data from separate config ─────────────────────────────────────────
from mmj_data_config import (
    PLAYER_DATA, TEAM_LOGOS, TEAM_FULL_NAMES, PRESIDENTS,
    POS_COLORS, TEAM_BUDGETS, TEAM_DT, PLAYERS_RAW
)

st.set_page_config(
    page_title="MMJ League · Mercado",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700;800;900&family=DM+Sans:ital,wght@0,300;0,400;0,600;1,400&family=Space+Mono:wght@400;700&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #050810; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 100% !important; }
  header[data-testid="stHeader"] { background: rgba(5,8,16,0.97); backdrop-filter: blur(12px); }

  /* ── METRICS ── */
  [data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1520 0%, #0a1218 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 18px !important;
    border-top: 2px solid #e8b84b;
    position: relative;
    overflow: hidden;
  }
  [data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #e8b84b, rgba(232,184,75,0.1));
  }
  [data-testid="stMetricValue"] { color: #e8b84b !important; font-family: 'Space Mono', monospace; font-size: 1.15rem !important; }
  [data-testid="stMetricLabel"] { color: #4a6070 !important; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 2px; }
  [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }

  /* ── PAGE HEADER ── */
  .mmj-header-bar {
    display: block;
    width: 100%;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(232,184,75,0.12);
  }
  .mmj-header-inner { display: flex; align-items: flex-start; gap: 14px; }
  .mmj-accent-line {
    width: 4px; min-height: 52px;
    background: linear-gradient(180deg, #e8b84b, rgba(232,184,75,0.05));
    border-radius: 2px; flex-shrink: 0; margin-top: 4px;
  }
  .page-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.6rem; letter-spacing: 6px;
    color: #e8b84b; margin-bottom: 0;
    text-shadow: 0 0 50px rgba(232,184,75,0.25);
    line-height: 1.05; display: block; width: 100%;
  }
  .page-sub {
    font-size: 0.68rem; color: #3a5060;
    text-transform: uppercase; letter-spacing: 3px;
    margin-top: 4px; display: block;
  }

  /* ── PLAYER ROW ── */
  .player-row {
    display: flex; align-items: center; gap: 12px;
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 10px; padding: 9px 16px; margin-bottom: 5px;
    transition: all 0.18s ease;
  }
  .player-row:hover {
    border-color: rgba(232,184,75,0.28);
    background: rgba(232,184,75,0.025);
    transform: translateX(2px);
  }

  /* ── CONTRACT BADGES ── */
  .badge-1s { background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.22); padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.5px; }
  .badge-2s { background: rgba(59,130,246,0.1); color: #3b82f6; border: 1px solid rgba(59,130,246,0.22); padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; }
  .badge-cc { background: rgba(249,115,22,0.12); color: #f97316; border: 1px solid rgba(249,115,22,0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; }
  .badge-cl { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.22); padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; }

  /* ── PLAYER CARD (grid view) ── */
  .player-card {
    background: linear-gradient(160deg, #0c1825 0%, #080f1a 70%, #050810 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; overflow: hidden; margin-bottom: 10px;
    transition: all 0.2s ease; position: relative;
  }
  .player-card:hover {
    border-color: rgba(232,184,75,0.4);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(232,184,75,0.1);
  }
  .player-card-header { padding: 14px 14px 10px; display: grid; grid-template-columns: 60px 1fr; gap: 10px; align-items: start; }
  .player-photo { width:60px; height:60px; border-radius:50%; object-fit:cover; border:2px solid rgba(232,184,75,0.35); background:#0a1520; }
  .player-name { font-family:'Barlow Condensed',sans-serif; font-size:0.9rem; font-weight:800; color:#f0f4f8; line-height:1.2; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .player-nat { font-size:0.66rem; color:#6a8da0; margin-top:3px; display:block; }
  .player-stats-bar { background:rgba(255,255,255,0.025); border-top:1px solid rgba(255,255,255,0.05); padding:8px 14px; display:grid; grid-template-columns:1fr 1fr; gap:4px; }
  .player-stat-val { font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:900; color:#e8b84b; }
  .player-stat-lbl { font-size:0.48rem; color:#4a7080; text-transform:uppercase; letter-spacing:1px; margin-top:1px; }

  /* ── TRANSFER SYSTEM ── */
  .transfer-offer-card {
    background: linear-gradient(135deg, #0c1825 0%, #081018 100%);
    border-radius: 16px; padding: 0; margin-bottom: 14px;
    transition: all 0.22s cubic-bezier(.4,0,.2,1);
    position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
  }
  .transfer-offer-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 36px rgba(0,0,0,0.5);
  }
  .offer-pending  { border: 1px solid rgba(245,158,11,0.35); border-top: 3px solid #f59e0b; }
  .offer-accepted { border: 1px solid rgba(34,197,94,0.3);  border-top: 3px solid #22c55e; }
  .offer-rejected { border: 1px solid rgba(239,68,68,0.3);  border-top: 3px solid #ef4444; }
  .offer-countered{ border: 1px solid rgba(139,92,246,0.3); border-top: 3px solid #8b5cf6; }
  .offer-withdrawn{ border: 1px solid rgba(100,116,139,0.25); border-top: 3px solid #64748b; }

  /* Transfer banner - team logos section */
  .transfer-banner {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 20px 12px;
    background: linear-gradient(135deg, rgba(232,184,75,0.04) 0%, transparent 60%);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    gap: 12px;
  }
  .transfer-team-block {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    min-width: 70px;
  }
  .transfer-team-logo {
    width: 52px; height: 52px; border-radius: 50%; object-fit: contain;
    background: rgba(255,255,255,0.04);
    border: 2px solid rgba(255,255,255,0.08);
    padding: 4px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
  }
  .transfer-team-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.72rem; font-weight: 800; color: #c0d4e0;
    text-align: center; letter-spacing: 0.5px;
  }
  .transfer-team-presi {
    font-size: 0.55rem; font-weight: 700; text-align: center;
    letter-spacing: 1px; text-transform: uppercase;
  }
  .transfer-arrow-block {
    display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1;
  }
  .transfer-player-card {
    display: flex; flex-direction: column; align-items: center; gap: 3px;
  }
  .transfer-player-photo {
    width: 56px; height: 56px; border-radius: 50%; object-fit: cover;
    border: 2px solid rgba(232,184,75,0.4);
    box-shadow: 0 0 18px rgba(232,184,75,0.15);
  }
  .transfer-player-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem; font-weight: 900; color: #f0f4f8; text-align: center;
  }
  .transfer-arrow {
    font-size: 1.1rem; color: #e8b84b; margin: 2px 0;
  }
  .transfer-amount {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem; font-weight: 700; color: #e8b84b;
    text-align: center;
  }
  .transfer-body {
    padding: 12px 20px 16px;
  }

  .offer-status-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.62rem; font-weight: 800; letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .status-pending  { background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); }
  .status-accepted { background:rgba(34,197,94,0.12);  color:#22c55e; border:1px solid rgba(34,197,94,0.25); }
  .status-rejected { background:rgba(239,68,68,0.12);  color:#ef4444; border:1px solid rgba(239,68,68,0.25); }
  .status-countered{ background:rgba(139,92,246,0.12); color:#8b5cf6; border:1px solid rgba(139,92,246,0.25); }
  .status-withdrawn{ background:rgba(100,116,139,0.1); color:#64748b; border:1px solid rgba(100,116,139,0.2); }

  /* WA button */
  .wa-btn {
    display: inline-flex; align-items: center; gap: 7px;
    background: linear-gradient(135deg, #128C7E, #25D366);
    color: #fff !important; font-family: 'DM Sans', sans-serif;
    font-size: 0.76rem; font-weight: 700;
    padding: 7px 16px; border-radius: 8px; text-decoration: none !important;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 2px 12px rgba(37,211,102,0.22);
    transition: opacity 0.15s, transform 0.15s;
    margin-top: 6px;
  }
  .wa-btn:hover { opacity: 0.88; transform: translateY(-1px); }

  /* ── NEGOTIATION THREAD ── */
  .nego-bubble {
    padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; max-width: 85%;
  }
  .nego-sent {
    background: rgba(232,184,75,0.1); border:1px solid rgba(232,184,75,0.2);
    margin-left: auto; border-bottom-right-radius: 3px;
  }
  .nego-received {
    background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
    margin-right: auto; border-bottom-left-radius: 3px;
  }

  /* ── TIMER ── */
  .timer-container {
    background: linear-gradient(135deg, #0d1520, #0a1018);
    border: 1px solid rgba(232,184,75,0.25);
    border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 20px;
    position: relative; overflow: hidden;
  }
  .timer-container::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #e8b84b, transparent);
  }
  .timer-label { font-family:'Bebas Neue',sans-serif; font-size:0.85rem; letter-spacing:4px; color:#4a6070; margin-bottom:8px; }
  .timer-value { font-family:'Space Mono',monospace; font-size:2.8rem; font-weight:700; color:#e8b84b; letter-spacing:3px; }
  .timer-expired { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:#ef4444; letter-spacing:4px; }

  /* ── SIDEBAR ── */
  [data-testid="stSidebar"] { background: #080e18 !important; border-right: 1px solid rgba(255,255,255,0.06); }
  [data-testid="stSidebar"] * { color: #e2eaf4 !important; }
  [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: 6px 12px; border-radius: 8px; transition: background 0.15s; }
  [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: rgba(232,184,75,0.08); }

  /* ── MARKET TABS ── */
  .stTabs [data-baseweb="tab"] { font-family:'Barlow Condensed',sans-serif; font-weight:700; letter-spacing:1px; font-size:0.85rem; }
  .stTabs [aria-selected="true"] { color: #e8b84b !important; }
  .stTabs [data-baseweb="tab-border"] { background: #e8b84b !important; }

  /* ── GENERAL ── */
  hr { border-color: rgba(255,255,255,0.06) !important; }
  .stExpander { border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 10px !important; background: rgba(255,255,255,0.01) !important; }
  .stSelectbox > div, .stTextInput > div { border-color: rgba(255,255,255,0.1) !important; }

  /* Market value color classes */
  .val-gold { color: #e8b84b; font-family:'Space Mono',monospace; font-weight:700; }
  .val-green { color: #22c55e; font-family:'Space Mono',monospace; }
  .val-blue  { color: #3b82f6; font-family:'Space Mono',monospace; }

  /* Notification dot */
  .notif-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #ef4444; border-radius: 50%;
    margin-left: 6px; vertical-align: middle;
    animation: pulse-dot 1.5s ease-in-out infinite;
  }
  @keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }

  /* Scrollable offer thread */
  .offer-thread { max-height: 320px; overflow-y: auto; padding: 4px 0; }
  .offer-thread::-webkit-scrollbar { width: 4px; }
  .offer-thread::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
  .offer-thread::-webkit-scrollbar-thumb { background: rgba(232,184,75,0.3); border-radius: 2px; }

  /* Valor rank badges */
  .rank-gold   { color: #e8b84b; font-weight:900; }
  .rank-silver { color: #94a3b8; font-weight:700; }
  .rank-bronze { color: #cd7f32; font-weight:700; }
</style>
""", unsafe_allow_html=True)


# ── STORAGE ───────────────────────────────────────────────────────────────────
STORAGE_FILE = "mmj_data.json"

def load_storage():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_storage(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_state(key, default=None):
    return load_storage().get(key, default)

def set_state(key, value):
    data = load_storage()
    data[key] = value
    save_storage(data)


# ── HELPERS ───────────────────────────────────────────────────────────────────
TEAM_PRESIDENT = {}
for _presi, _pdata in PRESIDENTS.items():
    for _t in _pdata["teams"]:
        TEAM_PRESIDENT[_t] = _presi

def get_flag_url(code):
    if not code: return ""
    return f"https://flagcdn.com/28x21/{code}.png"

def get_player_photo(player_name, sofifa_id):
    safe = player_name.encode('ascii', 'ignore').decode('ascii')
    initials = "+".join(safe.split()[:2]) if safe else "PL"
    if sofifa_id and sofifa_id != 0:
        s = str(sofifa_id)
        parts = (s[:-3] + "/" + s[-3:]) if len(s) > 3 else s
        sofifa_url = f"https://cdn.sofifa.net/players/{parts}/25_240.png"
        return f"https://images.weserv.nl/?url={sofifa_url}&w=120&h=120&fit=cover&mask=circle"
    return f"https://ui-avatars.com/api/?name={initials}&background=0d1825&color=e8b84b&size=128&bold=true&format=png"

def fmt_money(v):
    if not v or v == 0: return "—"
    if v >= 1_000_000_000: return f"${v/1e9:.2f}B"
    if v >= 1_000_000:     return f"${v/1e6:.1f}M"
    if v >= 1_000:         return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"

def fmt_money_short(v):
    if not v or v == 0: return "—"
    if v >= 1_000_000_000: return f"${v/1e9:.1f}B"
    if v >= 1_000_000:     return f"${v/1e6:.0f}M"
    return f"${v/1e3:.0f}K"

def contrato_badge(c):
    m = {
        "1 Season":    '<span class="badge-1s">1 Temp</span>',
        "2 Season":    '<span class="badge-2s">2 Temp</span>',
        "Cesion Corta":'<span class="badge-cc">Cesión ⚡</span>',
        "Cesion Larga":'<span class="badge-cl">Cesión 🔗</span>',
    }
    return m.get(c, f'<span style="color:#aaa;font-size:0.6rem;">{c}</span>')

def logo_img(team_code, size=22):
    logo = TEAM_LOGOS.get(team_code, "")
    if logo:
        return f'<img src="{logo}" style="width:{size}px;height:{size}px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.03);">'
    return f'<span style="font-size:0.7rem;font-weight:700;color:#e8b84b;">{team_code}</span>'


# ── WHATSAPP ──────────────────────────────────────────────────────────────────
WA_NUMBERS = {
    "JNKA": "573022105787",
    "MATI": "573184375432",
    "MAXI": "573025127701",
}

def wa_link(to_presi: str, text: str) -> str:
    """Genera un link de WhatsApp con mensaje pre-armado para abrir en nueva pestaña."""
    import urllib.parse
    number = WA_NUMBERS.get(to_presi, "")
    if not number:
        return ""
    encoded = urllib.parse.quote(text)
    return f"https://wa.me/{number}?text={encoded}"

def wa_button(to_presi: str, text: str, label: str = "📲 Notificar por WhatsApp") -> None:
    """Renderiza un botón verde de WhatsApp que abre el chat con mensaje pre-armado."""
    import urllib.parse
    link = wa_link(to_presi, text)
    if not link:
        return
    st.markdown(
        f'<a href="{link}" target="_blank" class="wa-btn">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="white">'
        f'<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15'
        f'-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475'
        f'-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52'
        f'.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207'
        f'-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372'
        f'-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2'
        f' 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719'
        f' 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>'
        f'<path d="M12 0C5.373 0 0 5.373 0 12c0 2.117.554 4.1 1.523 5.827L.057 23.882'
        f'a.5.5 0 0 0 .61.61l6.055-1.466A11.945 11.945 0 0 0 12 24c6.627 0 12-5.373 12-12'
        f'S18.627 0 12 0zm0 21.818a9.795 9.795 0 0 1-5.003-1.373l-.36-.214-3.714.9.917-3.617'
        f'-.234-.372A9.795 9.795 0 0 1 2.182 12C2.182 6.57 6.57 2.182 12 2.182'
        f'S21.818 6.57 21.818 12 17.43 21.818 12 21.818z"/>'
        f'</svg>'
        f'{label}</a>',
        unsafe_allow_html=True
    )


def render_offer_card(offer: dict, players_df, card_class: str = "offer-pending",
                      status_badge: str = "", show_pct: bool = True) -> None:
    """Renderiza una tarjeta de oferta estilo FIFA con logos de equipos prominentes."""
    from_team   = offer.get("from_team", "")
    to_team     = offer.get("to_team", "")
    from_presi  = offer.get("from_presi", "")
    to_presi    = offer.get("to_presi", "")
    player_name = offer.get("player", "")
    tipo        = offer.get("tipo", "")
    amount      = offer.get("amount", 0)

    from_logo  = TEAM_LOGOS.get(from_team, "")
    to_logo    = TEAM_LOGOS.get(to_team, "")
    from_pc    = PRESIDENTS.get(from_presi, {}).get("color", "#aaa")
    to_pc      = PRESIDENTS.get(to_presi,  {}).get("color", "#aaa")
    tipo_color = {"Compra":"#e8b84b","Cesion Corta":"#f97316","Cesion Larga":"#ef4444","Pagar Cesion":"#22c55e"}.get(tipo,"#aaa")

    pdata      = PLAYER_DATA.get(player_name, {})
    pos        = pdata.get("pos", "?")
    pos_color  = POS_COLORS.get(pos, "#667eea")
    nat        = pdata.get("nat", "")
    photo      = get_player_photo(player_name, pdata.get("sofifa", 0))

    mval_arr   = players_df[players_df["name"] == player_name]["price"].values
    mval       = mval_arr[0] if len(mval_arr) else 0
    pct_val    = (amount / mval * 100) if mval > 0 else 0
    pct_color  = "#22c55e" if pct_val >= 100 else "#f59e0b" if pct_val >= 70 else "#ef4444"

    flag_html  = f'<img src="{get_flag_url(nat)}" style="width:14px;height:10px;border-radius:1px;object-fit:cover;vertical-align:middle;" />' if nat else ""

    logo_from_html = (f'<img src="{from_logo}" class="transfer-team-logo" />'
                      if from_logo else
                      f'<div style="width:52px;height:52px;border-radius:50%;background:#0d1a24;'
                      f'border:2px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;'
                      f'font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#e8b84b;">{from_team}</div>')

    logo_to_html = (f'<img src="{to_logo}" class="transfer-team-logo" />'
                    if to_logo else
                    f'<div style="width:52px;height:52px;border-radius:50%;background:#0d1a24;'
                    f'border:2px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;'
                    f'font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#e8b84b;">{to_team}</div>')

    try:
        ts = datetime.fromisoformat(offer["created_at"]).strftime("%d/%m %H:%M")
    except:
        ts = "—"

    pct_bar = ""
    if show_pct and mval > 0:
        bar_w = min(100, int(pct_val))
        pct_bar = (
            f'<div style="margin-top:10px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">'
            f'<span style="font-size:0.58rem;color:#4a6070;text-transform:uppercase;letter-spacing:1px;">% del valor mercado</span>'
            f'<span style="font-size:0.7rem;color:{pct_color};font-weight:800;">{pct_val:.0f}%</span>'
            f'</div>'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:3px;height:4px;overflow:hidden;">'
            f'<div style="width:{bar_w}%;background:{pct_color};height:4px;border-radius:3px;'
            f'box-shadow:0 0 6px {pct_color}88;transition:width 0.4s;"></div>'
            f'</div>'
            f'</div>'
        )

    counter_badge = ""
    if offer.get("counter_amount"):
        counter_badge = (
            f'<div style="background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.28);'
            f'border-radius:6px;padding:5px 12px;margin-top:8px;display:inline-flex;align-items:center;gap:8px;">'
            f'<span style="font-size:0.65rem;color:#8b5cf6;font-weight:700;">↩️ Contraoferta: {fmt_money(offer["counter_amount"])}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div class="transfer-offer-card {card_class}">'
        # ── Banner: from team → player → to team
        f'<div class="transfer-banner">'
        # FROM team
        f'<div class="transfer-team-block">'
        f'{logo_from_html}'
        f'<span class="transfer-team-name">{from_team}</span>'
        f'<span class="transfer-team-presi" style="color:{from_pc};">{from_presi}</span>'
        f'</div>'
        # Arrow + player + amount
        f'<div class="transfer-arrow-block">'
        f'<div class="transfer-player-card">'
        f'<img src="{photo}" class="transfer-player-photo" />'
        f'<div style="display:flex;align-items:center;gap:5px;margin-top:4px;">'
        f'{flag_html}'
        f'<span class="transfer-player-name">{player_name}</span>'
        f'<span style="background:{pos_color}1a;color:{pos_color};border:1px solid {pos_color}40;'
        f'font-size:0.5rem;font-weight:900;padding:1px 5px;border-radius:3px;">{pos}</span>'
        f'</div>'
        f'</div>'
        f'<div class="transfer-arrow">→</div>'
        f'<div class="transfer-amount">{fmt_money(amount)}</div>'
        f'<span style="background:{tipo_color}18;color:{tipo_color};border:1px solid {tipo_color}35;'
        f'font-size:0.58rem;font-weight:800;padding:2px 10px;border-radius:20px;margin-top:2px;">{tipo}</span>'
        f'</div>'
        # TO team
        f'<div class="transfer-team-block">'
        f'{logo_to_html}'
        f'<span class="transfer-team-name">{to_team}</span>'
        f'<span class="transfer-team-presi" style="color:{to_pc};">{to_presi}</span>'
        f'</div>'
        f'</div>'
        # ── Body
        f'<div class="transfer-body">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
        f'{status_badge}'
        f'<span style="font-size:0.6rem;color:#3a5060;">Val. mercado: <span style="color:#c0d4e0;">{fmt_money(mval)}</span></span>'
        f'</div>'
        f'<span style="font-size:0.6rem;color:#2a3a48;">{ts}</span>'
        f'</div>'
        f'{pct_bar}'
        f'{counter_badge}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


@st.cache_data
def load_base_data():
    df = pd.DataFrame(PLAYERS_RAW)
    df = df[df["name"].isin(PLAYER_DATA.keys())].drop_duplicates(subset=["name"]).reset_index(drop=True)
    df["pos"]      = df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("pos", "?"))
    df["nat"]      = df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat", ""))
    df["nat_name"] = df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat_name", ""))
    df["sofifa"]   = df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("sofifa", 0))
    df["age"]      = df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("age", 0))
    return df

players_df_base = load_base_data()

def get_current_players():
    df = players_df_base.copy()
    for t in get_state("completed_transfers", []):
        mask = df["name"] == t["player"]
        if not mask.any(): continue
        tipo = t.get("tipo")
        if tipo == "Compra":
            df.loc[mask, "team"]     = t["to_team"]
            df.loc[mask, "cesion"]   = None
            df.loc[mask, "contrato"] = "1 Season"
        elif tipo in ("Cesion Corta","Cesion Larga"):
            df.loc[mask, "cesion"]   = t["from_team"]
            df.loc[mask, "team"]     = t["to_team"]
            df.loc[mask, "contrato"] = tipo
        elif tipo == "Pagar Cesion":
            df.loc[mask, "team"]     = t["to_team"]
            df.loc[mask, "cesion"]   = None
            df.loc[mask, "contrato"] = "1 Season"
    return df


# ── PAGE HEADER HELPER ────────────────────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(
        f'<div class="mmj-header-bar"><div class="mmj-header-inner">'
        f'<div class="mmj-accent-line"></div>'
        f'<div><span class="page-title">{title}</span>'
        f'<span class="page-sub">{subtitle}</span></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.2rem;letter-spacing:7px;'
        'color:#e8b84b;text-shadow:0 0 30px rgba(232,184,75,0.4);">MMJ</div>'
        '<div style="font-size:0.55rem;color:#2a4050;letter-spacing:4px;margin-top:-6px;margin-bottom:14px;">LEAGUE SEASON V</div>',
        unsafe_allow_html=True
    )
    st.divider()

    # Count pending offers for current president selection
    all_offers = get_state("offers", [])

    page = st.radio(
        "nav",
        ["⚽ Jugadores", "🏟️ Equipos", "💰 Presupuestos", "🔄 Cedidos", "📊 Estadísticas", "🤝 Fichajes"],
        label_visibility="collapsed"
    )
    st.divider()

    players_df_side = get_current_players()
    total_v = players_df_side["price"].sum()
    st.caption(f"**{len(players_df_side)}** jugadores · **{len(TEAM_LOGOS)}** equipos")
    st.caption(f"Valor liga: **{fmt_money(total_v)}**")

    pending_count = sum(1 for o in all_offers if o["status"] == "Pendiente")
    if pending_count > 0:
        st.markdown(f'<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-radius:8px;padding:8px 12px;margin-top:8px;">'
                    f'<span style="color:#ef4444;font-size:0.75rem;font-weight:700;">🔔 {pending_count} oferta{"s" if pending_count>1 else ""} pendiente{"s" if pending_count>1 else ""}</span>'
                    f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: JUGADORES
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚽ Jugadores":
    players_df = get_current_players()
    page_header("MERCADO DE JUGADORES", "MMJ League Season V · 30 Equipos · 270+ Jugadores")

    total_val = players_df["price"].sum()
    avg_val   = players_df["price"].mean()
    top_p     = players_df.loc[players_df["price"].idxmax()]
    cedidos   = players_df["cesion"].notna().sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Valor Total Liga",  fmt_money(total_val))
    c2.metric("Valor Promedio",    fmt_money(avg_val))
    c3.metric(f"⭐ {top_p['name']}", fmt_money(top_p["price"]))
    c4.metric("Cedidos Activos",   int(cedidos))
    c5.metric("Contratos 1 Temp.", int((players_df["contrato"] == "1 Season").sum()))

    st.divider()

    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([3, 2, 2, 1, 2, 1])
    search     = fc1.text_input("buscar", placeholder="🔍 Buscar jugador o equipo...", label_visibility="collapsed")
    team_f     = fc2.selectbox("eq", ["Todos"] + sorted(players_df["team"].unique()), label_visibility="collapsed")
    contrato_f = fc3.selectbox("ct", ["Todos","1 Season","2 Season","Cesion Corta","Cesion Larga"], label_visibility="collapsed")
    pos_f      = fc4.selectbox("ps", ["All","GK","DEF","MID","FWD"], label_visibility="collapsed")
    sort_f     = fc5.selectbox("so", ["Precio ↓","Precio ↑","Cláusula ↓","Nombre A-Z","Edad ↑"], label_visibility="collapsed")
    cedidos_f  = fc6.checkbox("Cedidos")

    df = players_df.copy()
    if search:
        df = df[df["name"].str.contains(search, case=False, na=False) |
                df["team"].str.contains(search, case=False, na=False) |
                df["nat_name"].str.contains(search, case=False, na=False)]
    if team_f     != "Todos": df = df[df["team"]     == team_f]
    if contrato_f != "Todos": df = df[df["contrato"] == contrato_f]
    if pos_f      != "All":   df = df[df["pos"]      == pos_f]
    if cedidos_f:              df = df[df["cesion"].notna()]

    sort_map = {
        "Precio ↓":   ("price",    False),
        "Precio ↑":   ("price",    True),
        "Cláusula ↓": ("clausula", False),
        "Nombre A-Z": ("name",     True),
        "Edad ↑":     ("age",      True),
    }
    scol, sasc = sort_map[sort_f]
    df = df.sort_values(scol, ascending=sasc).reset_index(drop=True)

    st.caption(f"Mostrando **{len(df)}** de **{len(players_df)}** jugadores")

    for rank, (_, row) in enumerate(df.iterrows()):
        pdata     = PLAYER_DATA.get(row["name"], {})
        pos       = pdata.get("pos", "?")
        nat       = pdata.get("nat", "")
        nat_name  = pdata.get("nat_name", "")
        sofifa_id = pdata.get("sofifa", 0)
        age       = pdata.get("age", 0)
        pos_color = POS_COLORS.get(pos, "#667eea")
        pos_bg    = pos_color + "1a"
        pos_bdr   = pos_color + "40"

        photo_url = get_player_photo(row["name"], sofifa_id)
        flag_url  = get_flag_url(nat)
        presi     = TEAM_PRESIDENT.get(row["team"], "?")
        presi_color = PRESIDENTS.get(presi, {}).get("color", "#aaa")

        flag_h = (f'<img src="{flag_url}" style="width:18px;height:13px;object-fit:cover;border-radius:2px;vertical-align:middle;" />'
                  if flag_url else "")

        # Loan display
        if pd.notna(row.get("cesion")):
            orig = str(row["cesion"])
            ol   = logo_img(orig, 18)
            tl   = logo_img(row["team"], 20)
            team_part = (f'<div style="display:flex;align-items:center;gap:5px;margin-top:3px;">'
                         f'{ol}<span style="font-size:0.62rem;color:#f97316;font-weight:700;">{orig}</span>'
                         f'<span style="color:#4a6070;font-size:0.62rem;">→ cedido a</span>'
                         f'{tl}<span style="font-size:0.62rem;color:#e2eaf4;font-weight:600;">{row["team"]}</span>'
                         f'</div>')
        else:
            tl   = logo_img(row["team"], 22)
            full = TEAM_FULL_NAMES.get(row["team"], "")
            team_part = (f'<div style="display:flex;align-items:center;gap:5px;margin-top:3px;">'
                         f'{tl}<span style="font-size:0.68rem;color:#5a7a90;">{row["team"]} · {full}</span>'
                         f'<span style="font-size:0.58rem;color:{presi_color};background:{presi_color}15;padding:1px 5px;border-radius:3px;border:1px solid {presi_color}30;">{presi}</span>'
                         f'</div>')

        age_str = f'<span style="font-size:0.58rem;color:#4a6070;margin-left:4px;">{age}a</span>' if age else ""

        st.markdown(
            f'<div class="player-row">'
            f'<img src="{photo_url}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid rgba(232,184,75,0.3);flex-shrink:0;background:#0a1520;" />'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">'
            f'<span style="font-size:0.95rem;font-weight:800;color:#f0f4f8;white-space:nowrap;">{row["name"]}</span>'
            f'<span style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};font-size:0.53rem;font-weight:900;letter-spacing:1.5px;padding:1px 6px;border-radius:3px;">{pos}</span>'
            f'{flag_h}<span style="font-size:0.63rem;color:#4a6070;">{nat_name}</span>{age_str}'
            f'</div>'
            f'{team_part}'
            f'</div>'
            f'<div style="text-align:right;flex-shrink:0;min-width:115px;">'
            f'<div style="font-size:0.9rem;font-weight:700;color:#e8b84b;font-family:\'Space Mono\',monospace;">{fmt_money(row["price"])}</div>'
            f'<div style="font-size:0.58rem;color:#4a6070;margin-top:2px;">Cláus: {fmt_money(row["clausula"])}</div>'
            f'<div style="margin-top:4px;">{contrato_badge(row["contrato"])}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏟️ Equipos":
    players_df = get_current_players()
    page_header("CLUBES", "Plantillas completas · 30 equipos · 3 presidentes")

    team_search = st.text_input("b", placeholder="🔍 Buscar equipo...", label_visibility="collapsed")

    # Group by president
    presi_filter = st.selectbox("Filtrar por Presidente", ["Todos","JNKA","MATI","MAXI"])

    for team_code in sorted(players_df["team"].unique()):
        if team_search and (
            team_search.lower() not in team_code.lower() and
            team_search.lower() not in TEAM_FULL_NAMES.get(team_code, "").lower()
        ):
            continue

        presi = TEAM_PRESIDENT.get(team_code, "?")
        if presi_filter != "Todos" and presi != presi_filter:
            continue

        squad      = players_df[players_df["team"] == team_code].sort_values("price", ascending=False)
        team_logo  = TEAM_LOGOS.get(team_code, "")
        presi_color = PRESIDENTS.get(presi, {}).get("color", "#aaa")
        dt_name    = TEAM_DT.get(team_code, "—")
        budget     = TEAM_BUDGETS.get(team_code, 0)
        total_val  = squad["price"].sum()

        hc1, hc2 = st.columns([1, 9])
        with hc1:
            if team_logo: st.image(team_logo, width=60)
        with hc2:
            st.markdown(
                f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.6rem;font-weight:900;color:#f0f4f8;">'
                f'{team_code} <span style="color:#5a7a90;font-size:0.95rem;font-weight:400;">— {TEAM_FULL_NAMES.get(team_code,"")}</span>'
                f' <span style="font-size:0.72rem;color:{presi_color};background:{presi_color}18;border:1px solid {presi_color}40;padding:2px 8px;border-radius:4px;">{presi}</span>'
                f'</div>'
                f'<div style="font-size:0.72rem;color:#4a6070;margin-top:3px;">'
                f'DT: <span style="color:#c0d4e0;">{dt_name}</span>'
                f' &nbsp;·&nbsp; {len(squad)} jugadores'
                f' &nbsp;·&nbsp; Valor: <span style="color:#e8b84b;font-weight:700;">{fmt_money(total_val)}</span>'
                f' &nbsp;·&nbsp; Pres: <span style="color:#22c55e;font-weight:700;">{fmt_money(budget)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander(f"Ver plantilla ({len(squad)} jugadores)", expanded=False):
            cols_per_row = 4
            for i in range(0, len(squad), cols_per_row):
                row_group = squad.iloc[i:i+cols_per_row]
                cols = st.columns(cols_per_row)
                for ci, (_, p) in enumerate(row_group.iterrows()):
                    with cols[ci]:
                        pdata    = PLAYER_DATA.get(p["name"], {})
                        pos      = pdata.get("pos", "?")
                        nat      = pdata.get("nat", "")
                        nat_name = pdata.get("nat_name", "")
                        sofifa   = pdata.get("sofifa", 0)
                        pos_color = POS_COLORS.get(pos, "#667eea")
                        photo_url = get_player_photo(p["name"], sofifa)
                        flag_url  = get_flag_url(nat)
                        safe_n    = str(p["name"]).replace("'", "").replace('"', "")
                        pos_bg    = pos_color + "1a"
                        pos_bdr   = pos_color + "40"
                        flag_h    = f'<img src="{flag_url}" style="width:14px;height:10px;border-radius:2px;object-fit:cover;vertical-align:middle;" />' if flag_url else ""

                        loan_html = ""
                        if pd.notna(p.get("cesion")):
                            orig_l = TEAM_LOGOS.get(p["cesion"], "")
                            olo = f'<img src="{orig_l}" style="width:12px;height:12px;object-fit:contain;border-radius:50%;vertical-align:middle;" />' if orig_l else ""
                            loan_html = f'<div style="font-size:0.58rem;color:#f97316;margin-top:2px;">{olo} {p["cesion"]} → cedido</div>'

                        st.markdown(
                            f'<div class="player-card">'
                            f'<div class="player-card-header">'
                            f'<img src="{photo_url}" class="player-photo" />'
                            f'<div>'
                            f'<span class="player-name">{p["name"]}</span>'
                            f'<div style="margin-top:3px;"><span style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};font-size:0.5rem;font-weight:900;padding:1px 5px;border-radius:3px;">{pos}</span></div>'
                            f'<span class="player-nat">{flag_h} {nat_name}</span>'
                            f'{loan_html}'
                            f'</div></div>'
                            f'<div class="player-stats-bar">'
                            f'<div><div class="player-stat-val">{fmt_money_short(p["price"])}</div><div class="player-stat-lbl">Valor</div></div>'
                            f'<div><div class="player-stat-val" style="font-size:0.7rem;">{p["contrato"][:6]}</div><div class="player-stat-lbl">Contrato</div></div>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRESUPUESTOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Presupuestos":
    players_df = get_current_players()
    page_header("PRESUPUESTOS", "Presupuesto disponible por equipo · Balance financiero")

    budget_rows = []
    for code, budget in TEAM_BUDGETS.items():
        presi = TEAM_PRESIDENT.get(code, "?")
        squad_val = players_df[players_df["team"] == code]["price"].sum()
        budget_rows.append({
            "team": code, "full_name": TEAM_FULL_NAMES.get(code, code),
            "presidente": presi, "dt": TEAM_DT.get(code, "—"),
            "presupuesto": budget, "valor_plantilla": squad_val,
        })

    tv = pd.DataFrame(budget_rows).sort_values("presupuesto", ascending=False).reset_index(drop=True)

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Presupuesto Total", fmt_money(tv["presupuesto"].sum()))
    b2.metric("Promedio por equipo", fmt_money(tv["presupuesto"].mean()))
    b3.metric("Mayor presupuesto", f'{tv.iloc[0]["team"]} — {fmt_money(tv.iloc[0]["presupuesto"])}')
    b4.metric("Menor presupuesto", f'{tv.iloc[-1]["team"]} — {fmt_money(tv.iloc[-1]["presupuesto"])}')

    st.divider()
    st.markdown("#### 👑 Balance por Presidente")
    pc1, pc2, pc3 = st.columns(3)
    for col, (presi, pdata) in zip([pc1, pc2, pc3], PRESIDENTS.items()):
        pv   = tv[tv["presidente"] == presi]["presupuesto"].sum()
        pval = tv[tv["presidente"] == presi]["valor_plantilla"].sum()
        col.markdown(
            f'<div style="background:linear-gradient(135deg,#0c1825,#080f18);'
            f'border:1px solid {pdata["color"]}33;border-top:3px solid {pdata["color"]};'
            f'border-radius:14px;padding:18px;text-align:center;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;letter-spacing:4px;color:{pdata["color"]};">{presi}</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:1.1rem;font-weight:700;color:#e8b84b;">{fmt_money(pv)}</div>'
            f'<div style="font-size:0.62rem;color:#3a5060;margin-top:2px;">Presupuesto</div>'
            f'<div style="font-size:0.75rem;color:#7a9db0;margin-top:6px;">Plantillas: {fmt_money(pval)}</div>'
            f'<div style="font-size:0.58rem;color:#3a5060;">{len(pdata["teams"])} equipos</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()
    for i, row in tv.iterrows():
        pct       = row["presupuesto"] / tv["presupuesto"].max()
        bar_w     = int(pct * 200)
        presi_c   = PRESIDENTS.get(row["presidente"], {}).get("color", "#aaa")
        logo      = TEAM_LOGOS.get(row["team"], "")
        logo_h    = f'<img src="{logo}" style="width:28px;height:28px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.03);" />' if logo else ""
        rank_c    = "#e8b84b" if i < 3 else "#4a6070"

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.018);'
            f'border:1px solid rgba(255,255,255,0.055);border-radius:10px;padding:9px 14px;margin-bottom:4px;">'
            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.1rem;font-weight:900;color:{rank_c};min-width:26px;">#{i+1}</span>'
            f'{logo_h}'
            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:#dce8f0;min-width:50px;font-size:0.9rem;">{row["team"]}</span>'
            f'<span style="color:{presi_c};font-size:0.6rem;font-weight:700;background:{presi_c}15;padding:1px 6px;border-radius:3px;border:1px solid {presi_c}30;flex-shrink:0;">{row["presidente"]}</span>'
            f'<span style="color:#3a5060;font-size:0.7rem;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["full_name"]} · <span style="color:#2a3a48;">{row["dt"]}</span></span>'
            f'<div style="width:200px;background:rgba(255,255,255,0.04);border-radius:3px;height:5px;flex-shrink:0;">'
            f'<div style="width:{bar_w}px;background:linear-gradient(90deg,#1a3a5c,#e8b84b);border-radius:3px;height:5px;"></div></div>'
            f'<span style="font-family:\'Space Mono\',monospace;font-size:0.82rem;font-weight:700;color:#e8b84b;min-width:82px;text-align:right;">{fmt_money(row["presupuesto"])}</span>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CEDIDOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Cedidos":
    players_df = get_current_players()
    page_header("CEDIDOS", "Cesiones activas · Equipo origen → equipo destino")

    loans = players_df[players_df["cesion"].notna()].sort_values("price", ascending=False)
    corta = loans[loans["contrato"] == "Cesion Corta"]
    larga = loans[loans["contrato"] == "Cesion Larga"]

    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Total Cedidos",     len(loans))
    l2.metric("Cesión Corta ⚡",   len(corta))
    l3.metric("Cesión Larga 🔗",   len(larga))
    l4.metric("Valor Total",       fmt_money(loans["price"].sum()))

    st.divider()

    for _, p in loans.iterrows():
        pdata     = PLAYER_DATA.get(p["name"], {})
        pos       = pdata.get("pos", "?")
        nat       = pdata.get("nat", "")
        nat_name  = pdata.get("nat_name", "")
        sofifa    = pdata.get("sofifa", 0)
        age       = pdata.get("age", 0)
        pos_color = POS_COLORS.get(pos, "#667eea")
        pos_bg    = pos_color + "1a"; pos_bdr = pos_color + "40"

        photo_url = get_player_photo(p["name"], sofifa)
        flag_url  = get_flag_url(nat)
        orig_team = p["cesion"]; dest_team = p["team"]
        accent_col = "#f97316" if p["contrato"] == "Cesion Corta" else "#ef4444"
        badge_lbl  = "⚡ Corta" if p["contrato"] == "Cesion Corta" else "🔗 Larga"
        flag_h     = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;" />' if flag_url else ""
        safe_n     = str(p["name"]).replace("'", "").replace('"', "")

        orig_l = logo_img(orig_team, 28)
        dest_l = logo_img(dest_team, 28)

        st.markdown(
            f'<div style="background:linear-gradient(160deg,#0c1825,#080f18);'
            f'border:1px solid rgba(255,255,255,0.06);border-left:3px solid {accent_col};'
            f'border-radius:12px;padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;gap:14px;">'
            f'<img src="{photo_url}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid {accent_col}55;flex-shrink:0;background:#0a1520;" />'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:4px;flex-wrap:wrap;">'
            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.05rem;font-weight:800;color:#f0f4f8;">{p["name"]}</span>'
            f'<span style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};font-size:0.52rem;font-weight:900;padding:1px 5px;border-radius:3px;">{pos}</span>'
            f'{flag_h}<span style="font-size:0.63rem;color:#4a6070;">{nat_name}</span>'
            f'<span style="font-size:0.6rem;color:#4a6070;">{age}a</span>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
            f'{orig_l}<span style="font-size:0.75rem;font-weight:700;color:#c0d4e0;">{orig_team}</span>'
            f'<span style="font-size:0.95rem;color:{accent_col};font-weight:900;">→</span>'
            f'{dest_l}<span style="font-size:0.75rem;font-weight:700;color:#c0d4e0;">{dest_team}</span>'
            f'<span style="background:{accent_col}20;color:{accent_col};border:1px solid {accent_col}40;font-size:0.6rem;font-weight:800;padding:2px 7px;border-radius:8px;">{badge_lbl}</span>'
            f'</div></div>'
            f'<div style="text-align:right;flex-shrink:0;">'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:0.92rem;font-weight:700;color:#e8b84b;">{fmt_money(p["price"])}</div>'
            f'<div style="font-size:0.58rem;color:#3a5060;margin-top:2px;">Clás: {fmt_money(p["clausula"])}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    if len(loans) > 0:
        st.divider()
        all_nodes = list(set(loans["cesion"].tolist() + loans["team"].tolist()))
        node_idx  = {n: i for i, n in enumerate(all_nodes)}
        source = [node_idx[r["cesion"]] for _, r in loans.iterrows()]
        target = [node_idx[r["team"]]   for _, r in loans.iterrows()]
        values = [r["price"] / 1e6      for _, r in loans.iterrows()]
        node_colors = []
        for n in all_nodes:
            p = TEAM_PRESIDENT.get(n, "?")
            node_colors.append(PRESIDENTS.get(p, {}).get("color", "#e8b84b"))

        fig = go.Figure(go.Sankey(
            node=dict(pad=14, thickness=18, label=all_nodes, color=node_colors, line=dict(color="rgba(0,0,0,0.3)", width=0.5)),
            link=dict(source=source, target=target, value=values, color="rgba(232,184,75,0.14)")
        ))
        fig.update_layout(title="Flujo de cesiones [tamaño = valor M$]",
            paper_bgcolor="#050810", font_color="#e2eaf4",
            title_font_color="#e8b84b", height=400)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Estadísticas":
    players_df = get_current_players()
    page_header("ESTADÍSTICAS", "Análisis de mercado · Distribuciones · Rankings")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Top Valores", "🏟️ Equipos", "📋 Contratos", "🌍 Naciones", "📈 Análisis"])

    with tab1:
        top20 = players_df.nlargest(20, "price").copy()
        colors = [POS_COLORS.get(p, "#667eea") for p in top20["pos"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top20["price"], y=top20["name"], orientation="h",
            marker_color=colors,
            text=[fmt_money(v) for v in top20["price"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        fig.update_layout(
            title="Top 20 jugadores más valiosos",
            plot_bgcolor="#0c1825", paper_bgcolor="#050810",
            font_color="#e2eaf4", title_font_color="#e8b84b",
            yaxis=dict(categoryorder="total ascending"),
            height=580, margin=dict(l=10, r=80, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Top by position
        for pos_label, pos_code in [("⭐ Top GKs", "GK"), ("🛡️ Top DEFs", "DEF"), ("⚙️ Top MIDs", "MID"), ("🔥 Top FWDs", "FWD")]:
            with st.expander(pos_label):
                top_pos = players_df[players_df["pos"] == pos_code].nlargest(10, "price")
                for _, r in top_pos.iterrows():
                    nat = PLAYER_DATA.get(r["name"], {}).get("nat", "")
                    flag = get_flag_url(nat)
                    fh = f'<img src="{flag}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;" />' if flag else ""
                    presi = TEAM_PRESIDENT.get(r["team"], "?")
                    pc = PRESIDENTS.get(presi, {}).get("color", "#aaa")
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                        f'{fh}<span style="flex:1;font-size:0.85rem;color:#e2eaf4;font-weight:600;">{r["name"]}</span>'
                        f'{logo_img(r["team"],18)}<span style="font-size:0.68rem;color:#4a6070;">{r["team"]}</span>'
                        f'<span style="color:{pc};font-size:0.58rem;font-weight:700;">{presi}</span>'
                        f'<span style="font-family:\'Space Mono\',monospace;font-size:0.82rem;color:#e8b84b;font-weight:700;min-width:70px;text-align:right;">{fmt_money(r["price"])}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    with tab2:
        team_stats = (players_df.groupby("team")
            .agg(valor_total=("price","sum"), jugadores=("name","count"), avg=("price","mean"))
            .reset_index().sort_values("valor_total", ascending=False))
        team_stats["presi"] = team_stats["team"].map(TEAM_PRESIDENT)
        team_stats["presi_color"] = team_stats["presi"].map(lambda p: PRESIDENTS.get(p, {}).get("color", "#667eea"))

        fig2 = go.Figure()
        for presi, pdata in PRESIDENTS.items():
            subset = team_stats[team_stats["presi"] == presi]
            fig2.add_trace(go.Bar(
                x=subset["team"], y=subset["valor_total"],
                name=presi, marker_color=pdata["color"],
                text=[fmt_money_short(v) for v in subset["valor_total"]],
                textposition="outside", textfont_size=8,
            ))
        fig2.update_layout(
            title="Valor de plantilla por equipo (color = presidente)",
            plot_bgcolor="#0c1825", paper_bgcolor="#050810",
            font_color="#e2eaf4", title_font_color="#e8b84b",
            height=450, barmode="stack",
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Scatter: budget vs squad value
        tv_scatter = []
        for code in TEAM_BUDGETS:
            squad_v = players_df[players_df["team"] == code]["price"].sum()
            presi   = TEAM_PRESIDENT.get(code, "?")
            tv_scatter.append({"team": code, "budget": TEAM_BUDGETS[code], "valor": squad_v, "presi": presi})
        sc_df = pd.DataFrame(tv_scatter)
        fig3 = px.scatter(sc_df, x="budget", y="valor", text="team",
            color="presi", color_discrete_map={p: d["color"] for p, d in PRESIDENTS.items()},
            title="Presupuesto vs Valor de plantilla",
            labels={"budget": "Presupuesto ($)", "valor": "Valor Plantilla ($)", "presi": "Presidente"})
        fig3.update_traces(textposition="top center", textfont_size=8, marker_size=10)
        fig3.update_layout(plot_bgcolor="#0c1825", paper_bgcolor="#050810",
            font_color="#e2eaf4", title_font_color="#e8b84b", height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        cc = players_df["contrato"].value_counts().reset_index()
        cc.columns = ["contrato", "count"]
        ccolors = {"1 Season":"#22c55e","2 Season":"#3b82f6","Cesion Corta":"#f97316","Cesion Larga":"#ef4444"}
        fig4 = go.Figure(go.Pie(
            labels=cc["contrato"], values=cc["count"],
            hole=0.55,
            marker_colors=[ccolors.get(c,"#667eea") for c in cc["contrato"]],
        ))
        fig4.update_layout(paper_bgcolor="#050810", font_color="#e2eaf4",
            title="Distribución de contratos", title_font_color="#e8b84b",
            annotations=[dict(text=f"<b>{len(players_df)}</b><br>jugadores", x=0.5, y=0.5, font_size=14, showarrow=False, font_color="#e8b84b")])
        st.plotly_chart(fig4, use_container_width=True)

    with tab4:
        nat_counts = players_df.groupby(["nat","nat_name"]).size().reset_index(name="count").sort_values("count", ascending=False).head(24)
        ncols = st.columns(4)
        for i, (_, row) in enumerate(nat_counts.iterrows()):
            flag_url = get_flag_url(row["nat"])
            fh = f'<img src="{flag_url}" style="width:24px;height:17px;object-fit:cover;border-radius:2px;vertical-align:middle;" />' if flag_url else ""
            pct = row["count"] / nat_counts["count"].max()
            bar = int(pct * 60)
            ncols[i % 4].markdown(
                f'<div style="display:flex;align-items:center;background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:7px 10px;margin-bottom:5px;gap:7px;">'
                f'{fh}<span style="font-size:0.75rem;color:#d0e4f0;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{row["nat_name"]}</span>'
                f'<div style="width:60px;background:rgba(255,255,255,0.04);border-radius:2px;height:4px;">'
                f'<div style="width:{bar}px;background:#e8b84b;border-radius:2px;height:4px;"></div></div>'
                f'<span style="font-family:monospace;font-size:0.8rem;font-weight:700;color:#e8b84b;min-width:18px;text-align:right;">{row["count"]}</span>'
                f'</div>', unsafe_allow_html=True
            )

    with tab5:
        st.markdown("#### Distribución de valores")
        fig5 = px.histogram(players_df, x="price", nbins=50,
            labels={"price":"Valor de mercado ($)"},
            title="Distribución de valores (todos los jugadores)",
            color_discrete_sequence=["#e8b84b"])
        fig5.update_layout(plot_bgcolor="#0c1825", paper_bgcolor="#050810",
            font_color="#e2eaf4", title_font_color="#e8b84b")
        st.plotly_chart(fig5, use_container_width=True)

        # Age vs value scatter
        players_df2 = players_df.copy()
        players_df2["age"] = players_df2["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("age", 25))
        players_df2["presi"] = players_df2["team"].map(TEAM_PRESIDENT)
        fig6 = px.scatter(players_df2[players_df2["price"] > 5_000_000], x="age", y="price",
            color="pos", color_discrete_map=POS_COLORS,
            hover_data=["name","team"], size="price", size_max=30,
            title="Edad vs Valor de mercado",
            labels={"age":"Edad","price":"Valor ($)","pos":"Posición"})
        fig6.update_layout(plot_bgcolor="#0c1825", paper_bgcolor="#050810",
            font_color="#e2eaf4", title_font_color="#e8b84b", height=500)
        st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VENTANA DE FICHAJES — Sistema tipo FC/FIFA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Fichajes":
    players_df = get_current_players()
    page_header("VENTANA DE FICHAJES", "Sistema de transferencias · Ofertas · Contraofertas · Negociación")

    # ── Admin Panel ───────────────────────────────────────────────────────────
    with st.expander("⚙️ Panel Administrador", expanded=False):
        ca1, ca2, ca3, ca4 = st.columns(4)
        with ca1:
            if st.button("🟢 Abrir Ventana (30 días)", use_container_width=True):
                end = (datetime.now() + timedelta(days=30)).isoformat()
                set_state("transfer_window_end", end)
                set_state("transfer_window_active", True)
                st.success("Ventana abierta!")
                st.rerun()
        with ca2:
            if st.button("🔴 Cerrar Ventana", use_container_width=True):
                set_state("transfer_window_active", False)
                st.rerun()
        with ca3:
            if st.button("🗑️ Borrar Ofertas", use_container_width=True):
                set_state("offers", [])
                st.success("Ofertas eliminadas."); st.rerun()
        with ca4:
            if st.button("💥 Reset Completo", use_container_width=True):
                set_state("offers", [])
                set_state("completed_transfers", [])
                st.success("Reset completo."); st.rerun()

    # ── Timer ─────────────────────────────────────────────────────────────────
    window_active  = get_state("transfer_window_active", False)
    window_end_str = get_state("transfer_window_end", None)
    window_open    = False

    if window_active and window_end_str:
        try:
            end_dt    = datetime.fromisoformat(window_end_str)
            remaining = end_dt - datetime.now()
            if remaining.total_seconds() > 0:
                window_open  = True
                days_left    = remaining.days
                hours_left   = remaining.seconds // 3600
                minutes_left = (remaining.seconds % 3600) // 60
                progress_pct = min(1.0, 1 - remaining.total_seconds() / (30 * 86400))
                st.markdown(
                    f'<div class="timer-container">'
                    f'<div class="timer-label">⏰ VENTANA DE FICHAJES · TIEMPO RESTANTE</div>'
                    f'<div class="timer-value">{days_left}d {hours_left:02d}h {minutes_left:02d}m</div>'
                    f'<div style="margin-top:10px;background:rgba(255,255,255,0.05);border-radius:4px;height:4px;overflow:hidden;">'
                    f'<div style="width:{int(progress_pct*100)}%;background:linear-gradient(90deg,#22c55e,#e8b84b);height:4px;transition:width 0.5s;"></div>'
                    f'</div>'
                    f'<div style="font-size:0.65rem;color:#3a5060;margin-top:6px;">Cierre: {end_dt.strftime("%d/%m/%Y %H:%M")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                set_state("transfer_window_active", False)
                st.markdown('<div class="timer-container"><div class="timer-expired">🔒 VENTANA CERRADA</div></div>', unsafe_allow_html=True)
        except:
            pass
    else:
        st.markdown(
            '<div style="background:#0c1825;border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:18px;text-align:center;margin-bottom:18px;">'
            '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;letter-spacing:4px;color:#4a6070;">🔒 VENTANA CERRADA</div>'
            '<div style="font-size:0.68rem;color:#2a3a48;margin-top:4px;">El administrador debe abrir la ventana de fichajes</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── President selector ────────────────────────────────────────────────────
    presi_sel   = st.selectbox("🧑‍💼 Actuar como Presidente", ["JNKA", "MATI", "MAXI"])
    presi_color = PRESIDENTS[presi_sel]["color"]
    my_teams    = PRESIDENTS[presi_sel]["teams"]

    all_offers = get_state("offers", [])
    my_pending_in = [o for o in all_offers if o["to_presi"] == presi_sel and o["status"] == "Pendiente"]
    my_pending_count_notif = len(my_pending_in)

    my_team_logos_html = ""
    for t in my_teams:
        logo_url = TEAM_LOGOS.get(t, "")
        if logo_url:
            my_team_logos_html += (
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;">'
                f'<img src="{logo_url}" style="width:32px;height:32px;object-fit:contain;border-radius:50%;'
                f'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);" />'
                f'<span style="font-size:0.55rem;color:#8aa0b0;font-weight:700;">{t}</span>'
                f'</div>'
            )
        else:
            my_team_logos_html += (
                f'<span style="font-size:0.7rem;color:{presi_color};font-weight:800;">{t}</span>'
            )

    notif_html = ""
    if my_pending_count_notif > 0:
        s = "s" if my_pending_count_notif > 1 else ""
        notif_html = (
            f'<div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);'
            f'border-radius:8px;padding:8px 16px;flex-shrink:0;">'
            f'<span style="color:#ef4444;font-size:0.82rem;font-weight:800;">🔔 {my_pending_count_notif} nueva{s}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:{presi_color}0d;border:1px solid {presi_color}30;border-radius:14px;padding:14px 20px;margin-bottom:18px;'
        f'display:flex;align-items:center;gap:16px;flex-wrap:wrap;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;letter-spacing:4px;color:{presi_color};min-width:80px;">{presi_sel}</div>'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:6px;">{my_team_logos_html}</div>'
        f'<div style="font-size:0.65rem;color:#4a6070;">Presupuesto total: '
        f'<span style="color:#e8b84b;font-weight:700;font-family:\'Space Mono\',monospace;">'
        f'{fmt_money(sum(TEAM_BUDGETS.get(t,0) for t in my_teams))}</span></div>'
        f'</div>'
        f'{notif_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    tab_nueva, tab_bandeja, tab_mis, tab_negociar, tab_historial, tab_export = st.tabs([
        "📤 Nueva Oferta",
        f"📥 Bandeja entrada{'  🔴' if my_pending_count_notif>0 else ''}",
        "📋 Mis ofertas",
        "💬 Negociación",
        "✅ Historial",
        "📊 Exportar"
    ])

    # ── Tab 1: Nueva oferta ───────────────────────────────────────────────────
    with tab_nueva:
        if not window_open:
            st.warning("⛔ La ventana de fichajes no está activa.")
        else:
            st.markdown("#### 📤 Enviar oferta de fichaje")

            rival_teams = sorted([t for t in players_df["team"].unique() if t not in my_teams])

            col_r1, col_r2 = st.columns(2)
            rival_team = col_r1.selectbox("🏟️ Equipo rival", rival_teams, key="rival_sel")
            rival_presi = TEAM_PRESIDENT.get(rival_team, "?")
            rpc = PRESIDENTS.get(rival_presi, {}).get("color", "#aaa")
            rival_logo = TEAM_LOGOS.get(rival_team, "")
            rival_logo_html = (f'<img src="{rival_logo}" style="width:36px;height:36px;object-fit:contain;border-radius:50%;'
                               f'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);padding:3px;" />'
                               if rival_logo else "")
            col_r2.markdown(
                f'<div style="padding:8px 14px;background:{rpc}10;border:1px solid {rpc}30;border-radius:10px;margin-top:22px;'
                f'display:flex;align-items:center;gap:10px;">'
                f'{rival_logo_html}'
                f'<div><span style="font-size:0.82rem;color:{rpc};font-weight:800;">{rival_presi}</span>'
                f'<div style="font-size:0.62rem;color:#4a6070;">{TEAM_FULL_NAMES.get(rival_team, rival_team)}</div></div>'
                f'</div>', unsafe_allow_html=True
            )

            squad_rival  = players_df[players_df["team"] == rival_team].sort_values("price", ascending=False)
            player_sel   = st.selectbox("⚽ Jugador objetivo", squad_rival["name"].tolist(), key="player_sel")

            if player_sel:
                pinfo    = squad_rival[squad_rival["name"] == player_sel].iloc[0]
                pdata    = PLAYER_DATA.get(player_sel, {})
                pos      = pdata.get("pos","?")
                pos_color = POS_COLORS.get(pos,"#667eea")
                age      = pdata.get("age", 0)
                nat      = pdata.get("nat","")
                photo    = get_player_photo(player_sel, pdata.get("sofifa",0))
                flag_url = get_flag_url(nat)
                fh       = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;" />' if flag_url else ""

                # Player info card
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#0c1825,#080f18);border:1px solid rgba(255,255,255,0.07);'
                    f'border-radius:14px;padding:16px;display:flex;align-items:center;gap:14px;margin-bottom:16px;">'
                    f'<img src="{photo}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid {pos_color}55;" />'
                    f'<div style="flex:1;">'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.3rem;font-weight:900;color:#f0f4f8;">{player_sel}</span>'
                    f'<span style="background:{pos_color}1a;color:{pos_color};border:1px solid {pos_color}40;font-size:0.55rem;font-weight:900;padding:2px 6px;border-radius:3px;">{pos}</span>'
                    f'{fh}<span style="font-size:0.65rem;color:#4a6070;">{pdata.get("nat_name","")}</span>'
                    f'<span style="font-size:0.63rem;color:#3a5060;">{age}a</span>'
                    f'</div>'
                    f'<div style="display:flex;gap:20px;margin-top:8px;">'
                    f'<div><div style="font-family:\'Space Mono\',monospace;font-size:0.9rem;color:#e8b84b;font-weight:700;">{fmt_money(pinfo["price"])}</div>'
                    f'<div style="font-size:0.55rem;color:#3a5060;text-transform:uppercase;letter-spacing:1px;">Valor</div></div>'
                    f'<div><div style="font-family:\'Space Mono\',monospace;font-size:0.9rem;color:#22c55e;font-weight:700;">{fmt_money(pinfo["renovation"])}</div>'
                    f'<div style="font-size:0.55rem;color:#3a5060;text-transform:uppercase;letter-spacing:1px;">Renovación</div></div>'
                    f'<div><div style="font-family:\'Space Mono\',monospace;font-size:0.9rem;color:#ef4444;font-weight:700;">{fmt_money(pinfo["clausula"])}</div>'
                    f'<div style="font-size:0.55rem;color:#3a5060;text-transform:uppercase;letter-spacing:1px;">Cláusula</div></div>'
                    f'<div><div style="font-size:0.85rem;font-weight:700;color:#c0d4e0;">{pinfo["contrato"]}</div>'
                    f'<div style="font-size:0.55rem;color:#3a5060;text-transform:uppercase;letter-spacing:1px;">Contrato</div></div>'
                    f'</div></div></div>',
                    unsafe_allow_html=True
                )

                is_cedido = pd.notna(pinfo.get("cesion"))
                tipo_opts = ["Compra"]
                if not is_cedido:
                    tipo_opts += ["Cesion Corta", "Cesion Larga"]
                else:
                    tipo_opts += ["Pagar Cesion"]
                    st.info(f"🔗 Este jugador está cedido de **{pinfo['cesion']}** a **{pinfo['team']}**.")

                col_t1, col_t2 = st.columns(2)
                tipo_oferta = col_t1.selectbox("💼 Tipo de operación", tipo_opts, key="tipo_sel")
                dest_team   = col_t2.selectbox("🏟️ Mi equipo receptor", sorted(my_teams), key="dest_sel")

                # Smart default offer
                defaults = {"Compra": pinfo["price"], "Cesion Corta": int(pinfo["price"]*0.12),
                            "Cesion Larga": int(pinfo["price"]*0.28), "Pagar Cesion": pinfo["renovation"]}
                default_offer = defaults.get(tipo_oferta, pinfo["price"])

                col_o1, col_o2 = st.columns([3,1])
                offer_amount = col_o1.number_input("💰 Monto oferta ($)", min_value=0, value=default_offer, step=500_000, format="%d")

                # Show % of market value
                pct_val = (offer_amount / pinfo["price"] * 100) if pinfo["price"] > 0 else 0
                pct_color = "#22c55e" if pct_val >= 100 else "#f59e0b" if pct_val >= 70 else "#ef4444"
                col_o2.markdown(f'<div style="padding-top:28px;font-family:\'Space Mono\',monospace;font-size:1.1rem;font-weight:700;color:{pct_color};">{pct_val:.0f}%</div>'
                                f'<div style="font-size:0.58rem;color:#3a5060;">del valor</div>', unsafe_allow_html=True)

                msg = st.text_area("💬 Mensaje al presidente (opcional)", placeholder="Detalla tu propuesta...", max_chars=400, key="msg_offer")

                col_btn1, col_btn2 = st.columns([3,1])
                with col_btn1:
                    if st.button("📤 Enviar Oferta", use_container_width=True, type="primary"):
                        offer_id = f"offer_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                        new_offer = {
                            "id": offer_id,
                            "from_presi": presi_sel, "to_presi": rival_presi,
                            "from_team": dest_team, "to_team": rival_team,
                            "player": player_sel, "tipo": tipo_oferta,
                            "amount": offer_amount,
                            "messages": [{"from": presi_sel, "text": msg, "ts": datetime.now().isoformat()}] if msg else [],
                            "status": "Pendiente",
                            "created_at": datetime.now().isoformat(),
                            "history": [{"action": "enviada", "presi": presi_sel, "amount": offer_amount, "ts": datetime.now().isoformat()}],
                        }
                        offers2 = get_state("offers", [])
                        offers2.append(new_offer)
                        set_state("offers", offers2)
                        st.success(f"✅ Oferta enviada a **{rival_presi}** por **{player_sel}** — {fmt_money(offer_amount)}")
                        st.session_state["last_wa"] = {
                            "event": "nueva_oferta",
                            "to_presi": rival_presi,
                            "player": player_sel,
                            "tipo": tipo_oferta,
                            "amount": offer_amount,
                            "from_presi": presi_sel,
                            "from_team": dest_team,
                            "to_team": rival_team,
                            "msg": msg,
                        }
                with col_btn2:
                    st.caption(f"Sugerido: {fmt_money(default_offer)}")

                # ── Botón WA tras enviar oferta ───────────────────────────────
                last_wa = st.session_state.get("last_wa", {})
                if last_wa.get("event") == "nueva_oferta" and last_wa.get("from_presi") == presi_sel:
                    wa_text = (
                        f"🚨 *MMJ LEAGUE — NUEVA OFERTA* 🚨\n\n"
                        f"⚽ Jugador: *{last_wa['player']}*\n"
                        f"💼 Tipo: *{last_wa['tipo']}*\n"
                        f"💰 Monto: *{fmt_money(last_wa['amount'])}*\n"
                        f"📤 De: *{last_wa['from_presi']}* ({last_wa['from_team']})\n"
                        f"📥 Tu equipo: *{last_wa['to_team']}*\n"
                        + (f"💬 Mensaje: _{last_wa['msg']}_\n" if last_wa.get('msg') else "") +
                        f"\n➡️ Entra a la app para responder."
                    )
                    st.markdown("**📲 Notifica al presidente contrario:**")
                    wa_button(last_wa["to_presi"], wa_text, f"WhatsApp a {last_wa['to_presi']}")

    # ── Tab 2: Bandeja de entrada ─────────────────────────────────────────────
    with tab_bandeja:
        if not window_open:
            st.warning("⛔ La ventana de fichajes no está activa.")
        else:
            st.markdown("#### 📥 Ofertas recibidas en tus equipos")
            my_received = [o for o in all_offers if o["to_presi"] == presi_sel and o["status"] == "Pendiente"]

            if not my_received:
                st.info("📭 No tienes ofertas pendientes de respuesta.")
            else:
                for offer in sorted(my_received, key=lambda x: x["created_at"], reverse=True):
                    from_pc    = PRESIDENTS.get(offer["from_presi"], {}).get("color", "#aaa")
                    tipo_color = {"Compra":"#e8b84b","Cesion Corta":"#f97316","Cesion Larga":"#ef4444","Pagar Cesion":"#22c55e"}.get(offer["tipo"],"#aaa")
                    pdata      = PLAYER_DATA.get(offer["player"], {})
                    sofifa     = pdata.get("sofifa", 0)
                    photo      = get_player_photo(offer["player"], sofifa)
                    pos        = pdata.get("pos","?")
                    pos_color  = POS_COLORS.get(pos,"#667eea")
                    market_val = players_df[players_df["name"] == offer["player"]]["price"].values
                    mval       = market_val[0] if len(market_val) else 0
                    pct_val    = (offer["amount"] / mval * 100) if mval > 0 else 0
                    pct_color  = "#22c55e" if pct_val >= 100 else "#f59e0b" if pct_val >= 70 else "#ef4444"
                    safe_n     = str(offer["player"]).replace("'","").replace('"',"")

                    render_offer_card(offer, players_df, card_class="offer-pending",
                                      status_badge='<span class="offer-status-badge status-pending">⏳ Pendiente</span>')

                    # Last message preview
                    msgs = offer.get("messages", [])
                    if msgs:
                        last_msg = msgs[-1]
                        bg = "nego-sent" if last_msg["from"] != presi_sel else "nego-received"
                        st.markdown(
                            f'<div class="nego-bubble {bg}" style="margin:8px 0;">'
                            f'<span style="font-size:0.62rem;color:#4a6070;font-weight:700;">{last_msg["from"]}</span>'
                            f'<p style="margin:3px 0;font-size:0.78rem;color:#c0d4e0;">{last_msg["text"]}</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    # Response actions
                    resp_key = f"resp_{offer['id']}"
                    msg_key = f"msg_{offer['id']}"

                    rcol1, rcol2, rcol3 = st.columns([2, 2, 3])
                    resp_msg = rcol3.text_input("Mensaje respuesta", key=msg_key, placeholder="Escribe un comentario...", label_visibility="collapsed")

                    with rcol1:
                        if st.button("✅ Aceptar oferta", key=f"acc_{offer['id']}", use_container_width=True, type="primary"):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Aceptada"
                                    if resp_msg:
                                        o.setdefault("messages", []).append({"from": presi_sel, "text": resp_msg, "ts": datetime.now().isoformat()})
                                    o.setdefault("history", []).append({"action":"aceptada","presi":presi_sel,"ts":datetime.now().isoformat()})
                            set_state("offers", all_offers2)
                            completed = get_state("completed_transfers", [])
                            completed.append({
                                "player": offer["player"], "from_team": offer["to_team"],
                                "to_team": offer["from_team"], "tipo": offer["tipo"],
                                "amount": offer["amount"], "from_presi": offer["to_presi"],
                                "to_presi": offer["from_presi"], "date": datetime.now().isoformat()
                            })
                            set_state("completed_transfers", completed)
                            st.success(f"✅ {offer['player']} → {offer['from_team']}")
                            wa_text = (
                                f"✅ *MMJ LEAGUE — OFERTA ACEPTADA* ✅\n\n"
                                f"⚽ Jugador: *{offer['player']}*\n"
                                f"💼 Tipo: *{offer['tipo']}*\n"
                                f"💰 Monto: *{fmt_money(offer['amount'])}*\n"
                                f"📤 De: *{offer['from_team']}* ({offer['from_presi']})\n"
                                f"📥 A: *{offer['to_team']}* ({offer['to_presi']})\n"
                                + (f"💬 Nota: _{resp_msg}_\n" if resp_msg else "") +
                                f"\n🎉 ¡Transferencia completada!"
                            )
                            st.markdown("**📲 Notifica al presidente:**")
                            wa_button(offer["from_presi"], wa_text, f"WhatsApp a {offer['from_presi']} — Aceptada")

                    with rcol2:
                        if st.button("❌ Rechazar", key=f"rej_{offer['id']}", use_container_width=True):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Rechazada"
                                    if resp_msg:
                                        o.setdefault("messages", []).append({"from": presi_sel, "text": resp_msg, "ts": datetime.now().isoformat()})
                            set_state("offers", all_offers2)
                            wa_text = (
                                f"❌ *MMJ LEAGUE — OFERTA RECHAZADA* ❌\n\n"
                                f"⚽ Jugador: *{offer['player']}*\n"
                                f"💰 Monto ofertado: *{fmt_money(offer['amount'])}*\n"
                                f"🏟️ Equipo: *{offer['to_team']}* rechazó la oferta\n"
                                + (f"💬 Motivo: _{resp_msg}_\n" if resp_msg else "") +
                                f"\nPuedes enviar una nueva oferta desde la app."
                            )
                            st.markdown("**📲 Notifica al presidente:**")
                            wa_button(offer["from_presi"], wa_text, f"WhatsApp a {offer['from_presi']} — Rechazada")

                    # Contraoferta
                    with st.expander(f"💬 Contraoferta por {offer['player']}", expanded=False):
                        mval2 = players_df[players_df["name"] == offer["player"]]["price"].values
                        mval2 = mval2[0] if len(mval2) else 0
                        counter_amount = st.number_input("Contraoferta ($)", min_value=0, value=int(mval2), step=500_000, format="%d", key=f"ca_{offer['id']}")
                        counter_msg    = st.text_input("Mensaje (opcional)", key=f"cm_{offer['id']}", placeholder="Explica tu contraoferta...")
                        if st.button(f"↩️ Enviar Contraoferta", key=f"co_{offer['id']}", use_container_width=True):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Contrapropuesta"
                                    o["counter_amount"] = counter_amount
                                    if counter_msg:
                                        o.setdefault("messages", []).append({"from": presi_sel, "text": f"Contraoferta: {fmt_money(counter_amount)} — {counter_msg}", "ts": datetime.now().isoformat()})
                                    o.setdefault("history", []).append({"action":"contrapropuesta","presi":presi_sel,"amount":counter_amount,"ts":datetime.now().isoformat()})
                            set_state("offers", all_offers2)
                            st.success(f"Contraoferta de {fmt_money(counter_amount)} enviada!")
                            wa_text = (
                                f"↩️ *MMJ LEAGUE — CONTRAOFERTA* ↩️\n\n"
                                f"⚽ Jugador: *{offer['player']}*\n"
                                f"💰 Tu oferta: *{fmt_money(offer['amount'])}*\n"
                                f"↩️ Contraoferta: *{fmt_money(counter_amount)}*\n"
                                f"🏟️ De: *{offer['to_team']}* ({presi_sel})\n"
                                + (f"💬 Mensaje: _{counter_msg}_\n" if counter_msg else "") +
                                f"\nEntra a la app para aceptar o negociar."
                            )
                            st.markdown("**📲 Notifica al presidente:**")
                            wa_button(offer["from_presi"], wa_text, f"WhatsApp a {offer['from_presi']} — Contraoferta")

                    st.markdown("---")

    # ── Tab 3: Mis ofertas ────────────────────────────────────────────────────
    with tab_mis:
        st.markdown("#### 📋 Ofertas que has enviado")
        my_sent = [o for o in all_offers if o["from_presi"] == presi_sel]

        if not my_sent:
            st.info("No has enviado ninguna oferta todavía.")
        else:
            for offer in sorted(my_sent, key=lambda x: x["created_at"], reverse=True):
                status_styles = {
                    "Pendiente":      ("⏳", "#f59e0b", "status-pending",   "offer-pending"),
                    "Aceptada":       ("✅", "#22c55e", "status-accepted",  "offer-accepted"),
                    "Rechazada":      ("❌", "#ef4444", "status-rejected",  "offer-rejected"),
                    "Contrapropuesta":("↩️", "#8b5cf6", "status-countered", "offer-countered"),
                    "Retirada":       ("🗑️", "#64748b", "status-withdrawn", "offer-withdrawn"),
                }
                icon, sc, badge_cls, card_cls = status_styles.get(offer["status"], ("❓","#aaa","",""))

                status_badge_html = f'<span class="offer-status-badge {badge_cls}">{icon} {offer["status"]}</span>'
                render_offer_card(offer, players_df, card_class=card_cls, status_badge=status_badge_html)

                # Accept counter offer or withdraw
                action_cols = st.columns([2, 2, 4])
                if offer["status"] == "Contrapropuesta" and offer.get("counter_amount"):
                    with action_cols[0]:
                        if st.button(f"✅ Aceptar contra", key=f"acc_co_{offer['id']}", use_container_width=True):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Aceptada"
                                    o["amount"]  = o["counter_amount"]
                            set_state("offers", all_offers2)
                            completed = get_state("completed_transfers", [])
                            completed.append({
                                "player": offer["player"], "from_team": offer["to_team"],
                                "to_team": offer["from_team"], "tipo": offer["tipo"],
                                "amount": offer["counter_amount"], "from_presi": offer["to_presi"],
                                "to_presi": offer["from_presi"], "date": datetime.now().isoformat()
                            })
                            set_state("completed_transfers", completed)
                            st.success(f"✅ Contraoferta aceptada! {offer['player']} → {offer['from_team']}")
                            wa_text = (
                                f"✅ *MMJ LEAGUE — CONTRAOFERTA ACEPTADA* ✅\n\n"
                                f"⚽ Jugador: *{offer['player']}*\n"
                                f"💼 Tipo: *{offer['tipo']}*\n"
                                f"💰 Monto final: *{fmt_money(offer.get('counter_amount', offer['amount']))}*\n"
                                f"🏟️ Va a: *{offer['from_team']}* ({offer['from_presi']})\n"
                                f"\n🎉 ¡Transferencia completada!"
                            )
                            st.markdown("**📲 Notifica al presidente:**")
                            wa_button(offer["to_presi"], wa_text, f"WhatsApp a {offer['to_presi']} — Contraoferta aceptada")

                if offer["status"] == "Pendiente":
                    with action_cols[0]:
                        if st.button(f"🗑️ Retirar", key=f"wd_{offer['id']}", use_container_width=True):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Retirada"
                            set_state("offers", all_offers2)
                            wa_text = (
                                f"🗑️ *MMJ LEAGUE — OFERTA RETIRADA*\n\n"
                                f"⚽ Jugador: *{offer['player']}*\n"
                                f"💰 Monto: *{fmt_money(offer['amount'])}*\n"
                                f"📤 *{presi_sel}* retiró su oferta por *{offer['to_team']}*."
                            )
                            st.markdown("**📲 Notifica al presidente:**")
                            wa_button(offer["to_presi"], wa_text, f"WhatsApp a {offer['to_presi']} — Oferta retirada")

                st.markdown("---")

    # ── Tab 4: Negociación ────────────────────────────────────────────────────
    with tab_negociar:
        st.markdown("#### 💬 Hilo de negociación")
        # Show all active negotiations involving me
        my_active = [o for o in all_offers
                     if (o["from_presi"] == presi_sel or o["to_presi"] == presi_sel)
                     and o["status"] in ("Pendiente","Contrapropuesta")]

        if not my_active:
            st.info("No hay negociaciones activas en este momento.")
        else:
            offer_labels = [f"{o['player']} — {o['from_presi']}→{o['to_presi']} ({o['status']})" for o in my_active]
            selected_idx = st.selectbox("Seleccionar negociación", range(len(my_active)),
                                        format_func=lambda i: offer_labels[i])
            sel_offer = my_active[selected_idx]

            pdata    = PLAYER_DATA.get(sel_offer["player"], {})
            photo    = get_player_photo(sel_offer["player"], pdata.get("sofifa",0))
            mval3    = players_df[players_df["name"] == sel_offer["player"]]["price"].values
            mval3    = mval3[0] if len(mval3) else 0

            st.markdown(
                f'<div style="background:#0c1825;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;margin-bottom:14px;'
                f'display:flex;align-items:center;gap:12px;">'
                f'<img src="{photo}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;" />'
                f'<div>'
                f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.1rem;font-weight:800;color:#f0f4f8;">⚽ {sel_offer["player"]}</div>'
                f'<div style="font-size:0.7rem;color:#5a7a90;">Oferta original: <span style="color:#e8b84b;font-family:monospace;">{fmt_money(sel_offer["amount"])}</span>'
                f' · Val. mercado: <span style="color:#c0d4e0;">{fmt_money(mval3)}</span></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            # Message thread
            msgs = sel_offer.get("messages", [])
            if msgs:
                st.markdown('<div class="offer-thread">', unsafe_allow_html=True)
                for m in msgs:
                    is_mine = m["from"] == presi_sel
                    bubble_cls = "nego-sent" if is_mine else "nego-received"
                    try:
                        ts = datetime.fromisoformat(m["ts"]).strftime("%d/%m %H:%M")
                    except:
                        ts = "—"
                    st.markdown(
                        f'<div class="nego-bubble {bubble_cls}">'
                        f'<span style="font-size:0.6rem;font-weight:700;color:#4a6070;">{m["from"]} · {ts}</span>'
                        f'<p style="margin:4px 0;font-size:0.78rem;color:#c0d4e0;">{m["text"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("Sin mensajes aún en esta negociación.")

            # Send message in negotiation
            new_msg = st.text_area("Escribir mensaje", placeholder="Tu mensaje para el otro presidente...", key=f"nego_msg_{sel_offer['id']}")
            if st.button("📨 Enviar mensaje", key=f"send_msg_{sel_offer['id']}"):
                if new_msg.strip():
                    all_offers2 = get_state("offers", [])
                    for o in all_offers2:
                        if o["id"] == sel_offer["id"]:
                            o.setdefault("messages", []).append({"from": presi_sel, "text": new_msg.strip(), "ts": datetime.now().isoformat()})
                    set_state("offers", all_offers2)
                    other_presi = sel_offer["to_presi"] if sel_offer["from_presi"] == presi_sel else sel_offer["from_presi"]
                    wa_text = (
                        f"💬 *MMJ LEAGUE — NUEVO MENSAJE EN NEGOCIACIÓN*\n\n"
                        f"⚽ Jugador: *{sel_offer['player']}*\n"
                        f"✉️ *{presi_sel}*: _{new_msg.strip()}_\n"
                        f"\nEntra a la app para responder."
                    )
                    st.success("Mensaje enviado.")
                    st.markdown("**📲 Notifica al presidente:**")
                    wa_button(other_presi, wa_text, f"WhatsApp a {other_presi} — Nuevo mensaje")

            # History of offer
            history = sel_offer.get("history", [])
            if history:
                st.markdown("**Historial de la oferta:**")
                for h in history:
                    try:
                        ts = datetime.fromisoformat(h["ts"]).strftime("%d/%m %H:%M")
                    except:
                        ts = "—"
                    amt = f" — {fmt_money(h['amount'])}" if h.get("amount") else ""
                    st.markdown(f'<div style="font-size:0.7rem;color:#4a6070;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.03);">'
                                f'{ts} · <span style="color:#c0d4e0;">{h["presi"]}</span> {h["action"]}{amt}</div>', unsafe_allow_html=True)

    # ── Tab 5: Historial ──────────────────────────────────────────────────────
    with tab_historial:
        st.markdown("#### ✅ Transferencias completadas")
        completed = get_state("completed_transfers", [])

        if not completed:
            st.info("Aún no se han completado transferencias en esta temporada.")
        else:
            total_moves = len(completed)
            total_spent = sum(t["amount"] for t in completed)
            c1, c2 = st.columns(2)
            c1.metric("Total transferencias", total_moves)
            c2.metric("Valor total movido", fmt_money(total_spent))

            for t in sorted(completed, key=lambda x: x["date"], reverse=True):
                # Build synthetic offer dict compatible with render_offer_card
                synth = {
                    "from_team":   t["from_team"],
                    "to_team":     t["to_team"],
                    "from_presi":  t.get("from_presi","?"),
                    "to_presi":    t.get("to_presi","?"),
                    "player":      t["player"],
                    "tipo":        t["tipo"],
                    "amount":      t["amount"],
                    "created_at":  t.get("date", datetime.now().isoformat()),
                    "counter_amount": None,
                }
                render_offer_card(synth, players_df, card_class="offer-accepted",
                                  status_badge='<span class="offer-status-badge status-accepted">✅ Completada</span>',
                                  show_pct=False)

    # ── Tab 6: Exportar Excel ─────────────────────────────────────────────────
    with tab_export:
        st.markdown("#### 📊 Exportar estado de la liga")
        current_df  = get_current_players()
        completed2  = get_state("completed_transfers", [])

        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Jugadores totales",       len(current_df))
        ec2.metric("Transferencias",          len(completed2))
        ec3.metric("Cedidos activos",         int(current_df["cesion"].notna().sum()))

        if st.button("⬇️ Generar Excel completo", use_container_width=True, type="primary"):
            export_rows = []
            for _, p in current_df.iterrows():
                pdata2 = PLAYER_DATA.get(p["name"], {})
                export_rows.append({
                    "Jugador": p["name"], "Posición": pdata2.get("pos","?"),
                    "Edad": pdata2.get("age",0),
                    "Nacionalidad": pdata2.get("nat_name",""),
                    "Equipo Actual": p["team"],
                    "Equipo Completo": TEAM_FULL_NAMES.get(p["team"],""),
                    "Presidente": TEAM_PRESIDENT.get(p["team"],""),
                    "DT": TEAM_DT.get(p["team"],""),
                    "Equipo Original (Cesion)": p["cesion"] if pd.notna(p.get("cesion")) else "",
                    "Tipo Contrato": p["contrato"],
                    "Valor Mercado ($)": p["price"],
                    "Renovación ($)": p["renovation"],
                    "Cláusula ($)": p["clausula"],
                })
            exp_df = pd.DataFrame(export_rows).sort_values(["Equipo Actual","Valor Mercado ($)"], ascending=[True,False])

            tr_rows = [{"Jugador":t["player"],"Tipo":t["tipo"],"Monto ($)":t["amount"],
                        "De":t["from_team"],"Pres. De":t.get("from_presi",""),
                        "A":t["to_team"],"Pres. A":t.get("to_presi",""),"Fecha":t.get("date","")}
                       for t in completed2]
            tr_df = pd.DataFrame(tr_rows) if tr_rows else pd.DataFrame()

            team_sum = exp_df.groupby(["Equipo Actual","Equipo Completo","Presidente","DT"]).agg(
                Jugadores=("Jugador","count"), Valor_Total=("Valor Mercado ($)","sum")
            ).reset_index().sort_values("Valor_Total", ascending=False)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                exp_df.to_excel(writer, sheet_name="Plantillas", index=False)
                if not tr_df.empty: tr_df.to_excel(writer, sheet_name="Transferencias", index=False)
                team_sum.to_excel(writer, sheet_name="Resumen Equipos", index=False)
            buf.seek(0)

            st.download_button(
                label="📥 Descargar MMJ_League.xlsx",
                data=buf,
                file_name=f"MMJ_League_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
