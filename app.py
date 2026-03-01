import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
import io

st.set_page_config(
    page_title="MMJ League — Mercado",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700;800;900&family=DM+Sans:wght@300;400;600&family=Space+Mono:wght@400;700&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #060a0f; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
  header[data-testid="stHeader"] { background: rgba(6,10,15,0.95); }

  [data-testid="stMetric"] {
    background: #0d1520;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 18px !important;
    border-top: 2px solid #e8b84b;
  }
  [data-testid="stMetricValue"] { color: #e8b84b !important; font-family: 'Space Mono', monospace; font-size: 1.2rem !important; }
  [data-testid="stMetricLabel"] { color: #5a7080 !important; font-size: 0.68rem !important; text-transform: uppercase; letter-spacing: 2px; }

  .page-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    letter-spacing: 4px;
    color: #e8b84b;
    margin-bottom: 2px;
  }
  .page-sub { font-size: 0.75rem; color: #5a7080; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; }

  /* ── Player card ── completely rewritten to avoid Streamlit column overflow ── */
  .player-card {
    background: linear-gradient(160deg, #0d1b2a 0%, #0a1a28 60%, #071018 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 10px;
    transition: border-color 0.2s, transform 0.15s;
    position: relative;
    width: 100%;
    box-sizing: border-box;
  }
  .player-card:hover { border-color: rgba(232,184,75,0.4); transform: translateY(-2px); }

  /* Use CSS Grid to avoid flex overflow issues inside Streamlit columns */
  .player-card-header {
    padding: 12px 12px 8px 12px;
    display: grid;
    grid-template-columns: 56px 1fr;
    gap: 10px;
    align-items: start;
    width: 100%;
    box-sizing: border-box;
  }
  .player-photo {
    width: 56px; height: 56px;
    border-radius: 50%; object-fit: cover;
    border: 2px solid rgba(232,184,75,0.4);
    background: #0a1520;
    display: block;
  }
  .player-info {
    overflow: hidden;
    min-width: 0;
    width: 100%;
  }
  .player-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.88rem;
    font-weight: 800;
    color: #f0f4f8;
    line-height: 1.2;
    margin-bottom: 3px;
    /* Key fix: clip text that doesn't fit */
    display: block;
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .player-pos-badge {
    display: inline-block;
    font-size: 0.55rem; font-weight: 900; letter-spacing: 1.5px;
    text-transform: uppercase; padding: 1px 5px; border-radius: 3px;
    margin-right: 3px; vertical-align: middle;
  }
  .player-nat {
    display: block;
    margin-top: 3px; font-size: 0.68rem; color: #7a9db0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .player-stats-bar {
    background: rgba(255,255,255,0.03);
    border-top: 1px solid rgba(255,255,255,0.05);
    padding: 7px 12px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
  }
  .player-stat { text-align: center; }
  .player-stat-val {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.95rem; font-weight: 900; color: #e8b84b; line-height: 1;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .player-stat-lbl { font-size: 0.5rem; color: #5a8090; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

  /* Loan badge */
  .loan-badge { position: absolute; top: 10px; right: 10px; padding: 2px 7px; border-radius: 10px; font-size: 0.6rem; font-weight: 900; letter-spacing: 0.5px; }
  .loan-corta { background: rgba(249,115,22,0.18); border: 1px solid rgba(249,115,22,0.4); color: #f97316; }
  .loan-larga { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }

  .price-gold { color: #e8b84b; font-family: 'Space Mono', monospace; font-weight: 700; }
  .price-green { color: #22c55e; font-family: 'Space Mono', monospace; }

  [data-testid="stSidebar"] { background: #0d1520 !important; border-right: 1px solid rgba(255,255,255,0.07); }
  [data-testid="stSidebar"] * { color: #e2eaf4 !important; }

  hr { border-color: rgba(255,255,255,0.07) !important; }

  .player-row {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 8px 14px; margin-bottom: 5px;
    transition: border-color 0.15s;
  }
  .player-row:hover { border-color: rgba(232,184,75,0.25); }

  .badge-1s { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-2s { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-cc { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.35); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-cl { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }

  /* Transfer window styles */
  .transfer-card {
    background: linear-gradient(160deg, #0d1b2a, #0a1520);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    transition: all 0.2s;
  }
  .transfer-card:hover { border-color: rgba(232,184,75,0.3); }

  .presi-jnka { color: #e8b84b; }
  .presi-mati { color: #3b82f6; }
  .presi-maxi { color: #a78bfa; }

  .offer-pending { border-left: 3px solid #f59e0b; }
  .offer-accepted { border-left: 3px solid #22c55e; }
  .offer-rejected { border-left: 3px solid #ef4444; }

  /* Timer styles */
  .timer-container {
    background: linear-gradient(135deg, #0d1520, #111827);
    border: 2px solid #e8b84b;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 20px;
  }
  .timer-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 3px;
    color: #5a7080;
    margin-bottom: 8px;
  }
  .timer-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.5rem;
    font-weight: 700;
    color: #e8b84b;
    letter-spacing: 2px;
  }
  .timer-expired {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #ef4444;
    letter-spacing: 4px;
  }
</style>
""", unsafe_allow_html=True)


# ── STORAGE FILE ─────────────────────────────────────────────────────────────
STORAGE_FILE = "mmj_data.json"

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_storage(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_state(key, default=None):
    data = load_storage()
    return data.get(key, default)

def set_state(key, value):
    data = load_storage()
    data[key] = value
    save_storage(data)


# ── Helpers de imágenes ──────────────────────────────────────────────────────
def get_flag_url(code):
    if not code:
        return ""
    return f"https://flagcdn.com/28x21/{code}.png"

def get_player_photo(player_name, sofifa_id):
    safe_name = player_name.encode('ascii', 'ignore').decode('ascii')
    initials = "+".join(safe_name.split()[:2]) if safe_name else "PL"
    if sofifa_id and sofifa_id != 0:
        s = str(sofifa_id)
        parts = s[:-3] + "/" + s[-3:] if len(s) > 3 else s
        sofifa_url = f"https://cdn.sofifa.net/players/{parts}/25_240.png"
        return f"https://images.weserv.nl/?url={sofifa_url}&w=120&h=120&fit=cover&mask=circle"
    return f"https://ui-avatars.com/api/?name={initials}&background=1a2a3a&color=f0c040&size=128&bold=true"


# ── PLAYER_DATA ───────────────────────────────────────────────────────────────
PLAYER_DATA = {
    "U. Simón":            {"pos": "GK",  "nat": "es", "nat_name": "España",        "sofifa": 230869},
    "J. Musiala":          {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 256790},
    "Rodrygo":             {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 243812},
    "J. Brandt":           {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 212194},
    "P. Dybala":           {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 211110},
    "K. Mbappé":           {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 231747},
    "P. Hincapié":         {"pos": "DEF", "nat": "ec", "nat_name": "Ecuador",        "sofifa": 256197},
    "N. Madueke":          {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 254796},
    "J. Enciso":           {"pos": "FWD", "nat": "py", "nat_name": "Paraguay",       "sofifa": 255434},
    "Y. Asprilla":         {"pos": "FWD", "nat": "co", "nat_name": "Colombia",       "sofifa": 271464},
    "Ederson":             {"pos": "GK",  "nat": "br", "nat_name": "Brasil",         "sofifa": 210257},
    "J. Tah":              {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 213331},
    "L. Messi":            {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 158023},
    "E. Haaland":          {"pos": "FWD", "nat": "no", "nat_name": "Noruega",        "sofifa": 239085},
    "J. Bynoe-Gittens":    {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 266032},
    "G. Puerta":           {"pos": "MID", "nat": "co", "nat_name": "Colombia",       "sofifa": 273827},
    "O. Bobb":             {"pos": "MID", "nat": "no", "nat_name": "Noruega",        "sofifa": 277295},
    "J. Durán":            {"pos": "FWD", "nat": "co", "nat_name": "Colombia",       "sofifa": 247172},
    "G. Mamardashvili":    {"pos": "GK",  "nat": "ge", "nat_name": "Georgia",        "sofifa": 262621},
    "F. Kessié":           {"pos": "MID", "nat": "ci", "nat_name": "Costa de Marfil","sofifa": 230938},
    "Raphinha":            {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 233419},
    "M. Llorente":         {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 226161},
    "J. Maddison":         {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 220697},
    "Moleiro":             {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 264388},
    "Nico González":       {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 255069},
    "Fermín":              {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 277179},
    "Marc Guiu":           {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 278813},
    "N. Pope":             {"pos": "GK",  "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 203841},
    "R. Andrich":          {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 212242},
    "R. Mahrez":           {"pos": "FWD", "nat": "dz", "nat_name": "Argelia",        "sofifa": 204485},
    "Nico Williams":       {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 256516},
    "D. Malen":            {"pos": "FWD", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 231447},
    "R. Gravenberch":      {"pos": "MID", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 246104},
    "T. Lamptey":          {"pos": "DEF", "nat": "gh", "nat_name": "Ghana",          "sofifa": 242418},
    "A. Pavlovic":         {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 275298},
    "K. Gordon":           {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 260406},
    "G. Ochoa":            {"pos": "GK",  "nat": "mx", "nat_name": "México",         "sofifa": 140233},
    "João Cancelo":        {"pos": "DEF", "nat": "pt", "nat_name": "Portugal",       "sofifa": 210514},
    "H. Kane":             {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 202126},
    "M. Olise":            {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 247827},
    "C. Lukeba":           {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 262138},
    "T. Gulliksen":        {"pos": "FWD", "nat": "no", "nat_name": "Noruega",        "sofifa": 247025},
    "R. Bardghji":         {"pos": "FWD", "nat": "se", "nat_name": "Suecia",         "sofifa": 265600},
    "M. Maignan":          {"pos": "GK",  "nat": "fr", "nat_name": "Francia",        "sofifa": 215698},
    "N. Schlotterbeck":    {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 257710},
    "F. Torres":           {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 241461},
    "L. Díaz":             {"pos": "FWD", "nat": "co", "nat_name": "Colombia",       "sofifa": 241084},
    "A. Davies":           {"pos": "DEF", "nat": "ca", "nat_name": "Canadá",         "sofifa": 234396},
    "L. Romero":           {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 258467},
    "A. Scott":            {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 261299},
    "Pau Cubarsí":         {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 278046},
    "J. Duranville":       {"pos": "FWD", "nat": "be", "nat_name": "Bélgica",        "sofifa": 262105},
    "M. Neuer":            {"pos": "GK",  "nat": "de", "nat_name": "Alemania",       "sofifa": 167495},
    "E. Tapsoba":          {"pos": "DEF", "nat": "bf", "nat_name": "Burkina Faso",   "sofifa": 247263},
    "Pedri":               {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 251854},
    "L. Sané":             {"pos": "FWD", "nat": "de", "nat_name": "Alemania",       "sofifa": 222492},
    "A. Hložek":           {"pos": "FWD", "nat": "cz", "nat_name": "Rep. Checa",     "sofifa": 246618},
    "Fábio Carvalho":      {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 256725},
    "Y. Eduardo":          {"pos": "FWD", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 0},
    "O. Diomande":         {"pos": "DEF", "nat": "ci", "nat_name": "Costa de Marfil","sofifa": 270531},
    "L. Hrádecký":         {"pos": "GK",  "nat": "fi", "nat_name": "Finlandia",      "sofifa": 190941},
    "R. James":            {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 238074},
    "D. Szoboszlai":       {"pos": "MID", "nat": "hu", "nat_name": "Hungría",        "sofifa": 236772},
    "J. Álvarez":          {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 246191},
    "S. Gnabry":           {"pos": "FWD", "nat": "de", "nat_name": "Alemania",       "sofifa": 206113},
    "H. Elliott":          {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 261275},
    "F. Pellistri":        {"pos": "FWD", "nat": "uy", "nat_name": "Uruguay",        "sofifa": 253283},
    "Marc Casadó":         {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 272600},
    "B. Domínguez":        {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 269558},
    "G. Rulli":            {"pos": "GK",  "nat": "ar", "nat_name": "Argentina",      "sofifa": 215316},
    "N. Barella":          {"pos": "MID", "nat": "it", "nat_name": "Italia",         "sofifa": 224232},
    "H. Son":              {"pos": "FWD", "nat": "kr", "nat_name": "Corea del Sur",  "sofifa": 200104},
    "Vini Jr.":            {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 238794},
    "Marquinhos":          {"pos": "DEF", "nat": "br", "nat_name": "Brasil",         "sofifa": 207865},
    "R. Lewis":            {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 271574},
    "E. Millot":           {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 252259},
    "V. Barco":            {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 263370},
    "B. Doak":             {"pos": "FWD", "nat": "gb-sct","nat_name": "Escocia",     "sofifa": 266815},
    "J. Oblak":            {"pos": "GK",  "nat": "si", "nat_name": "Eslovenia",      "sofifa": 200389},
    "R. Sterling":         {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 202652},
    "İ. Gündoğan":         {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 186942},
    "K. Kvaratskhelia":    {"pos": "FWD", "nat": "ge", "nat_name": "Georgia",        "sofifa": 247635},
    "X. Simons":           {"pos": "MID", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 245367},
    "L. Badé":             {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 255106},
    "P. Wanner":           {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 266237},
    "P. Brunner":          {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 274126},
    "A. Lopes":            {"pos": "GK",  "nat": "pt", "nat_name": "Portugal",       "sofifa": 199482},
    "A. Rüdiger":          {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 205452},
    "F. Valverde":         {"pos": "MID", "nat": "uy", "nat_name": "Uruguay",        "sofifa": 239053},
    "T. Kubo":             {"pos": "FWD", "nat": "jp", "nat_name": "Japón",          "sofifa": 237681},
    "K. Benzema":          {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 165153},
    "J. Doku":             {"pos": "FWD", "nat": "be", "nat_name": "Bélgica",        "sofifa": 246420},
    "Yeremy Pino":         {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 259377},
    "A. Gray":             {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 270208},
    "A. Gómez":            {"pos": "MID", "nat": "co", "nat_name": "Colombia",       "sofifa": 266674},
    "P. Gulácsi":          {"pos": "GK",  "nat": "hu", "nat_name": "Hungría",        "sofifa": 185122},
    "A. Rabiot":           {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 210008},
    "M. Depay":            {"pos": "FWD", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 202556},
    "J. Koundé":           {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 241486},
    "A. Balde":            {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 253578},
    "A. Ezzalzouli":       {"pos": "FWD", "nat": "ma", "nat_name": "Marruecos",      "sofifa": 264432},
    "D. Moreira":          {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 270039},
    "L. Miley":            {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 274246},
    "M. ter Stegen":       {"pos": "GK",  "nat": "de", "nat_name": "Alemania",       "sofifa": 192448},
    "V. van Dijk":         {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 203376},
    "L. Modrić":           {"pos": "MID", "nat": "hr", "nat_name": "Croacia",        "sofifa": 177003},
    "Rafael Leão":         {"pos": "FWD", "nat": "pt", "nat_name": "Portugal",       "sofifa": 241721},
    "J. Frimpong":         {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 253149},
    "K. Coman":            {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 213345},
    "P. Barrios":          {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 272449},
    "N. Zalewski":         {"pos": "MID", "nat": "pl", "nat_name": "Polonia",        "sofifa": 262113},
    "Á. Alarcón":          {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 0},
    "G. Scalvini":         {"pos": "DEF", "nat": "it", "nat_name": "Italia",         "sofifa": 265188},
    "T. Courtois":         {"pos": "GK",  "nat": "be", "nat_name": "Bélgica",        "sofifa": 192119},
    "Kim Min Jae":         {"pos": "DEF", "nat": "kr", "nat_name": "Corea del Sur",  "sofifa": 237086},
    "F. de Jong":          {"pos": "MID", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 228702},
    "T. Alexander-Arnold": {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 231281},
    "H. Ekitike":          {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 257289},
    "C. Medina":           {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 261082},
    "Afonso Moreira":      {"pos": "DEF", "nat": "pt", "nat_name": "Portugal",       "sofifa": 276901},
    "M. Tel":              {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 268421},
    "A. Onana":            {"pos": "GK",  "nat": "cm", "nat_name": "Camerún",        "sofifa": 226753},
    "A. Laporte":          {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 212218},
    "V. Osimhen":          {"pos": "FWD", "nat": "ng", "nat_name": "Nigeria",        "sofifa": 232293},
    "R. Araujo":           {"pos": "DEF", "nat": "uy", "nat_name": "Uruguay",        "sofifa": 246340},
    "João Félix":          {"pos": "FWD", "nat": "pt", "nat_name": "Portugal",       "sofifa": 242444},
    "Stefan Bajcetic":     {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 271975},
    "L. Abada":            {"pos": "FWD", "nat": "il", "nat_name": "Israel",         "sofifa": 263377},
    "C. Bradley":          {"pos": "DEF", "nat": "gg", "nat_name": "Irlanda del Norte","sofifa": 264298},
    "C. Cassano":          {"pos": "MID", "nat": "it", "nat_name": "Italia",         "sofifa": 0},
    "Alisson":             {"pos": "GK",  "nat": "br", "nat_name": "Brasil",         "sofifa": 212831},
    "Casemiro":            {"pos": "MID", "nat": "br", "nat_name": "Brasil",         "sofifa": 200145},
    "C. Nkunku":           {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 232411},
    "Rúben Dias":          {"pos": "DEF", "nat": "pt", "nat_name": "Portugal",       "sofifa": 239477},
    "Neymar Jr":           {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 190871},
    "G. Reyna":            {"pos": "MID", "nat": "us", "nat_name": "EE.UU.",         "sofifa": 245541},
    "B. Castro":           {"pos": "MID", "nat": "co", "nat_name": "Colombia",       "sofifa": 271549},
    "O. Cortés":           {"pos": "MID", "nat": "co", "nat_name": "Colombia",       "sofifa": 266673},
    "K. Páez":             {"pos": "MID", "nat": "ec", "nat_name": "Ecuador",        "sofifa": 274559},
    "K. Navas":            {"pos": "GK",  "nat": "cr", "nat_name": "Costa Rica",     "sofifa": 0},
    "M. de Ligt":          {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 235243},
    "N. Okafor":           {"pos": "FWD", "nat": "ch", "nat_name": "Suiza",          "sofifa": 242530},
    "J. Bellingham":       {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 252371},
    "T. Baldanzi":         {"pos": "MID", "nat": "it", "nat_name": "Italia",         "sofifa": 269312},
    "Talles Magno":        {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 0},
    "E. Mbappé":           {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 278172},
    "I. Babadi":           {"pos": "MID", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 277465},
    "Y. Bounou":           {"pos": "GK",  "nat": "ma", "nat_name": "Marruecos",      "sofifa": 209981},
    "N. Süle":             {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 212190},
    "Diogo Jota":          {"pos": "FWD", "nat": "pt", "nat_name": "Portugal",       "sofifa": 0},
    "M. Ødegaard":         {"pos": "MID", "nat": "no", "nat_name": "Noruega",        "sofifa": 222665},
    "A. Meret":            {"pos": "GK",  "nat": "it", "nat_name": "Italia",         "sofifa": 225116},
    "O. Dembélé":          {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 231443},
    "Gonçalo Inácio":      {"pos": "DEF", "nat": "pt", "nat_name": "Portugal",       "sofifa": 257179},
    "S. Magassa":          {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 275102},
    "R. Cherki":           {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 251570},
    "B. Norton-Cuffy":     {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 260653},
    "G. Donnarumma":       {"pos": "GK",  "nat": "it", "nat_name": "Italia",         "sofifa": 230621},
    "Éder Militão":        {"pos": "DEF", "nat": "br", "nat_name": "Brasil",         "sofifa": 240130},
    "Á. Di María":         {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 183898},
    "Rodri":               {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 231866},
    "J. Grealish":         {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 206517},
    "N. Rovella":          {"pos": "MID", "nat": "it", "nat_name": "Italia",         "sofifa": 255001},
    "D. Udogie":           {"pos": "DEF", "nat": "it", "nat_name": "Italia",         "sofifa": 259583},
    "D. Washington":       {"pos": "MID", "nat": "us", "nat_name": "EE.UU.",         "sofifa": 0},
    "Ângelo":              {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 272829},
    "E. Martínez":         {"pos": "GK",  "nat": "ar", "nat_name": "Argentina",      "sofifa": 202811},
    "S. Milinković-Savić": {"pos": "MID", "nat": "rs", "nat_name": "Serbia",         "sofifa": 223848},
    "Bruno Fernandes":     {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 212198},
    "S. Chukwueze":        {"pos": "FWD", "nat": "ng", "nat_name": "Nigeria",        "sofifa": 246172},
    "R. Lewandowski":      {"pos": "FWD", "nat": "pl", "nat_name": "Polonia",        "sofifa": 188545},
    "D. Alaba":            {"pos": "DEF", "nat": "at", "nat_name": "Austria",        "sofifa": 197445},
    "Antony":              {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 255475},
    "R. Højlund":          {"pos": "FWD", "nat": "dk", "nat_name": "Dinamarca",      "sofifa": 259399},
    "T. Pembélé":          {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 257270},
    "Y. Moukoko":          {"pos": "FWD", "nat": "de", "nat_name": "Alemania",       "sofifa": 240833},
    "Matheus França":      {"pos": "MID", "nat": "br", "nat_name": "Brasil",         "sofifa": 265420},
    "M. Flekken":          {"pos": "GK",  "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 211738},
    "Brahim":              {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 231410},
    "S. Mané":             {"pos": "FWD", "nat": "sn", "nat_name": "Senegal",        "sofifa": 208722},
    "E. Fernández":        {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 247090},
    "Bernardo Silva":      {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 218667},
    "C. Palmer":           {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 257534},
    "A. Velasco":          {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 252238},
    "K. Yıldız":           {"pos": "FWD", "nat": "tr", "nat_name": "Turquía",        "sofifa": 277954},
    "S. Charles":          {"pos": "MID", "nat": "gg", "nat_name": "Irlanda del Norte","sofifa": 276695},
    "W. Szczęsny":         {"pos": "GK",  "nat": "pl", "nat_name": "Polonia",        "sofifa": 186153},
    "F. Tomori":           {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 232756},
    "J. Kimmich":          {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 212622},
    "L. Martínez":         {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 231478},
    "Gavi":                {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 264240},
    "Vitor Roque":         {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 0},
    "Héctor Fort":         {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 278923},
    "I. Fresneda":         {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 266253},
    "G. Kobel":            {"pos": "GK",  "nat": "ch", "nat_name": "Suiza",          "sofifa": 235073},
    "K. Trippier":         {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 186345},
    "G. Martinelli":       {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 251566},
    "K. Havertz":          {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 235790},
    "L. Goretzka":         {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 209658},
    "F. Chiesa":           {"pos": "FWD", "nat": "it", "nat_name": "Italia",         "sofifa": 235805},
    "Ansu Fati":           {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 253004},
    "A. Kalimuendo":       {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 253444},
    "S. Pafundi":          {"pos": "MID", "nat": "it", "nat_name": "Italia",         "sofifa": 271575},
    "D. Doué":             {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 271421},
    "J. Pickford":         {"pos": "GK",  "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 204935},
    "Sergio Ramos":        {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 0},
    "H. Lozano":           {"pos": "FWD", "nat": "mx", "nat_name": "México",         "sofifa": 221992},
    "K. Adeyemi":          {"pos": "FWD", "nat": "de", "nat_name": "Alemania",       "sofifa": 251852},
    "M. Hummels":          {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 0},
    "António Silva":       {"pos": "DEF", "nat": "pt", "nat_name": "Portugal",       "sofifa": 270086},
    "M. Thiaw":            {"pos": "DEF", "nat": "de", "nat_name": "Alemania",       "sofifa": 256261},
    "C. Chukwuemeka":      {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 259356},
    "B. El Khannouss":     {"pos": "MID", "nat": "ma", "nat_name": "Marruecos",      "sofifa": 257504},
    "Y. Sommer":           {"pos": "GK",  "nat": "ch", "nat_name": "Suiza",          "sofifa": 177683},
    "T. Hernández":        {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 232656},
    "B. Saka":             {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 246669},
    "K. De Bruyne":        {"pos": "MID", "nat": "be", "nat_name": "Bélgica",        "sofifa": 192985},
    "M. Salah":            {"pos": "FWD", "nat": "eg", "nat_name": "Egipto",         "sofifa": 209331},
    "K. Casteels":         {"pos": "GK",  "nat": "be", "nat_name": "Bélgica",        "sofifa": 192984},
    "J. Castrop":          {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 264194},
    "B. Brobbey":          {"pos": "FWD", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 258513},
    "M. Soulé":            {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 265695},
    "W. Zaïre-Emery":      {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 270673},
    "A. Ramsdale":         {"pos": "GK",  "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 233934},
    "K. Walker":           {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 188377},
    "M. Diaby":            {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 241852},
    "C. Gakpo":            {"pos": "FWD", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 242516},
    "P. Foden":            {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 237692},
    "A. Lafont":           {"pos": "GK",  "nat": "fr", "nat_name": "Francia",        "sofifa": 231691},
    "B. Barcola":          {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 264652},
    "Q. Sullivan":         {"pos": "MID", "nat": "us", "nat_name": "EE.UU.",         "sofifa": 260547},
    "Iker Bravo":          {"pos": "FWD", "nat": "es", "nat_name": "España",         "sofifa": 265194},
    "T. Land":             {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 275411},
    "É. Mendy":            {"pos": "GK",  "nat": "sn", "nat_name": "Senegal",        "sofifa": 234642},
    "A. Griezmann":        {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 194765},
    "L. Paqueta":          {"pos": "MID", "nat": "br", "nat_name": "Brasil",         "sofifa": 233927},
    "Grimaldo":            {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 210035},
    "A. Hakimi":           {"pos": "DEF", "nat": "ma", "nat_name": "Marruecos",      "sofifa": 235212},
    "M. Rashford":         {"pos": "FWD", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 231677},
    "A. Correa":           {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 214997},
    "Sávio":               {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 270409},
    "A. Richardson":       {"pos": "MID", "nat": "ma", "nat_name": "Marruecos",      "sofifa": 262236},
    "C. Echeverri":        {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 276528},
    "J. Hato":             {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 272978},
    "Diogo Costa":         {"pos": "GK",  "nat": "pt", "nat_name": "Portugal",       "sofifa": 234577},
    "Gabriel":             {"pos": "DEF", "nat": "br", "nat_name": "Brasil",         "sofifa": 232580},
    "Cristiano Ronaldo":   {"pos": "FWD", "nat": "pt", "nat_name": "Portugal",       "sofifa": 0},
    "A. Robertson":        {"pos": "DEF", "nat": "gb-sct","nat_name": "Escocia",     "sofifa": 216267},
    "Peter":               {"pos": "MID", "nat": "br", "nat_name": "Brasil",         "sofifa": 266136},
    "K. Mainoo":           {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 269136},
    "V. Carboni":          {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 272602},
    "A. van Axel Dongen":  {"pos": "DEF", "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 266448},
    "H. Lloris":           {"pos": "GK",  "nat": "fr", "nat_name": "Francia",        "sofifa": 167948},
    "Gabriel Jesús":       {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 230666},
    "N. Kanté":            {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 215914},
    "G. Xhaka":            {"pos": "MID", "nat": "ch", "nat_name": "Suiza",          "sofifa": 199503},
    "S. Haller":           {"pos": "FWD", "nat": "ci", "nat_name": "Costa de Marfil","sofifa": 205693},
    "A. Garnacho":         {"pos": "FWD", "nat": "ar", "nat_name": "Argentina",      "sofifa": 268438},
    "M. Kerkez":           {"pos": "DEF", "nat": "hu", "nat_name": "Hungría",        "sofifa": 260908},
    "M. Del Blanco":       {"pos": "DEF", "nat": "ar", "nat_name": "Argentina",      "sofifa": 273028},
    "Y. Bonny":            {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 259565},
    "Alex Remiro":         {"pos": "GK",  "nat": "es", "nat_name": "España",         "sofifa": 227127},
    "D. Silva":            {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 0},
    "D. Rice":             {"pos": "MID", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 234378},
    "R. Kolo Muani":       {"pos": "FWD", "nat": "fr", "nat_name": "Francia",        "sofifa": 237679},
    "F. Wirtz":            {"pos": "MID", "nat": "de", "nat_name": "Alemania",       "sofifa": 256630},
    "A. Güler":            {"pos": "MID", "nat": "tr", "nat_name": "Turquía",        "sofifa": 264309},
    "M. Caicedo":          {"pos": "MID", "nat": "ec", "nat_name": "Ecuador",        "sofifa": 256079},
    "Newerton":            {"pos": "FWD", "nat": "br", "nat_name": "Brasil",         "sofifa": 277194},
    "E. Ferguson":         {"pos": "FWD", "nat": "ie", "nat_name": "Irlanda",        "sofifa": 259608},
    "A. Bastoni":          {"pos": "DEF", "nat": "it", "nat_name": "Italia",         "sofifa": 239685},
    "A. Isak":             {"pos": "FWD", "nat": "se", "nat_name": "Suecia",         "sofifa": 232079},
    "A. Mac Allister":     {"pos": "MID", "nat": "ar", "nat_name": "Argentina",      "sofifa": 246801},
    "H. Çalhanoğlu":       {"pos": "MID", "nat": "tr", "nat_name": "Turquía",        "sofifa": 213348},
    "D. Carvajal":         {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 211361},
    "Bremer":              {"pos": "DEF", "nat": "br", "nat_name": "Brasil",         "sofifa": 230678},
    "David Raya":          {"pos": "GK",  "nat": "es", "nat_name": "España",         "sofifa": 218945},
    "Mikel Merino":        {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 228906},
    "Palhinha":            {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 222006},
    "A. Tchouaméni":       {"pos": "MID", "nat": "fr", "nat_name": "Francia",        "sofifa": 246165},
    "J. Stones":           {"pos": "DEF", "nat": "gb-eng","nat_name": "Inglaterra",  "sofifa": 199202},
    "B. Verbruggen":       {"pos": "GK",  "nat": "nl", "nat_name": "Países Bajos",   "sofifa": 252520},
    "De Gea":              {"pos": "GK",  "nat": "es", "nat_name": "España",         "sofifa": 193080},
    "P. Gonçalves":        {"pos": "MID", "nat": "pt", "nat_name": "Portugal",       "sofifa": 235596},
    "D. Olmo":             {"pos": "MID", "nat": "es", "nat_name": "España",         "sofifa": 236096},
    "Bruno Guimarães":     {"pos": "MID", "nat": "br", "nat_name": "Brasil",         "sofifa": 236580},
    "G. Di Lorenzo":       {"pos": "DEF", "nat": "it", "nat_name": "Italia",         "sofifa": 218627},
    "D. Berardi":          {"pos": "FWD", "nat": "it", "nat_name": "Italia",         "sofifa": 190043},
    "L. Hernández":        {"pos": "DEF", "nat": "fr", "nat_name": "Francia",        "sofifa": 212190},
    "I. Provedel":         {"pos": "GK",  "nat": "it", "nat_name": "Italia",         "sofifa": 213527},
    "G. Vicario":          {"pos": "GK",  "nat": "it", "nat_name": "Italia",         "sofifa": 215583},
    "D. Livaković":        {"pos": "GK",  "nat": "hr", "nat_name": "Croacia",        "sofifa": 232080},
    "A. Lookman":          {"pos": "FWD", "nat": "ng", "nat_name": "Nigeria",        "sofifa": 238519},
    "I. Bennacer":         {"pos": "MID", "nat": "dz", "nat_name": "Argelia",        "sofifa": 223741},
    "A. Bastoni":          {"pos": "DEF", "nat": "it", "nat_name": "Italia",         "sofifa": 239685},
}

# ── TEAM DATA ─────────────────────────────────────────────────────────────────
TEAM_LOGOS = {
    "LAFC": "https://a.espncdn.com/guid/090bf04b-bafb-ac27-0cc5-3fee8a7375ca/logos/primary_logo_on_black_color.png",
    "SEA":  "https://a.espncdn.com/guid/c847331a-0291-a79c-5b8e-22416f8fe26a/logos/primary_logo_on_black_color.png",
    "MIN":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/17362.png",
    "VAN":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9727.png",
    "COL":  "https://a.espncdn.com/i/teamlogos/soccer/500/184.png",
    "NHS":  "https://a.espncdn.com/i/teamlogos/soccer/500/18986.png",
    "NSH":  "https://a.espncdn.com/i/teamlogos/soccer/500/18986.png",
    "CLB":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/183.png",
    "SDFC": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/22529.png",
    "ATX":  "https://a.espncdn.com/guid/ea2b097a-74d8-3164-b55e-7fd490d63b46/logos/primary_logo_on_primary_color.png",
    "CHI":  "https://a.espncdn.com/i/teamlogos/soccer/500/182.png",
    "NE":   "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/189.png",
    "ORL":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/12011.png",
    "LA":   "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/187.png",
    "SKC":  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Sporting_Kansas_City_logo.svg/1280px-Sporting_Kansas_City_logo.svg.png",
    "CLT":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/21300.png&h=200&w=200",
    "MIA":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/20232.png",
    "NYC":  "https://a.espncdn.com/guid/d902d6f8-8673-29e3-15d9-3ef4c12ce9d0/logos/primary_logo_on_primary_color.png",
    "RSL":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/4771.png",
    "TOR":  "https://a.espncdn.com/i/teamlogos/soccer/500/7318.png",
    "MTL":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9720.png",
    "DAL":  "https://a.espncdn.com/guid/fa2f128b-c698-3d43-2910-5561f4442748/logos/primary_logo_on_primary_color.png",
    "POR":  "https://a.espncdn.com/guid/67f3641d-0e73-f4c3-39ca-e0ad4020d315/logos/secondary_logo_on_black_color.png",
    "HOU":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/6077.png",
    "STL":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/21812.png",
    "ATL":  "https://a.espncdn.com/i/teamlogos/soccer/500-dark/18418.png",
    "PHI":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/10739.png",
    "DCU":  "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/193.png",
    "RBNY": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/190.png&h=200&w=200",
    "CIN":  "https://a.espncdn.com/i/teamlogos/soccer/500/18267.png",
    "SJ":   "https://a.espncdn.com/i/teamlogos/soccer/500/191.png",
}

TEAM_FULL_NAMES = {
    "LAFC": "Los Angeles FC",   "SEA": "Seattle Sounders",   "MIN": "Minnesota United",
    "VAN":  "Vancouver Whitecaps","COL": "Colorado Rapids",  "NHS": "Nashville SC",
    "NSH":  "Nashville SC",     "CLB": "Columbus Crew",      "SDFC": "San Diego FC",
    "ATX":  "Austin FC",        "CHI": "Chicago Fire",       "NE":  "New England Revolution",
    "ORL":  "Orlando City",     "LA":  "LA Galaxy",          "SKC": "Sporting Kansas City",
    "CLT":  "Charlotte FC",     "MIA": "Inter Miami",        "NYC": "New York City FC",
    "RSL":  "Real Salt Lake",   "TOR": "Toronto FC",         "MTL": "CF Montréal",
    "DAL":  "FC Dallas",        "POR": "Portland Timbers",   "HOU": "Houston Dynamo",
    "STL":  "St. Louis City",   "ATL": "Atlanta United",     "PHI": "Philadelphia Union",
    "DCU":  "DC United",        "RBNY":"New York Red Bulls", "CIN": "FC Cincinnati",
    "SJ":   "San Jose Earthquakes",
}

# President → teams mapping
PRESIDENTS = {
    "JNKA": {"color": "#e8b84b", "teams": ["LAFC","ATL","VAN","ATX","CHI","SJ","DAL","DCU","NE","MIA"]},
    "MATI": {"color": "#3b82f6", "teams": ["NSH","MTL","POR","HOU","CLB","SEA","SKC","SDFC","ORL","MIN"]},
    "MAXI": {"color": "#a78bfa", "teams": ["NYC","PHI","TOR","STL","CLT","CIN","RBNY","COL","RSL","LA"]},
}

# Build reverse mapping: team → president
TEAM_PRESIDENT = {}
for presi, data in PRESIDENTS.items():
    for team in data["teams"]:
        TEAM_PRESIDENT[team] = presi

POS_COLORS = {"GK": "#f59e0b", "DEF": "#3b82f6", "MID": "#22c55e", "FWD": "#ef4444"}
CONTRATO_COLORS = {
    "1 Season": "#22c55e", "2 Season": "#3b82f6",
    "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444"
}

# ── Presupuestos reales del Excel (hoja Teams, columna Presupuesto) ───────────
TEAM_BUDGETS = {
    "ATL":  28000000,
    "ATX":  64000000,
    "MTL":  70050000,
    "CLT":  23850000,
    "CHI":  56850000,
    "CLB":  5500000,
    "COL":  79500000,
    "DCU":  25000000,
    "CIN":  15000000,
    "DAL":  96200000,
    "HOU":  107250000,
    "MIA":  52900000,
    "LAFC": 717850000,
    "LA":   71650000,
    "MIN":  55000000,
    "NHS":  112900000,
    "NE":   77450000,
    "NYC":  5500000,
    "ORL":  25500000,
    "PHI":  22200000,
    "POR":  22000000,
    "RSL":  22500000,
    "RBNY": 5000000,
    "SDFC": 24100000,
    "SJ":   50000000,
    "SEA":  32000000,
    "SKC":  68000000,
    "STL":  20500000,
    "TOR":  8000000,
    "VAN":  60750000,
}

TEAM_DT = {
    "ATL":  "Sérgio Conceição",
    "ATX":  "Pep Guardiola",
    "MTL":  "Didier Deschamps",
    "CLT":  "Nuno Espírito Santo",
    "CHI":  "Thomas Tuchel",
    "CLB":  "Arne Slot",
    "COL":  "Unai Emery",
    "DCU":  "Carlo Ancelotti",
    "CIN":  "Antonio Conte",
    "DAL":  "Julian Nagelsmann",
    "HOU":  "Mike Tullberg",
    "MIA":  "Marcelo Bielsa",
    "LAFC": "José Mourinho",
    "LA":   "Vincent Kompany",
    "MIN":  "Hansi Flick",
    "NHS":  "Lionel Scaloni",
    "NE":   "Jürgen Klopp",
    "NYC":  "Ruben Amorim",
    "ORL":  "Mikel Arteta",
    "PHI":  "Néstor Lorenzo",
    "POR":  "Steven Gerrard",
    "RSL":  "Enzo Maresca",
    "RBNY": "Phil Parkinson",
    "SDFC": "Luis de la Fuente",
    "SJ":   "Gian Piero Gasperini",
    "SEA":  "Xabi Alonso",
    "SKC":  "Luis Enrique",
    "STL":  "Simone Inzaghi",
    "TOR":  "Ernesto Valverde",
    "VAN":  "Diego Simeone",
}


# ── Full player data ──────────────────────────────────────────────────────────
@st.cache_data
def load_full_data():
    raw = [
        {"name":"M. Salah",       "team":"ATL",  "price":104000000,"renovation":52000000, "clausula":468000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Brandt",      "team":"LAFC",  "price":41000000,"renovation":20500000, "clausula":184500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Rodri",          "team":"TOR",  "price":115500000,"renovation":57750000, "clausula":519750000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Mbappé",      "team":"LAFC", "price":211000000,"renovation":105500000,"clausula":949500000, "contrato":"Cesion Corta", "cesion":"NSH"},
        {"name":"Vini Jr.",       "team":"ATX",  "price":193500000,"renovation":96750000, "clausula":870750000, "contrato":"1 Season",     "cesion":None},
        {"name":"E. Haaland",     "team":"SEA",  "price":196000000,"renovation":98000000, "clausula":882000000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Kane",        "team":"COL",  "price":117500000,"renovation":58750000, "clausula":528750000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Bellingham",  "team":"NYC",  "price":174500000,"renovation":87250000, "clausula":785250000, "contrato":"1 Season",     "cesion":None},
        {"name":"V. van Dijk",    "team":"LA",   "price":77500000, "renovation":38750000, "clausula":348750000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Lewandowski", "team":"MIA",  "price":44000000, "renovation":22000000, "clausula":198000000, "contrato":"Cesion Larga", "cesion":"MTL"},
        {"name":"K. De Bruyne",   "team":"ATL",  "price":97000000, "renovation":48500000, "clausula":436500000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Wirtz",       "team":"SJ",   "price":145500000,"renovation":72750000, "clausula":654750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Alisson",        "team":"MIA",  "price":63000000, "renovation":31500000, "clausula":283500000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Courtois",    "team":"SKC",  "price":51000000, "renovation":25500000, "clausula":229500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Neymar Jr",      "team":"MIA",  "price":64000000, "renovation":32000000, "clausula":288000000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Martínez",    "team":"POR",  "price":101500000,"renovation":50750000, "clausula":456750000, "contrato":"1 Season",     "cesion":None},
        {"name":"B. Saka",        "team":"ATL",  "price":126000000,"renovation":63000000, "clausula":567000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Musiala",     "team":"LAFC", "price":232000000,"renovation":116000000,"clausula":1044000000,"contrato":"1 Season",     "cesion":None},
        {"name":"F. Valverde",    "team":"NE",   "price":120000000,"renovation":60000000, "clausula":540000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Ødegaard",    "team":"RSL",  "price":108500000,"renovation":54250000, "clausula":488250000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Kimmich",     "team":"POR",  "price":82000000, "renovation":41000000, "clausula":369000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Rüdiger",     "team":"NE",   "price":62500000, "renovation":31250000, "clausula":281250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. ter Stegen",  "team":"LA",   "price":45000000, "renovation":22500000, "clausula":202500000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Oblak",       "team":"CHI",  "price":74500000, "renovation":37250000, "clausula":335250000, "contrato":"1 Season",     "cesion":None},
        {"name":"O. Dembélé",     "team":"RSL",  "price":85000000, "renovation":42500000, "clausula":382500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Raphinha",       "team":"MIN",  "price":85000000, "renovation":42500000, "clausula":382500000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Messi",       "team":"SEA",  "price":38000000, "renovation":19000000, "clausula":171000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Griezmann",   "team":"DCU",  "price":74000000, "renovation":37000000, "clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"V. Osimhen",     "team":"CLT",  "price":116000000,"renovation":58000000, "clausula":522000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Pedri",          "team":"CLB",  "price":125000000,"renovation":62500000, "clausula":562500000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Rice",        "team":"SJ",   "price":86000000, "renovation":43000000, "clausula":387000000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Barella",     "team":"ATX",  "price":84500000, "renovation":42250000, "clausula":380250000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Palmer",      "team":"DAL",  "price":111000000,"renovation":55500000, "clausula":499500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Marquinhos",     "team":"ATX",  "price":65500000, "renovation":32750000, "clausula":294750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Gabriel",        "team":"RBNY", "price":82500000, "renovation":41250000, "clausula":371250000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Tah",         "team":"SEA",  "price":68500000, "renovation":34250000, "clausula":308250000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Schlotterbeck","team":"NHS", "price":92000000, "renovation":46000000, "clausula":414000000, "contrato":"2 Season",     "cesion":None},
        {"name":"A. Bastoni",     "team":"MIA",  "price":88500000, "renovation":44250000, "clausula":398250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Maignan",     "team":"NHS",  "price":74000000, "renovation":37000000, "clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Donnarumma",  "team":"TOR",  "price":76000000, "renovation":38000000, "clausula":342000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Sommer",      "team":"ORL",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"Cesion Larga", "cesion":"ATL"},
        {"name":"Rodrygo",        "team":"LAFC", "price":232000000,"renovation":116000000,"clausula":1044000000,"contrato":"1 Season",     "cesion":None},
        {"name":"H. Son",         "team":"ATX",  "price":56500000, "renovation":28250000, "clausula":254250000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Benzema",     "team":"NE",   "price":26000000, "renovation":13000000, "clausula":117000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Álvarez",     "team":"SDFC", "price":94000000, "renovation":47000000, "clausula":423000000, "contrato":"2 Season",     "cesion":None},
        {"name":"A. Isak",        "team":"SEA",  "price":89500000, "renovation":44750000, "clausula":402750000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Dybala",      "team":"LAFC", "price":81000000, "renovation":40500000, "clausula":364500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bruno Fernandes","team":"MTL",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Foden",       "team":"NE",   "price":88000000, "renovation":44000000, "clausula":396000000, "contrato":"Cesion Larga", "cesion":"PHI"},
        {"name":"F. de Jong",     "team":"SKC",  "price":77500000, "renovation":38750000, "clausula":348750000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Xhaka",       "team":"CIN",  "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Mac Allister","team":"MIA",  "price":84500000, "renovation":42250000, "clausula":380250000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Çalhanoğlu",  "team":"VAN",  "price":57000000, "renovation":28500000, "clausula":256500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Rúben Dias",     "team":"MIA",  "price":68500000, "renovation":34250000, "clausula":308250000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Alexander-Arnold","team":"SKC","price":74000000,"renovation":37000000,"clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Hernández",   "team":"ATL",  "price":73000000, "renovation":36500000, "clausula":328500000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Koundé",      "team":"ORL",  "price":83000000, "renovation":41500000, "clausula":373500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Hakimi",      "team":"ORL",  "price":78500000, "renovation":39250000, "clausula":353250000, "contrato":"Cesion Corta", "cesion":"DCU"},
        {"name":"E. Martínez",    "team":"MTL",  "price":49000000, "renovation":24500000, "clausula":220500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Ederson",        "team":"SEA",  "price":45000000, "renovation":22500000, "clausula":202500000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Kobel",       "team":"HOU",  "price":68500000, "renovation":34250000, "clausula":308250000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Díaz",        "team":"NHS",  "price":118500000,"renovation":59250000, "clausula":533250000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Mahrez",      "team":"VAN",  "price":33500000, "renovation":16750000, "clausula":150750000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Kvaratskhelia","team":"CLT", "price":81000000, "renovation":40500000, "clausula":364500000, "contrato":"Cesion Larga", "cesion":"CHI"},
        {"name":"Rafael Leão",    "team":"LA",   "price":86000000, "renovation":43000000, "clausula":387000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Cristiano Ronaldo","team":"RBNY","price":18500000,"renovation":9250000,  "clausula":83250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Nico Williams",  "team":"VAN",  "price":78500000, "renovation":39250000, "clausula":353250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Olise",       "team":"COL",  "price":75000000, "renovation":37500000, "clausula":337500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bernardo Silva", "team":"DAL",  "price":77000000, "renovation":38500000, "clausula":346500000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Milinković-Savić","team":"MTL","price":54500000,"renovation":27250000,"clausula":245250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Casemiro",       "team":"MIA",  "price":36000000, "renovation":18000000, "clausula":162000000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Modrić",      "team":"LA",   "price":39000000, "renovation":19500000, "clausula":175500000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Kanté",       "team":"CIN",  "price":26500000, "renovation":13250000, "clausula":119250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Caicedo",     "team":"SJ",   "price":68000000, "renovation":34000000, "clausula":306000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Grimaldo",       "team":"CLT",  "price":54500000, "renovation":27250000, "clausula":245250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Éder Militão",   "team":"TOR",  "price":73000000, "renovation":36500000, "clausula":328500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Araujo",      "team":"CLT",  "price":76000000, "renovation":38000000, "clausula":342000000, "contrato":"1 Season",     "cesion":None},
        {"name":"João Cancelo",   "team":"COL",  "price":46500000, "renovation":23250000, "clausula":209250000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Trippier",    "team":"HOU",  "price":37500000, "renovation":18750000, "clausula":168750000, "contrato":"1 Season",     "cesion":None},
        {"name":"U. Simón",       "team":"LAFC", "price":49000000, "renovation":24500000, "clausula":220500000, "contrato":"1 Season",     "cesion":None},
        {"name":"W. Szczęsny",    "team":"POR",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"G. Mamardashvili","team":"MIN", "price":57500000, "renovation":28750000, "clausula":258750000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Gakpo",       "team":"PHI",  "price":103000000,"renovation":51500000, "clausula":463500000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Sané",        "team":"STL",  "price":80000000, "renovation":40000000, "clausula":360000000, "contrato":"Cesion Corta", "cesion":"CLB"},
        {"name":"S. Mané",        "team":"DAL",  "price":45500000, "renovation":22750000, "clausula":204750000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Coman",       "team":"CHI",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"Cesion Larga", "cesion":"LA"},
        {"name":"Diogo Jota",     "team":"RSL",  "price":50000000, "renovation":25000000, "clausula":225000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Maddison",    "team":"MIN",  "price":70000000, "renovation":35000000, "clausula":315000000, "contrato":"1 Season",     "cesion":None},
        {"name":"İ. Gündoğan",    "team":"CHI",  "price":44000000, "renovation":22000000, "clausula":198000000, "contrato":"1 Season",     "cesion":None},
        {"name":"X. Simons",      "team":"CHI",  "price":65000000, "renovation":32500000, "clausula":292500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Gravenberch", "team":"VAN",  "price":53500000, "renovation":26750000, "clausula":240750000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Alaba",       "team":"MTL",  "price":36000000, "renovation":18000000, "clausula":162000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Frimpong",    "team":"LA",   "price":57000000, "renovation":28500000, "clausula":256500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Sergio Ramos",   "team":"STL",  "price":2000000,  "renovation":1000000,  "clausula":9000000,   "contrato":"1 Season",     "cesion":None},
        {"name":"M. Hummels",     "team":"ATX",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"Cesion Larga", "cesion":"STL"},
        {"name":"A. Davies",      "team":"NHS",  "price":74000000, "renovation":37000000, "clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Stones",      "team":"SKC",  "price":34500000, "renovation":17250000, "clausula":155250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Alex Remiro",    "team":"SJ",   "price":32500000, "renovation":16250000, "clausula":146250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Neuer",       "team":"ATX",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"Cesion Larga", "cesion":"CLB"},
        {"name":"Diogo Costa",    "team":"RBNY", "price":54000000, "renovation":27000000, "clausula":243000000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Gulácsi",     "team":"ORL",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Diaby",       "team":"PHI",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"B. Barcola",     "team":"PHI",  "price":56000000, "renovation":28000000, "clausula":252000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Á. Di María",    "team":"TOR",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"D. Malen",       "team":"VAN",  "price":35000000, "renovation":17500000, "clausula":157500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Rabiot",      "team":"ORL",  "price":38000000, "renovation":19000000, "clausula":171000000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Goretzka",    "team":"HOU",  "price":35500000, "renovation":17750000, "clausula":159750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Gavi",           "team":"POR",  "price":55000000, "renovation":27500000, "clausula":247500000, "contrato":"1 Season",     "cesion":None},
        {"name":"E. Fernández",   "team":"DAL",  "price":80000000, "renovation":40000000, "clausula":360000000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Andrich",     "team":"VAN",  "price":31000000, "renovation":15500000, "clausula":139500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Laporte",     "team":"CLT",  "price":30000000, "renovation":15000000, "clausula":135000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. de Ligt",     "team":"NYC",  "price":79000000, "renovation":39500000, "clausula":355500000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Hincapié",    "team":"LAFC", "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Kim Min Jae",    "team":"SKC",  "price":62000000, "renovation":31000000, "clausula":279000000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. James",       "team":"SDFC", "price":50000000, "renovation":25000000, "clausula":225000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Balde",       "team":"ORL",  "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Bounou",      "team":"RSL",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Hrádecký",    "team":"SDFC", "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Pickford",    "team":"STL",  "price":24000000, "renovation":12000000, "clausula":108000000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Nkunku",      "team":"MIA",  "price":107000000,"renovation":53500000, "clausula":481500000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Kubo",        "team":"NE",   "price":52500000, "renovation":26250000, "clausula":236250000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Martinelli",  "team":"HOU",  "price":64000000, "renovation":32000000, "clausula":288000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Depay",       "team":"ORL",  "price":22500000, "renovation":11250000, "clausula":101250000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Gnabry",      "team":"SDFC", "price":46000000, "renovation":23000000, "clausula":207000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Rashford",    "team":"SKC",  "price":76000000, "renovation":38000000, "clausula":342000000, "contrato":"Cesion Larga", "cesion":"DCU"},
        {"name":"A. Correa",      "team":"DCU",  "price":31000000, "renovation":15500000, "clausula":139500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Sterling",    "team":"CHI",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Gabriel Jesús",  "team":"CIN",  "price":78000000, "renovation":39000000, "clausula":351000000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Havertz",     "team":"HOU",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Sávio",          "team":"DCU",  "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Kessié",      "team":"MIN",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Paqueta",     "team":"DCU",  "price":65000000, "renovation":32500000, "clausula":292500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Brahim",         "team":"COL",  "price":43500000, "renovation":21750000, "clausula":195750000, "contrato":"Cesion Larga", "cesion":"DAL"},
        {"name":"D. Szoboszlai",  "team":"SDFC", "price":75000000, "renovation":37500000, "clausula":337500000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Walker",      "team":"PHI",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"E. Tapsoba",     "team":"CLB",  "price":40000000, "renovation":20000000, "clausula":180000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Robertson",   "team":"RBNY", "price":43000000, "renovation":21500000, "clausula":193500000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Tomori",      "team":"POR",  "price":37000000, "renovation":18500000, "clausula":166500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Onana",       "team":"CLT",  "price":32000000, "renovation":16000000, "clausula":144000000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Pope",        "team":"VAN",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Casteels",    "team":"ATL",  "price":15000000, "renovation":7500000,  "clausula":67500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Meret",       "team":"RSL",  "price":28000000, "renovation":14000000, "clausula":126000000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Kolo Muani",  "team":"SJ",   "price":70000000, "renovation":35000000, "clausula":315000000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Haller",      "team":"CIN",  "price":18000000, "renovation":9000000,  "clausula":81000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Grealish",    "team":"DAL",  "price":57500000, "renovation":28750000, "clausula":258750000, "contrato":"Cesion Larga", "cesion":"TOR"},
        {"name":"D. Udogie",      "team":"TOR",  "price":35500000, "renovation":17750000, "clausula":159750000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Süle",        "team":"RSL",  "price":24500000, "renovation":12250000, "clausula":110250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Kerkez",      "team":"CIN",  "price":33500000, "renovation":16750000, "clausula":150750000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Navas",       "team":"NYC",  "price":4000000,  "renovation":2000000,  "clausula":18000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"F. Torres",      "team":"NHS",  "price":75000000, "renovation":37500000, "clausula":337500000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Chukwueze",   "team":"MTL",  "price":29000000, "renovation":14500000, "clausula":130500000, "contrato":"1 Season",     "cesion":None},
        {"name":"João Félix",     "team":"CLT",  "price":30000000, "renovation":15000000, "clausula":135000000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Lozano",      "team":"STL",  "price":22000000, "renovation":11000000, "clausula":99000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Adeyemi",     "team":"STL",  "price":118000000,"renovation":59000000, "clausula":531000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Doku",        "team":"NE",   "price":32500000, "renovation":16250000, "clausula":146250000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Doué",        "team":"HOU",  "price":45500000, "renovation":22750000, "clausula":204750000, "contrato":"1 Season",     "cesion":None},
        {"name":"W. Zaïre-Emery", "team":"ATL",  "price":44500000, "renovation":22250000, "clausula":200250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Pau Cubarsí",    "team":"NHS",  "price":40500000, "renovation":20250000, "clausula":182250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Gonçalo Inácio", "team":"RSL",  "price":40000000, "renovation":20000000, "clausula":180000000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Lukeba",      "team":"COL",  "price":40000000, "renovation":20000000, "clausula":180000000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Rulli",       "team":"CLB",  "price":10000000, "renovation":5000000,  "clausula":45000000,  "contrato":"Cesion Larga", "cesion":"ATX"},
        {"name":"É. Mendy",       "team":"DCU",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Flekken",     "team":"DAL",  "price":14000000, "renovation":7000000,  "clausula":63000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Lopes",       "team":"NE",   "price":8000000,  "renovation":4000000,  "clausula":36000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"N. Madueke",     "team":"LAFC", "price":48000000, "renovation":24000000, "clausula":216000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Yeremy Pino",    "team":"PHI",  "price":39500000, "renovation":19750000, "clausula":177750000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Ekitike",     "team":"SKC",  "price":28500000, "renovation":14250000, "clausula":128250000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Durán",       "team":"SEA",  "price":35000000, "renovation":17500000, "clausula":157500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Moleiro",        "team":"MIN",  "price":35000000, "renovation":17500000, "clausula":157500000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Rovella",     "team":"TOR",  "price":35500000, "renovation":17750000, "clausula":159750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Nico González",  "team":"MIN",  "price":26000000, "renovation":13000000, "clausula":117000000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Barrios",     "team":"LA",   "price":39500000, "renovation":19750000, "clausula":177750000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Cherki",      "team":"RSL",  "price":38500000, "renovation":19250000, "clausula":173250000, "contrato":"1 Season",     "cesion":None},
        {"name":"O. Diomande",    "team":"CLB",  "price":40000000, "renovation":20000000, "clausula":180000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Thiaw",       "team":"STL",  "price":25500000, "renovation":12750000, "clausula":114750000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Ramsdale",    "team":"PHI",  "price":49000000, "renovation":24500000, "clausula":220500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Antony",         "team":"MTL",  "price":35000000, "renovation":17500000, "clausula":157500000, "contrato":"1 Season",     "cesion":None},
        {"name":"B. Brobbey",     "team":"ATL",  "price":23000000, "renovation":11500000, "clausula":103500000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Elliott",     "team":"SDFC", "price":23000000, "renovation":11500000, "clausula":103500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Fermín",         "team":"MIN",  "price":31500000, "renovation":15750000, "clausula":141750000, "contrato":"1 Season",     "cesion":None},
        {"name":"E. Millot",      "team":"ATX",  "price":22500000, "renovation":11250000, "clausula":101250000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Güler",       "team":"SJ",   "price":30500000, "renovation":15250000, "clausula":137250000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Bynoe-Gittens","team":"CLB", "price":27500000, "renovation":13750000, "clausula":123750000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Pavlovic",    "team":"VAN",  "price":29000000, "renovation":14500000, "clausula":130500000, "contrato":"1 Season",     "cesion":None},
        {"name":"António Silva",  "team":"STL",  "price":29000000, "renovation":14500000, "clausula":130500000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Badé",        "team":"CHI",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"R. Lewis",       "team":"SKC",  "price":26000000, "renovation":13000000, "clausula":117000000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Scalvini",    "team":"LA",   "price":29000000, "renovation":14500000, "clausula":130500000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Lloris",      "team":"CIN",  "price":3000000,  "renovation":1500000,  "clausula":13500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"R. Højlund",     "team":"MTL",  "price":21500000, "renovation":10750000, "clausula":96750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"N. Okafor",      "team":"NYC",  "price":21500000, "renovation":10750000, "clausula":96750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Asprilla",    "team":"LAFC", "price":21000000, "renovation":10500000, "clausula":94500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Garnacho",    "team":"CIN",  "price":21000000, "renovation":10500000, "clausula":94500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Kalimuendo",  "team":"HOU",  "price":15500000, "renovation":7750000,  "clausula":69750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Tel",         "team":"SKC",  "price":23000000, "renovation":11500000, "clausula":103500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Ezzalzouli",  "team":"ORL",  "price":16000000, "renovation":8000000,  "clausula":72000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Mainoo",      "team":"RBNY", "price":22500000, "renovation":11250000, "clausula":101250000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Bradley",     "team":"CLT",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Hato",        "team":"DCU",  "price":21000000, "renovation":10500000, "clausula":94500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Hložek",      "team":"CLB",  "price":16500000, "renovation":8250000,  "clausula":74250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Ansu Fati",      "team":"HOU",  "price":38000000, "renovation":19000000, "clausula":171000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Vitor Roque",    "team":"POR",  "price":17500000, "renovation":8750000,  "clausula":78750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"T. Baldanzi",    "team":"NYC",  "price":16000000, "renovation":8000000,  "clausula":72000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Soulé",       "team":"ATL",  "price":17000000, "renovation":8500000,  "clausula":76500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"B. El Khannouss","team":"STL",  "price":16500000, "renovation":8250000,  "clausula":74250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"N. Zalewski",    "team":"LA",   "price":11000000, "renovation":5500000,  "clausula":49500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Yıldız",      "team":"DAL",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"G. Reyna",       "team":"MIA",  "price":27500000, "renovation":13750000, "clausula":123750000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Silva",       "team":"SJ",   "price":450000,   "renovation":225000,   "clausula":2025000,   "contrato":"1 Season",     "cesion":None},
        {"name":"A. Gray",        "team":"NE",   "price":12500000, "renovation":6250000,  "clausula":56250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Marc Casadó",    "team":"DAL",  "price":11600000, "renovation":5800000,  "clausula":52200000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Lafont",      "team":"PHI",  "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"G. Ochoa",       "team":"COL",  "price":1500000,  "renovation":750000,   "clausula":6750000,   "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Moukoko",     "team":"MTL",  "price":22500000, "renovation":11250000, "clausula":101250000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Velasco",     "team":"DAL",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Abada",       "team":"CLT",  "price":9500000,  "renovation":4750000,  "clausula":42750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Bonny",       "team":"CIN",  "price":9500000,  "renovation":4750000,  "clausula":42750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Fábio Carvalho", "team":"CLB",  "price":9500000,  "renovation":4750000,  "clausula":42750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Scott",       "team":"NHS",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"C. Medina",      "team":"SKC",  "price":12500000, "renovation":6250000,  "clausula":56250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"C. Echeverri",   "team":"DCU",  "price":10000000, "renovation":5000000,  "clausula":45000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"C. Chukwuemeka", "team":"STL",  "price":9500000,  "renovation":4750000,  "clausula":42750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"D. Moreira",     "team":"ORL",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"V. Barco",       "team":"ATX",  "price":8500000,  "renovation":4250000,  "clausula":38250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"I. Fresneda",    "team":"POR",  "price":8500000,  "renovation":4250000,  "clausula":38250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Talles Magno",   "team":"NYC",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"E. Ferguson",    "team":"SJ",   "price":10000000, "renovation":5000000,  "clausula":45000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Páez",        "team":"MIA",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Enciso",      "team":"LAFC", "price":6500000,  "renovation":3250000,  "clausula":29250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Ângelo",         "team":"TOR",  "price":6500000,  "renovation":3250000,  "clausula":29250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Richardson",  "team":"DCU",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"B. Domínguez",   "team":"SDFC", "price":6500000,  "renovation":3250000,  "clausula":29250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"T. Lamptey",     "team":"VAN",  "price":8000000,  "renovation":4000000,  "clausula":36000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"S. Magassa",     "team":"RSL",  "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Gómez",       "team":"NE",   "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"O. Bobb",        "team":"SEA",  "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Romero",      "team":"NHS",  "price":3200000,  "renovation":1600000,  "clausula":14400000,  "contrato":"1 Season",     "cesion":None},
        {"name":"C. Cassano",     "team":"CLT",  "price":18300000, "renovation":9150000,  "clausula":82350000,  "contrato":"1 Season",     "cesion":None},
        {"name":"F. Pellistri",   "team":"SDFC", "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Miley",       "team":"ORL",  "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Stefan Bajcetic","team":"CLT",  "price":4800000,  "renovation":2400000,  "clausula":21600000,  "contrato":"1 Season",     "cesion":None},
        {"name":"V. Carboni",     "team":"RBNY", "price":5500000,  "renovation":2750000,  "clausula":24750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Duranville",  "team":"NHS",  "price":4800000,  "renovation":2400000,  "clausula":21600000,  "contrato":"1 Season",     "cesion":None},
        {"name":"P. Wanner",      "team":"CHI",  "price":4400000,  "renovation":2200000,  "clausula":19800000,  "contrato":"1 Season",     "cesion":None},
        {"name":"S. Charles",     "team":"DAL",  "price":4100000,  "renovation":2050000,  "clausula":18450000,  "contrato":"1 Season",     "cesion":None},
        {"name":"O. Cortés",      "team":"MIA",  "price":3500000,  "renovation":1750000,  "clausula":15750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Marc Guiu",      "team":"MIN",  "price":3700000,  "renovation":1850000,  "clausula":16650000,  "contrato":"1 Season",     "cesion":None},
        {"name":"B. Doak",        "team":"ATX",  "price":4000000,  "renovation":2000000,  "clausula":18000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Peter",          "team":"RBNY", "price":3600000,  "renovation":1800000,  "clausula":16200000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Newerton",       "team":"SJ",   "price":3800000,  "renovation":1900000,  "clausula":17100000,  "contrato":"1 Season",     "cesion":None},
        {"name":"T. Gulliksen",   "team":"COL",  "price":3500000,  "renovation":1750000,  "clausula":15750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Castrop",     "team":"ATL",  "price":3500000,  "renovation":1750000,  "clausula":15750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"T. Pembélé",     "team":"MTL",  "price":3400000,  "renovation":1700000,  "clausula":15300000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Del Blanco",  "team":"CIN",  "price":3300000,  "renovation":1650000,  "clausula":14850000,  "contrato":"1 Season",     "cesion":None},
        {"name":"R. Bardghji",    "team":"COL",  "price":3600000,  "renovation":1800000,  "clausula":16200000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Matheus França", "team":"MTL",  "price":3600000,  "renovation":1800000,  "clausula":16200000,  "contrato":"1 Season",     "cesion":None},
        {"name":"S. Pafundi",     "team":"HOU",  "price":3500000,  "renovation":1750000,  "clausula":15750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"D. Washington",  "team":"TOR",  "price":3100000,  "renovation":1550000,  "clausula":13950000,  "contrato":"1 Season",     "cesion":None},
        {"name":"E. Mbappé",      "team":"NYC",  "price":2700000,  "renovation":1350000,  "clausula":12150000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Afonso Moreira", "team":"SKC",  "price":2900000,  "renovation":1450000,  "clausula":13050000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Héctor Fort",    "team":"POR",  "price":2700000,  "renovation":1350000,  "clausula":12150000,  "contrato":"1 Season",     "cesion":None},
        {"name":"B. Castro",      "team":"MIA",  "price":2500000,  "renovation":1250000,  "clausula":11250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Q. Sullivan",    "team":"PHI",  "price":2500000,  "renovation":1250000,  "clausula":11250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Á. Alarcón",     "team":"LA",   "price":2400000,  "renovation":1200000,  "clausula":10800000,  "contrato":"1 Season",     "cesion":None},
        {"name":"I. Babadi",      "team":"NYC",  "price":2600000,  "renovation":1300000,  "clausula":11700000,  "contrato":"1 Season",     "cesion":None},
        {"name":"G. Puerta",      "team":"SEA",  "price":2400000,  "renovation":1200000,  "clausula":10800000,  "contrato":"1 Season",     "cesion":None},
        {"name":"B. Norton-Cuffy","team":"RSL",  "price":2300000,  "renovation":1150000,  "clausula":10350000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Iker Bravo",     "team":"PHI",  "price":2200000,  "renovation":1100000,  "clausula":9900000,   "contrato":"1 Season",     "cesion":None},
        {"name":"A. van Axel Dongen","team":"RBNY","price":1800000,"renovation":900000,   "clausula":8100000,   "contrato":"1 Season",     "cesion":None},
        {"name":"P. Brunner",     "team":"CHI",  "price":2300000,  "renovation":1150000,  "clausula":10350000,  "contrato":"1 Season",     "cesion":None},
        {"name":"T. Land",        "team":"PHI",  "price":1600000,  "renovation":800000,   "clausula":7200000,   "contrato":"1 Season",     "cesion":None},
        {"name":"K. Gordon",      "team":"VAN",  "price":1000000,  "renovation":500000,   "clausula":4500000,   "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Eduardo",     "team":"CLB",  "price":1300000,  "renovation":650000,   "clausula":5850000,   "contrato":"1 Season",     "cesion":None},
    ]
    df = pd.DataFrame(raw)
    df = df[df["name"].isin(PLAYER_DATA.keys())].drop_duplicates(subset=["name"]).reset_index(drop=True)
    return df


def fmt_money(v):
    if not v or v == 0: return "—"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.1f}M"
    if v >= 1e3:  return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"


def contrato_badge(c):
    badges = {
        "1 Season":    '<span class="badge-1s">1 Season</span>',
        "2 Season":    '<span class="badge-2s">2 Season</span>',
        "Cesion Corta":'<span class="badge-cc">Cesión Corta</span>',
        "Cesion Larga":'<span class="badge-cl">Cesión Larga</span>',
    }
    return badges.get(c, f'<span style="color:#aaa;font-size:0.62rem;">{c}</span>')


def shield_img(team_code, size=22):
    logo = TEAM_LOGOS.get(team_code, "")
    if logo:
        return f'<img src="{logo}" style="width:{size}px;height:{size}px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.04);">'
    return f'<span style="font-size:0.7rem;font-weight:700;color:#e8b84b;">{team_code}</span>'


# ── Load data ────────────────────────────────────────────────────────────────
players_df_base = load_full_data()
players_df_base["pos"]      = players_df_base["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("pos", "?"))
players_df_base["nat"]      = players_df_base["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat", ""))
players_df_base["nat_name"] = players_df_base["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat_name", ""))
players_df_base["sofifa"]   = players_df_base["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("sofifa", 0))

# Apply transfers from storage (mutations to team/cesion)
def get_current_players():
    df = players_df_base.copy()
    completed = get_state("completed_transfers", [])
    for t in completed:
        mask = df["name"] == t["player"]
        if not mask.any():
            continue
        tipo = t.get("tipo")
        if tipo == "Compra":
            df.loc[mask, "team"] = t["to_team"]
            df.loc[mask, "cesion"] = None
            df.loc[mask, "contrato"] = "1 Season"
        elif tipo == "Cesion Corta":
            df.loc[mask, "cesion"] = df.loc[mask, "team"].values[0]
            df.loc[mask, "team"] = t["to_team"]
            df.loc[mask, "contrato"] = "Cesion Corta"
        elif tipo == "Cesion Larga":
            df.loc[mask, "cesion"] = df.loc[mask, "team"].values[0]
            df.loc[mask, "team"] = t["to_team"]
            df.loc[mask, "contrato"] = "Cesion Larga"
        elif tipo == "Pagar Cesion":
            df.loc[mask, "team"] = t["to_team"]
            df.loc[mask, "cesion"] = None
            df.loc[mask, "contrato"] = "1 Season"
    return df


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="page-title" style="font-size:1.6rem">MMJ</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub" style="margin-top:-8px">LEAGUE SEASON V</div>', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navegación",
        ["⚽ Jugadores", "🏟️ Equipos", "💰 Presupuestos", "🔄 Cedidos", "📊 Estadísticas", "🤝 Ventana de Fichajes"],
        label_visibility="collapsed"
    )
    st.divider()
    players_df = get_current_players()
    st.caption(f"**{len(players_df)}** jugadores · **{len(TEAM_LOGOS)}** equipos")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: JUGADORES
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚽ Jugadores":
    players_df = get_current_players()
    st.markdown('<div class="page-title">MERCADO DE JUGADORES</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">MMJ League Season V · Jugadores · 30 Equipos</div>', unsafe_allow_html=True)

    total_val = players_df["price"].sum()
    avg_val   = players_df["price"].mean()
    top_p     = players_df.loc[players_df["price"].idxmax()]
    cedidos   = players_df["cesion"].notna().sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Valor Total Liga", fmt_money(total_val))
    c2.metric("Valor Promedio",   fmt_money(avg_val))
    c3.metric(f"Top: {top_p['name']}", fmt_money(top_p["price"]))
    c4.metric("Jugadores Cedidos", int(cedidos))
    c5.metric("Contratos 1 Season", int((players_df["contrato"] == "1 Season").sum()))

    st.divider()

    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([3, 2, 2, 1, 2, 1])
    search       = fc1.text_input("Buscar", placeholder="🔍 Buscar jugador o equipo...", label_visibility="collapsed")
    teams_list   = sorted(players_df["team"].unique())
    team_f       = fc2.selectbox("Equipo", ["Todos"] + teams_list, label_visibility="collapsed")
    contrato_f   = fc3.selectbox("Contrato", ["Todos","1 Season","2 Season","Cesion Corta","Cesion Larga"], label_visibility="collapsed")
    pos_f        = fc4.selectbox("Pos", ["All","GK","DEF","MID","FWD"], label_visibility="collapsed")
    sort_f       = fc5.selectbox("Ordenar", ["Precio ↓","Precio ↑","Cláusula ↓","Nombre A-Z"], label_visibility="collapsed")
    solo_cedidos = fc6.checkbox("Cedidos", value=False)

    df = players_df.copy()
    if search:
        df = df[df["name"].str.contains(search, case=False, na=False) |
                df["team"].str.contains(search, case=False, na=False)]
    if team_f != "Todos":
        df = df[df["team"] == team_f]
    if contrato_f != "Todos":
        df = df[df["contrato"] == contrato_f]
    if pos_f != "All":
        df = df[df["pos"] == pos_f]
    if solo_cedidos:
        df = df[df["cesion"].notna()]

    sort_map = {"Precio ↓": ("price",False), "Precio ↑": ("price",True),
                "Cláusula ↓": ("clausula",False), "Nombre A-Z": ("name",True)}
    scol, sasc = sort_map[sort_f]
    df = df.sort_values(scol, ascending=sasc).reset_index(drop=True)

    st.caption(f"Mostrando **{len(df)}** jugadores")

    for _, row in df.iterrows():
        pdata     = PLAYER_DATA.get(row["name"], {})
        pos       = pdata.get("pos", "?")
        nat       = pdata.get("nat", "")
        nat_name  = pdata.get("nat_name", "")
        sofifa_id = pdata.get("sofifa", 0)
        pos_color = POS_COLORS.get(pos, "#667eea")

        photo_url   = get_player_photo(row["name"], sofifa_id)
        flag_url    = get_flag_url(nat)
        team_logo   = TEAM_LOGOS.get(row["team"], "")
        orig_logo   = TEAM_LOGOS.get(row.get("cesion"), "") if pd.notna(row.get("cesion")) else ""

        safe_name = str(row["name"]).replace("'", "").replace('"', "")
        initials  = "+".join(safe_name.split()[:2])
        fallback  = f"https://ui-avatars.com/api/?name={initials}&background=1a2a3a&color=f0c040&size=80&bold=true"

        flag_html  = f'<img src="{flag_url}" style="width:18px;height:13px;object-fit:cover;border-radius:2px;vertical-align:middle;">' if flag_url else ""
        tlogo_html = f'<img src="{team_logo}" style="width:22px;height:22px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.04);">' if team_logo else ""

        loan_html = ""
        if pd.notna(row.get("cesion")):
            orig_logo_html = f'<img src="{orig_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.04);">' if orig_logo else ""
            loan_html = (
                f'<div style="display:flex;align-items:center;gap:4px;margin-top:3px;">'
                f'{orig_logo_html}'
                f'<span style="font-size:0.62rem;color:#f97316;font-weight:700;">{row["cesion"]}</span>'
                f'<span style="font-size:0.62rem;color:#5a7080;">→ cedido a</span>'
                f'{tlogo_html}'
                f'<span style="font-size:0.62rem;color:#e2eaf4;font-weight:600;">{row["team"]}</span>'
                f'</div>'
            )
        else:
            loan_html = (
                f'<div style="display:flex;align-items:center;gap:4px;margin-top:3px;">'
                f'{tlogo_html}'
                f'<span style="font-size:0.7rem;color:#7a9db0;">{row["team"]} · {TEAM_FULL_NAMES.get(row["team"],"")}</span>'
                f'</div>'
            )

        contrato_html = contrato_badge(row["contrato"])
        pos_bg  = pos_color + "22"
        pos_bdr = pos_color + "44"

        st.markdown(f"""
        <div class="player-row">
          <img src="{photo_url}" style="width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid rgba(232,184,75,0.35);flex-shrink:0;background:#0a1520;"
               onerror="this.onerror=null;this.src='{fallback}'">
          <div style="flex:1;min-width:0;overflow:hidden;">
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;font-weight:800;color:#f0f4f8;white-space:nowrap;">{row["name"]}</span>
              <span style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};font-size:0.55rem;font-weight:900;letter-spacing:1.5px;padding:1px 6px;border-radius:3px;flex-shrink:0;">{pos}</span>
              {flag_html}
              <span style="font-size:0.65rem;color:#5a7080;white-space:nowrap;">{nat_name}</span>
            </div>
            {loan_html}
          </div>
          <div style="text-align:right;flex-shrink:0;min-width:120px;">
            <div style="font-family:'Space Mono',monospace;font-size:0.88rem;font-weight:700;color:#e8b84b;">{fmt_money(row["price"])}</div>
            <div style="font-size:0.6rem;color:#5a7080;">Cláus: {fmt_money(row["clausula"])}</div>
            <div style="margin-top:3px;">{contrato_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏟️ Equipos":
    players_df = get_current_players()
    st.markdown('<div class="page-title">CLUBES</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Plantillas por equipo · escudos · valor</div>', unsafe_allow_html=True)

    team_search = st.text_input("Buscar", placeholder="🔍 Buscar equipo...", label_visibility="collapsed")

    all_teams = sorted(players_df["team"].unique())
    for team_code in all_teams:
        if team_search and team_search.lower() not in team_code.lower() and team_search.lower() not in TEAM_FULL_NAMES.get(team_code,"").lower():
            continue

        squad = players_df[players_df["team"] == team_code].sort_values("price", ascending=False)
        total_val = squad["price"].sum()
        team_logo = TEAM_LOGOS.get(team_code, "")

        hc1, hc2 = st.columns([1, 8])
        with hc1:
            if team_logo:
                st.image(team_logo, width=64)
        with hc2:
            presi = TEAM_PRESIDENT.get(team_code, "?")
            presi_color = PRESIDENTS.get(presi, {}).get("color", "#aaa")
            dt_name = TEAM_DT.get(team_code, "—")
            budget  = TEAM_BUDGETS.get(team_code, 0)
            st.markdown(
                f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.5rem;font-weight:900;color:#f0f4f8;">'
                f'{team_code} <span style="color:#7a9db0;font-size:1rem;font-weight:400;">— {TEAM_FULL_NAMES.get(team_code,"")}</span>'
                f' <span style="font-size:0.75rem;color:{presi_color};background:{presi_color}22;border:1px solid {presi_color}44;padding:2px 8px;border-radius:4px;">{presi}</span></div>'
                f'<div style="font-size:0.75rem;color:#5a7080;margin-top:3px;">'
                f'DT: <span style="color:#e2eaf4;">{dt_name}</span>'
                f' &nbsp;·&nbsp; {len(squad)} jugadores'
                f' &nbsp;·&nbsp; Presupuesto: <span style="color:#e8b84b;font-weight:700;">{fmt_money(budget)}</span></div>',
                unsafe_allow_html=True
            )

        with st.expander(f"Ver plantilla completa de {team_code}", expanded=False):
            cols_per_row = 3
            rows_of_players = [squad.iloc[i:i+cols_per_row] for i in range(0, len(squad), cols_per_row)]
            for row_group in rows_of_players:
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
                        safe_n    = str(p["name"]).replace("'","").replace('"',"")
                        fallback  = f"https://ui-avatars.com/api/?name={'+'.join(safe_n.split()[:2])}&background=1a2a3a&color=f0c040&size=80&bold=true"
                        flag_img  = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;">' if flag_url else ""

                        if pd.notna(p.get("cesion")):
                            orig_logo = TEAM_LOGOS.get(p["cesion"], "")
                            orig_logo_html = f'<img src="{orig_logo}" style="width:14px;height:14px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if orig_logo else ""
                            loan_info = f'<div style="font-size:0.6rem;color:#f97316;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{orig_logo_html} {p["cesion"]} → cedido</div>'
                        else:
                            loan_info = ""

                        pos_bg  = pos_color + "22"
                        pos_bdr = pos_color + "44"
                        # FIXED card: CSS grid layout, name clipped correctly
                        st.markdown(f"""
                        <div class="player-card">
                          <div class="player-card-header">
                            <img src="{photo_url}" class="player-photo"
                                 onerror="this.onerror=null;this.src='{fallback}'">
                            <div class="player-info">
                              <div class="player-name" title="{p['name']}">{p['name']}</div>
                              <div style="margin-top:2px;">
                                <span class="player-pos-badge" style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};">{pos}</span>
                              </div>
                              <div class="player-nat">{flag_img} {nat_name}</div>
                              {loan_info}
                            </div>
                          </div>
                          <div class="player-stats-bar">
                            <div class="player-stat">
                              <div class="player-stat-val">{fmt_money(p["price"])}</div>
                              <div class="player-stat-lbl">Valor</div>
                            </div>
                            <div class="player-stat">
                              <div class="player-stat-val" style="font-size:0.72rem;">{p["contrato"][:9]}</div>
                              <div class="player-stat-lbl">Contrato</div>
                            </div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRESUPUESTOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Presupuestos":
    players_df = get_current_players()
    st.markdown('<div class="page-title">PRESUPUESTOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Presupuesto real de cada equipo · Fuente: hoja Teams del Excel</div>', unsafe_allow_html=True)

    # ── Build table using REAL BUDGETS from Excel ─────────────────────────────
    budget_rows = []
    for team_code, budget in TEAM_BUDGETS.items():
        presi = TEAM_PRESIDENT.get(team_code, "?")
        dt    = TEAM_DT.get(team_code, "—")
        budget_rows.append({
            "team":       team_code,
            "full_name":  TEAM_FULL_NAMES.get(team_code, team_code),
            "presidente": presi,
            "dt":         dt,
            "presupuesto": budget,
        })

    team_vals = (pd.DataFrame(budget_rows)
                 .sort_values("presupuesto", ascending=False)
                 .reset_index(drop=True))

    total_b = team_vals["presupuesto"].sum()
    avg_b   = team_vals["presupuesto"].mean()
    top_row = team_vals.iloc[0]
    bot_row = team_vals.iloc[-1]

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Presupuesto Total Liga", fmt_money(total_b))
    b2.metric("Promedio por equipo",    fmt_money(avg_b))
    b3.metric("Mayor presupuesto",      f'{top_row["team"]} — {fmt_money(top_row["presupuesto"])}')
    b4.metric("Menor presupuesto",      f'{bot_row["team"]} — {fmt_money(bot_row["presupuesto"])}')

    st.divider()

    # ── BY PRESIDENT ─────────────────────────────────────────────────────────
    st.markdown("#### 👑 Presupuesto total por Presidente")
    pc1, pc2, pc3 = st.columns(3)
    for col, (presi, pdata) in zip([pc1, pc2, pc3], PRESIDENTS.items()):
        presi_val = team_vals[team_vals["presidente"] == presi]["presupuesto"].sum()
        num_teams = len(pdata["teams"])
        col.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1520,#111827);border:1px solid {pdata['color']}44;
                    border-top:3px solid {pdata['color']};border-radius:14px;padding:16px;text-align:center;">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:3px;color:{pdata['color']};">{presi}</div>
          <div style="font-family:'Space Mono',monospace;font-size:1.1rem;font-weight:700;color:#e8b84b;">{fmt_money(presi_val)}</div>
          <div style="font-size:0.65rem;color:#5a7080;margin-top:4px;">{num_teams} equipos</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── RANKING ROWS ──────────────────────────────────────────────────────────
    for i, row in team_vals.iterrows():
        logo     = TEAM_LOGOS.get(row["team"], "")
        logo_html = f'<img src="{logo}" style="width:30px;height:30px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);">' if logo else ""
        pct      = row["presupuesto"] / team_vals["presupuesto"].max()
        bar_w    = int(pct * 220)
        rank_color = "#e8b84b" if i < 3 else "#3b82f6" if i < 10 else "#5a7080"
        presi_c  = PRESIDENTS.get(row["presidente"], {}).get("color", "#aaa")

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.02);
                    border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:9px 14px;margin-bottom:5px;">
          <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:900;
                       color:{rank_color};min-width:28px;">#{i+1}</span>
          {logo_html}
          <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;color:#dce8f0;min-width:52px;font-size:0.9rem;">{row["team"]}</span>
          <span style="color:{presi_c};font-size:0.62rem;font-weight:700;background:{presi_c}18;padding:1px 6px;border-radius:4px;border:1px solid {presi_c}33;flex-shrink:0;">{row["presidente"]}</span>
          <span style="color:#5a7080;font-size:0.72rem;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["full_name"]} <span style="color:#3a5060;">· {row["dt"]}</span></span>
          <div style="width:220px;background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin-right:10px;flex-shrink:0;">
            <div style="width:{bar_w}px;background:linear-gradient(90deg,#e8b84b,#f0c040);border-radius:4px;height:6px;"></div>
          </div>
          <span style="font-family:'Space Mono',monospace;font-size:0.85rem;font-weight:700;color:#e8b84b;min-width:85px;text-align:right;">{fmt_money(row["presupuesto"])}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    fig = px.bar(
        team_vals, x="presupuesto", y="team", orientation="h",
        title="Presupuesto disponible por equipo (datos del Excel · hoja Teams)",
        labels={"presupuesto": "Presupuesto ($)", "team": "Equipo"},
        color="presupuesto",
        color_continuous_scale=["#1a3a5c", "#e8b84b"],
        text=team_vals["presupuesto"].apply(fmt_money),
    )
    fig.update_layout(
        plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
        font_color="#e2eaf4", title_font_color="#e8b84b",
        yaxis=dict(categoryorder="total ascending"),
        height=700, showlegend=False, coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", textfont_size=9)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CEDIDOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Cedidos":
    players_df = get_current_players()
    st.markdown('<div class="page-title">JUGADORES CEDIDOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Cesiones activas · equipo original → equipo actual</div>', unsafe_allow_html=True)

    loans = players_df[players_df["cesion"].notna()].copy()
    corta = loans[loans["contrato"] == "Cesion Corta"]
    larga = loans[loans["contrato"] == "Cesion Larga"]

    l1, l2, l3 = st.columns(3)
    l1.metric("Total Cedidos",    len(loans))
    l2.metric("Cesión Corta ⚡",  len(corta))
    l3.metric("Cesión Larga 🔗",  len(larga))

    st.divider()

    for _, p in loans.sort_values("price", ascending=False).iterrows():
        pdata    = PLAYER_DATA.get(p["name"], {})
        pos      = pdata.get("pos", "?")
        nat      = pdata.get("nat", "")
        nat_name = pdata.get("nat_name", "")
        sofifa   = pdata.get("sofifa", 0)
        pos_color = POS_COLORS.get(pos, "#667eea")

        photo_url = get_player_photo(p["name"], sofifa)
        flag_url  = get_flag_url(nat)
        orig_team = p["cesion"]
        dest_team = p["team"]
        orig_logo = TEAM_LOGOS.get(orig_team, "")
        dest_logo = TEAM_LOGOS.get(dest_team, "")

        safe_n   = str(p["name"]).replace("'","").replace('"',"")
        fallback = f"https://ui-avatars.com/api/?name={'+'.join(safe_n.split()[:2])}&background=1a2a3a&color=f0c040&size=80&bold=true"
        flag_img = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;">' if flag_url else ""

        orig_logo_html = f'<img src="{orig_logo}" style="width:28px;height:28px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);vertical-align:middle;">' if orig_logo else f'<span style="font-weight:700;color:#e8b84b;">{orig_team}</span>'
        dest_logo_html = f'<img src="{dest_logo}" style="width:28px;height:28px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);vertical-align:middle;">' if dest_logo else f'<span style="font-weight:700;color:#e8b84b;">{dest_team}</span>'

        accent_col  = "#f97316" if p["contrato"] == "Cesion Corta" else "#ef4444"
        badge_label = "⚡ Cesión Corta" if p["contrato"] == "Cesion Corta" else "🔗 Cesión Larga"

        pos_bg  = pos_color + "22"
        pos_bdr = pos_color + "44"
        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0d1b2a,#0a1a28);border:1px solid rgba(255,255,255,0.07);
                    border-left:3px solid {accent_col};border-radius:12px;padding:14px 16px;margin-bottom:8px;
                    display:flex;align-items:center;gap:14px;">
          <img src="{photo_url}" style="width:54px;height:54px;border-radius:50%;object-fit:cover;border:2px solid {accent_col}66;flex-shrink:0;background:#0a1520;"
               onerror="this.onerror=null;this.src='{fallback}'">
          <div style="flex:1;min-width:0;overflow:hidden;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;flex-wrap:wrap;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;font-weight:800;color:#f0f4f8;white-space:nowrap;">{p["name"]}</span>
              <span style="background:{pos_bg};color:{pos_color};border:1px solid {pos_bdr};font-size:0.55rem;font-weight:900;padding:1px 6px;border-radius:3px;">{pos}</span>
              {flag_img}<span style="font-size:0.65rem;color:#5a7080;">{nat_name}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              {orig_logo_html}
              <span style="font-size:0.75rem;font-weight:700;color:#e2eaf4;">{orig_team}</span>
              <span style="font-size:0.9rem;color:{accent_col};font-weight:900;">→</span>
              {dest_logo_html}
              <span style="font-size:0.75rem;font-weight:700;color:#e2eaf4;">{dest_team}</span>
              <span style="font-size:0.62rem;background:{accent_col}22;color:{accent_col};border:1px solid {accent_col}44;padding:1px 7px;border-radius:8px;font-weight:800;">{badge_label}</span>
            </div>
          </div>
          <div style="text-align:right;flex-shrink:0;">
            <div style="font-family:'Space Mono',monospace;font-size:0.9rem;font-weight:700;color:#e8b84b;">{fmt_money(p["price"])}</div>
            <div style="font-size:0.6rem;color:#5a7080;margin-top:2px;">Cláusula: {fmt_money(p["clausula"])}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    if len(loans) > 0:
        st.divider()
        st.markdown("#### Flujo de cesiones")
        all_nodes = list(set(loans["cesion"].tolist() + loans["team"].tolist()))
        node_idx  = {n: i for i, n in enumerate(all_nodes)}
        source = [node_idx[r["cesion"]] for _, r in loans.iterrows()]
        target = [node_idx[r["team"]]   for _, r in loans.iterrows()]
        values = [r["price"] / 1e6      for _, r in loans.iterrows()]

        fig_sankey = go.Figure(go.Sankey(
            node=dict(pad=12, thickness=16, label=all_nodes, color=["#e8b84b"] * len(all_nodes)),
            link=dict(source=source, target=target, value=values, color="rgba(232,184,75,0.18)")
        ))
        fig_sankey.update_layout(
            title="Origen → Destino [tamaño = valor M$]",
            paper_bgcolor="#060a0f", font_color="#e2eaf4",
            title_font_color="#e8b84b", height=400
        )
        st.plotly_chart(fig_sankey, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Estadísticas":
    players_df = get_current_players()
    st.markdown('<div class="page-title">ESTADÍSTICAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Distribuciones · Rankings · Contratos</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribución valores", "🏆 Rankings", "🗂️ Contratos", "🌍 Nacionalidades"])

    with tab1:
        top20 = players_df.nlargest(20, "price").copy()
        fig_top = go.Figure()
        for _, row in top20.iterrows():
            pos_color = POS_COLORS.get(row["pos"], "#667eea")
            fig_top.add_trace(go.Bar(
                x=[row["price"]], y=[row["name"]],
                orientation="h",
                marker_color=pos_color,
                text=fmt_money(row["price"]),
                textposition="outside",
                name=row["pos"],
                showlegend=False,
                hovertemplate=f"<b>{row['name']}</b><br>{row['team']}<br>{fmt_money(row['price'])}<extra></extra>",
            ))
        fig_top.update_layout(
            title="Top 20 jugadores más valiosos",
            plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
            font_color="#e2eaf4", title_font_color="#e8b84b",
            yaxis=dict(categoryorder="total ascending"),
            height=600, margin=dict(l=10, r=80, t=40, b=10),
            barmode="overlay",
        )
        st.plotly_chart(fig_top, use_container_width=True)

        fig_hist = px.histogram(players_df, x="price", nbins=40,
            labels={"price": "Precio ($)", "count": "Jugadores"},
            title="Distribución de valores de mercado",
            color_discrete_sequence=["#e8b84b"])
        fig_hist.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                               font_color="#e2eaf4", title_font_color="#e8b84b")
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab2:
        team_stats = (players_df.groupby("team")
            .agg(valor_total=("price","sum"), jugadores=("name","count"), avg_valor=("price","mean"))
            .reset_index().sort_values("valor_total", ascending=False))
        fig_teams = px.bar(team_stats, x="team", y="valor_total",
            title="Valor total de plantilla por equipo",
            labels={"team":"Equipo","valor_total":"Valor Total ($)"},
            color="valor_total", color_continuous_scale=["#1a3a5c","#e8b84b"],
            text=team_stats["valor_total"].apply(fmt_money))
        fig_teams.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
            font_color="#e2eaf4", title_font_color="#e8b84b", height=450, coloraxis_showscale=False)
        fig_teams.update_traces(textposition="outside", textfont_size=8)
        st.plotly_chart(fig_teams, use_container_width=True)

        pos_stats = players_df.groupby("pos").agg(total=("price","sum"), count=("name","count")).reset_index()
        fig_pos = px.bar(pos_stats, x="pos", y="total",
            title="Valor total por posición", labels={"pos":"Posición","total":"Valor ($)"},
            color="pos", color_discrete_map=POS_COLORS, text=pos_stats["total"].apply(fmt_money))
        fig_pos.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
            font_color="#e2eaf4", title_font_color="#e8b84b", showlegend=False)
        fig_pos.update_traces(textposition="outside")
        st.plotly_chart(fig_pos, use_container_width=True)

    with tab3:
        contrato_counts = players_df["contrato"].value_counts().reset_index()
        contrato_counts.columns = ["contrato","count"]
        fig_pie = px.pie(contrato_counts, values="count", names="contrato",
            title="Distribución de tipos de contrato",
            color="contrato", color_discrete_map=CONTRATO_COLORS)
        fig_pie.update_layout(paper_bgcolor="#060a0f", font_color="#e2eaf4", title_font_color="#e8b84b")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab4:
        nat_counts = players_df.groupby(["nat","nat_name"]).size().reset_index(name="count")
        nat_counts = nat_counts.sort_values("count", ascending=False).head(20)
        cols = st.columns(4)
        for i, (_, row) in enumerate(nat_counts.iterrows()):
            with cols[i % 4]:
                flag_url = get_flag_url(row["nat"])
                flag_html = f'<img src="{flag_url}" style="width:24px;height:18px;object-fit:cover;border-radius:3px;vertical-align:middle;margin-right:6px;">' if flag_url else ""
                st.markdown(
                    f'<div style="display:flex;align-items:center;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);'
                    f'border-radius:8px;padding:7px 10px;margin-bottom:5px;">'
                    f'{flag_html}<span style="font-size:0.78rem;color:#dce8f0;flex:1;">{row["nat_name"]}</span>'
                    f'<span style="font-family:monospace;font-size:0.85rem;font-weight:700;color:#e8b84b;">{row["count"]}</span>'
                    f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VENTANA DE FICHAJES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Ventana de Fichajes":
    players_df = get_current_players()
    st.markdown('<div class="page-title">VENTANA DE FICHAJES</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Negociaciones entre presidentes · Timer 30 días</div>', unsafe_allow_html=True)

    # ── ADMIN: Timer control ──────────────────────────────────────────────────
    with st.expander("⚙️ Control Administrador (Timer)", expanded=False):
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            if st.button("🟢 Iniciar Ventana de 30 días", use_container_width=True):
                end_date = (datetime.now() + timedelta(days=30)).isoformat()
                set_state("transfer_window_end", end_date)
                set_state("transfer_window_active", True)
                st.success("¡Ventana de fichajes iniciada! Termina en 30 días.")
                st.rerun()
        with col_a2:
            if st.button("🔴 Cerrar Ventana", use_container_width=True):
                set_state("transfer_window_active", False)
                st.warning("Ventana de fichajes cerrada.")
                st.rerun()
        with col_a3:
            if st.button("🗑️ Resetear Transferencias", use_container_width=True):
                set_state("offers", [])
                set_state("completed_transfers", [])
                st.success("Transferencias reseteadas.")
                st.rerun()

    # ── TIMER ─────────────────────────────────────────────────────────────────
    window_active = get_state("transfer_window_active", False)
    window_end_str = get_state("transfer_window_end", None)
    window_open = False

    if window_active and window_end_str:
        try:
            end_dt = datetime.fromisoformat(window_end_str)
            now    = datetime.now()
            remaining = end_dt - now
            if remaining.total_seconds() > 0:
                window_open = True
                days_left    = remaining.days
                hours_left   = remaining.seconds // 3600
                minutes_left = (remaining.seconds % 3600) // 60
                timer_html = f"""
                <div class="timer-container">
                  <div class="timer-label">⏱ VENTANA DE FICHAJES — TIEMPO RESTANTE</div>
                  <div class="timer-value">{days_left}d {hours_left:02d}h {minutes_left:02d}m</div>
                  <div style="font-size:0.7rem;color:#5a7080;margin-top:6px;">Cierre: {end_dt.strftime('%d/%m/%Y %H:%M')}</div>
                </div>
                """
                st.markdown(timer_html, unsafe_allow_html=True)
            else:
                # Time expired — auto close and generate excel
                set_state("transfer_window_active", False)
                st.markdown('<div class="timer-container"><div class="timer-expired">⛔ VENTANA CERRADA</div><div style="font-size:0.8rem;color:#5a7080;margin-top:6px;">El periodo de fichajes ha terminado</div></div>', unsafe_allow_html=True)
        except:
            pass
    elif not window_active:
        st.markdown('<div style="background:#0d1520;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px;text-align:center;margin-bottom:20px;"><div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#5a7080;">⏸ VENTANA CERRADA</div><div style="font-size:0.75rem;color:#3a5060;margin-top:4px;">El administrador debe iniciar la ventana de fichajes</div></div>', unsafe_allow_html=True)

    st.divider()

    # ── SELECTOR DE PRESIDENTE ────────────────────────────────────────────────
    presi_sel = st.selectbox("🧑‍💼 Actuar como Presidente", ["JNKA", "MATI", "MAXI"], key="presi_selector")
    presi_color = PRESIDENTS[presi_sel]["color"]
    my_teams = PRESIDENTS[presi_sel]["teams"]

    st.markdown(f"""
    <div style="background:{presi_color}11;border:1px solid {presi_color}33;border-radius:10px;padding:10px 16px;margin-bottom:16px;display:flex;align-items:center;gap:10px;">
      <span style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:2px;color:{presi_color};">{presi_sel}</span>
      <span style="font-size:0.75rem;color:#7a9db0;">Equipos: {', '.join(my_teams)}</span>
    </div>
    """, unsafe_allow_html=True)

    tab_enviar, tab_recibidas, tab_mis_ofertas, tab_historial, tab_excel = st.tabs([
        "📤 Nueva Oferta", "📥 Ofertas Recibidas", "📋 Mis Ofertas", "✅ Historial", "📊 Exportar Excel"
    ])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: NUEVA OFERTA
    # ──────────────────────────────────────────────────────────────────────────
    with tab_enviar:
        if not window_open:
            st.warning("⛔ La ventana de fichajes no está activa. Solo el administrador puede abrirla.")
        else:
            st.markdown("#### 📤 Enviar oferta de fichaje")
            
            # Select the selling team (NOT owned by current president)
            rival_teams = [t for t in players_df["team"].unique() if t not in my_teams]
            rival_team = st.selectbox("🏟️ Equipo del que quieres fichar", sorted(rival_teams), key="rival_team_sel")
            
            # Players from that team
            squad_rival = players_df[players_df["team"] == rival_team].sort_values("price", ascending=False)
            player_options = squad_rival["name"].tolist()
            
            if player_options:
                player_sel = st.selectbox("⚽ Jugador", player_options, key="player_offer_sel")
                player_info = squad_rival[squad_rival["name"] == player_sel].iloc[0]
                
                # Show player info
                pdata = PLAYER_DATA.get(player_sel, {})
                pos_color = POS_COLORS.get(pdata.get("pos","?"), "#667eea")
                ci1, ci2, ci3, ci4 = st.columns(4)
                ci1.metric("Valor Mercado", fmt_money(player_info["price"]))
                ci2.metric("Renovación", fmt_money(player_info["renovation"]))
                ci3.metric("Cláusula", fmt_money(player_info["clausula"]))
                ci4.metric("Posición", pdata.get("pos","?"))

                st.markdown("---")
                
                # Offer type
                is_cedido = pd.notna(player_info.get("cesion"))
                tipo_options = ["Compra"]
                
                if not is_cedido:
                    tipo_options += ["Cesion Corta", "Cesion Larga"]
                else:
                    tipo_options += ["Pagar Cesion"]
                    st.info(f"Este jugador está cedido de **{player_info['cesion']}** a **{player_info['team']}**. Puedes 'Pagar Cesion' para hacerlo definitivo.")
                
                tipo_oferta = st.selectbox("💼 Tipo de operación", tipo_options, key="tipo_oferta_sel")
                
                # Destination team (one of my teams)
                dest_team = st.selectbox("🏟️ Mi equipo que recibe al jugador", sorted(my_teams), key="dest_team_sel")
                
                # Offer amount
                default_offer = player_info["price"]
                if tipo_oferta == "Cesion Corta":
                    default_offer = int(player_info["price"] * 0.15)
                elif tipo_oferta == "Cesion Larga":
                    default_offer = int(player_info["price"] * 0.30)
                elif tipo_oferta == "Pagar Cesion":
                    default_offer = int(player_info["renovation"])
                
                offer_amount = st.number_input(
                    f"💰 Monto de oferta ($)", 
                    min_value=0, 
                    value=default_offer, 
                    step=500000,
                    format="%d",
                    key="offer_amount_input"
                )
                
                msg = st.text_area("💬 Mensaje (opcional)", placeholder="Escribe un mensaje para el otro presidente...", key="offer_msg", max_chars=300)
                
                col_btn1, col_btn2 = st.columns([2,1])
                with col_btn1:
                    if st.button("📤 Enviar Oferta", use_container_width=True, type="primary"):
                        # Validation
                        if rival_team in my_teams:
                            st.error("No puedes fichar de tu propio equipo.")
                        else:
                            rival_presi = TEAM_PRESIDENT.get(rival_team, "?")
                            new_offer = {
                                "id": f"offer_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                                "from_presi": presi_sel,
                                "to_presi": rival_presi,
                                "from_team": dest_team,
                                "to_team": rival_team,
                                "player": player_sel,
                                "tipo": tipo_oferta,
                                "amount": offer_amount,
                                "message": msg,
                                "status": "Pendiente",
                                "created_at": datetime.now().isoformat(),
                                "response_msg": ""
                            }
                            offers = get_state("offers", [])
                            offers.append(new_offer)
                            set_state("offers", offers)
                            st.success(f"✅ Oferta enviada a **{rival_presi}** por **{player_sel}** ({tipo_oferta}) por {fmt_money(offer_amount)}")
                            st.rerun()
                with col_btn2:
                    st.caption(f"Precio sugerido: {fmt_money(default_offer)}")
            else:
                st.info("Este equipo no tiene jugadores disponibles.")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: OFERTAS RECIBIDAS
    # ──────────────────────────────────────────────────────────────────────────
    with tab_recibidas:
        if not window_open:
            st.warning("⛔ La ventana de fichajes no está activa.")
        else:
            st.markdown("#### 📥 Ofertas recibidas para mis equipos")
            all_offers = get_state("offers", [])
            my_received = [o for o in all_offers if o["to_presi"] == presi_sel and o["status"] == "Pendiente"]
            
            if not my_received:
                st.info("No tienes ofertas pendientes.")
            else:
                for offer in my_received:
                    from_presi_c = PRESIDENTS.get(offer["from_presi"], {}).get("color", "#aaa")
                    tipo_color = {"Compra": "#e8b84b", "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444", "Pagar Cesion": "#22c55e"}.get(offer["tipo"], "#aaa")
                    
                    pdata = PLAYER_DATA.get(offer["player"], {})
                    pos   = pdata.get("pos", "?")
                    sofifa = pdata.get("sofifa", 0)
                    photo_url = get_player_photo(offer["player"], sofifa)
                    safe_n = str(offer["player"]).replace("'","").replace('"',"")
                    fallback = f"https://ui-avatars.com/api/?name={'+'.join(safe_n.split()[:2])}&background=1a2a3a&color=f0c040&size=80&bold=true"
                    pos_color = POS_COLORS.get(pos, "#667eea")
                    
                    # Find player current price
                    p_row = players_df[players_df["name"] == offer["player"]]
                    market_val = p_row["price"].values[0] if len(p_row) > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background:#0d1520;border:1px solid {tipo_color}44;border-left:3px solid {tipo_color};
                                border-radius:12px;padding:14px 16px;margin-bottom:8px;">
                      <div style="display:flex;align-items:center;gap:12px;">
                        <img src="{photo_url}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;flex-shrink:0;"
                             onerror="this.onerror=null;this.src='{fallback}'">
                        <div style="flex:1;min-width:0;">
                          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                            <span style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:800;color:#f0f4f8;">{offer['player']}</span>
                            <span style="background:{pos_color}22;color:{pos_color};font-size:0.55rem;font-weight:900;padding:1px 5px;border-radius:3px;">{pos}</span>
                            <span style="background:{tipo_color}22;color:{tipo_color};font-size:0.62rem;font-weight:800;padding:2px 7px;border-radius:5px;border:1px solid {tipo_color}44;">{offer['tipo']}</span>
                          </div>
                          <div style="font-size:0.75rem;color:#7a9db0;margin-top:2px;">
                            De: <span style="color:{from_presi_c};font-weight:700;">{offer['from_presi']}</span> ({offer['from_team']}) → Tu equipo: <b style="color:#e2eaf4;">{offer['to_team']}</b>
                          </div>
                          <div style="font-size:0.72rem;color:#5a7080;margin-top:2px;">Valor mercado: {fmt_money(market_val)} · Oferta: <span style="color:#e8b84b;font-weight:700;font-family:monospace;">{fmt_money(offer['amount'])}</span></div>
                          {f'<div style="font-size:0.7rem;color:#7a9db0;margin-top:3px;font-style:italic;">"{offer["message"]}"</div>' if offer.get("message") else ""}
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_acc, col_rej, col_msg = st.columns([1, 1, 3])
                    resp_key = f"resp_{offer['id']}"
                    resp_msg = col_msg.text_input("Respuesta (opcional)", key=resp_key, placeholder="Comentario...")
                    
                    with col_acc:
                        if st.button(f"✅ Aceptar", key=f"acc_{offer['id']}", use_container_width=True):
                            # Update offer
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Aceptada"
                                    o["response_msg"] = resp_msg
                            set_state("offers", all_offers2)
                            
                            # Execute transfer
                            completed = get_state("completed_transfers", [])
                            completed.append({
                                "player": offer["player"],
                                "from_team": offer["to_team"],
                                "to_team": offer["from_team"],
                                "tipo": offer["tipo"],
                                "amount": offer["amount"],
                                "from_presi": offer["to_presi"],
                                "to_presi": offer["from_presi"],
                                "date": datetime.now().isoformat()
                            })
                            set_state("completed_transfers", completed)
                            st.success(f"✅ Oferta aceptada. {offer['player']} → {offer['from_team']}")
                            st.rerun()
                    
                    with col_rej:
                        if st.button(f"❌ Rechazar", key=f"rej_{offer['id']}", use_container_width=True):
                            all_offers2 = get_state("offers", [])
                            for o in all_offers2:
                                if o["id"] == offer["id"]:
                                    o["status"] = "Rechazada"
                                    o["response_msg"] = resp_msg
                            set_state("offers", all_offers2)
                            st.warning(f"Oferta por {offer['player']} rechazada.")
                            st.rerun()
                    
                    st.markdown("---")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: MIS OFERTAS
    # ──────────────────────────────────────────────────────────────────────────
    with tab_mis_ofertas:
        st.markdown("#### 📋 Ofertas que he enviado")
        all_offers = get_state("offers", [])
        my_sent = [o for o in all_offers if o["from_presi"] == presi_sel]
        
        if not my_sent:
            st.info("No has enviado ninguna oferta todavía.")
        else:
            for offer in sorted(my_sent, key=lambda x: x["created_at"], reverse=True):
                status_color = {"Pendiente": "#f59e0b", "Aceptada": "#22c55e", "Rechazada": "#ef4444"}.get(offer["status"], "#aaa")
                status_icon  = {"Pendiente": "⏳", "Aceptada": "✅", "Rechazada": "❌"}.get(offer["status"], "❓")
                tipo_color   = {"Compra": "#e8b84b", "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444", "Pagar Cesion": "#22c55e"}.get(offer["tipo"], "#aaa")
                to_presi_c   = PRESIDENTS.get(offer["to_presi"], {}).get("color", "#aaa")
                
                st.markdown(f"""
                <div style="background:#0d1520;border:1px solid {status_color}33;border-left:3px solid {status_color};
                            border-radius:10px;padding:12px 16px;margin-bottom:7px;">
                  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:800;color:#f0f4f8;">{offer['player']}</span>
                    <span style="background:{tipo_color}22;color:{tipo_color};font-size:0.62rem;font-weight:800;padding:2px 7px;border-radius:5px;">{offer['tipo']}</span>
                    <span style="background:{status_color}22;color:{status_color};font-size:0.62rem;font-weight:800;padding:2px 7px;border-radius:5px;">{status_icon} {offer['status']}</span>
                  </div>
                  <div style="font-size:0.73rem;color:#7a9db0;margin-top:4px;">
                    Para: <span style="color:{to_presi_c};font-weight:700;">{offer['to_presi']}</span> ({offer['to_team']}) · Oferta: 
                    <span style="color:#e8b84b;font-weight:700;font-family:monospace;">{fmt_money(offer['amount'])}</span>
                  </div>
                  {f'<div style="font-size:0.68rem;color:#5a7080;margin-top:2px;font-style:italic;">Respuesta: "{offer["response_msg"]}"</div>' if offer.get("response_msg") else ""}
                </div>
                """, unsafe_allow_html=True)
                
                # Allow cancelling pending offers
                if offer["status"] == "Pendiente":
                    if st.button(f"🗑️ Cancelar oferta por {offer['player']}", key=f"cancel_{offer['id']}"):
                        all_offers2 = get_state("offers", [])
                        all_offers2 = [o for o in all_offers2 if o["id"] != offer["id"]]
                        set_state("offers", all_offers2)
                        st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: HISTORIAL
    # ──────────────────────────────────────────────────────────────────────────
    with tab_historial:
        st.markdown("#### ✅ Transferencias completadas")
        completed = get_state("completed_transfers", [])
        
        if not completed:
            st.info("Aún no se han completado transferencias.")
        else:
            for t in sorted(completed, key=lambda x: x["date"], reverse=True):
                tipo_color = {"Compra": "#e8b84b", "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444", "Pagar Cesion": "#22c55e"}.get(t["tipo"], "#aaa")
                from_presi_c = PRESIDENTS.get(t["from_presi"], {}).get("color", "#aaa")
                to_presi_c   = PRESIDENTS.get(t["to_presi"], {}).get("color", "#aaa")
                
                # logos
                ol = TEAM_LOGOS.get(t["from_team"], "")
                dl = TEAM_LOGOS.get(t["to_team"], "")
                ol_html = f'<img src="{ol}" style="width:22px;height:22px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if ol else ""
                dl_html = f'<img src="{dl}" style="width:22px;height:22px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if dl else ""
                
                try:
                    date_str = datetime.fromisoformat(t["date"]).strftime("%d/%m/%Y %H:%M")
                except:
                    date_str = t.get("date","")
                
                st.markdown(f"""
                <div style="background:#0d1520;border:1px solid rgba(34,197,94,0.2);border-left:3px solid #22c55e;
                            border-radius:10px;padding:12px 16px;margin-bottom:7px;">
                  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:800;color:#f0f4f8;">⚽ {t['player']}</span>
                    <span style="background:{tipo_color}22;color:{tipo_color};font-size:0.62rem;font-weight:800;padding:2px 7px;border-radius:5px;">{t['tipo']}</span>
                    <span style="font-family:monospace;font-size:0.8rem;color:#e8b84b;font-weight:700;">{fmt_money(t['amount'])}</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:6px;margin-top:5px;flex-wrap:wrap;">
                    {ol_html} <span style="font-size:0.72rem;color:{from_presi_c};font-weight:600;">{t['from_team']} ({t['from_presi']})</span>
                    <span style="color:#22c55e;font-weight:900;">→</span>
                    {dl_html} <span style="font-size:0.72rem;color:{to_presi_c};font-weight:600;">{t['to_team']} ({t['to_presi']})</span>
                    <span style="color:#3a5060;font-size:0.65rem;margin-left:auto;">{date_str}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # TAB: EXPORTAR EXCEL
    # ──────────────────────────────────────────────────────────────────────────
    with tab_excel:
        st.markdown("#### 📊 Exportar estado actual de equipos")
        st.info("Genera un Excel con el estado actual de todos los jugadores, incluyendo transferencias completadas durante la ventana de fichajes.")
        
        current_df = get_current_players()
        completed  = get_state("completed_transfers", [])
        
        # Stats
        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Jugadores totales", len(current_df))
        ec2.metric("Transferencias completadas", len(completed))
        ec3.metric("Cedidos activos", int(current_df["cesion"].notna().sum()))
        
        if st.button("⬇️ Descargar Excel", use_container_width=True, type="primary"):
            # Build export DataFrame
            export_rows = []
            for _, p in current_df.iterrows():
                presi = TEAM_PRESIDENT.get(p["team"], "?")
                pdata = PLAYER_DATA.get(p["name"], {})
                row = {
                    "Jugador": p["name"],
                    "Posición": pdata.get("pos", "?"),
                    "Nacionalidad": pdata.get("nat_name", ""),
                    "Equipo Actual": p["team"],
                    "Equipo Completo": TEAM_FULL_NAMES.get(p["team"], ""),
                    "Presidente": presi,
                    "Equipo Original (Cesion)": p.get("cesion") if pd.notna(p.get("cesion")) else "",
                    "Tipo Contrato": p["contrato"],
                    "Valor Mercado ($)": p["price"],
                    "Renovación ($)": p["renovation"],
                    "Cláusula ($)": p["clausula"],
                }
                export_rows.append(row)
            
            export_df = pd.DataFrame(export_rows).sort_values(["Equipo Actual", "Valor Mercado ($)"], ascending=[True, False])
            
            # Transfers sheet
            transfer_rows = []
            for t in completed:
                transfer_rows.append({
                    "Jugador": t["player"],
                    "Tipo": t["tipo"],
                    "Monto ($)": t["amount"],
                    "Equipo Origen": t["from_team"],
                    "Presidente Origen": t.get("from_presi",""),
                    "Equipo Destino": t["to_team"],
                    "Presidente Destino": t.get("to_presi",""),
                    "Fecha": t.get("date",""),
                })
            transfer_df = pd.DataFrame(transfer_rows) if transfer_rows else pd.DataFrame(columns=["Jugador","Tipo","Monto ($)","Equipo Origen","Equipo Destino","Fecha"])
            
            # Team summary sheet
            team_summary = export_df.groupby(["Equipo Actual","Equipo Completo","Presidente"]).agg(
                Jugadores=("Jugador","count"),
                Valor_Total=("Valor Mercado ($)","sum")
            ).reset_index().sort_values("Valor_Total", ascending=False)
            team_summary.columns = ["Equipo","Equipo Completo","Presidente","Jugadores","Valor Total ($)"]
            
            # Write to Excel in memory
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                export_df.to_excel(writer, sheet_name="Plantillas", index=False)
                transfer_df.to_excel(writer, sheet_name="Transferencias", index=False)
                team_summary.to_excel(writer, sheet_name="Resumen Equipos", index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Descargar MMJ_League_Estado.xlsx",
                data=buffer,
                file_name=f"MMJ_League_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.success("✅ Excel generado con 3 hojas: Plantillas, Transferencias y Resumen por Equipo.")
