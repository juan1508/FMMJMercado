"""
mmj_fichajes.py  —  Sistema de Fichajes MMJ League
Modelo FC/EA Sports completo con cláusula obligatoria, cesiones por duración,
intercambios, recall con multa, oficina privada + admin global.
"""
import streamlit as st
import urllib.parse
from datetime import datetime, timedelta

from mmj_data_config import (
    PLAYER_DATA, TEAM_LOGOS, TEAM_FULL_NAMES, PRESIDENTS,
    POS_COLORS, TEAM_BUDGETS,
)

# ── Helpers inyectados desde app.py (sin import circular) ─────────────────────
_fmt_fn        = None
_get_budget_fn = None
_adjust_fn     = None
_photo_fn      = None

def init_helpers(fmt_money, get_team_budget, adjust_budget, get_player_photo):
    global _fmt_fn, _get_budget_fn, _adjust_fn, _photo_fn
    _fmt_fn        = fmt_money
    _get_budget_fn = get_team_budget
    _adjust_fn     = adjust_budget
    _photo_fn      = get_player_photo

# ── Constantes ─────────────────────────────────────────────────────────────────
RECALL_PCT = 0.20   # multa recall = 20 % del valor

# Tipos internos — en el menú se desglosan más (ver MENU_TIPOS)
TIPO_COLOR = {
    "Compra":          "#e8b84b",
    "Clausula":        "#f43f5e",
    "CesionCorta":     "#f97316",
    "CesionLarga":     "#fb923c",
    "CesionMaxima":    "#fbbf24",
    "Intercambio":     "#3b82f6",
    "Dinero+Jugador":  "#8b5cf6",
    "Recall":          "#ef4444",
    "OfertaCedido":    "#06b6d4",
    "PagarCesion":     "#22c55e",
}

# Porcentajes default por tipo de cesión
CESION_PCT = {
    "CesionCorta":    0.12,   # ~12 %  (media temporada)
    "CesionLarga":    0.25,   # ~25 %  (1 season)
    "CesionMaxima":   0.38,   # ~38 %  (2 seasons)
}

CESION_LABEL = {
    "CesionCorta":  "📤 Cesión Corta (Media Temp.)",
    "CesionLarga":  "📤 Cesión Larga (1 Season)",
    "CesionMaxima": "📤 Cesión Máxima (2 Seasons)",
}

CESION_CONTRATO = {
    "CesionCorta":  "Media Temporada",
    "CesionLarga":  "1 Season",
    "CesionMaxima": "2 Seasons",
}

# Menú ordenado como en FC
MENU_TIPOS = [
    ("Clausula",       "⚖️ Pagar Cláusula"),
    ("CesionCorta",    "📤 Cesión Corta (Media Temp.)"),
    ("CesionLarga",    "📤 Cesión Larga (1 Season)"),
    ("CesionMaxima",   "📤 Cesión Máxima (2 Seasons)"),
    ("Intercambio",    "🔄 Intercambio"),
    ("Dinero+Jugador", "💰+🔄 Dinero + Jugador"),
    ("Recall",         "↩️ Recall de Cesión"),
    ("OfertaCedido",   "📋 Oferta sobre Cedido"),
    ("PagarCesion",    "✅ Pagar Cesión (comprar cedido)"),
]
MENU_LABEL  = [lbl for _, lbl in MENU_TIPOS]
MENU_KEY    = {lbl: key for key, lbl in MENU_TIPOS}
MENU_DISPLAY= {key: lbl for key, lbl in MENU_TIPOS}

STATUS_META = {
    "Pendiente":         ("#f59e0b", "⏳"),
    "Aceptada":          ("#22c55e", "✅"),
    "Rechazada":         ("#ef4444", "❌"),
    "Contrapropuesta":   ("#8b5cf6", "↩️"),
    "Retirada":          ("#64748b", "🗑️"),
    "AutoAceptada":      ("#f43f5e", "⚖️"),
}

WA = {
    "JNKA": "573022105787",
    "MATI": "573184375432",
    "MAXI": "573025127701",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """<style>
.fc-deal{background:linear-gradient(135deg,#0d1928,#070e1a);border-radius:14px;overflow:hidden;margin-bottom:12px;box-shadow:0 4px 24px rgba(0,0,0,.45);}
.fc-deal:hover{transform:translateY(-1px);transition:transform .18s;}
.fc-deal-banner{display:flex;align-items:center;gap:10px;padding:12px 16px 10px;border-bottom:1px solid rgba(255,255,255,.05);flex-wrap:wrap;}
.fc-deal-body{padding:10px 16px 14px;}
.fc-team-block{display:flex;flex-direction:column;align-items:center;gap:3px;min-width:58px;}
.fc-team-logo{width:42px;height:42px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);padding:3px;}
.fc-team-name{font-size:.6rem;font-weight:800;color:#c0d4e0;text-align:center;}
.fc-team-presi{font-size:.5rem;font-weight:700;}
.fc-player-chip{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:10px;padding:6px 10px;}
.fc-stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;}
.fc-stat-box{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:8px;padding:9px 11px;}
.fc-stat-val{font-family:'Space Mono',monospace;font-size:.8rem;font-weight:700;}
.fc-stat-lbl{font-size:.44rem;color:#4a6070;text-transform:uppercase;letter-spacing:1px;margin-top:3px;}
.fc-bar{background:rgba(255,255,255,.05);border-radius:3px;height:4px;margin-top:5px;overflow:hidden;}
.fc-bar-fill{height:4px;border-radius:3px;}
.fc-tipo{display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:20px;font-size:.57rem;font-weight:900;letter-spacing:.5px;text-transform:uppercase;}
.fc-status{display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:20px;font-size:.58rem;font-weight:800;}
.fc-clausula-box{background:linear-gradient(135deg,rgba(244,63,94,.1),rgba(244,63,94,.05));border:1px solid rgba(244,63,94,.35);border-radius:12px;padding:14px 18px;margin:10px 0;}
.fc-clausula-title{font-size:.78rem;font-weight:800;color:#f43f5e;margin-bottom:8px;display:flex;align-items:center;gap:6px;}
.fc-warn-box{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.3);border-radius:10px;padding:12px 16px;margin:8px 0;}
.fc-ok-box{background:rgba(34,197,94,.07);border:1px solid rgba(34,197,94,.25);border-radius:10px;padding:12px 16px;margin:8px 0;}
.fc-block-box{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:12px 16px;margin:8px 0;}
.fc-recall-box{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:12px 16px;margin:8px 0;}
.fc-cesion-selector{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;}
.fc-cesion-btn{padding:8px 14px;border-radius:8px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);cursor:pointer;font-size:.72rem;font-weight:700;color:#8aa0b0;text-align:center;}
.fc-cesion-btn-active{background:rgba(249,115,22,.15);border-color:rgba(249,115,22,.5);color:#f97316;}
.fc-chat{max-height:260px;overflow-y:auto;padding:2px 0;}
.fc-chat::-webkit-scrollbar{width:3px;}
.fc-chat::-webkit-scrollbar-thumb{background:rgba(232,184,75,.3);border-radius:2px;}
.fc-bubble-me{background:rgba(232,184,75,.1);border:1px solid rgba(232,184,75,.22);border-radius:10px 10px 3px 10px;padding:7px 11px;margin:4px 0 4px 16%;}
.fc-bubble-them{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:10px 10px 10px 3px;padding:7px 11px;margin:4px 16% 4px 0;}
.fc-bubble-who{font-size:.57rem;color:#4a6070;font-weight:700;}
.fc-bubble-txt{font-size:.74rem;color:#c0d4e0;margin:2px 0 0;}
.fc-presi-bar{border-radius:14px;padding:14px 20px;margin-bottom:14px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;}
.fc-notif{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.35);border-radius:8px;padding:6px 14px;}
.fc-notif span{color:#ef4444;font-size:.78rem;font-weight:800;}
.fc-deal-type-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:6px;margin:10px 0;}
.fc-deal-type-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:10px 12px;cursor:pointer;transition:all .15s;}
.fc-deal-type-card:hover{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.15);}
.fc-deal-type-card-active{border-color:rgba(232,184,75,.5);background:rgba(232,184,75,.08);}
</style>"""

# ── Micro-helpers ──────────────────────────────────────────────────────────────
def _pc(p):    return PRESIDENTS.get(p, {}).get("color", "#aaa")
def _fmt(v):   return _fmt_fn(v) if _fmt_fn else str(v)
def _budget(t):return _get_budget_fn(t) if _get_budget_fn else TEAM_BUDGETS.get(t, 0)
def _adjust(t, d): return _adjust_fn(t, d) if _adjust_fn else None

def _logo_img(team, size=42):
    url = TEAM_LOGOS.get(team, "")
    if url:
        return (f'<img src="{url}" class="fc-team-logo" '
                f'style="width:{size}px;height:{size}px;" />')
    return f'<span style="font-size:.65rem;font-weight:900;color:#e8b84b;">{team}</span>'

def _flag(code, w=13):
    if not code: return ""
    return (f'<img src="https://flagcdn.com/28x21/{code}.png" '
            f'style="width:{w}px;height:{int(w*.75)}px;border-radius:2px;'
            f'object-fit:cover;vertical-align:middle;" />')

def _photo(name):
    pdata = PLAYER_DATA.get(name, {})
    return _photo_fn(name, pdata.get("sofifa", 0)) if _photo_fn else ""

def _team_presi(team):
    for p, pd in PRESIDENTS.items():
        if team in pd["teams"]: return p
    return "?"

def _wa_btn(to_presi, text, label="📲 WhatsApp"):
    num = WA.get(to_presi, "")
    if not num: return
    link = f"https://wa.me/{num}?text={urllib.parse.quote(text)}"
    st.markdown(
        f'<a href="{link}" target="_blank" style="display:inline-flex;align-items:center;'
        f'gap:6px;background:linear-gradient(135deg,#128C7E,#25D366);color:#fff;'
        f'font-size:.72rem;font-weight:700;padding:6px 13px;border-radius:7px;'
        f'text-decoration:none;border:1px solid rgba(255,255,255,.12);margin-top:4px;">'
        f'🟢 {label}</a>',
        unsafe_allow_html=True,
    )

def _tipo_badge(tipo):
    c   = TIPO_COLOR.get(tipo, "#aaa")
    lbl = MENU_DISPLAY.get(tipo, tipo)
    return (f'<span class="fc-tipo" '
            f'style="background:{c}18;color:{c};border:1px solid {c}33;">{lbl}</span>')

def _status_badge(status):
    c, icon = STATUS_META.get(status, ("#aaa", "❓"))
    return (f'<span class="fc-status" '
            f'style="background:{c}18;color:{c};border:1px solid {c}33;">{icon} {status}</span>')

# ── Player chip (inline HTML) ─────────────────────────────────────────────────
def _chip(name, players_df, size=44, show_val=True):
    pdata = PLAYER_DATA.get(name, {})
    pos   = pdata.get("pos", "?")
    pc    = POS_COLORS.get(pos, "#aaa")
    nat   = pdata.get("nat", "")
    photo = _photo(name)
    vr    = players_df[players_df["name"] == name]["price"].values
    val   = vr[0] if len(vr) else 0
    vh    = (f'<div style="font-family:\'Space Mono\',monospace;font-size:.63rem;'
             f'color:#e8b84b;font-weight:700;">{_fmt(val)}</div>') if show_val else ""
    return (
        f'<div class="fc-player-chip">'
        f'<img src="{photo}" style="width:{size}px;height:{size}px;border-radius:50%;'
        f'object-fit:cover;border:2px solid {pc}55;" />'
        f'<div><div style="display:flex;align-items:center;gap:5px;">'
        f'{_flag(nat, 12)}'
        f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:.88rem;'
        f'font-weight:900;color:#f0f4f8;">{name}</span>'
        f'<span style="background:{pc}1a;color:{pc};border:1px solid {pc}40;'
        f'font-size:.48rem;font-weight:900;padding:1px 4px;border-radius:3px;">{pos}</span>'
        f'</div>{vh}</div></div>'
    )

# ── Player info card (full) ───────────────────────────────────────────────────
def _info_card(name, players_df):
    prow = players_df[players_df["name"] == name]
    if prow.empty: return None
    pi    = prow.iloc[0]
    pdata = PLAYER_DATA.get(name, {})
    pos   = pdata.get("pos", "?")
    pc    = POS_COLORS.get(pos, "#aaa")
    nat   = pdata.get("nat", "")
    age   = pdata.get("age", 0)
    photo = _photo(name)

    # Cesion tag
    cesion_val = pi.get("cesion", "")
    cesion_h   = ""
    if cesion_val and str(cesion_val) not in ("nan", "None", ""):
        cesion_h = (f'<span style="background:rgba(249,115,22,.15);color:#f97316;'
                    f'border:1px solid rgba(249,115,22,.3);font-size:.5rem;font-weight:800;'
                    f'padding:2px 6px;border-radius:4px;">CEDIDO DE {cesion_val}</span>')

    # Clausula display
    claus = pi.get("clausula", 0)
    claus_h = (f'<div><div style="font-family:\'Space Mono\',monospace;font-size:.8rem;'
               f'color:#f43f5e;font-weight:700;">{_fmt(claus)}</div>'
               f'<div style="font-size:.48rem;color:#3a5060;text-transform:uppercase;'
               f'letter-spacing:1px;">Cláusula</div></div>') if claus and claus > 0 else (
               f'<div><div style="font-size:.72rem;color:#3a5060;font-weight:700;">—</div>'
               f'<div style="font-size:.48rem;color:#2a3a48;text-transform:uppercase;'
               f'letter-spacing:1px;">Sin cláusula</div></div>')

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0c1825,#080f18);'
        f'border:1px solid rgba(255,255,255,.07);border-radius:12px;'
        f'padding:13px;display:flex;align-items:center;gap:13px;margin:10px 0;">'
        f'<img src="{photo}" style="width:58px;height:58px;border-radius:50%;'
        f'object-fit:cover;border:2px solid {pc}55;" />'
        f'<div style="flex:1;">'
        f'<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:7px;">'
        f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.2rem;'
        f'font-weight:900;color:#f0f4f8;">{name}</span>'
        f'<span style="background:{pc}1a;color:{pc};border:1px solid {pc}40;'
        f'font-size:.5rem;font-weight:900;padding:1px 5px;border-radius:3px;">{pos}</span>'
        f'{_flag(nat)} <span style="font-size:.58rem;color:#4a6070;">'
        f'{pdata.get("nat_name","")} · {age}a</span>'
        f'{cesion_h}'
        f'</div>'
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        f'<div><div style="font-family:\'Space Mono\',monospace;font-size:.8rem;'
        f'color:#e8b84b;font-weight:700;">{_fmt(pi["price"])}</div>'
        f'<div style="font-size:.48rem;color:#3a5060;text-transform:uppercase;'
        f'letter-spacing:1px;">Valor</div></div>'
        f'<div><div style="font-family:\'Space Mono\',monospace;font-size:.8rem;'
        f'color:#22c55e;font-weight:700;">{_fmt(pi["renovation"])}</div>'
        f'<div style="font-size:.48rem;color:#3a5060;text-transform:uppercase;'
        f'letter-spacing:1px;">Renovación</div></div>'
        f'{claus_h}'
        f'<div><div style="font-size:.78rem;font-weight:700;color:#c0d4e0;">'
        f'{pi["contrato"]}</div>'
        f'<div style="font-size:.48rem;color:#3a5060;text-transform:uppercase;'
        f'letter-spacing:1px;">Contrato</div></div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )
    return pi

# ── Finance panel (4 stats) ───────────────────────────────────────────────────
def _fin_panel(team, players_df, cost=0, label="Finanzas"):
    ct      = st.session_state.get("_ct_cache", [])
    budget  = _budget(team)
    base_b  = TEAM_BUDGETS.get(team, 0)
    spent   = sum(t["amount"] for t in ct if t.get("from_team") == team)
    income  = sum(t["amount"] for t in ct if t.get("to_team")   == team)
    sq_val  = players_df[players_df["team"] == team]["price"].sum()
    after   = budget - cost
    bf      = max(0, min(100, int((budget / base_b) * 100))) if base_b > 0 else 0
    bc      = "#22c55e" if budget >= 0 else "#ef4444"
    in_red  = after < 0 and cost > 0
    tl      = TEAM_LOGOS.get(team, "")
    tl_h    = (f'<img src="{tl}" style="width:22px;height:22px;object-fit:contain;'
               f'border-radius:50%;padding:2px;" />') if tl else ""
    ss = ""
    if cost > 0:
        ss = (f'<span style="margin-left:auto;font-size:.62rem;color:#ef4444;font-weight:800;">'
              f'⛔ Faltan {_fmt(abs(after))}</span>'
              if in_red else
              f'<span style="margin-left:auto;font-size:.62rem;color:#22c55e;font-weight:700;">'
              f'✅ Puede pagar</span>')
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(13,22,36,.95),rgba(7,13,22,.98));'
        f'border:1px solid {"rgba(239,68,68,.3)" if in_red else "rgba(232,184,75,.15)"};'
        f'border-radius:12px;padding:13px 17px;margin:8px 0;">'
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:9px;">'
        f'{tl_h}<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:.88rem;'
        f'font-weight:800;color:#c0d4e0;">{team} — {label}</span>{ss}</div>'
        f'<div class="fc-stat-grid">'
        f'<div class="fc-stat-box"><div class="fc-stat-val" '
        f'style="color:{"#ef4444" if budget<0 else "#e8b84b"};">{_fmt(budget)}</div>'
        f'<div class="fc-stat-lbl">Presupuesto</div>'
        f'<div class="fc-bar"><div class="fc-bar-fill" '
        f'style="width:{bf}%;background:{bc};"></div></div></div>'
        f'<div class="fc-stat-box"><div class="fc-stat-val" style="color:#3b82f6;">'
        f'{_fmt(sq_val)}</div><div class="fc-stat-lbl">Plantilla</div></div>'
        f'<div class="fc-stat-box"><div class="fc-stat-val" style="color:#f97316;">'
        f'{_fmt(spent) if spent else "—"}</div><div class="fc-stat-lbl">Gastado</div></div>'
        f'<div class="fc-stat-box"><div class="fc-stat-val" style="color:#22c55e;">'
        f'{_fmt(income) if income else "—"}</div><div class="fc-stat-lbl">Ingresos</div></div>'
        f'</div>'
        + (f'<div style="margin-top:7px;font-size:.62rem;font-weight:700;'
           f'color:{"#ef4444" if after<0 else "#22c55e"};">'
           f'Tras esta operación: {_fmt(after)}</div>' if cost > 0 else "") +
        f'</div>',
        unsafe_allow_html=True,
    )
    return after >= 0   # returns can_pay bool

# ── Deal card ─────────────────────────────────────────────────────────────────
def _deal_card(offer, players_df):
    tipo    = offer.get("tipo", "Compra")
    top_c   = TIPO_COLOR.get(tipo, "#e8b84b")
    from_t  = offer.get("from_team", "")
    to_t    = offer.get("to_team", "")
    fp      = offer.get("from_presi", "?")
    tp      = offer.get("to_presi", "?")
    player  = offer.get("player", "")
    player2 = offer.get("player2", "")
    amount  = offer.get("amount", 0)
    status  = offer.get("status", "Pendiente")
    dur_lbl = offer.get("duration_label", "")

    try:    ts = datetime.fromisoformat(offer["created_at"]).strftime("%d/%m %H:%M")
    except: ts = "—"

    vr  = players_df[players_df["name"] == player]["price"].values
    mv  = vr[0] if len(vr) else 0
    pct = (amount / mv * 100) if mv > 0 and amount else 0
    pc  = "#22c55e" if pct >= 100 else "#f59e0b" if pct >= 70 else "#ef4444"

    # Clausula indicator
    claus_h = ""
    if tipo == "Clausula" and mv > 0:
        claus_row = players_df[players_df["name"] == player]["clausula"].values
        claus_val = claus_row[0] if len(claus_row) else 0
        if claus_val and claus_val > 0:
            diff = amount - claus_val
            diff_c = "#22c55e" if diff >= 0 else "#ef4444"
            diff_txt = f'{"+" if diff>=0 else ""}{_fmt(diff)} vs cláusula'
            claus_h = (f'<div style="font-size:.6rem;color:{diff_c};font-weight:700;'
                       f'margin-top:4px;">{diff_txt}</div>')

    counter_h = ""
    if offer.get("counter_amount"):
        counter_h = (
            f'<div style="background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.28);'
            f'border-radius:6px;padding:5px 12px;margin-top:6px;display:inline-flex;'
            f'align-items:center;gap:8px;">'
            f'<span style="font-size:.64rem;color:#8b5cf6;font-weight:700;">'
            f'↩️ Contra: {_fmt(offer["counter_amount"])}'
            + (f' + {offer["counter_player"]}' if offer.get("counter_player") else "") +
            f'</span></div>'
        )

    # Duration badge for cesiones
    dur_h = ""
    if dur_lbl:
        dur_h = (f'<span style="background:rgba(249,115,22,.15);color:#f97316;'
                 f'border:1px solid rgba(249,115,22,.3);font-size:.52rem;font-weight:800;'
                 f'padding:2px 7px;border-radius:4px;margin-left:4px;">📅 {dur_lbl}</span>')

    # Center content
    center_h = ""
    if player:   center_h += _chip(player, players_df, size=44)
    if player2:
        center_h += (f'<div style="font-size:.72rem;color:#3a5060;text-align:center;">'
                     f'{"＋" if tipo=="Dinero+Jugador" else "🔄"}</div>'
                     + _chip(player2, players_df, size=38))
    if amount and tipo != "Intercambio":
        center_h += (f'<div style="font-family:\'Space Mono\',monospace;font-size:1rem;'
                     f'font-weight:700;color:#e8b84b;text-align:center;">{_fmt(amount)}</div>')
    center_h += f'<div style="text-align:center;">{_tipo_badge(tipo)}{dur_h}</div>'

    st.markdown(
        f'<div class="fc-deal" style="border-top:3px solid {top_c};">'
        f'<div class="fc-deal-banner">'
        f'<div class="fc-team-block">{_logo_img(from_t,42)}'
        f'<div class="fc-team-name">{from_t}</div>'
        f'<div class="fc-team-presi" style="color:{_pc(fp)};">{fp}</div></div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:5px;">'
        f'{center_h}</div>'
        f'<div style="font-size:1.4rem;color:{top_c}66;">→</div>'
        f'<div class="fc-team-block">{_logo_img(to_t,42)}'
        f'<div class="fc-team-name">{to_t}</div>'
        f'<div class="fc-team-presi" style="color:{_pc(tp)};">{tp}</div></div>'
        f'</div>'
        f'<div class="fc-deal-body">'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
        f'{_status_badge(status)}'
        + (f'<div style="background:rgba(255,255,255,.04);border-radius:3px;width:70px;'
           f'height:4px;overflow:hidden;display:inline-block;vertical-align:middle;">'
           f'<div style="width:{min(100,int(pct))}%;height:4px;background:{pc};"></div></div>'
           f'<span style="font-size:.57rem;color:{pc};font-weight:700;">{pct:.0f}% val.</span>'
           if amount and mv else "") +
        f'<span style="margin-left:auto;font-size:.56rem;color:#2a3a48;">{ts}</span>'
        f'</div>'
        f'{claus_h}{counter_h}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

# ── Budget helpers ─────────────────────────────────────────────────────────────
def _apply_budgets(offer, final_amount):
    tipo   = offer["tipo"]
    buyer  = offer["from_team"]   # quien hace la oferta / paga
    seller = offer["to_team"]     # quien tiene el jugador / recibe

    if tipo in ("Compra", "Clausula", "OfertaCedido", "PagarCesion"):
        _adjust(buyer,  -final_amount)
        _adjust(seller, +final_amount)
    elif tipo in ("CesionCorta", "CesionLarga", "CesionMaxima"):
        _adjust(buyer,  -final_amount)
        _adjust(seller, +final_amount)
    elif tipo == "Intercambio":
        pass   # sin flujo de dinero
    elif tipo == "Dinero+Jugador":
        if final_amount > 0:
            _adjust(buyer,  -final_amount)
            _adjust(seller, +final_amount)
    elif tipo == "Recall":
        multa = offer.get("recall_penalty", 0)
        _adjust(buyer,  -multa)
        _adjust(seller, +multa)

def _complete(offer, final_amount, actor, note, get_state, set_state):
    offers = get_state("offers", [])
    for o in offers:
        if o["id"] == offer["id"]:
            o["status"] = "Aceptada"
            o["amount"] = final_amount
            if note:
                o.setdefault("messages", []).append(
                    {"from": actor, "text": note, "ts": datetime.now().isoformat()})
            o.setdefault("history", []).append(
                {"action": "aceptada", "presi": actor, "ts": datetime.now().isoformat()})
    set_state("offers", offers)
    entry = {
        "player":          offer["player"],
        "player2":         offer.get("player2", ""),
        "from_team":       offer["to_team"],
        "to_team":         offer["from_team"],
        "tipo":            offer["tipo"],
        "duration_label":  offer.get("duration_label", ""),
        "amount":          final_amount,
        "recall_penalty":  offer.get("recall_penalty", 0),
        "from_presi":      offer["to_presi"],
        "to_presi":        offer["from_presi"],
        "date":            datetime.now().isoformat(),
    }
    completed = get_state("completed_transfers", [])
    completed.append(entry)
    set_state("completed_transfers", completed)
    _apply_budgets(offer, final_amount)
    st.session_state["_ct_cache"] = get_state("completed_transfers", [])
    st.success(f"✅ Transferencia completada — {offer['player']} → {offer['from_team']}")

def _set_status(offer_id, status, actor, note, get_state, set_state):
    offers = get_state("offers", [])
    for o in offers:
        if o["id"] == offer_id:
            o["status"] = status
            if note:
                o.setdefault("messages", []).append(
                    {"from": actor, "text": note, "ts": datetime.now().isoformat()})
            o.setdefault("history", []).append(
                {"action": status.lower(), "presi": actor, "ts": datetime.now().isoformat()})
    set_state("offers", offers)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: NUEVA OFERTA — menú completo estilo FC
# ─────────────────────────────────────────────────────────────────────────────
def _tab_nueva(presi, players_df, get_state, set_state, window_open):
    if not window_open:
        st.warning("⛔ La ventana de fichajes no está activa."); return

    my_teams    = PRESIDENTS[presi]["teams"]
    rival_teams = sorted([t for t in players_df["team"].unique() if t not in my_teams])

    # ── 1. Equipo rival ───────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    rival_team  = c1.selectbox("🏟️ Equipo rival", rival_teams, key=f"riv_{presi}")
    rival_presi = _team_presi(rival_team)
    rpc = _pc(rival_presi)
    rl  = TEAM_LOGOS.get(rival_team, "")
    rl_h= f'<img src="{rl}" style="width:30px;height:30px;object-fit:contain;border-radius:50%;padding:2px;" />' if rl else ""
    c2.markdown(
        f'<div style="padding:8px 13px;background:{rpc}10;border:1px solid {rpc}28;'
        f'border-radius:10px;margin-top:22px;display:flex;align-items:center;gap:8px;">'
        f'{rl_h}<div><span style="font-size:.8rem;color:{rpc};font-weight:800;">{rival_presi}</span>'
        f'<div style="font-size:.58rem;color:#4a6070;">'
        f'{TEAM_FULL_NAMES.get(rival_team, rival_team)}</div></div></div>',
        unsafe_allow_html=True,
    )

    # ── 2. Tipo de operación ──────────────────────────────────────────────────
    tipo_lbl = st.selectbox("💼 Tipo de operación", MENU_LABEL, key=f"tipo_{presi}")
    tipo     = MENU_KEY[tipo_lbl]

    # ── 3. Jugador objetivo ───────────────────────────────────────────────────
    player_sel     = None
    pinfo          = None
    recall_pen_amt = 0
    duration_label = ""   # para cesiones

    if tipo == "Recall":
        # Mis jugadores cedidos a este equipo
        cedidos_mios = players_df[
            (players_df["cesion"].notna()) &
            (players_df["cesion"].apply(lambda x: str(x) not in ("nan","None",""))) &
            (players_df["cesion"].isin(my_teams)) &
            (players_df["team"] == rival_team)
        ]
        if cedidos_mios.empty:
            st.info("No tenés jugadores cedidos en este equipo para hacer recall."); return
        player_sel = st.selectbox("↩️ Jugador a recuperar", cedidos_mios["name"].tolist(),
                                   key=f"rcp_{presi}")
        pinfo = _info_card(player_sel, players_df)
        prow2 = players_df[players_df["name"] == player_sel]
        rv    = prow2["price"].values[0] if not prow2.empty else 0
        recall_pen_amt = int(rv * RECALL_PCT)
        host  = prow2["team"].values[0] if not prow2.empty else rival_team
        cont  = prow2["contrato"].values[0] if not prow2.empty else "—"
        st.markdown(
            f'<div class="fc-recall-box">'
            f'<div style="font-size:.76rem;font-weight:800;color:#ef4444;margin-bottom:5px;">'
            f'↩️ Condiciones del Recall</div>'
            f'<div style="font-size:.7rem;color:#c0d4e0;">Cedido en <b>{host}</b> · '
            f'Contrato: <b>{cont}</b></div>'
            f'<div style="margin-top:7px;font-size:.68rem;color:#8aa0b0;">'
            f'Multa ({int(RECALL_PCT*100)}% del valor):</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:.95rem;'
            f'color:#ef4444;font-weight:700;">{_fmt(recall_pen_amt)}</div>'
            f'<div style="font-size:.6rem;color:#5a7a90;margin-top:3px;">'
            f'Se descuenta de tu presupuesto. {host} lo recibe como indemnización.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    elif tipo == "OfertaCedido":
        cedidos_rival = players_df[
            (players_df["cesion"].notna()) &
            (players_df["cesion"].apply(lambda x: str(x) not in ("nan","None",""))) &
            (players_df["team"] == rival_team)
        ]
        if cedidos_rival.empty:
            st.info("Este equipo no tiene jugadores cedidos de otros equipos."); return
        player_sel = st.selectbox("📋 Jugador cedido objetivo",
                                   cedidos_rival["name"].tolist(), key=f"ocp_{presi}")
        pinfo = _info_card(player_sel, players_df)

    else:
        squad_rival = players_df[players_df["team"] == rival_team].sort_values("price", ascending=False)
        if squad_rival.empty:
            st.info("Este equipo no tiene jugadores registrados."); return
        player_sel = st.selectbox("⚽ Jugador objetivo", squad_rival["name"].tolist(),
                                   key=f"psel_{presi}")
        pinfo = _info_card(player_sel, players_df)

    if not player_sel: return
    pv_arr  = players_df[players_df["name"] == player_sel]["price"].values
    pv      = pv_arr[0] if len(pv_arr) else 0
    claus_arr = players_df[players_df["name"] == player_sel]["clausula"].values
    claus_val = claus_arr[0] if len(claus_arr) else 0
    renov_arr = players_df[players_df["name"] == player_sel]["renovation"].values
    renov_val = renov_arr[0] if len(renov_arr) else 0

    # ── 4. Jugador propio para intercambio / D+J ──────────────────────────────
    player2_sel = None
    if tipo in ("Intercambio", "Dinero+Jugador"):
        my_squad = players_df[players_df["team"].isin(my_teams)].sort_values("price", ascending=False)
        if my_squad.empty:
            st.warning("No tenés jugadores disponibles para ofrecer.")
        else:
            player2_sel = st.selectbox("🔄 Mi jugador (va en sentido inverso)",
                                        my_squad["name"].tolist(), key=f"p2_{presi}")
            st.markdown(_chip(player2_sel, players_df), unsafe_allow_html=True)

    # ── 5. Monto / lógica por tipo ────────────────────────────────────────────
    offer_amount   = 0
    is_clausula    = (tipo == "Clausula")
    clausula_ok    = (claus_val and claus_val > 0)

    def _amount_input(label, default=0):
        """Renders number input + % of market value indicator."""
        ca, cb = st.columns([3, 1])
        amt = ca.number_input(label, min_value=0, value=max(0, default),
                              step=500_000, format="%d", key=f"amt_{presi}")
        pct_v = (amt / pv * 100) if pv > 0 else 0
        pct_c = "#22c55e" if pct_v >= 100 else "#f59e0b" if pct_v >= 70 else "#ef4444"
        cb.markdown(
            f'<div style="padding-top:28px;font-family:\'Space Mono\',monospace;'
            f'font-size:1rem;font-weight:700;color:{pct_c};">{pct_v:.0f}%</div>'
            f'<div style="font-size:.52rem;color:#3a5060;">del valor</div>',
            unsafe_allow_html=True,
        )
        return amt

    if tipo == "Recall":
        offer_amount = recall_pen_amt

    elif tipo == "Intercambio":
        st.info("🔄 Intercambio puro — sin flujo de dinero.")

    elif tipo == "Clausula":
        # ── Cláusula: monto fijo, muestra diferencia vs cláusula real ─────────
        if not clausula_ok:
            st.markdown(
                f'<div class="fc-block-box">'
                f'<span style="font-size:.78rem;font-weight:800;color:#ef4444;">'
                f'⛔ Este jugador no tiene cláusula de rescisión registrada.</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            return

        offer_amount = int(claus_val)

        # Show clausula amount + diff vs market value
        diff_cv  = offer_amount - int(pv)
        diff_c   = "#22c55e" if diff_cv >= 0 else "#ef4444"
        diff_txt = f'{"+" if diff_cv >= 0 else ""}{_fmt(diff_cv)} vs valor de mercado'
        st.markdown(
            f'<div class="fc-clausula-box">'
            f'<div class="fc-clausula-title">⚖️ Cláusula de Rescisión</div>'
            f'<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-end;">'
            f'<div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:1.05rem;'
            f'color:#f43f5e;font-weight:700;">{_fmt(offer_amount)}</div>'
            f'<div style="font-size:.5rem;color:#4a6070;text-transform:uppercase;'
            f'letter-spacing:1px;margin-top:2px;">Monto fijo</div>'
            f'</div>'
            f'<div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:.82rem;'
            f'color:{diff_c};font-weight:700;">{diff_txt}</div>'
            f'<div style="font-size:.5rem;color:#4a6070;text-transform:uppercase;'
            f'letter-spacing:1px;margin-top:2px;">Diferencia</div>'
            f'</div>'
            f'<div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:.82rem;'
            f'color:#e8b84b;font-weight:700;">{_fmt(int(pv))}</div>'
            f'<div style="font-size:.5rem;color:#4a6070;text-transform:uppercase;'
            f'letter-spacing:1px;margin-top:2px;">Valor de mercado</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    elif tipo in ("CesionCorta", "CesionLarga", "CesionMaxima"):
        # ── Cesión con duración — monto libre ─────────────────────────────────
        duration_label = CESION_CONTRATO[tipo]
        st.markdown(
            f'<div style="background:rgba(249,115,22,.07);border:1px solid rgba(249,115,22,.25);'
            f'border-radius:10px;padding:10px 16px;margin:8px 0;">'
            f'<span style="font-size:.72rem;font-weight:800;color:#f97316;">'
            f'📅 {CESION_LABEL[tipo]}</span>'
            f'<span style="font-size:.62rem;color:#8aa0b0;margin-left:10px;">'
            f'Monto libre — valor de mercado del jugador: {_fmt(int(pv))}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        offer_amount = _amount_input("💰 Monto cesión ($)", default=0)

    elif tipo == "PagarCesion":
        offer_amount = _amount_input("💰 Monto compra cesión ($)", default=0)

    else:
        # OfertaCedido, Dinero+Jugador
        pv2_arr = players_df[players_df["name"] == player2_sel]["price"].values if player2_sel else []
        pv2     = pv2_arr[0] if len(pv2_arr) else 0
        def_val = max(0, int(pv) - int(pv2)) if tipo == "Dinero+Jugador" else 0
        offer_amount = _amount_input("💰 Monto ($)", default=def_val)

    # ── 6. Equipo receptor ────────────────────────────────────────────────────
    dest_team = st.selectbox("🏟️ Mi equipo receptor", sorted(my_teams), key=f"dest_{presi}")

    # ── 7. Panel financiero ───────────────────────────────────────────────────
    cost_d = offer_amount if tipo != "Intercambio" else 0
    if cost_d > 0:
        can_pay = _fin_panel(dest_team, players_df, cost=cost_d)
        if not can_pay:
            st.warning(
                f"⚠️ **{dest_team}** no tiene presupuesto suficiente — "
                f"le faltan **{_fmt(abs(_budget(dest_team) - cost_d))}**. "
                f"Podés enviar la oferta igualmente, pero no podrá completarse hasta tener fondos."
            )

    # ── 8. Mensaje ────────────────────────────────────────────────────────────
    msg = st.text_area("💬 Mensaje (opcional)", placeholder="Detalla tu propuesta...",
                        max_chars=400, key=f"msg_{presi}")

    # ── 9. Enviar ─────────────────────────────────────────────────────────────
    if st.button("📤 Enviar Oferta", use_container_width=True, type="primary", key=f"send_{presi}"):
        oid = f"offer_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        new_offer = {
            "id":             oid,
            "from_presi":     presi,
            "to_presi":       rival_presi,
            "from_team":      dest_team,
            "to_team":        rival_team,
            "player":         player_sel,
            "player2":        player2_sel or "",
            "tipo":           tipo,
            "amount":         offer_amount,
            "duration_label": duration_label,
            "recall_penalty": recall_pen_amt,
            "clausula_val":   claus_val if is_clausula else 0,
            "is_clausula":    is_clausula,
            "messages":       [{"from": presi, "text": msg,
                                "ts": datetime.now().isoformat()}] if msg else [],
            "status":         "Pendiente",
            "created_at":     datetime.now().isoformat(),
            "history":        [{"action":"enviada","presi":presi,
                                "ts":datetime.now().isoformat()}],
        }
        offers = get_state("offers", [])
        offers.append(new_offer)
        set_state("offers", offers)
        st.success(f"✅ Oferta enviada a **{rival_presi}** — {player_sel}")

        wa_text = (
            f"🚨 *MMJ LEAGUE — NUEVA OFERTA* 🚨\n\n"
            f"Tipo: *{tipo_lbl}*\n"
            f"⚽ Jugador: *{player_sel}*\n"
            + (f"🔄 Mi jugador: *{player2_sel}*\n" if player2_sel else "")
            + (f"⏱️ Duración: *{duration_label}*\n" if duration_label else "")
            + (f"⚖️ Cláusula: *{_fmt(claus_val)}*\n" if is_clausula else "")
            + (f"💰 Monto: *{_fmt(offer_amount)}*\n" if offer_amount else "")
            + f"📤 De: *{presi}* ({dest_team}) → *{rival_team}*\n"
            + (f"💬 _{msg}_\n" if msg else "")
            + "\n➡️ Entrá a la app para responder."
        )
        st.markdown("**📲 Notificá al presidente:**")
        _wa_btn(rival_presi, wa_text, f"WhatsApp a {rival_presi}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: BANDEJA DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
def _tab_bandeja(presi, players_df, get_state, set_state):
    all_offers = get_state("offers", [])
    received   = [o for o in all_offers
                  if o["to_presi"] == presi and o["status"] == "Pendiente"]

    if not received:
        st.info("📭 No tenés ofertas pendientes."); return

    for offer in sorted(received, key=lambda x: x["created_at"], reverse=True):
        _deal_card(offer, players_df)

        # Last message
        msgs = offer.get("messages", [])
        if msgs:
            m   = msgs[-1]
            cls = "fc-bubble-me" if m["from"] == presi else "fc-bubble-them"
            st.markdown(
                f'<div class="{cls}"><div class="fc-bubble-who">{m["from"]}</div>'
                f'<div class="fc-bubble-txt">{m["text"]}</div></div>',
                unsafe_allow_html=True,
            )

        buyer_bud   = _budget(offer["from_team"])
        buyer_after = buyer_bud - offer["amount"]
        can_pay     = buyer_after >= 0
        is_claus    = offer.get("is_clausula", False)

        _fin_panel(offer["from_team"], players_df, cost=offer["amount"],
                   label="Finanzas del comprador")

        # ── Cláusula: mostrar info de diferencia ──────────────────────────────
        if is_claus:
            claus_orig = offer.get("clausula_val", 0)
            diff_co    = offer["amount"] - int(players_df[players_df["name"]==offer["player"]]["price"].values[0]) if len(players_df[players_df["name"]==offer["player"]]["price"].values) else 0
            diff_c     = "#22c55e" if diff_co >= 0 else "#ef4444"
            diff_txt   = f'{"+" if diff_co >= 0 else ""}{_fmt(diff_co)} vs valor de mercado'
            st.markdown(
                f'<div class="fc-clausula-box">'
                f'<div class="fc-clausula-title">⚖️ Oferta de Cláusula de Rescisión</div>'
                f'<div style="display:flex;gap:22px;flex-wrap:wrap;">'
                f'<div><div style="font-family:\'Space Mono\',monospace;font-size:.88rem;'
                f'color:#f43f5e;font-weight:700;">{_fmt(claus_orig)}</div>'
                f'<div style="font-size:.5rem;color:#4a6070;text-transform:uppercase;'
                f'letter-spacing:1px;margin-top:2px;">Monto cláusula</div></div>'
                f'<div><div style="font-family:\'Space Mono\',monospace;font-size:.88rem;'
                f'color:{diff_c};font-weight:700;">{diff_txt}</div>'
                f'<div style="font-size:.5rem;color:#4a6070;text-transform:uppercase;'
                f'letter-spacing:1px;margin-top:2px;">Diferencia</div></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # ── Acciones (iguales para todos los tipos) ───────────────────────────
        note_key = f"note_{offer['id']}"
        rc1, rc2, rc3 = st.columns([2, 2, 3])
        note = rc3.text_input("Nota", key=note_key, placeholder="Comentario...",
                               label_visibility="collapsed")

        with rc1:
            if not can_pay:
                st.button("✅ Aceptar", key=f"acc_{offer['id']}", use_container_width=True,
                           type="primary", disabled=True)
                st.caption(f"⛔ Le faltan {_fmt(abs(buyer_after))}")
            elif st.button("✅ Aceptar", key=f"acc_{offer['id']}", use_container_width=True,
                            type="primary"):
                _complete(offer, offer["amount"], presi, note, get_state, set_state)
                wa_tipo = "CLÁUSULA ACEPTADA" if is_claus else "OFERTA ACEPTADA"
                _wa_btn(offer["from_presi"],
                        f"✅ *MMJ LEAGUE — {wa_tipo}*\n\n"
                        f"⚽ *{offer['player']}* → {offer['from_team']}\n"
                        f"💰 {_fmt(offer['amount'])}\n"
                        + (f"💬 _{note}_\n" if note else "") + "🎉 ¡Completada!",
                        f"WhatsApp a {offer['from_presi']}")
        with rc2:
            if st.button("❌ Rechazar", key=f"rej_{offer['id']}", use_container_width=True):
                _set_status(offer["id"], "Rechazada", presi, note, get_state, set_state)
                _wa_btn(offer["from_presi"],
                        f"❌ *MMJ LEAGUE — OFERTA RECHAZADA*\n\n"
                        f"⚽ *{offer['player']}* — {offer['to_team']} rechazó\n"
                        + (f"💬 _{note}_" if note else ""),
                        f"WhatsApp a {offer['from_presi']}")
                st.rerun()

        # ── Contraoferta ──────────────────────────────────────────────────────
        with st.expander(f"↩️ Contraoferta — {offer['player']}", expanded=False):
            pv_r  = players_df[players_df["name"] == offer["player"]]["price"].values
            pv_d  = int(pv_r[0]) if len(pv_r) else 0
            co_amt= st.number_input("Monto contraoferta ($)", min_value=0, value=pv_d,
                                     step=500_000, format="%d", key=f"coamt_{offer['id']}")
            mt_b  = PRESIDENTS[presi]["teams"]
            my_sq = players_df[players_df["team"].isin(mt_b)]["name"].tolist()
            co_pl = st.selectbox("+ Incluir jugador (opcional)", ["—"]+my_sq,
                                  key=f"copl_{offer['id']}")
            co_pl = co_pl if co_pl != "—" else ""
            co_note = st.text_input("Mensaje", key=f"conote_{offer['id']}",
                                     placeholder="Explicá tu contraoferta...")
            if st.button("↩️ Enviar Contraoferta", key=f"cosend_{offer['id']}",
                          use_container_width=True):
                offers2 = get_state("offers", [])
                for o in offers2:
                    if o["id"] == offer["id"]:
                        o["status"]         = "Contrapropuesta"
                        o["counter_amount"] = co_amt
                        o["counter_player"] = co_pl
                        txt = f"Contraoferta: {_fmt(co_amt)}"
                        if co_pl:   txt += f" + {co_pl}"
                        if co_note: txt += f" — {co_note}"
                        o.setdefault("messages", []).append(
                            {"from": presi, "text": txt, "ts": datetime.now().isoformat()})
                        o.setdefault("history", []).append(
                            {"action":"contrapropuesta","presi":presi,"ts":datetime.now().isoformat()})
                set_state("offers", offers2)
                _wa_btn(offer["from_presi"],
                        f"↩️ *MMJ LEAGUE — CONTRAOFERTA*\n\n"
                        f"⚽ *{offer['player']}*\n"
                        f"Original: {_fmt(offer['amount'])} → Contra: {_fmt(co_amt)}\n"
                        + (f"🔄 + {co_pl}\n" if co_pl else "")
                        + (f"💬 _{co_note}_\n" if co_note else "")
                        + "Entrá a la app.",
                        f"WhatsApp a {offer['from_presi']}")
                st.rerun()

        st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: MIS OFERTAS
# ─────────────────────────────────────────────────────────────────────────────
def _tab_mis_ofertas(presi, players_df, get_state, set_state):
    all_offers = get_state("offers", [])
    sent       = [o for o in all_offers if o["from_presi"] == presi]
    if not sent:
        st.info("No enviaste ninguna oferta todavía."); return

    for offer in sorted(sent, key=lambda x: x["created_at"], reverse=True):
        _deal_card(offer, players_df)

        if offer["status"] == "Contrapropuesta" and offer.get("counter_amount") is not None:
            co_amt = offer["counter_amount"]
            co_pl  = offer.get("counter_player", "")
            bud    = _budget(offer["from_team"])
            can    = (bud - co_amt) >= 0
            st.markdown(
                f'<div style="background:rgba(139,92,246,.08);border:1px solid rgba(139,92,246,.28);'
                f'border-radius:8px;padding:9px 13px;margin:5px 0;">'
                f'<span style="font-size:.7rem;color:#8b5cf6;font-weight:800;">'
                f'↩️ Contraoferta: {_fmt(co_amt)}'
                + (f' + {co_pl}' if co_pl else "") +
                f'</span></div>',
                unsafe_allow_html=True,
            )
            ac1, ac2 = st.columns(2)
            with ac1:
                if not can:
                    st.button("✅ Aceptar contra", key=f"accco_{offer['id']}",
                               use_container_width=True, disabled=True)
                    st.caption(f"⛔ Le faltan {_fmt(abs(bud - co_amt))}")
                elif st.button("✅ Aceptar contra", key=f"accco_{offer['id']}",
                                use_container_width=True, type="primary"):
                    mod = {**offer, "amount": co_amt,
                           "player2": co_pl if co_pl else offer.get("player2","")}
                    _complete(mod, co_amt, presi, "", get_state, set_state)
                    _wa_btn(offer["to_presi"],
                            f"✅ *MMJ LEAGUE — CONTRAOFERTA ACEPTADA*\n\n"
                            f"⚽ *{offer['player']}* → {offer['from_team']}\n"
                            f"💰 {_fmt(co_amt)}\n🎉 Completada!",
                            f"WhatsApp a {offer['to_presi']}")
            with ac2:
                if st.button("🗑️ Rechazar contra", key=f"rejco_{offer['id']}",
                              use_container_width=True):
                    _set_status(offer["id"], "Rechazada", presi, "", get_state, set_state)
                    st.rerun()

        if offer["status"] == "Pendiente":
            if st.button("🗑️ Retirar oferta", key=f"wd_{offer['id']}",
                          use_container_width=True):
                _set_status(offer["id"], "Retirada", presi, "", get_state, set_state)
                _wa_btn(offer["to_presi"],
                        f"🗑️ *MMJ LEAGUE — OFERTA RETIRADA*\n\n"
                        f"⚽ *{offer['player']}* — {presi} retiró su oferta.",
                        f"WhatsApp a {offer['to_presi']}")
                st.rerun()
        st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: NEGOCIACIÓN
# ─────────────────────────────────────────────────────────────────────────────
def _tab_negociacion(presi, players_df, get_state, set_state):
    all_offers = get_state("offers", [])
    active     = [o for o in all_offers
                  if (o["from_presi"] == presi or o["to_presi"] == presi)
                  and o["status"] in ("Pendiente","Contrapropuesta")]
    if not active:
        st.info("No hay negociaciones activas."); return

    labels = [f"{o['player']} · {o['from_team']}→{o['to_team']} "
              f"({MENU_DISPLAY.get(o['tipo'], o['tipo'])})" for o in active]
    idx   = st.selectbox("Negociación activa", range(len(labels)),
                          format_func=lambda i: labels[i], key=f"negsel_{presi}")
    offer = active[idx]
    _deal_card(offer, players_df)

    msgs   = offer.get("messages", [])
    chat_h = '<div class="fc-chat">'
    for m in msgs:
        try: ts = datetime.fromisoformat(m["ts"]).strftime("%d/%m %H:%M")
        except: ts = "—"
        cls = "fc-bubble-me" if m["from"] == presi else "fc-bubble-them"
        chat_h += (f'<div class="{cls}"><div class="fc-bubble-who">{m["from"]} · {ts}</div>'
                   f'<div class="fc-bubble-txt">{m["text"]}</div></div>')
    chat_h += '</div>'
    st.markdown(chat_h, unsafe_allow_html=True)

    new_msg = st.text_area("✉️ Mensaje", placeholder="Escribí tu mensaje...",
                            key=f"negmsg_{offer['id']}")
    if st.button("📨 Enviar mensaje", key=f"negsend_{offer['id']}"):
        if new_msg.strip():
            offers2 = get_state("offers", [])
            for o in offers2:
                if o["id"] == offer["id"]:
                    o.setdefault("messages", []).append(
                        {"from": presi, "text": new_msg.strip(),
                         "ts": datetime.now().isoformat()})
            set_state("offers", offers2)
            other = offer["to_presi"] if offer["from_presi"] == presi else offer["from_presi"]
            st.success("Mensaje enviado.")
            _wa_btn(other,
                    f"💬 *MMJ LEAGUE — NUEVO MENSAJE*\n\n"
                    f"⚽ *{offer['player']}*\n"
                    f"✉️ {presi}: _{new_msg.strip()}_\nEntrá a la app.",
                    f"WhatsApp a {other}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: HISTORIAL
# ─────────────────────────────────────────────────────────────────────────────
def _tab_historial(presi, players_df, get_state):
    completed = get_state("completed_transfers", [])
    mine      = [t for t in completed
                 if t.get("from_presi") == presi or t.get("to_presi") == presi]
    if not mine:
        st.info("Aún no tenés transferencias completadas."); return

    spent  = sum(t["amount"] for t in mine if t.get("to_presi") == presi)
    income = sum(t["amount"] for t in mine if t.get("from_presi") == presi)
    c1, c2, c3 = st.columns(3)
    c1.metric("Transferencias", len(mine))
    c2.metric("Gastado",  _fmt(spent))
    c3.metric("Ingresos", _fmt(income))

    for t in sorted(mine, key=lambda x: x["date"], reverse=True):
        synth = {
            "from_team":      t["from_team"],
            "to_team":        t["to_team"],
            "from_presi":     t.get("from_presi","?"),
            "to_presi":       t.get("to_presi","?"),
            "player":         t["player"],
            "player2":        t.get("player2",""),
            "tipo":           t["tipo"],
            "amount":         t["amount"],
            "duration_label": t.get("duration_label",""),
            "created_at":     t.get("date", datetime.now().isoformat()),
            "status":         "Aceptada",
            "counter_amount": None,
            "is_clausula":    False,
        }
        _deal_card(synth, players_df)

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
def _admin_global(players_df, get_state, set_state):
    st.markdown(
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;'
        f'letter-spacing:4px;color:#e8b84b;margin-bottom:10px;">'
        f'🔐 PANEL ADMINISTRADOR GLOBAL</div>',
        unsafe_allow_html=True,
    )

    with st.expander("⚙️ Controles de ventana", expanded=False):
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            if st.button("🟢 Abrir (30 días)", use_container_width=True):
                set_state("transfer_window_end",
                          (datetime.now() + timedelta(days=30)).isoformat())
                set_state("transfer_window_active", True)
                st.success("Ventana abierta."); st.rerun()
        with a2:
            if st.button("🔴 Cerrar ventana", use_container_width=True):
                set_state("transfer_window_active", False); st.rerun()
        with a3:
            if st.button("🗑️ Borrar ofertas", use_container_width=True):
                set_state("offers", []); st.success("Ofertas eliminadas."); st.rerun()
        with a4:
            if st.button("💥 Reset completo", use_container_width=True):
                set_state("offers", [])
                set_state("completed_transfers", [])
                set_state("budget_overrides", {})
                st.success("Reset completo."); st.rerun()

    ct = get_state("completed_transfers", [])
    with st.expander("💰 Estado financiero — Todos los equipos", expanded=True):
        for pname, pdata in PRESIDENTS.items():
            pc = pdata["color"]
            st.markdown(
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:.88rem;'
                f'letter-spacing:3px;color:{pc};margin:10px 0 6px;'
                f'border-bottom:1px solid {pc}22;padding-bottom:3px;">{pname}</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(len(pdata["teams"]))
            for ci, team in enumerate(pdata["teams"]):
                budget  = _budget(team)
                base_b  = TEAM_BUDGETS.get(team, 0)
                delta   = budget - base_b
                spent   = sum(t["amount"] for t in ct if t.get("from_team") == team)
                income  = sum(t["amount"] for t in ct if t.get("to_team")   == team)
                sq_val  = players_df[players_df["team"] == team]["price"].sum()
                tl      = TEAM_LOGOS.get(team, "")
                tl_h    = (f'<img src="{tl}" style="width:20px;height:20px;object-fit:contain;'
                           f'border-radius:50%;padding:1px;" />') if tl else ""
                bf      = max(0, min(100, int((budget/base_b)*100))) if base_b else 0
                bc      = "#22c55e" if budget >= 0 else "#ef4444"
                dc      = "#22c55e" if delta >= 0 else "#ef4444"
                in_red  = budget < 0
                with cols[ci]:
                    st.markdown(
                        f'<div style="background:{"rgba(239,68,68,.06)" if in_red else "#0c1825"};'
                        f'border:1px solid {"rgba(239,68,68,.3)" if in_red else "rgba(255,255,255,.07)"};'
                        f'border-radius:9px;padding:9px 11px;margin-bottom:5px;">'
                        f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:7px;">'
                        f'{tl_h}<span style="font-size:.68rem;font-weight:800;color:#c0d4e0;">{team}</span>'
                        f'{"<span style=\\'margin-left:auto;color:#ef4444;font-size:.5rem;\\'>🔴</span>" if in_red else ""}'
                        f'</div>'
                        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">'
                        f'<div><div class="fc-stat-val" style="font-size:.66rem;color:{"#ef4444" if in_red else "#e8b84b"};">{_fmt(budget)}</div><div class="fc-stat-lbl">Presup.</div></div>'
                        f'<div><div class="fc-stat-val" style="font-size:.66rem;color:#3b82f6;">{_fmt(sq_val)}</div><div class="fc-stat-lbl">Plantilla</div></div>'
                        f'<div><div class="fc-stat-val" style="font-size:.62rem;color:#f97316;">{_fmt(spent) if spent else "—"}</div><div class="fc-stat-lbl">Gastado</div></div>'
                        f'<div><div class="fc-stat-val" style="font-size:.62rem;color:#22c55e;">{_fmt(income) if income else "—"}</div><div class="fc-stat-lbl">Ingresos</div></div>'
                        f'</div>'
                        f'<div class="fc-bar"><div class="fc-bar-fill" style="width:{bf}%;background:{bc};"></div></div>'
                        f'<div style="font-size:.44rem;color:{dc};margin-top:2px;font-weight:700;">'
                        f'{"+" if delta>=0 else ""}{_fmt(delta)} vs inicial</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    all_offers = get_state("offers", [])
    completed  = get_state("completed_transfers", [])
    active_all = [o for o in all_offers if o["status"] in ("Pendiente","Contrapropuesta")]

    with st.expander(f"📋 Ofertas activas ({len(active_all)})", expanded=False):
        if not active_all: st.info("No hay ofertas activas.")
        for o in sorted(active_all, key=lambda x: x["created_at"], reverse=True):
            _deal_card(o, players_df)

    with st.expander(f"✅ Transferencias completadas ({len(completed)})", expanded=False):
        if not completed: st.info("Ninguna aún.")
        for t in sorted(completed, key=lambda x: x["date"], reverse=True):
            synth = {
                "from_team": t["from_team"], "to_team": t["to_team"],
                "from_presi": t.get("from_presi","?"), "to_presi": t.get("to_presi","?"),
                "player": t["player"], "player2": t.get("player2",""),
                "tipo": t["tipo"], "amount": t["amount"],
                "duration_label": t.get("duration_label",""),
                "created_at": t.get("date", datetime.now().isoformat()),
                "status": "Aceptada", "counter_amount": None, "is_clausula": False,
            }
            _deal_card(synth, players_df)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def render_fichajes(players_df, get_state, set_state, page_header, window_open):
    st.session_state["_ct_cache"] = get_state("completed_transfers", [])
    st.markdown(CSS, unsafe_allow_html=True)
    page_header("OFICINA DE FICHAJES",
                "Sistema de transferencias MMJ League — Modelo FC/EA Sports")

    mode = st.radio("Modo", ["🧑‍💼 Oficina privada", "🔐 Admin global"],
                    horizontal=True, label_visibility="collapsed")

    if mode == "🔐 Admin global":
        _admin_global(players_df, get_state, set_state); return

    presi       = st.selectbox("Presidente", ["JNKA","MATI","MAXI"],
                                key="presi_sel_office")
    presi_color = PRESIDENTS[presi]["color"]
    my_teams    = PRESIDENTS[presi]["teams"]

    all_offers  = get_state("offers", [])
    pending_in  = [o for o in all_offers
                   if o["to_presi"] == presi and o["status"] == "Pendiente"]
    counter_in  = [o for o in all_offers
                   if o["from_presi"] == presi and o["status"] == "Contrapropuesta"]
    notif_total = len(pending_in) + len(counter_in)

    # President header
    logos_h = ""
    for t in my_teams:
        lurl = TEAM_LOGOS.get(t, "")
        bud  = _budget(t)
        red  = bud < 0
        if lurl:
            logos_h += (
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">'
                f'<img src="{lurl}" style="width:36px;height:36px;object-fit:contain;'
                f'border-radius:50%;border:2px solid {"#ef4444" if red else "rgba(255,255,255,.1)"};" />'
                f'<span style="font-size:.5rem;color:{"#ef4444" if red else "#8aa0b0"};'
                f'font-weight:700;">{t}</span>'
                f'<span style="font-size:.46rem;font-family:\'Space Mono\',monospace;'
                f'color:{"#ef4444" if red else "#e8b84b"};">{_fmt(bud)}</span>'
                f'</div>'
            )

    notif_h = (f'<div class="fc-notif"><span>🔔 {notif_total} notif.</span></div>'
               if notif_total > 0 else "")

    st.markdown(
        f'<div class="fc-presi-bar" style="background:{presi_color}0d;'
        f'border:1px solid {presi_color}28;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
        f'letter-spacing:4px;color:{presi_color};">{presi}</div>'
        f'<div style="flex:1;display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;">'
        f'{logos_h}</div>{notif_h}</div>',
        unsafe_allow_html=True,
    )

    t1, t2, t3, t4, t5 = st.tabs([
        "📤 Nueva Oferta",
        f"📥 Bandeja{'  🔴' if pending_in else ''}",
        f"📋 Mis Ofertas{'  🟣' if counter_in else ''}",
        "💬 Negociación",
        "📊 Historial",
    ])
    with t1: _tab_nueva(presi, players_df, get_state, set_state, window_open)
    with t2: _tab_bandeja(presi, players_df, get_state, set_state)
    with t3: _tab_mis_ofertas(presi, players_df, get_state, set_state)
    with t4: _tab_negociacion(presi, players_df, get_state, set_state)
    with t5: _tab_historial(presi, players_df, get_state)
