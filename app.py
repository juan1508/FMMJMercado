import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

  /* Player card */
  .player-card {
    background: linear-gradient(160deg, #0d1b2a 0%, #0a1a28 60%, #071018 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 0;
    overflow: hidden;
    margin-bottom: 10px;
    transition: border-color 0.2s, transform 0.15s;
    position: relative;
  }
  .player-card:hover { border-color: rgba(232,184,75,0.4); transform: translateY(-2px); }

  .player-card-header { padding: 14px 14px 10px 14px; display: flex; align-items: center; gap: 12px; }
  .player-photo { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(232,184,75,0.4); flex-shrink: 0; background: #0a1520; }
  .player-info { flex: 1; min-width: 0; }
  .player-name { font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; font-weight: 800; color: #f0f4f8; line-height: 1.1; margin-bottom: 2px; }
  .player-pos-badge { display: inline-block; font-size: 0.58rem; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; margin-right: 4px; }
  .player-nat { display: flex; align-items: center; gap: 5px; margin-top: 4px; font-size: 0.7rem; color: #7a9db0; }
  .player-stats-bar { background: rgba(255,255,255,0.03); border-top: 1px solid rgba(255,255,255,0.05); padding: 8px 14px; display: flex; justify-content: space-around; }
  .player-stat { text-align: center; }
  .player-stat-val { font-family: 'Barlow Condensed', sans-serif; font-size: 1.05rem; font-weight: 900; color: #e8b84b; line-height: 1; }
  .player-stat-lbl { font-size: 0.55rem; color: #5a8090; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px; }

  /* Loan badge */
  .loan-badge { position: absolute; top: 10px; right: 10px; padding: 2px 7px; border-radius: 10px; font-size: 0.6rem; font-weight: 900; letter-spacing: 0.5px; }
  .loan-corta { background: rgba(249,115,22,0.18); border: 1px solid rgba(249,115,22,0.4); color: #f97316; }
  .loan-larga { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }

  /* Team shield in card */
  .team-shield { width: 26px; height: 26px; object-fit: contain; border-radius: 50%; background: rgba(255,255,255,0.04); flex-shrink: 0; }

  /* Price tag */
  .price-gold { color: #e8b84b; font-family: 'Space Mono', monospace; font-weight: 700; }
  .price-green { color: #22c55e; font-family: 'Space Mono', monospace; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0d1520 !important; border-right: 1px solid rgba(255,255,255,0.07); }
  [data-testid="stSidebar"] * { color: #e2eaf4 !important; }

  hr { border-color: rgba(255,255,255,0.07) !important; }

  /* Table rows */
  .player-row {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 8px 14px; margin-bottom: 5px;
    transition: border-color 0.15s;
  }
  .player-row:hover { border-color: rgba(232,184,75,0.25); }

  /* Cedido arrow */
  .cedido-arrow { color: #f97316; font-size: 0.75rem; font-weight: 700; }

  /* Contract badges */
  .badge-1s { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-2s { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-cc { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.35); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }
  .badge-cl { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.62rem; font-weight: 700; }

  /* Equipo card */
  .equipo-card {
    background: #0d1520;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 3px solid #e8b84b;
  }
</style>
""", unsafe_allow_html=True)


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


# ── PLAYER_DATA del league manager (solo jugadores en la app) ────────────────
# sofifa IDs + pos + nacionalidad para fotos y banderas
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
    "A. Balde":            {"pos": "DEF", "nat": "es", "nat_name": "España",         "sofifa": 263578},
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
}

# ── TEAM LOGOS ───────────────────────────────────────────────────────────────
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

POS_COLORS = {"GK": "#f59e0b", "DEF": "#3b82f6", "MID": "#22c55e", "FWD": "#ef4444"}

CONTRATO_COLORS = {
    "1 Season": "#22c55e", "2 Season": "#3b82f6",
    "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444"
}

PRESI_COLORS = {"JNKA": "#e8b84b", "MATI": "#3b82f6", "MAXI": "#a78bfa"}


# ── Full player data (market data + league data merged) ──────────────────────
@st.cache_data
def load_full_data():
    # All players from the market app — only those that exist in PLAYER_DATA
    raw = [
        # team = current team (where they play, including loan destination)
        # cesion = original team (only for loaned players, from Excel)
        # For loaned players: team=destination, cesion=original_owner
        {"name":"M. Salah",       "team":"ATL",  "price":104000000,"renovation":52000000, "clausula":468000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Rodri",          "team":"TOR",  "price":115500000,"renovation":57750000, "clausula":519750000, "contrato":"1 Season",     "cesion":None},
        # Mbappé: juega en LAFC (cedido), su equipo original/dueño es NSH
        {"name":"K. Mbappé",      "team":"LAFC", "price":211000000,"renovation":105500000,"clausula":949500000, "contrato":"Cesion Corta", "cesion":"NSH"},
        {"name":"Vini Jr.",       "team":"ATX",  "price":193500000,"renovation":96750000, "clausula":870750000, "contrato":"1 Season",     "cesion":None},
        {"name":"E. Haaland",     "team":"SEA",  "price":196000000,"renovation":98000000, "clausula":882000000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Kane",        "team":"COL",  "price":117500000,"renovation":58750000, "clausula":528750000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Bellingham",  "team":"NYC",  "price":174500000,"renovation":87250000, "clausula":785250000, "contrato":"1 Season",     "cesion":None},
        {"name":"V. van Dijk",    "team":"LA",   "price":77500000, "renovation":38750000, "clausula":348750000, "contrato":"1 Season",     "cesion":None},
        # Lewandowski: juega en MIA (cedido largo), dueño MTL
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
        # Sommer: juega en ORL (cedido largo), dueño ATL
        {"name":"Y. Sommer",      "team":"ORL",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"Cesion Larga", "cesion":"ATL"},
        {"name":"Rodrygo",        "team":"LAFC", "price":232000000,"renovation":116000000,"clausula":1044000000,"contrato":"1 Season",     "cesion":None},
        {"name":"H. Son",         "team":"ATX",  "price":56500000, "renovation":28250000, "clausula":254250000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Benzema",     "team":"NE",   "price":26000000, "renovation":13000000, "clausula":117000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Álvarez",     "team":"SDFC", "price":94000000, "renovation":47000000, "clausula":423000000, "contrato":"2 Season",     "cesion":None},
        {"name":"E. Haaland",     "team":"SEA",  "price":196000000,"renovation":98000000, "clausula":882000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Isak",        "team":"SEA",  "price":89500000, "renovation":44750000, "clausula":402750000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Dybala",      "team":"LAFC", "price":81000000, "renovation":40500000, "clausula":364500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bruno Fernandes","team":"MTL",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"1 Season",     "cesion":None},
        # Foden: juega en NE (cedido largo), dueño PHI
        {"name":"P. Foden",       "team":"NE",   "price":88000000, "renovation":44000000, "clausula":396000000, "contrato":"Cesion Larga", "cesion":"PHI"},
        {"name":"F. de Jong",     "team":"SKC",  "price":77500000, "renovation":38750000, "clausula":348750000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Xhaka",       "team":"CIN",  "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Mac Allister","team":"MIA",  "price":84500000, "renovation":42250000, "clausula":380250000, "contrato":"1 Season",     "cesion":None},
        {"name":"H. Çalhanoğlu",  "team":"VAN",  "price":57000000, "renovation":28500000, "clausula":256500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Rúben Dias",     "team":"MIA",  "price":68500000, "renovation":34250000, "clausula":308250000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Alexander-Arnold","team":"SKC","price":74000000,"renovation":37000000,"clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Hernández",   "team":"ATL",  "price":73000000, "renovation":36500000, "clausula":328500000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Koundé",      "team":"ORL",  "price":83000000, "renovation":41500000, "clausula":373500000, "contrato":"1 Season",     "cesion":None},
        # Hakimi: juega en ORL (cedido corto), dueño DCU
        {"name":"A. Hakimi",      "team":"ORL",  "price":78500000, "renovation":39250000, "clausula":353250000, "contrato":"Cesion Corta", "cesion":"DCU"},
        {"name":"D. Carvajal",    "team":"LA",   "price":47000000, "renovation":23500000, "clausula":211500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bremer",         "team":"POR",  "price":72500000, "renovation":36250000, "clausula":326250000, "contrato":"1 Season",     "cesion":None},
        {"name":"E. Martínez",    "team":"MTL",  "price":49000000, "renovation":24500000, "clausula":220500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Ederson",        "team":"SEA",  "price":45000000, "renovation":22500000, "clausula":202500000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Kobel",       "team":"HOU",  "price":68500000, "renovation":34250000, "clausula":308250000, "contrato":"1 Season",     "cesion":None},
        {"name":"David Raya",     "team":"HOU",  "price":54000000, "renovation":27000000, "clausula":243000000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Díaz",        "team":"NHS",  "price":118500000,"renovation":59250000, "clausula":533250000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Mahrez",      "team":"VAN",  "price":33500000, "renovation":16750000, "clausula":150750000, "contrato":"1 Season",     "cesion":None},
        # Kvaratskhelia: juega en CLT (cedido largo), dueño CHI
        {"name":"K. Kvaratskhelia","team":"CLT", "price":81000000, "renovation":40500000, "clausula":364500000, "contrato":"Cesion Larga", "cesion":"CHI"},
        {"name":"Rafael Leão",    "team":"LA",   "price":86000000, "renovation":43000000, "clausula":387000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Cristiano Ronaldo","team":"RBNY","price":18500000,"renovation":9250000,  "clausula":83250000,  "contrato":"1 Season",     "cesion":None},
        {"name":"Nico Williams",  "team":"VAN",  "price":78500000, "renovation":39250000, "clausula":353250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Olise",       "team":"COL",  "price":75000000, "renovation":37500000, "clausula":337500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bernardo Silva", "team":"DAL",  "price":77000000, "renovation":38500000, "clausula":346500000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Milinković-Savić","team":"MTL","price":54500000,"renovation":27250000,"clausula":245250000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Olmo",        "team":"VAN",  "price":66500000, "renovation":33250000, "clausula":299250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Casemiro",       "team":"MIA",  "price":36000000, "renovation":18000000, "clausula":162000000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Modrić",      "team":"LA",   "price":39000000, "renovation":19500000, "clausula":175500000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Kanté",       "team":"CIN",  "price":26500000, "renovation":13250000, "clausula":119250000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Caicedo",     "team":"SJ",   "price":68000000, "renovation":34000000, "clausula":306000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Bruno Guimarães","team":"SDFC", "price":56500000, "renovation":28250000, "clausula":254250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Grimaldo",       "team":"CLT",  "price":54500000, "renovation":27250000, "clausula":245250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Éder Militão",   "team":"TOR",  "price":73000000, "renovation":36500000, "clausula":328500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Araujo",      "team":"CLT",  "price":76000000, "renovation":38000000, "clausula":342000000, "contrato":"1 Season",     "cesion":None},
        {"name":"João Cancelo",   "team":"COL",  "price":46500000, "renovation":23250000, "clausula":209250000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Trippier",    "team":"HOU",  "price":37500000, "renovation":18750000, "clausula":168750000, "contrato":"1 Season",     "cesion":None},
        {"name":"U. Simón",       "team":"LAFC", "price":49000000, "renovation":24500000, "clausula":220500000, "contrato":"1 Season",     "cesion":None},
        {"name":"W. Szczęsny",    "team":"POR",  "price":9000000,  "renovation":4500000,  "clausula":40500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"G. Mamardashvili","team":"MIN", "price":57500000, "renovation":28750000, "clausula":258750000, "contrato":"1 Season",     "cesion":None},
        {"name":"De Gea",         "team":"TOR",  "price":17500000, "renovation":8750000,  "clausula":78750000,  "contrato":"1 Season",     "cesion":None},
        {"name":"C. Gakpo",       "team":"PHI",  "price":103000000,"renovation":51500000, "clausula":463500000, "contrato":"1 Season",     "cesion":None},
        # Sané: juega en STL (cedido corto), dueño CLB
        {"name":"L. Sané",        "team":"STL",  "price":80000000, "renovation":40000000, "clausula":360000000, "contrato":"Cesion Corta", "cesion":"CLB"},
        {"name":"S. Mané",        "team":"DAL",  "price":45500000, "renovation":22750000, "clausula":204750000, "contrato":"1 Season",     "cesion":None},
        # Coman: juega en CHI (cedido largo), dueño LA
        {"name":"K. Coman",       "team":"CHI",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"Cesion Larga", "cesion":"LA"},
        {"name":"Diogo Jota",     "team":"RSL",  "price":50000000, "renovation":25000000, "clausula":225000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Olise",       "team":"COL",  "price":43000000, "renovation":21500000, "clausula":193500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Lookman",     "team":"ATL",  "price":50500000, "renovation":25250000, "clausula":227250000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Maddison",    "team":"MIN",  "price":70000000, "renovation":35000000, "clausula":315000000, "contrato":"1 Season",     "cesion":None},
        {"name":"İ. Gündoğan",    "team":"CHI",  "price":44000000, "renovation":22000000, "clausula":198000000, "contrato":"1 Season",     "cesion":None},
        {"name":"X. Simons",      "team":"CHI",  "price":65000000, "renovation":32500000, "clausula":292500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Gravenberch", "team":"VAN",  "price":53500000, "renovation":26750000, "clausula":240750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Mikel Merino",   "team":"NE",   "price":42000000, "renovation":21000000, "clausula":189000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Palhinha",       "team":"SKC",  "price":37000000, "renovation":18500000, "clausula":166500000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Tchouaméni",  "team":"LA",   "price":52000000, "renovation":26000000, "clausula":234000000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Alaba",       "team":"MTL",  "price":36000000, "renovation":18000000, "clausula":162000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Frimpong",    "team":"LA",   "price":57000000, "renovation":28500000, "clausula":256500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Sergio Ramos",   "team":"STL",  "price":2000000,  "renovation":1000000,  "clausula":9000000,   "contrato":"1 Season",     "cesion":None},
        # Hummels: juega en ATX (cedido largo), dueño STL
        {"name":"M. Hummels",     "team":"ATX",  "price":69000000, "renovation":34500000, "clausula":310500000, "contrato":"Cesion Larga", "cesion":"STL"},
        {"name":"A. Davies",      "team":"NHS",  "price":74000000, "renovation":37000000, "clausula":333000000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Stones",      "team":"SKC",  "price":34500000, "renovation":17250000, "clausula":155250000, "contrato":"1 Season",     "cesion":None},
        {"name":"Alex Remiro",    "team":"SJ",   "price":32500000, "renovation":16250000, "clausula":146250000, "contrato":"1 Season",     "cesion":None},
        # Neuer: juega en ATX (cedido largo), dueño CLB
        {"name":"M. Neuer",       "team":"ATX",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"Cesion Larga", "cesion":"CLB"},
        {"name":"Diogo Costa",    "team":"RBNY", "price":54000000, "renovation":27000000, "clausula":243000000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Gulácsi",     "team":"ORL",  "price":7000000,  "renovation":3500000,  "clausula":31500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Diaby",       "team":"PHI",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"B. Barcola",     "team":"PHI",  "price":56000000, "renovation":28000000, "clausula":252000000, "contrato":"1 Season",     "cesion":None},
        {"name":"Á. Di María",    "team":"TOR",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"D. Malen",       "team":"VAN",  "price":35000000, "renovation":17500000, "clausula":157500000, "contrato":"1 Season",     "cesion":None},
        {"name":"P. Gonçalves",   "team":"MTL",  "price":43000000, "renovation":21500000, "clausula":193500000, "contrato":"1 Season",     "cesion":None},
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
        {"name":"G. Di Lorenzo",  "team":"CIN",  "price":31500000, "renovation":15750000, "clausula":141750000, "contrato":"1 Season",     "cesion":None},
        {"name":"Y. Bounou",      "team":"RSL",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Hrádecký",    "team":"SDFC", "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"J. Pickford",    "team":"STL",  "price":24000000, "renovation":12000000, "clausula":108000000, "contrato":"1 Season",     "cesion":None},
        {"name":"I. Provedel",    "team":"CLT",  "price":24000000, "renovation":12000000, "clausula":108000000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Vicario",     "team":"SDFC", "price":35500000, "renovation":17750000, "clausula":159750000, "contrato":"1 Season",     "cesion":None},
        {"name":"C. Nkunku",      "team":"MIA",  "price":107000000,"renovation":53500000, "clausula":481500000, "contrato":"1 Season",     "cesion":None},
        {"name":"T. Kubo",        "team":"NE",   "price":52500000, "renovation":26250000, "clausula":236250000, "contrato":"1 Season",     "cesion":None},
        {"name":"G. Martinelli",  "team":"HOU",  "price":64000000, "renovation":32000000, "clausula":288000000, "contrato":"1 Season",     "cesion":None},
        {"name":"M. Depay",       "team":"ORL",  "price":22500000, "renovation":11250000, "clausula":101250000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Gnabry",      "team":"SDFC", "price":46000000, "renovation":23000000, "clausula":207000000, "contrato":"1 Season",     "cesion":None},
        # Rashford: juega en SKC (cedido largo), dueño DCU
        {"name":"M. Rashford",    "team":"SKC",  "price":76000000, "renovation":38000000, "clausula":342000000, "contrato":"Cesion Larga", "cesion":"DCU"},
        {"name":"A. Correa",      "team":"DCU",  "price":31000000, "renovation":15500000, "clausula":139500000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Sterling",    "team":"CHI",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Gabriel Jesús",  "team":"CIN",  "price":78000000, "renovation":39000000, "clausula":351000000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Havertz",     "team":"HOU",  "price":53000000, "renovation":26500000, "clausula":238500000, "contrato":"1 Season",     "cesion":None},
        {"name":"Sávio",          "team":"DCU",  "price":47500000, "renovation":23750000, "clausula":213750000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Wirtz",       "team":"SJ",   "price":145500000,"renovation":72750000, "clausula":654750000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. de Jong",     "team":"SKC",  "price":77500000, "renovation":38750000, "clausula":348750000, "contrato":"1 Season",     "cesion":None},
        {"name":"J. Maddison",    "team":"MIN",  "price":70000000, "renovation":35000000, "clausula":315000000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Kessié",      "team":"MIN",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"L. Paqueta",     "team":"DCU",  "price":65000000, "renovation":32500000, "clausula":292500000, "contrato":"1 Season",     "cesion":None},
        # Brahim: juega en COL (cedido largo), dueño DAL
        {"name":"Brahim",         "team":"COL",  "price":43500000, "renovation":21750000, "clausula":195750000, "contrato":"Cesion Larga", "cesion":"DAL"},
        {"name":"D. Szoboszlai",  "team":"SDFC", "price":75000000, "renovation":37500000, "clausula":337500000, "contrato":"1 Season",     "cesion":None},
        {"name":"I. Bennacer",    "team":"ATL",  "price":36000000, "renovation":18000000, "clausula":162000000, "contrato":"1 Season",     "cesion":None},
        {"name":"D. Berardi",     "team":"NHS",  "price":30000000, "renovation":15000000, "clausula":135000000, "contrato":"1 Season",     "cesion":None},
        {"name":"K. Walker",      "team":"PHI",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"E. Tapsoba",     "team":"CLB",  "price":40000000, "renovation":20000000, "clausula":180000000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Robertson",   "team":"RBNY", "price":43000000, "renovation":21500000, "clausula":193500000, "contrato":"1 Season",     "cesion":None},
        {"name":"F. Tomori",      "team":"POR",  "price":37000000, "renovation":18500000, "clausula":166500000, "contrato":"1 Season",     "cesion":None},
        {"name":"L. Hernández",   "team":"PHI",  "price":26500000, "renovation":13250000, "clausula":119250000, "contrato":"1 Season",     "cesion":None},
        {"name":"A. Onana",       "team":"CLT",  "price":32000000, "renovation":16000000, "clausula":144000000, "contrato":"1 Season",     "cesion":None},
        {"name":"N. Pope",        "team":"VAN",  "price":20000000, "renovation":10000000, "clausula":90000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"K. Casteels",    "team":"ATL",  "price":15000000, "renovation":7500000,  "clausula":67500000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Meret",       "team":"RSL",  "price":28000000, "renovation":14000000, "clausula":126000000, "contrato":"1 Season",     "cesion":None},
        {"name":"R. Kolo Muani",  "team":"SJ",   "price":70000000, "renovation":35000000, "clausula":315000000, "contrato":"1 Season",     "cesion":None},
        {"name":"S. Haller",      "team":"CIN",  "price":18000000, "renovation":9000000,  "clausula":81000000,  "contrato":"1 Season",     "cesion":None},
        # Grealish: juega en DAL (cedido largo), dueño TOR
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
        # Rulli: juega en CLB (cedido largo), dueño ATX
        {"name":"G. Rulli",       "team":"CLB",  "price":10000000, "renovation":5000000,  "clausula":45000000,  "contrato":"Cesion Larga", "cesion":"ATX"},
        {"name":"É. Mendy",       "team":"DCU",  "price":12000000, "renovation":6000000,  "clausula":54000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"M. Flekken",     "team":"DAL",  "price":14000000, "renovation":7000000,  "clausula":63000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"A. Lopes",       "team":"NE",   "price":8000000,  "renovation":4000000,  "clausula":36000000,  "contrato":"1 Season",     "cesion":None},
        {"name":"D. Livaković",   "team":"CIN",  "price":16000000, "renovation":8000000,  "clausula":72000000,  "contrato":"1 Season",     "cesion":None},
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
        {"name":"B. Verbruggen",  "team":"NE",   "price":18500000, "renovation":9250000,  "clausula":83250000,  "contrato":"1 Season",     "cesion":None},
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
    # Filter: only keep players in PLAYER_DATA
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
players_df = load_full_data()

# Merge PLAYER_DATA info
players_df["pos"]      = players_df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("pos", "?"))
players_df["nat"]      = players_df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat", ""))
players_df["nat_name"] = players_df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("nat_name", ""))
players_df["sofifa"]   = players_df["name"].map(lambda n: PLAYER_DATA.get(n, {}).get("sofifa", 0))


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="page-title" style="font-size:1.6rem">MMJ</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub" style="margin-top:-8px">LEAGUE SEASON V</div>', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navegación",
        ["⚽ Jugadores", "🏟️ Equipos", "💰 Presupuestos", "🔄 Cedidos", "📊 Estadísticas"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption(f"**{len(players_df)}** jugadores · **{len(TEAM_LOGOS)}** equipos")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: JUGADORES
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚽ Jugadores":
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

    # Filters
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

    # ── Player rows with photo + shield ──────────────────────────────────────
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
        # For loaned players cesion = original owner team
        orig_logo   = TEAM_LOGOS.get(row["cesion"], "") if pd.notna(row.get("cesion")) else ""

        safe_name = row["name"].replace("'", "").replace('"', "")
        initials  = "+".join(safe_name.split()[:2])
        fallback  = f"https://ui-avatars.com/api/?name={initials}&background=1a2a3a&color=f0c040&size=80&bold=true"

        flag_html  = f'<img src="{flag_url}" style="width:18px;height:13px;object-fit:cover;border-radius:2px;vertical-align:middle;">' if flag_url else ""
        tlogo_html = f'<img src="{team_logo}" style="width:22px;height:22px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.04);">' if team_logo else ""

        # Loan info
        loan_html = ""
        if pd.notna(row.get("cesion")):
            orig_logo_html = f'<img src="{orig_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;background:rgba(255,255,255,0.04);">' if orig_logo else ""
            badge_cls = "loan-corta" if row["contrato"] == "Cesion Corta" else "loan-larga"
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

        st.markdown(f""
        <div class="player-row">
          <img src="{photo_url}" style="width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid rgba(232,184,75,0.35);flex-shrink:0;background:#0a1520;"
               onerror="this.onerror=null;this.src='{fallback}'">
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;font-weight:800;color:#f0f4f8;">{row["name"]}</span>
              <span style="background:{pos_color}22;color:{pos_color};border:1px solid {pos_color}44;font-size:0.55rem;font-weight:900;letter-spacing:1.5px;padding:1px 6px;border-radius:3px;">{pos}</span>
              {flag_html}
              <span style="font-size:0.65rem;color:#5a7080;">{nat_name}</span>
            </div>
            {loan_html}
          </div>
          <div style="text-align:right;flex-shrink:0;min-width:120px;">
            <div style="font-family:'Space Mono',monospace;font-size:0.88rem;font-weight:700;color:#e8b84b;">{fmt_money(row["price"])}</div>
            <div style="font-size:0.6rem;color:#5a7080;">Cláus: {fmt_money(row["clausula"])}</div>
            <div style="margin-top:3px;">{contrato_html}</div>
          </div>
        </div>
        "", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏟️ Equipos":
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

        # Header
        hc1, hc2 = st.columns([1, 8])
        with hc1:
            if team_logo:
                st.image(team_logo, width=64)
        with hc2:
            st.markdown(
                f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.5rem;font-weight:900;color:#f0f4f8;">'
                f'{team_code} <span style="color:#7a9db0;font-size:1rem;font-weight:400;">— {TEAM_FULL_NAMES.get(team_code,"")}</span></div>'
                f'<div style="font-size:0.75rem;color:#5a7080;">'
                f'{len(squad)} jugadores · Valor plantilla: <span style="color:#e8b84b;font-weight:700;">{fmt_money(total_val)}</span></div>',
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
                        safe_n    = p["name"].replace("'","").replace('"',"")
                        fallback  = f"https://ui-avatars.com/api/?name={'+'.join(safe_n.split()[:2])}&background=1a2a3a&color=f0c040&size=80&bold=true"
                        flag_img  = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;">' if flag_url else ""

                        # Loan indicator
                        if pd.notna(p.get("cesion")):
                            orig_logo = TEAM_LOGOS.get(p["cesion"], "")
                            orig_logo_html = f'<img src="{orig_logo}" style="width:14px;height:14px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if orig_logo else ""
                            loan_info = f'<div style="font-size:0.6rem;color:#f97316;margin-top:2px;">{orig_logo_html} {p["cesion"]} → cedido</div>'
                        else:
                            loan_info = ""

                        st.markdown(f"""
                        <div class="player-card">
                          <div class="player-card-header">
                            <img src="{photo_url}" class="player-photo"
                                 onerror="this.onerror=null;this.src='{fallback}'">
                            <div class="player-info">
                              <div class="player-name">{p["name"]}</div>
                              <div>
                                <span class="player-pos-badge" style="background:{pos_color}22;color:{pos_color};border:1px solid {pos_color}44;">{pos}</span>
                              </div>
                              <div class="player-nat">{flag_img}<span>{nat_name}</span></div>
                              {loan_info}
                            </div>
                          </div>
                          <div class="player-stats-bar">
                            <div class="player-stat">
                              <div class="player-stat-val">{fmt_money(p["price"])}</div>
                              <div class="player-stat-lbl">Valor</div>
                            </div>
                            <div class="player-stat">
                              <div class="player-stat-val" style="font-size:0.75rem;">{p["contrato"][:8]}</div>
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
    st.markdown('<div class="page-title">PRESUPUESTOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Valor de plantilla por equipo</div>', unsafe_allow_html=True)

    # Value by team
    team_vals = (
        players_df.groupby("team")["price"]
        .sum()
        .reset_index()
        .rename(columns={"price": "valor_total"})
        .sort_values("valor_total", ascending=False)
    )
    team_vals["full_name"] = team_vals["team"].map(TEAM_FULL_NAMES)

    total_b = team_vals["valor_total"].sum()
    avg_b   = team_vals["valor_total"].mean()

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Valor Total Liga",    fmt_money(total_b))
    b2.metric("Promedio por equipo", fmt_money(avg_b))
    b3.metric("Mayor plantilla",     f'{team_vals.iloc[0]["team"]} — {fmt_money(team_vals.iloc[0]["valor_total"])}')
    b4.metric("Menor plantilla",     f'{team_vals.iloc[-1]["team"]} — {fmt_money(team_vals.iloc[-1]["valor_total"])}')

    st.divider()

    # Ranking rows with shield
    for i, (_, row) in enumerate(team_vals.iterrows()):
        logo = TEAM_LOGOS.get(row["team"], "")
        logo_html = f'<img src="{logo}" style="width:30px;height:30px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);">' if logo else ""
        pct = row["valor_total"] / team_vals["valor_total"].max()
        bar_w = int(pct * 260)
        rank_color = "#e8b84b" if i < 3 else "#3b82f6" if i < 10 else "#5a7080"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;background:rgba(255,255,255,0.02);
                    border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:9px 14px;margin-bottom:5px;">
          <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:900;
                       color:{rank_color};min-width:26px;">#{i+1}</span>
          {logo_html}
          <span style="font-weight:700;color:#dce8f0;min-width:50px;">{row["team"]}</span>
          <span style="color:#5a7080;font-size:0.75rem;flex:1;">{row["full_name"]}</span>
          <div style="width:260px;background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin-right:12px;">
            <div style="width:{bar_w}px;background:linear-gradient(90deg,#e8b84b,#f0c040);border-radius:4px;height:6px;"></div>
          </div>
          <span style="font-family:'Space Mono',monospace;font-size:0.85rem;font-weight:700;color:#e8b84b;min-width:80px;text-align:right;">{fmt_money(row["valor_total"])}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    fig = px.bar(
        team_vals, x="valor_total", y="team", orientation="h",
        title="Valor de plantilla por equipo",
        labels={"valor_total": "Valor ($)", "team": "Equipo"},
        color="valor_total",
        color_continuous_scale=["#1a3a5c", "#e8b84b"],
        text=team_vals["valor_total"].apply(fmt_money),
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

    # ── Visual loan cards ────────────────────────────────────────────────────
    for _, p in loans.sort_values("price", ascending=False).iterrows():
        pdata    = PLAYER_DATA.get(p["name"], {})
        pos      = pdata.get("pos", "?")
        nat      = pdata.get("nat", "")
        nat_name = pdata.get("nat_name", "")
        sofifa   = pdata.get("sofifa", 0)
        pos_color = POS_COLORS.get(pos, "#667eea")

        photo_url = get_player_photo(p["name"], sofifa)
        flag_url  = get_flag_url(nat)
        # cesion = equipo ORIGINAL (propietario)
        # team   = equipo ACTUAL (donde juega cedido)
        orig_team   = p["cesion"]
        dest_team   = p["team"]
        orig_logo   = TEAM_LOGOS.get(orig_team, "")
        dest_logo   = TEAM_LOGOS.get(dest_team, "")

        safe_n   = p["name"].replace("'","").replace('"',"")
        fallback = f"https://ui-avatars.com/api/?name={'+'.join(safe_n.split()[:2])}&background=1a2a3a&color=f0c040&size=80&bold=true"
        flag_img = f'<img src="{flag_url}" style="width:16px;height:12px;border-radius:2px;object-fit:cover;vertical-align:middle;">' if flag_url else ""

        orig_logo_html = f'<img src="{orig_logo}" style="width:28px;height:28px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);vertical-align:middle;">' if orig_logo else f'<span style="font-weight:700;color:#e8b84b;">{orig_team}</span>'
        dest_logo_html = f'<img src="{dest_logo}" style="width:28px;height:28px;object-fit:contain;border-radius:50%;background:rgba(255,255,255,0.04);vertical-align:middle;">' if dest_logo else f'<span style="font-weight:700;color:#e8b84b;">{dest_team}</span>'

        badge_cls   = "loan-corta" if p["contrato"] == "Cesion Corta" else "loan-larga"
        badge_label = "⚡ Cesión Corta" if p["contrato"] == "Cesion Corta" else "🔗 Cesión Larga"
        accent_col  = "#f97316" if p["contrato"] == "Cesion Corta" else "#ef4444"

        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0d1b2a,#0a1a28);border:1px solid rgba(255,255,255,0.07);
                    border-left:3px solid {accent_col};border-radius:12px;padding:14px 16px;margin-bottom:8px;
                    display:flex;align-items:center;gap:14px;">
          <img src="{photo_url}" style="width:54px;height:54px;border-radius:50%;object-fit:cover;border:2px solid {accent_col}66;flex-shrink:0;background:#0a1520;"
               onerror="this.onerror=null;this.src='{fallback}'">
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;font-weight:800;color:#f0f4f8;">{p["name"]}</span>
              <span style="background:{pos_color}22;color:{pos_color};border:1px solid {pos_color}44;font-size:0.55rem;font-weight:900;padding:1px 6px;border-radius:3px;">{pos}</span>
              {flag_img}<span style="font-size:0.65rem;color:#5a7080;">{nat_name}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
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

    st.divider()

    # Sankey
    st.markdown("#### Flujo de cesiones")
    all_nodes    = list(set(loans["cesion"].tolist() + loans["team"].tolist()))
    node_idx     = {n: i for i, n in enumerate(all_nodes)}
    source = [node_idx[r["cesion"]] for _, r in loans.iterrows()]
    target = [node_idx[r["team"]]   for _, r in loans.iterrows()]
    values = [r["price"] / 1e6       for _, r in loans.iterrows()]

    fig_sankey = go.Figure(go.Sankey(
        node=dict(pad=12, thickness=16, label=all_nodes, color=["#e8b84b"] * len(all_nodes)),
        link=dict(source=source, target=target, value=values, color="rgba(232,184,75,0.18)")
    ))
    fig_sankey.update_layout(
        title="Origen (equipo propietario) → Destino (equipo actual)  [tamaño = valor M$]",
        paper_bgcolor="#060a0f", font_color="#e2eaf4",
        title_font_color="#e8b84b", height=400
    )
    st.plotly_chart(fig_sankey, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Estadísticas":
    st.markdown('<div class="page-title">ESTADÍSTICAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Distribuciones · Rankings · Contratos</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribución valores", "🏆 Rankings", "🗂️ Contratos", "🌍 Nacionalidades"])

    with tab1:
        # Top 20
        top20 = players_df.nlargest(20, "price").copy()
        top20["Precio"] = top20["price"].apply(fmt_money)

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

        fig_hist = px.histogram(
            players_df, x="price", nbins=40,
            labels={"price": "Precio ($)", "count": "Jugadores"},
            title="Distribución de valores de mercado",
            color_discrete_sequence=["#e8b84b"],
        )
        fig_hist.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                               font_color="#e2eaf4", title_font_color="#e8b84b")
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab2:
        team_stats = (
            players_df.groupby("team")
            .agg(valor_total=("price","sum"), jugadores=("name","count"), avg_valor=("price","mean"))
            .reset_index()
            .sort_values("valor_total", ascending=False)
        )
        fig_teams = px.bar(
            team_stats, x="team", y="valor_total",
            title="Valor total de plantilla por equipo",
            labels={"team":"Equipo","valor_total":"Valor Total ($)"},
            color="valor_total",
            color_continuous_scale=["#1a3a5c","#e8b84b"],
            text=team_stats["valor_total"].apply(fmt_money),
        )
        fig_teams.update_layout(
            plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
            font_color="#e2eaf4", title_font_color="#e8b84b",
            height=450, coloraxis_showscale=False
        )
        fig_teams.update_traces(textposition="outside", textfont_size=8)
        st.plotly_chart(fig_teams, use_container_width=True)

        # By position
        pos_stats = players_df.groupby("pos").agg(total=("price","sum"), count=("name","count")).reset_index()
        fig_pos = px.bar(
            pos_stats, x="pos", y="total",
            title="Valor total por posición",
            labels={"pos":"Posición","total":"Valor ($)"},
            color="pos",
            color_discrete_map=POS_COLORS,
            text=pos_stats["total"].apply(fmt_money),
        )
        fig_pos.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                              font_color="#e2eaf4", title_font_color="#e8b84b",
                              showlegend=False)
        fig_pos.update_traces(textposition="outside")
        st.plotly_chart(fig_pos, use_container_width=True)

    with tab3:
        contrato_counts = players_df["contrato"].value_counts().reset_index()
        contrato_counts.columns = ["contrato","count"]
        fig_pie = px.pie(
            contrato_counts, values="count", names="contrato",
            title="Distribución de tipos de contrato",
            color="contrato",
            color_discrete_map=CONTRATO_COLORS,
        )
        fig_pie.update_layout(paper_bgcolor="#060a0f", font_color="#e2eaf4",
                              title_font_color="#e8b84b")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Cedidos breakdown
        loans_df = players_df[players_df["cesion"].notna()]
        st.markdown("#### Detalle de cedidos por tipo")
        c1, c2 = st.columns(2)
        with c1:
            corta_df = loans_df[loans_df["contrato"]=="Cesion Corta"].sort_values("price",ascending=False)
            st.markdown("**⚡ Cesión Corta**")
            for _, p in corta_df.iterrows():
                orig_logo = TEAM_LOGOS.get(p["cesion"],""); dest_logo = TEAM_LOGOS.get(p["team"],"")
                ol = f'<img src="{orig_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if orig_logo else ""
                dl = f'<img src="{dest_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if dest_logo else ""
                st.markdown(
                    f'<div style="background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.2);border-radius:8px;padding:6px 10px;margin-bottom:4px;font-size:0.78rem;">'
                    f'<b style="color:#f0f4f8;">{p["name"]}</b><br>'
                    f'{ol} <span style="color:#f97316;font-size:0.7rem;">{p["cesion"]}</span>'
                    f' <span style="color:#555;">→</span> {dl} <span style="color:#e2eaf4;font-size:0.7rem;">{p["team"]}</span>'
                    f'<span style="float:right;color:#e8b84b;font-family:monospace;">{fmt_money(p["price"])}</span></div>',
                    unsafe_allow_html=True
                )
        with c2:
            larga_df = loans_df[loans_df["contrato"]=="Cesion Larga"].sort_values("price",ascending=False)
            st.markdown("**🔗 Cesión Larga**")
            for _, p in larga_df.iterrows():
                orig_logo = TEAM_LOGOS.get(p["cesion"],""); dest_logo = TEAM_LOGOS.get(p["team"],"")
                ol = f'<img src="{orig_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if orig_logo else ""
                dl = f'<img src="{dest_logo}" style="width:18px;height:18px;object-fit:contain;border-radius:50%;vertical-align:middle;">' if dest_logo else ""
                st.markdown(
                    f'<div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:6px 10px;margin-bottom:4px;font-size:0.78rem;">'
                    f'<b style="color:#f0f4f8;">{p["name"]}</b><br>'
                    f'{ol} <span style="color:#ef4444;font-size:0.7rem;">{p["cesion"]}</span>'
                    f' <span style="color:#555;">→</span> {dl} <span style="color:#e2eaf4;font-size:0.7rem;">{p["team"]}</span>'
                    f'<span style="float:right;color:#e8b84b;font-family:monospace;">{fmt_money(p["price"])}</span></div>',
                    unsafe_allow_html=True
                )

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
                    f'</div>',
                    unsafe_allow_html=True
                )
