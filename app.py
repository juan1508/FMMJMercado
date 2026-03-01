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
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;600&family=Space+Mono:wght@400;700&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .main { background: #060a0f; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Hide default streamlit header */
  header[data-testid="stHeader"] { background: rgba(6,10,15,0.95); }

  /* Metric cards */
  [data-testid="stMetric"] {
    background: #0d1520;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 18px !important;
    border-top: 2px solid #e8b84b;
  }
  [data-testid="stMetricValue"] { color: #e8b84b !important; font-family: 'Space Mono', monospace; font-size: 1.2rem !important; }
  [data-testid="stMetricLabel"] { color: #5a7080 !important; font-size: 0.68rem !important; text-transform: uppercase; letter-spacing: 2px; }

  /* Page title */
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
    background: #0d1520;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
  }
  .player-card:hover { border-color: rgba(232,184,75,0.35); }
  .player-name { font-weight: 600; font-size: 0.95rem; color: #e2eaf4; }
  .player-team { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #8aaabb; }
  .price-gold { color: #e8b84b; font-family: 'Space Mono', monospace; font-weight: 700; }
  .price-green { color: #22c55e; font-family: 'Space Mono', monospace; }
  .price-red { color: #ef4444; font-family: 'Space Mono', monospace; }

  /* Badge */
  .badge-1s { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
  .badge-2s { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
  .badge-cc { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.35); padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
  .badge-cl { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0d1520 !important; border-right: 1px solid rgba(255,255,255,0.07); }
  [data-testid="stSidebar"] * { color: #e2eaf4 !important; }

  /* Dataframe */
  [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

  /* Divider */
  hr { border-color: rgba(255,255,255,0.07) !important; }
</style>
""", unsafe_allow_html=True)


# ── Data ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Team code mapping
    team_codes = {
        "Atlanta United": "ATL", "Austin FC": "ATX", "CF Montréal": "MTL",
        "Charlotte FC": "CLT", "Chicago Fire": "CHI", "Colombus Crew": "CLB",
        "Colorado Rapids": "COL", "DC United": "DCU", "FC Cincinnati": "CIN",
        "FC Dallas": "DAL", "Houston Dynamo": "HOU", "Inter Miami": "MIA",
        "Los Angeles FC": "LAFC", "Los Angeles Galaxy": "LA",
        "Minnesota United FC": "MIN", "Nashville SC": "NHS",
        "New England Revolution": "NE", "New York City": "NYC",
        "Orlando City": "ORL", "Philadelphia Union": "PHI",
        "Portland Timbers": "POR", "Real Salt Lake": "RSL",
        "Red Bull New York": "RBNY", "San Diego FC": "SDFC",
        "San Jose Earthquakes": "SJ", "Seattle Sounders FC": "SEA",
        "Sporting Kansas City": "SKC", "St. Louis City SC": "STL",
        "Toronto FC": "TOR", "Vancouver Whitecaps": "VAN",
    }

    players = pd.read_excel("JUGADORES.xlsx", sheet_name="Players")
    teams   = pd.read_excel("JUGADORES.xlsx", sheet_name="Teams")

    # Rename columns
    players.columns = ["name", "price", "renovation", "clausula", "contrato", "cesion"]
    teams.columns   = ["full_name", "estadio", "presi", "dt", "presupuesto"]

    teams["code"] = teams["full_name"].map(team_codes)

    # Fill missing cesion
    players["cesion"] = players["cesion"].where(players["cesion"].notna(), None)

    # Join team code into players (players already have code from HTML)
    # We need to map team in players — but players don't have team col in xlsx!
    # Use the HTML static data merged into xlsx via re-reading original
    # Actually the xlsx doesn't have team column, so we load from embedded data
    return players, teams, team_codes

# Load embedded players data (from HTML source, which matches xlsx + adds team codes)
@st.cache_data
def load_full_data():
    teams_df = pd.read_excel("JUGADORES.xlsx", sheet_name="Teams")
    teams_df.columns = ["full_name", "estadio", "presi", "dt", "presupuesto"]

    team_codes = {
        "Atlanta United": "ATL", "Austin FC": "ATX", "CF Montréal": "MTL",
        "Charlotte FC": "CLT", "Chicago Fire": "CHI", "Colombus Crew": "CLB",
        "Colorado Rapids": "COL", "DC United": "DCU", "FC Cincinnati": "CIN",
        "FC Dallas": "DAL", "Houston Dynamo": "HOU", "Inter Miami": "MIA",
        "Los Angeles FC": "LAFC", "Los Angeles Galaxy": "LA",
        "Minnesota United FC": "MIN", "Nashville SC": "NHS",
        "New England Revolution": "NE", "New York City": "NYC",
        "Orlando City": "ORL", "Philadelphia Union": "PHI",
        "Portland Timbers": "POR", "Real Salt Lake": "RSL",
        "Red Bull New York": "RBNY", "San Diego FC": "SDFC",
        "San Jose Earthquakes": "SJ", "Seattle Sounders FC": "SEA",
        "Sporting Kansas City": "SKC", "St. Louis City SC": "STL",
        "Toronto FC": "TOR", "Vancouver Whitecaps": "VAN",
    }
    teams_df["code"] = teams_df["full_name"].map(team_codes)

    # Static player+team data (from HTML which has team codes)
    data = [
        {"name":"M. Salah","team":"ATL","price":104000000,"renovation":52000000,"clausula":468000000,"contrato":"1 Season","cesion":None},
        {"name":"Rodri","team":"TOR","price":115500000,"renovation":57750000,"clausula":519750000,"contrato":"1 Season","cesion":None},
        {"name":"K. Mbappé","team":"LAFC","price":211000000,"renovation":105500000,"clausula":949500000,"contrato":"Cesion Corta","cesion":"NSH"},
        {"name":"Vinícius Jr.","team":"ATX","price":193500000,"renovation":96750000,"clausula":870750000,"contrato":"1 Season","cesion":None},
        {"name":"E. Haaland","team":"SEA","price":196000000,"renovation":98000000,"clausula":882000000,"contrato":"1 Season","cesion":None},
        {"name":"H. Kane","team":"COL","price":117500000,"renovation":58750000,"clausula":528750000,"contrato":"1 Season","cesion":None},
        {"name":"J. Bellingham","team":"NYC","price":174500000,"renovation":87250000,"clausula":785250000,"contrato":"1 Season","cesion":None},
        {"name":"V. van Dijk","team":"LA","price":77500000,"renovation":38750000,"clausula":348750000,"contrato":"1 Season","cesion":None},
        {"name":"R. Lewandowski","team":"MTL","price":44000000,"renovation":22000000,"clausula":198000000,"contrato":"Cesion Larga","cesion":"MIA"},
        {"name":"K. de Bruyne","team":"ATL","price":97000000,"renovation":48500000,"clausula":436500000,"contrato":"1 Season","cesion":None},
        {"name":"F. Wirtz","team":"SJ","price":145500000,"renovation":72750000,"clausula":654750000,"contrato":"1 Season","cesion":None},
        {"name":"Alisson","team":"MIA","price":63000000,"renovation":31500000,"clausula":283500000,"contrato":"1 Season","cesion":None},
        {"name":"T. Courtois","team":"SKC","price":51000000,"renovation":25500000,"clausula":229500000,"contrato":"1 Season","cesion":None},
        {"name":"Neymar Jr","team":"MIA","price":64000000,"renovation":32000000,"clausula":288000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Martínez","team":"POR","price":101500000,"renovation":50750000,"clausula":456750000,"contrato":"1 Season","cesion":None},
        {"name":"B. Saka","team":"ATL","price":126000000,"renovation":63000000,"clausula":567000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Musiala","team":"LAFC","price":232000000,"renovation":116000000,"clausula":1044000000,"contrato":"1 Season","cesion":None},
        {"name":"F. Valverde","team":"NE","price":120000000,"renovation":60000000,"clausula":540000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Ødegaard","team":"RSL","price":108500000,"renovation":54250000,"clausula":488250000,"contrato":"1 Season","cesion":None},
        {"name":"J. Kimmich","team":"POR","price":82000000,"renovation":41000000,"clausula":369000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Rüdiger","team":"NE","price":62500000,"renovation":31250000,"clausula":281250000,"contrato":"1 Season","cesion":None},
        {"name":"M. ter Stegen","team":"LA","price":45000000,"renovation":22500000,"clausula":202500000,"contrato":"1 Season","cesion":None},
        {"name":"J. Oblak","team":"CHI","price":74500000,"renovation":37250000,"clausula":335250000,"contrato":"1 Season","cesion":None},
        {"name":"O. Dembélé","team":"RSL","price":85000000,"renovation":42500000,"clausula":382500000,"contrato":"1 Season","cesion":None},
        {"name":"Raphinha","team":"MIN","price":85000000,"renovation":42500000,"clausula":382500000,"contrato":"1 Season","cesion":None},
        {"name":"L. Messi","team":"SEA","price":38000000,"renovation":19000000,"clausula":171000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Griezmann","team":"DCU","price":74000000,"renovation":37000000,"clausula":333000000,"contrato":"1 Season","cesion":None},
        {"name":"V. Osimhen","team":"CLT","price":116000000,"renovation":58000000,"clausula":522000000,"contrato":"1 Season","cesion":None},
        {"name":"Pedri","team":"CLB","price":125000000,"renovation":62500000,"clausula":562500000,"contrato":"1 Season","cesion":None},
        {"name":"D. Rice","team":"SJ","price":86000000,"renovation":43000000,"clausula":387000000,"contrato":"1 Season","cesion":None},
        {"name":"N. Barella","team":"ATX","price":84500000,"renovation":42250000,"clausula":380250000,"contrato":"1 Season","cesion":None},
        {"name":"C. Palmer","team":"DAL","price":111000000,"renovation":55500000,"clausula":499500000,"contrato":"1 Season","cesion":None},
        {"name":"Marquinhos","team":"ATX","price":65500000,"renovation":32750000,"clausula":294750000,"contrato":"1 Season","cesion":None},
        {"name":"Gabriel","team":"RBNY","price":82500000,"renovation":41250000,"clausula":371250000,"contrato":"1 Season","cesion":None},
        {"name":"J. Tah","team":"SEA","price":68500000,"renovation":34250000,"clausula":308250000,"contrato":"1 Season","cesion":None},
        {"name":"W. Saliba","team":"NHS","price":92000000,"renovation":46000000,"clausula":414000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Bastoni","team":"MIA","price":88500000,"renovation":44250000,"clausula":398250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Maignan","team":"NHS","price":74000000,"renovation":37000000,"clausula":333000000,"contrato":"1 Season","cesion":None},
        {"name":"G. Donnarumma","team":"TOR","price":76000000,"renovation":38000000,"clausula":342000000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Sommer","team":"ATL","price":9000000,"renovation":4500000,"clausula":40500000,"contrato":"Cesion Larga","cesion":"ORL"},
        {"name":"Rodrygo","team":"LAFC","price":232000000,"renovation":116000000,"clausula":1044000000,"contrato":"1 Season","cesion":None},
        {"name":"H. Son","team":"ATX","price":56500000,"renovation":28250000,"clausula":254250000,"contrato":"1 Season","cesion":None},
        {"name":"K. Benzema","team":"NE","price":26000000,"renovation":13000000,"clausula":117000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Álvarez","team":"SDFC","price":94000000,"renovation":47000000,"clausula":423000000,"contrato":"2 Season","cesion":None},
        {"name":"V. Gyökeres","team":"CLB","price":90000000,"renovation":45000000,"clausula":405000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Isak","team":"SEA","price":89500000,"renovation":44750000,"clausula":402750000,"contrato":"1 Season","cesion":None},
        {"name":"P. Dybala","team":"LAFC","price":81000000,"renovation":40500000,"clausula":364500000,"contrato":"1 Season","cesion":None},
        {"name":"Bruno Fernandes","team":"MTL","price":69000000,"renovation":34500000,"clausula":310500000,"contrato":"1 Season","cesion":None},
        {"name":"P. Foden","team":"PHI","price":88000000,"renovation":44000000,"clausula":396000000,"contrato":"Cesion Larga","cesion":"NE"},
        {"name":"F. de Jong","team":"SKC","price":77500000,"renovation":38750000,"clausula":348750000,"contrato":"1 Season","cesion":None},
        {"name":"G. Xhaka","team":"CIN","price":47500000,"renovation":23750000,"clausula":213750000,"contrato":"1 Season","cesion":None},
        {"name":"A. Mac Allister","team":"MIA","price":84500000,"renovation":42250000,"clausula":380250000,"contrato":"1 Season","cesion":None},
        {"name":"H. Çalhanoğlu","team":"VAN","price":57000000,"renovation":28500000,"clausula":256500000,"contrato":"1 Season","cesion":None},
        {"name":"Rúben Dias","team":"MIA","price":68500000,"renovation":34250000,"clausula":308250000,"contrato":"1 Season","cesion":None},
        {"name":"T. Alexander-Arnold","team":"SKC","price":74000000,"renovation":37000000,"clausula":333000000,"contrato":"1 Season","cesion":None},
        {"name":"T.Hernández","team":"ATL","price":73000000,"renovation":36500000,"clausula":328500000,"contrato":"1 Season","cesion":None},
        {"name":"J. Koundé","team":"ORL","price":83000000,"renovation":41500000,"clausula":373500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Hakimi","team":"DCU","price":78500000,"renovation":39250000,"clausula":353250000,"contrato":"Cesion Corta","cesion":"ORL"},
        {"name":"D. Carvajal","team":"LA","price":47000000,"renovation":23500000,"clausula":211500000,"contrato":"1 Season","cesion":None},
        {"name":"Bremer","team":"POR","price":72500000,"renovation":36250000,"clausula":326250000,"contrato":"1 Season","cesion":None},
        {"name":"E. Martínez","team":"MTL","price":49000000,"renovation":24500000,"clausula":220500000,"contrato":"1 Season","cesion":None},
        {"name":"Ederson","team":"SEA","price":45000000,"renovation":22500000,"clausula":202500000,"contrato":"1 Season","cesion":None},
        {"name":"G. Kobel","team":"HOU","price":68500000,"renovation":34250000,"clausula":308250000,"contrato":"1 Season","cesion":None},
        {"name":"David Raya","team":"HOU","price":54000000,"renovation":27000000,"clausula":243000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Díaz","team":"NHS","price":118500000,"renovation":59250000,"clausula":533250000,"contrato":"1 Season","cesion":None},
        {"name":"R. Mahrez","team":"VAN","price":33500000,"renovation":16750000,"clausula":150750000,"contrato":"1 Season","cesion":None},
        {"name":"K. Kvaratskhelia","team":"CHI","price":81000000,"renovation":40500000,"clausula":364500000,"contrato":"Cesion Larga","cesion":"CLT"},
        {"name":"R. Leão","team":"LA","price":86000000,"renovation":43000000,"clausula":387000000,"contrato":"1 Season","cesion":None},
        {"name":"C. Ronaldo","team":"RBNY","price":18500000,"renovation":9250000,"clausula":83250000,"contrato":"1 Season","cesion":None},
        {"name":"Nico Williams","team":"VAN","price":78500000,"renovation":39250000,"clausula":353250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Olise","team":"COL","price":75000000,"renovation":37500000,"clausula":337500000,"contrato":"1 Season","cesion":None},
        {"name":"Bernardo Silva","team":"DAL","price":77000000,"renovation":38500000,"clausula":346500000,"contrato":"1 Season","cesion":None},
        {"name":"S. Milinković-Savić","team":"MTL","price":54500000,"renovation":27250000,"clausula":245250000,"contrato":"1 Season","cesion":None},
        {"name":"D. Olmo","team":"VAN","price":66500000,"renovation":33250000,"clausula":299250000,"contrato":"1 Season","cesion":None},
        {"name":"Casemiro","team":"MIA","price":36000000,"renovation":18000000,"clausula":162000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Modrić","team":"LA","price":39000000,"renovation":19500000,"clausula":175500000,"contrato":"1 Season","cesion":None},
        {"name":"N. Kanté","team":"CIN","price":26500000,"renovation":13250000,"clausula":119250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Caicedo","team":"SJ","price":68000000,"renovation":34000000,"clausula":306000000,"contrato":"1 Season","cesion":None},
        {"name":"Bruno Guimarães","team":"SDFC","price":56500000,"renovation":28250000,"clausula":254250000,"contrato":"1 Season","cesion":None},
        {"name":"N. Schlotterbeck","team":"NHS","price":66000000,"renovation":33000000,"clausula":297000000,"contrato":"2 Season","cesion":None},
        {"name":"A. Grimaldo","team":"CLT","price":54500000,"renovation":27250000,"clausula":245250000,"contrato":"1 Season","cesion":None},
        {"name":"Éder Militão","team":"TOR","price":73000000,"renovation":36500000,"clausula":328500000,"contrato":"1 Season","cesion":None},
        {"name":"R. Araujo","team":"CLT","price":76000000,"renovation":38000000,"clausula":342000000,"contrato":"1 Season","cesion":None},
        {"name":"João Cancelo","team":"COL","price":46500000,"renovation":23250000,"clausula":209250000,"contrato":"1 Season","cesion":None},
        {"name":"K. Trippier","team":"HOU","price":37500000,"renovation":18750000,"clausula":168750000,"contrato":"1 Season","cesion":None},
        {"name":"U. Simón","team":"LAFC","price":49000000,"renovation":24500000,"clausula":220500000,"contrato":"1 Season","cesion":None},
        {"name":"W. Szczęsny","team":"POR","price":9000000,"renovation":4500000,"clausula":40500000,"contrato":"1 Season","cesion":None},
        {"name":"G. Mamardashvili","team":"MIN","price":57500000,"renovation":28750000,"clausula":258750000,"contrato":"1 Season","cesion":None},
        {"name":"De Gea","team":"TOR","price":17500000,"renovation":8750000,"clausula":78750000,"contrato":"1 Season","cesion":None},
        {"name":"C. Gakpo","team":"PHI","price":103000000,"renovation":51500000,"clausula":463500000,"contrato":"1 Season","cesion":None},
        {"name":"L. Sané","team":"CLB","price":80000000,"renovation":40000000,"clausula":360000000,"contrato":"Cesion Corta","cesion":"STL"},
        {"name":"S. Mané","team":"DAL","price":45500000,"renovation":22750000,"clausula":204750000,"contrato":"1 Season","cesion":None},
        {"name":"K. Coman","team":"LA","price":69000000,"renovation":34500000,"clausula":310500000,"contrato":"Cesion Larga","cesion":"CHI"},
        {"name":"Diogo Jota","team":"RSL","price":50000000,"renovation":25000000,"clausula":225000000,"contrato":"1 Season","cesion":None},
        {"name":"P. Schick","team":"MIN","price":43000000,"renovation":21500000,"clausula":193500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Lookman","team":"ATL","price":50500000,"renovation":25250000,"clausula":227250000,"contrato":"1 Season","cesion":None},
        {"name":"O. Watkins","team":"NE","price":43000000,"renovation":21500000,"clausula":193500000,"contrato":"1 Season","cesion":None},
        {"name":"L. Openda","team":"ORL","price":58500000,"renovation":29250000,"clausula":263250000,"contrato":"1 Season","cesion":None},
        {"name":"J. Maddison","team":"MIN","price":70000000,"renovation":35000000,"clausula":315000000,"contrato":"1 Season","cesion":None},
        {"name":"İ. Gündoğan","team":"CHI","price":44000000,"renovation":22000000,"clausula":198000000,"contrato":"1 Season","cesion":None},
        {"name":"X. Simons","team":"CHI","price":65000000,"renovation":32500000,"clausula":292500000,"contrato":"1 Season","cesion":None},
        {"name":"R. Gravenberch","team":"VAN","price":53500000,"renovation":26750000,"clausula":240750000,"contrato":"1 Season","cesion":None},
        {"name":"Mikel Merino","team":"NE","price":42000000,"renovation":21000000,"clausula":189000000,"contrato":"1 Season","cesion":None},
        {"name":"Palhinha","team":"SKC","price":37000000,"renovation":18500000,"clausula":166500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Tchouaméni","team":"LA","price":52000000,"renovation":26000000,"clausula":234000000,"contrato":"1 Season","cesion":None},
        {"name":"D. Alaba","team":"MTL","price":36000000,"renovation":18000000,"clausula":162000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Frimpong","team":"LA","price":57000000,"renovation":28500000,"clausula":256500000,"contrato":"1 Season","cesion":None},
        {"name":"S. Ramos","team":"STL","price":2000000,"renovation":1000000,"clausula":9000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Hummels","team":"STL","price":69000000,"renovation":34500000,"clausula":310500000,"contrato":"Cesion Larga","cesion":"ATX"},
        {"name":"A. Davies","team":"NHS","price":74000000,"renovation":37000000,"clausula":333000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Stones","team":"SKC","price":34500000,"renovation":17250000,"clausula":155250000,"contrato":"1 Season","cesion":None},
        {"name":"A. Remiro","team":"SJ","price":32500000,"renovation":16250000,"clausula":146250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Neuer","team":"CLB","price":7000000,"renovation":3500000,"clausula":31500000,"contrato":"Cesion Larga","cesion":"ATX"},
        {"name":"Diogo Costa","team":"RBNY","price":54000000,"renovation":27000000,"clausula":243000000,"contrato":"1 Season","cesion":None},
        {"name":"P. Gulácsi","team":"ORL","price":7000000,"renovation":3500000,"clausula":31500000,"contrato":"1 Season","cesion":None},
        {"name":"M. Diaby","team":"PHI","price":53000000,"renovation":26500000,"clausula":238500000,"contrato":"1 Season","cesion":None},
        {"name":"B. Barcola","team":"PHI","price":56000000,"renovation":28000000,"clausula":252000000,"contrato":"1 Season","cesion":None},
        {"name":"Á. Di María","team":"TOR","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"D. Malen","team":"VAN","price":35000000,"renovation":17500000,"clausula":157500000,"contrato":"1 Season","cesion":None},
        {"name":"P. Gonçalves","team":"MTL","price":43000000,"renovation":21500000,"clausula":193500000,"contrato":"1 Season","cesion":None},
        {"name":"Morata","team":"ATX","price":30500000,"renovation":15250000,"clausula":137250000,"contrato":"1 Season","cesion":None},
        {"name":"Gerard Moreno","team":"COL","price":29500000,"renovation":14750000,"clausula":132750000,"contrato":"1 Season","cesion":None},
        {"name":"L. Trossard","team":"NE","price":35500000,"renovation":17750000,"clausula":159750000,"contrato":"1 Season","cesion":None},
        {"name":"M. Llorente","team":"MIN","price":32000000,"renovation":16000000,"clausula":144000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Rabiot","team":"ORL","price":38000000,"renovation":19000000,"clausula":171000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Goretzka","team":"HOU","price":35500000,"renovation":17750000,"clausula":159750000,"contrato":"1 Season","cesion":None},
        {"name":"Gavi","team":"POR","price":55000000,"renovation":27500000,"clausula":247500000,"contrato":"1 Season","cesion":None},
        {"name":"E. Fernández","team":"DAL","price":80000000,"renovation":40000000,"clausula":360000000,"contrato":"1 Season","cesion":None},
        {"name":"R. Andrich","team":"VAN","price":31000000,"renovation":15500000,"clausula":139500000,"contrato":"1 Season","cesion":None},
        {"name":"Rafa","team":"DCU","price":30000000,"renovation":15000000,"clausula":135000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Laporte","team":"CLT","price":30000000,"renovation":15000000,"clausula":135000000,"contrato":"1 Season","cesion":None},
        {"name":"M. de Ligt","team":"NYC","price":79000000,"renovation":39500000,"clausula":355500000,"contrato":"1 Season","cesion":None},
        {"name":"P. Hincapié","team":"LAFC","price":47500000,"renovation":23750000,"clausula":213750000,"contrato":"1 Season","cesion":None},
        {"name":"Kim Min Jae","team":"SKC","price":62000000,"renovation":31000000,"clausula":279000000,"contrato":"1 Season","cesion":None},
        {"name":"R. James","team":"SDFC","price":50000000,"renovation":25000000,"clausula":225000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Balde","team":"ORL","price":47500000,"renovation":23750000,"clausula":213750000,"contrato":"1 Season","cesion":None},
        {"name":"L. Martínez","team":"POR","price":37500000,"renovation":18750000,"clausula":168750000,"contrato":"1 Season","cesion":None},
        {"name":"G. Di Lorenzo","team":"CIN","price":31500000,"renovation":15750000,"clausula":141750000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Bounou","team":"RSL","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Hrádecký","team":"SDFC","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Pickford","team":"STL","price":24000000,"renovation":12000000,"clausula":108000000,"contrato":"1 Season","cesion":None},
        {"name":"I. Provedel","team":"CLT","price":24000000,"renovation":12000000,"clausula":108000000,"contrato":"1 Season","cesion":None},
        {"name":"G. Vicario","team":"SDFC","price":35500000,"renovation":17750000,"clausula":159750000,"contrato":"1 Season","cesion":None},
        {"name":"C. Nkunku","team":"MIA","price":107000000,"renovation":53500000,"clausula":481500000,"contrato":"1 Season","cesion":None},
        {"name":"T. Kubo","team":"NE","price":52500000,"renovation":26250000,"clausula":236250000,"contrato":"1 Season","cesion":None},
        {"name":"G. Martinelli","team":"HOU","price":64000000,"renovation":32000000,"clausula":288000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Depay","team":"ORL","price":22500000,"renovation":11250000,"clausula":101250000,"contrato":"1 Season","cesion":None},
        {"name":"S. Gnabry","team":"SDFC","price":46000000,"renovation":23000000,"clausula":207000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Rashford","team":"DCU","price":76000000,"renovation":38000000,"clausula":342000000,"contrato":"Cesion Larga","cesion":"SKC"},
        {"name":"A. Correa","team":"DCU","price":31000000,"renovation":15500000,"clausula":139500000,"contrato":"1 Season","cesion":None},
        {"name":"R. Sterling","team":"CHI","price":53000000,"renovation":26500000,"clausula":238500000,"contrato":"1 Season","cesion":None},
        {"name":"Gabriel Jesús","team":"CIN","price":78000000,"renovation":39000000,"clausula":351000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Havertz","team":"HOU","price":53000000,"renovation":26500000,"clausula":238500000,"contrato":"1 Season","cesion":None},
        {"name":"Savinho","team":"DCU","price":47500000,"renovation":23750000,"clausula":213750000,"contrato":"1 Season","cesion":None},
        {"name":"C. Immobile","team":"HOU","price":15000000,"renovation":7500000,"clausula":67500000,"contrato":"1 Season","cesion":None},
        {"name":"Iñaki Williams","team":"COL","price":29500000,"renovation":14750000,"clausula":132750000,"contrato":"1 Season","cesion":None},
        {"name":"Oyarzabal","team":"SJ","price":33000000,"renovation":16500000,"clausula":148500000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Carrasco","team":"DCU","price":29500000,"renovation":14750000,"clausula":132750000,"contrato":"1 Season","cesion":None},
        {"name":"J. Brandt","team":"LAFC","price":41000000,"renovation":20500000,"clausula":184500000,"contrato":"1 Season","cesion":None},
        {"name":"F. Chiesa","team":"HOU","price":50000000,"renovation":25000000,"clausula":225000000,"contrato":"1 Season","cesion":None},
        {"name":"F. Kessié","team":"MIN","price":20000000,"renovation":10000000,"clausula":90000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Paqueta","team":"DCU","price":65000000,"renovation":32500000,"clausula":292500000,"contrato":"1 Season","cesion":None},
        {"name":"Brahim","team":"DAL","price":43500000,"renovation":21750000,"clausula":195750000,"contrato":"Cesion Larga","cesion":"COL"},
        {"name":"D. Szoboszlai","team":"SDFC","price":75000000,"renovation":37500000,"clausula":337500000,"contrato":"1 Season","cesion":None},
        {"name":"Parejo","team":"SJ","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"I. Bennacer","team":"ATL","price":36000000,"renovation":18000000,"clausula":162000000,"contrato":"1 Season","cesion":None},
        {"name":"Joelinton","team":"MIN","price":32000000,"renovation":16000000,"clausula":144000000,"contrato":"1 Season","cesion":None},
        {"name":"D. Berardi","team":"NHS","price":30000000,"renovation":15000000,"clausula":135000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Walker","team":"PHI","price":20000000,"renovation":10000000,"clausula":90000000,"contrato":"1 Season","cesion":None},
        {"name":"E. Tapsoba","team":"CLB","price":40000000,"renovation":20000000,"clausula":180000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Robertson","team":"RBNY","price":43000000,"renovation":21500000,"clausula":193500000,"contrato":"1 Season","cesion":None},
        {"name":"F. Tomori","team":"POR","price":37000000,"renovation":18500000,"clausula":166500000,"contrato":"1 Season","cesion":None},
        {"name":"L. Hernández","team":"PHI","price":26500000,"renovation":13250000,"clausula":119250000,"contrato":"1 Season","cesion":None},
        {"name":"A. Onana","team":"CLT","price":32000000,"renovation":16000000,"clausula":144000000,"contrato":"1 Season","cesion":None},
        {"name":"N. Pope","team":"VAN","price":20000000,"renovation":10000000,"clausula":90000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Casteels","team":"ATL","price":15000000,"renovation":7500000,"clausula":67500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Meret","team":"RSL","price":28000000,"renovation":14000000,"clausula":126000000,"contrato":"1 Season","cesion":None},
        {"name":"B. Samba","team":"DAL","price":20500000,"renovation":10250000,"clausula":92250000,"contrato":"1 Season","cesion":None},
        {"name":"K. Trapp","team":"STL","price":10000000,"renovation":5000000,"clausula":45000000,"contrato":"1 Season","cesion":None},
        {"name":"R. Kolo Muani","team":"SJ","price":70000000,"renovation":35000000,"clausula":315000000,"contrato":"1 Season","cesion":None},
        {"name":"S. Haller","team":"CIN","price":18000000,"renovation":9000000,"clausula":81000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Suárez","team":"MIA","price":9000000,"renovation":4500000,"clausula":40500000,"contrato":"1 Season","cesion":None},
        {"name":"J. Grealish","team":"TOR","price":57500000,"renovation":28750000,"clausula":258750000,"contrato":"Cesion Larga","cesion":"DAL"},
        {"name":"D. Udogie","team":"TOR","price":35500000,"renovation":17750000,"clausula":159750000,"contrato":"1 Season","cesion":None},
        {"name":"N. Süle","team":"RSL","price":24500000,"renovation":12250000,"clausula":110250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Kerkez","team":"CIN","price":33500000,"renovation":16750000,"clausula":150750000,"contrato":"1 Season","cesion":None},
        {"name":"K. Navas","team":"NYC","price":4000000,"renovation":2000000,"clausula":18000000,"contrato":"1 Season","cesion":None},
        {"name":"F. Torres","team":"NHS","price":75000000,"renovation":37500000,"clausula":337500000,"contrato":"1 Season","cesion":None},
        {"name":"S. Chukwueze","team":"MTL","price":29000000,"renovation":14500000,"clausula":130500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Saint-Maximin","team":"PHI","price":22500000,"renovation":11250000,"clausula":101250000,"contrato":"1 Season","cesion":None},
        {"name":"L. Bailey","team":"ORL","price":23000000,"renovation":11500000,"clausula":103500000,"contrato":"1 Season","cesion":None},
        {"name":"João Félix","team":"CLT","price":30000000,"renovation":15000000,"clausula":135000000,"contrato":"1 Season","cesion":None},
        {"name":"H. Lozano","team":"STL","price":22000000,"renovation":11000000,"clausula":99000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Adeyemi","team":"STL","price":118000000,"renovation":59000000,"clausula":531000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Doku","team":"NE","price":32500000,"renovation":16250000,"clausula":146250000,"contrato":"1 Season","cesion":None},
        {"name":"D. Doué","team":"HOU","price":45500000,"renovation":22750000,"clausula":204750000,"contrato":"1 Season","cesion":None},
        {"name":"W. Zaïre-Emery","team":"ATL","price":44500000,"renovation":22250000,"clausula":200250000,"contrato":"1 Season","cesion":None},
        {"name":"P. Cubarsí","team":"NHS","price":40500000,"renovation":20250000,"clausula":182250000,"contrato":"1 Season","cesion":None},
        {"name":"G. Inácio","team":"RSL","price":40000000,"renovation":20000000,"clausula":180000000,"contrato":"1 Season","cesion":None},
        {"name":"C. Lukeba","team":"COL","price":40000000,"renovation":20000000,"clausula":180000000,"contrato":"1 Season","cesion":None},
        {"name":"G. Rulli","team":"ATX","price":10000000,"renovation":5000000,"clausula":45000000,"contrato":"Cesion Larga","cesion":"CLB"},
        {"name":"É. Mendy","team":"DCU","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Flekken","team":"DAL","price":14000000,"renovation":7000000,"clausula":63000000,"contrato":"1 Season","cesion":None},
        {"name":"A. Lopes","team":"NE","price":8000000,"renovation":4000000,"clausula":36000000,"contrato":"1 Season","cesion":None},
        {"name":"D. Livaković","team":"CIN","price":16000000,"renovation":8000000,"clausula":72000000,"contrato":"1 Season","cesion":None},
        {"name":"Richarlison","team":"CLT","price":19000000,"renovation":9500000,"clausula":85500000,"contrato":"1 Season","cesion":None},
        {"name":"N. Madueke","team":"LAFC","price":48000000,"renovation":24000000,"clausula":216000000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Pino","team":"PHI","price":39500000,"renovation":19750000,"clausula":177750000,"contrato":"1 Season","cesion":None},
        {"name":"H. Ekitike","team":"SKC","price":28500000,"renovation":14250000,"clausula":128250000,"contrato":"1 Season","cesion":None},
        {"name":"J. Durán","team":"SEA","price":35000000,"renovation":17500000,"clausula":157500000,"contrato":"1 Season","cesion":None},
        {"name":"Moleiro","team":"MIN","price":35000000,"renovation":17500000,"clausula":157500000,"contrato":"1 Season","cesion":None},
        {"name":"N. Rovella","team":"TOR","price":35500000,"renovation":17750000,"clausula":159750000,"contrato":"1 Season","cesion":None},
        {"name":"Nico González","team":"MIN","price":26000000,"renovation":13000000,"clausula":117000000,"contrato":"1 Season","cesion":None},
        {"name":"P. Barrios","team":"LA","price":39500000,"renovation":19750000,"clausula":177750000,"contrato":"1 Season","cesion":None},
        {"name":"R. Cherki","team":"RSL","price":38500000,"renovation":19250000,"clausula":173250000,"contrato":"1 Season","cesion":None},
        {"name":"O. Diomande","team":"CLB","price":40000000,"renovation":20000000,"clausula":180000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Thiaw","team":"STL","price":25500000,"renovation":12750000,"clausula":114750000,"contrato":"1 Season","cesion":None},
        {"name":"A. Ramsdale","team":"PHI","price":49000000,"renovation":24500000,"clausula":220500000,"contrato":"1 Season","cesion":None},
        {"name":"Antony","team":"MTL","price":35000000,"renovation":17500000,"clausula":157500000,"contrato":"1 Season","cesion":None},
        {"name":"B. Brobbey","team":"ATL","price":23000000,"renovation":11500000,"clausula":103500000,"contrato":"1 Season","cesion":None},
        {"name":"H. Elliott","team":"SDFC","price":23000000,"renovation":11500000,"clausula":103500000,"contrato":"1 Season","cesion":None},
        {"name":"Fermín","team":"MIN","price":31500000,"renovation":15750000,"clausula":141750000,"contrato":"1 Season","cesion":None},
        {"name":"Enzo Millot","team":"ATX","price":22500000,"renovation":11250000,"clausula":101250000,"contrato":"1 Season","cesion":None},
        {"name":"A. Güler","team":"SJ","price":30500000,"renovation":15250000,"clausula":137250000,"contrato":"1 Season","cesion":None},
        {"name":"J. Gittens","team":"CLB","price":27500000,"renovation":13750000,"clausula":123750000,"contrato":"1 Season","cesion":None},
        {"name":"A. Pavlovic","team":"VAN","price":29000000,"renovation":14500000,"clausula":130500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Silva","team":"STL","price":29000000,"renovation":14500000,"clausula":130500000,"contrato":"1 Season","cesion":None},
        {"name":"L. Badé","team":"CHI","price":20000000,"renovation":10000000,"clausula":90000000,"contrato":"1 Season","cesion":None},
        {"name":"Rico Lewis","team":"SKC","price":26000000,"renovation":13000000,"clausula":117000000,"contrato":"1 Season","cesion":None},
        {"name":"G. Scalvini","team":"LA","price":29000000,"renovation":14500000,"clausula":130500000,"contrato":"1 Season","cesion":None},
        {"name":"H. Lloris","team":"CIN","price":3000000,"renovation":1500000,"clausula":13500000,"contrato":"1 Season","cesion":None},
        {"name":"B. Verbruggen","team":"NE","price":18500000,"renovation":9250000,"clausula":83250000,"contrato":"1 Season","cesion":None},
        {"name":"R. Højlund","team":"MTL","price":21500000,"renovation":10750000,"clausula":96750000,"contrato":"1 Season","cesion":None},
        {"name":"N. Okafor","team":"NYC","price":21500000,"renovation":10750000,"clausula":96750000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Asprilla","team":"LAFC","price":21000000,"renovation":10500000,"clausula":94500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Garnacho","team":"CIN","price":21000000,"renovation":10500000,"clausula":94500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Kalimuendo","team":"HOU","price":15500000,"renovation":7750000,"clausula":69750000,"contrato":"1 Season","cesion":None},
        {"name":"M. Tel","team":"SKC","price":23000000,"renovation":11500000,"clausula":103500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Ezzalzouli","team":"ORL","price":16000000,"renovation":8000000,"clausula":72000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Mainoo","team":"RBNY","price":22500000,"renovation":11250000,"clausula":101250000,"contrato":"1 Season","cesion":None},
        {"name":"C. Bradley","team":"CLT","price":20000000,"renovation":10000000,"clausula":90000000,"contrato":"1 Season","cesion":None},
        {"name":"J. Hato","team":"DCU","price":21000000,"renovation":10500000,"clausula":94500000,"contrato":"1 Season","cesion":None},
        {"name":"A. Hložek","team":"CLB","price":16500000,"renovation":8250000,"clausula":74250000,"contrato":"1 Season","cesion":None},
        {"name":"Ansu Fati","team":"HOU","price":38000000,"renovation":19000000,"clausula":171000000,"contrato":"1 Season","cesion":None},
        {"name":"V. Roque","team":"POR","price":17500000,"renovation":8750000,"clausula":78750000,"contrato":"1 Season","cesion":None},
        {"name":"T. Baldanzi","team":"NYC","price":16000000,"renovation":8000000,"clausula":72000000,"contrato":"1 Season","cesion":None},
        {"name":"M. Soulé","team":"ATL","price":17000000,"renovation":8500000,"clausula":76500000,"contrato":"1 Season","cesion":None},
        {"name":"B. El Khannouss","team":"STL","price":16500000,"renovation":8250000,"clausula":74250000,"contrato":"1 Season","cesion":None},
        {"name":"N. Zalewski","team":"LA","price":11000000,"renovation":5500000,"clausula":49500000,"contrato":"1 Season","cesion":None},
        {"name":"K. Yıldız","team":"DAL","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"G. Reyna","team":"MIA","price":27500000,"renovation":13750000,"clausula":123750000,"contrato":"1 Season","cesion":None},
        {"name":"D. Silva","team":"SJ","price":450000,"renovation":225000,"clausula":2025000,"contrato":"1 Season","cesion":None},
        {"name":"A. Gray","team":"NE","price":12500000,"renovation":6250000,"clausula":56250000,"contrato":"1 Season","cesion":None},
        {"name":"M. Casadó","team":"DAL","price":11600000,"renovation":5800000,"clausula":52200000,"contrato":"1 Season","cesion":None},
        {"name":"A. Lafont","team":"PHI","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"G. Ochoa","team":"COL","price":1500000,"renovation":750000,"clausula":6750000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Moukoko","team":"MTL","price":22500000,"renovation":11250000,"clausula":101250000,"contrato":"1 Season","cesion":None},
        {"name":"A. Velasco","team":"DAL","price":12000000,"renovation":6000000,"clausula":54000000,"contrato":"1 Season","cesion":None},
        {"name":"L. Abada","team":"CLT","price":9500000,"renovation":4750000,"clausula":42750000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Bonny","team":"CIN","price":9500000,"renovation":4750000,"clausula":42750000,"contrato":"1 Season","cesion":None},
        {"name":"Fábio Carvalho","team":"CLB","price":9500000,"renovation":4750000,"clausula":42750000,"contrato":"1 Season","cesion":None},
        {"name":"A. Scott","team":"NHS","price":9000000,"renovation":4500000,"clausula":40500000,"contrato":"1 Season","cesion":None},
        {"name":"C. Medina","team":"SKC","price":12500000,"renovation":6250000,"clausula":56250000,"contrato":"1 Season","cesion":None},
        {"name":"C. Echeverri","team":"DCU","price":10000000,"renovation":5000000,"clausula":45000000,"contrato":"1 Season","cesion":None},
        {"name":"C. Chukwuemeka","team":"STL","price":9500000,"renovation":4750000,"clausula":42750000,"contrato":"1 Season","cesion":None},
        {"name":"D. Moreira","team":"ORL","price":9000000,"renovation":4500000,"clausula":40500000,"contrato":"1 Season","cesion":None},
        {"name":"V. Barco","team":"ATX","price":8500000,"renovation":4250000,"clausula":38250000,"contrato":"1 Season","cesion":None},
        {"name":"I. Fresneda","team":"POR","price":8500000,"renovation":4250000,"clausula":38250000,"contrato":"1 Season","cesion":None},
        {"name":"T. Magno","team":"NYC","price":7000000,"renovation":3500000,"clausula":31500000,"contrato":"1 Season","cesion":None},
        {"name":"E. Ferguson","team":"SJ","price":10000000,"renovation":5000000,"clausula":45000000,"contrato":"1 Season","cesion":None},
        {"name":"K. Páez","team":"MIA","price":7000000,"renovation":3500000,"clausula":31500000,"contrato":"1 Season","cesion":None},
        {"name":"J. Enciso","team":"LAFC","price":6500000,"renovation":3250000,"clausula":29250000,"contrato":"1 Season","cesion":None},
        {"name":"Ângelo","team":"TOR","price":6500000,"renovation":3250000,"clausula":29250000,"contrato":"1 Season","cesion":None},
        {"name":"A. Richardson","team":"DCU","price":7000000,"renovation":3500000,"clausula":31500000,"contrato":"1 Season","cesion":None},
        {"name":"B. Domínguez","team":"SDFC","price":6500000,"renovation":3250000,"clausula":29250000,"contrato":"1 Season","cesion":None},
        {"name":"T. Lamptey","team":"VAN","price":8000000,"renovation":4000000,"clausula":36000000,"contrato":"1 Season","cesion":None},
        {"name":"S. Magassa","team":"RSL","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"A. Gómez","team":"NE","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"O. Bobb","team":"SEA","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"L. Romero","team":"NHS","price":3200000,"renovation":1600000,"clausula":14400000,"contrato":"1 Season","cesion":None},
        {"name":"C. Cassano","team":"CLT","price":18300000,"renovation":9150000,"clausula":82350000,"contrato":"1 Season","cesion":None},
        {"name":"F. Pellistri","team":"SDFC","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"L. Miley","team":"ORL","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"Stefan Bajcetic","team":"CLT","price":4800000,"renovation":2400000,"clausula":21600000,"contrato":"1 Season","cesion":None},
        {"name":"V. Carboni","team":"RBNY","price":5500000,"renovation":2750000,"clausula":24750000,"contrato":"1 Season","cesion":None},
        {"name":"J. Duranville","team":"NHS","price":4800000,"renovation":2400000,"clausula":21600000,"contrato":"1 Season","cesion":None},
        {"name":"P. Wanner","team":"CHI","price":4400000,"renovation":2200000,"clausula":19800000,"contrato":"1 Season","cesion":None},
        {"name":"S. Charles","team":"DAL","price":4100000,"renovation":2050000,"clausula":18450000,"contrato":"1 Season","cesion":None},
        {"name":"O. Cortés","team":"MIA","price":3500000,"renovation":1750000,"clausula":15750000,"contrato":"1 Season","cesion":None},
        {"name":"M. Guiu","team":"MIN","price":3700000,"renovation":1850000,"clausula":16650000,"contrato":"1 Season","cesion":None},
        {"name":"B. Doak","team":"ATX","price":4000000,"renovation":2000000,"clausula":18000000,"contrato":"1 Season","cesion":None},
        {"name":"Peter","team":"RBNY","price":3600000,"renovation":1800000,"clausula":16200000,"contrato":"1 Season","cesion":None},
        {"name":"Newerton","team":"SJ","price":3800000,"renovation":1900000,"clausula":17100000,"contrato":"1 Season","cesion":None},
        {"name":"T. Gulliksen","team":"COL","price":3500000,"renovation":1750000,"clausula":15750000,"contrato":"1 Season","cesion":None},
        {"name":"J. Castrop","team":"ATL","price":3500000,"renovation":1750000,"clausula":15750000,"contrato":"1 Season","cesion":None},
        {"name":"T. Pembélé","team":"MTL","price":3400000,"renovation":1700000,"clausula":15300000,"contrato":"1 Season","cesion":None},
        {"name":"M. Del Blanco","team":"CIN","price":3300000,"renovation":1650000,"clausula":14850000,"contrato":"1 Season","cesion":None},
        {"name":"R. Bardghji","team":"COL","price":3600000,"renovation":1800000,"clausula":16200000,"contrato":"1 Season","cesion":None},
        {"name":"Matheus França","team":"MTL","price":3600000,"renovation":1800000,"clausula":16200000,"contrato":"1 Season","cesion":None},
        {"name":"S. Pafundi","team":"HOU","price":3500000,"renovation":1750000,"clausula":15750000,"contrato":"1 Season","cesion":None},
        {"name":"D. Washington","team":"TOR","price":3100000,"renovation":1550000,"clausula":13950000,"contrato":"1 Season","cesion":None},
        {"name":"E. Mbappé","team":"NYC","price":2700000,"renovation":1350000,"clausula":12150000,"contrato":"1 Season","cesion":None},
        {"name":"A. Moreira","team":"SKC","price":2900000,"renovation":1450000,"clausula":13050000,"contrato":"1 Season","cesion":None},
        {"name":"H. Fort","team":"POR","price":2700000,"renovation":1350000,"clausula":12150000,"contrato":"1 Season","cesion":None},
        {"name":"B. Castro","team":"MIA","price":2500000,"renovation":1250000,"clausula":11250000,"contrato":"1 Season","cesion":None},
        {"name":"Q. Sullivan","team":"PHI","price":2500000,"renovation":1250000,"clausula":11250000,"contrato":"1 Season","cesion":None},
        {"name":"Á. Alarcón","team":"LA","price":2400000,"renovation":1200000,"clausula":10800000,"contrato":"1 Season","cesion":None},
        {"name":"I. Babadi","team":"NYC","price":2600000,"renovation":1300000,"clausula":11700000,"contrato":"1 Season","cesion":None},
        {"name":"G. Puerta","team":"SEA","price":2400000,"renovation":1200000,"clausula":10800000,"contrato":"1 Season","cesion":None},
        {"name":"B. Norton-Cuffy","team":"RSL","price":2300000,"renovation":1150000,"clausula":10350000,"contrato":"1 Season","cesion":None},
        {"name":"Iker Bravo","team":"PHI","price":2200000,"renovation":1100000,"clausula":9900000,"contrato":"1 Season","cesion":None},
        {"name":"A. van Axel Dongen","team":"RBNY","price":1800000,"renovation":900000,"clausula":8100000,"contrato":"1 Season","cesion":None},
        {"name":"P. Brunner","team":"CHI","price":2300000,"renovation":1150000,"clausula":10350000,"contrato":"1 Season","cesion":None},
        {"name":"T. Land","team":"PHI","price":1600000,"renovation":800000,"clausula":7200000,"contrato":"1 Season","cesion":None},
        {"name":"K. Gordon","team":"VAN","price":1000000,"renovation":500000,"clausula":4500000,"contrato":"1 Season","cesion":None},
        {"name":"Y. Eduardo","team":"CLB","price":1300000,"renovation":650000,"clausula":5850000,"contrato":"1 Season","cesion":None},
    ]
    players_df = pd.DataFrame(data)
    return players_df, teams_df


def fmt_money(v):
    if not v or v == 0: return "—"
    if v >= 1e9: return f"${v/1e9:.2f}B"
    if v >= 1e6: return f"${v/1e6:.1f}M"
    if v >= 1e3: return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"


PRESI_COLORS = {"JNKA": "#e8b84b", "MATI": "#3b82f6", "MAXI": "#a78bfa"}
CONTRATO_COLORS = {
    "1 Season": "#22c55e", "2 Season": "#3b82f6",
    "Cesion Corta": "#f97316", "Cesion Larga": "#ef4444"
}


# ── App ──────────────────────────────────────────────────────────────────────
players_df, teams_df = load_full_data()

# Sidebar navigation
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
    st.caption(f"**{len(players_df)}** jugadores · **{len(teams_df)}** equipos")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: JUGADORES
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚽ Jugadores":
    st.markdown('<div class="page-title">MERCADO DE JUGADORES</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">MMJ League Season V · 317 Jugadores · 30 Equipos</div>', unsafe_allow_html=True)

    # Stats strip
    total_val = players_df["price"].sum()
    avg_val   = players_df["price"].mean()
    top_p     = players_df.loc[players_df["price"].idxmax()]
    cedidos   = players_df["cesion"].notna().sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Valor Total Liga", fmt_money(total_val))
    c2.metric("Valor Promedio", fmt_money(avg_val))
    c3.metric(f"Top: {top_p['name']}", fmt_money(top_p["price"]))
    c4.metric("Jugadores Cedidos", int(cedidos))
    c5.metric("Contratos 1 Season", int((players_df["contrato"] == "1 Season").sum()))

    st.divider()

    # Filters
    fc1, fc2, fc3, fc4, fc5 = st.columns([3, 2, 2, 2, 1])
    search   = fc1.text_input("🔍 Buscar jugador...", label_visibility="collapsed", placeholder="🔍 Buscar jugador...")
    teams_list = sorted(players_df["team"].unique())
    team_f   = fc2.selectbox("Equipo", ["Todos"] + teams_list, label_visibility="collapsed")
    contrato_f = fc3.selectbox("Contrato", ["Todos", "1 Season", "2 Season", "Cesion Corta", "Cesion Larga"], label_visibility="collapsed")
    sort_f   = fc4.selectbox("Ordenar", ["Precio ↓", "Precio ↑", "Cláusula ↓", "Nombre A-Z"], label_visibility="collapsed")
    solo_cedidos = fc5.checkbox("Cedidos", value=False)

    # Apply filters
    df = players_df.copy()
    if search:
        df = df[df["name"].str.contains(search, case=False, na=False) |
                df["team"].str.contains(search, case=False, na=False)]
    if team_f != "Todos":
        df = df[df["team"] == team_f]
    if contrato_f != "Todos":
        df = df[df["contrato"] == contrato_f]
    if solo_cedidos:
        df = df[df["cesion"].notna()]

    sort_map = {"Precio ↓": ("price", False), "Precio ↑": ("price", True),
                "Cláusula ↓": ("clausula", False), "Nombre A-Z": ("name", True)}
    scol, sasc = sort_map[sort_f]
    df = df.sort_values(scol, ascending=sasc).reset_index(drop=True)

    st.caption(f"Mostrando **{len(df)}** de **{len(players_df)}** jugadores")

    # Display table
    display_df = df.copy()
    display_df["Precio M."]   = display_df["price"].apply(fmt_money)
    display_df["Renovación"]  = display_df["renovation"].apply(fmt_money)
    display_df["Cláusula"]    = display_df["clausula"].apply(fmt_money)
    display_df["Cedido a"]    = display_df["cesion"].fillna("—")

    st.dataframe(
        display_df[["name", "team", "contrato", "Precio M.", "Renovación", "Cláusula", "Cedido a"]].rename(columns={
            "name": "Jugador", "team": "Equipo", "contrato": "Contrato"
        }),
        use_container_width=True,
        height=520,
        hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏟️ Equipos":
    st.markdown('<div class="page-title">CLUBES</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Información de equipos · Estadios · Cuerpo técnico</div>', unsafe_allow_html=True)

    # Search & filter
    fc1, fc2 = st.columns([3, 1])
    team_search = fc1.text_input("Buscar", placeholder="🔍 Buscar equipo o DT...", label_visibility="collapsed")
    presi_f = fc2.selectbox("Presidente", ["Todos", "JNKA", "MATI", "MAXI"], label_visibility="collapsed")

    tf = teams_df.copy()
    if team_search:
        tf = tf[tf["full_name"].str.contains(team_search, case=False) |
                tf["dt"].str.contains(team_search, case=False, na=False)]
    if presi_f != "Todos":
        tf = tf[tf["presi"] == presi_f]
    tf = tf.sort_values("full_name").reset_index(drop=True)

    for _, team in tf.iterrows():
        squad = players_df[players_df["team"] == team["code"]].sort_values("price", ascending=False)
        total_squad_val = squad["price"].sum()
        top5 = squad.head(5)

        with st.expander(f"**{team['code']}** — {team['full_name']}  |  🏟️ {team['estadio']}  |  💼 {team['presi']}", expanded=False):
            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("DT", team["dt"] or "—")
            ec2.metric("Valor Plantilla", fmt_money(total_squad_val))
            ec3.metric("Presupuesto", fmt_money(team["presupuesto"]))
            ec4.metric("Jugadores", len(squad))

            st.caption("**Top 5 jugadores más valiosos:**")
            for _, p in top5.iterrows():
                cesion_txt = f" → {p['cesion']}" if pd.notna(p["cesion"]) else ""
                st.markdown(
                    f"&nbsp;&nbsp;`{team['code']}` **{p['name']}**{cesion_txt} — "
                    f"<span style='color:#e8b84b'>{fmt_money(p['price'])}</span> · "
                    f"<span style='font-size:0.75rem;color:#5a7080'>{p['contrato']}</span>",
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRESUPUESTOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Presupuestos":
    st.markdown('<div class="page-title">PRESUPUESTOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ranking de presupuesto disponible por equipo</div>', unsafe_allow_html=True)

    budget_df = teams_df.sort_values("presupuesto", ascending=False).reset_index(drop=True)
    total_b = budget_df["presupuesto"].sum()
    avg_b   = budget_df["presupuesto"].mean()

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Total Presupuestos", fmt_money(total_b))
    b2.metric("Promedio por equipo", fmt_money(avg_b))
    b3.metric("Mayor presupuesto", f"{budget_df.iloc[0]['code']} — {fmt_money(budget_df.iloc[0]['presupuesto'])}")
    b4.metric("Menor presupuesto", f"{budget_df.iloc[-1]['code']} — {fmt_money(budget_df.iloc[-1]['presupuesto'])}")

    st.divider()

    # Bar chart
    fig = px.bar(
        budget_df,
        x="presupuesto", y="code",
        orientation="h",
        color="presi",
        color_discrete_map=PRESI_COLORS,
        labels={"presupuesto": "Presupuesto ($)", "code": "Equipo", "presi": "Presidente"},
        title="Presupuesto disponible por equipo",
        text=budget_df["presupuesto"].apply(fmt_money),
    )
    fig.update_layout(
        plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
        font_color="#e2eaf4", title_font_color="#e8b84b",
        yaxis=dict(categoryorder="total ascending"),
        height=700, showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    st.plotly_chart(fig, use_container_width=True)

    # Table
    budget_display = budget_df.copy()
    budget_display["#"] = range(1, len(budget_display) + 1)
    budget_display["Presupuesto"] = budget_display["presupuesto"].apply(fmt_money)
    st.dataframe(
        budget_display[["#", "code", "full_name", "presi", "dt", "Presupuesto"]].rename(columns={
            "code": "Código", "full_name": "Equipo", "presi": "Presidente", "dt": "DT"
        }),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CEDIDOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Cedidos":
    st.markdown('<div class="page-title">JUGADORES CEDIDOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Cesiones cortas y largas activas</div>', unsafe_allow_html=True)

    loans = players_df[players_df["cesion"].notna()].copy()
    corta = loans[loans["contrato"] == "Cesion Corta"]
    larga = loans[loans["contrato"] == "Cesion Larga"]

    l1, l2, l3 = st.columns(3)
    l1.metric("Total Cedidos", len(loans))
    l2.metric("Cesión Corta ⚡", len(corta))
    l3.metric("Cesión Larga 🔗", len(larga))

    st.divider()

    col1, col2 = st.columns(2)

    def loan_table(df_l, label):
        df_l = df_l.sort_values("price", ascending=False).copy()
        df_l["Precio M."]  = df_l["price"].apply(fmt_money)
        df_l["Cláusula"]   = df_l["clausula"].apply(fmt_money)
        df_l["Cedido a"]   = df_l["cesion"]
        st.markdown(f"**{label} ({len(df_l)})**")
        st.dataframe(
            df_l[["name", "team", "Cedido a", "Precio M.", "Cláusula"]].rename(columns={
                "name": "Jugador", "team": "Club propietario"
            }),
            use_container_width=True, hide_index=True
        )

    with col1:
        loan_table(corta, "⚡ Cesión Corta")
    with col2:
        loan_table(larga, "🔗 Cesión Larga")

    st.divider()
    st.markdown("#### Detalle completo")

    # Sankey diagram of loans
    owner_nodes  = loans["team"].unique().tolist()
    dest_nodes   = loans["cesion"].unique().tolist()
    all_nodes    = list(set(owner_nodes + dest_nodes))
    node_idx     = {n: i for i, n in enumerate(all_nodes)}

    source = [node_idx[r["team"]] for _, r in loans.iterrows()]
    target = [node_idx[r["cesion"]] for _, r in loans.iterrows()]
    values = [r["price"] / 1e6 for _, r in loans.iterrows()]

    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=12, thickness=16,
            label=all_nodes,
            color=["#e8b84b"] * len(all_nodes),
        ),
        link=dict(source=source, target=target, value=values, color="rgba(232,184,75,0.18)")
    ))
    fig_sankey.update_layout(
        title="Flujo de cesiones (tamaño = valor en M$)",
        paper_bgcolor="#060a0f", font_color="#e2eaf4",
        title_font_color="#e8b84b", height=400
    )
    st.plotly_chart(fig_sankey, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Estadísticas":
    st.markdown('<div class="page-title">ESTADÍSTICAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Análisis de la liga · Distribuciones · Rankings</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Distribución de valores", "🏆 Rankings por equipo", "🗂️ Contratos"])

    with tab1:
        fig_hist = px.histogram(
            players_df, x="price", nbins=40,
            labels={"price": "Precio de Mercado ($)", "count": "Jugadores"},
            title="Distribución de valores de mercado",
            color_discrete_sequence=["#e8b84b"],
        )
        fig_hist.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                               font_color="#e2eaf4", title_font_color="#e8b84b")
        st.plotly_chart(fig_hist, use_container_width=True)

        # Top 20 players
        top20 = players_df.nlargest(20, "price").copy()
        top20["Precio"] = top20["price"].apply(fmt_money)
        fig_top = px.bar(
            top20, x="price", y="name", orientation="h",
            color="team", title="Top 20 jugadores más valiosos",
            labels={"price": "Precio ($)", "name": "Jugador", "team": "Equipo"},
            text=top20["Precio"],
        )
        fig_top.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                              font_color="#e2eaf4", title_font_color="#e8b84b",
                              yaxis=dict(categoryorder="total ascending"), height=600,
                              showlegend=False)
        fig_top.update_traces(textposition="outside")
        st.plotly_chart(fig_top, use_container_width=True)

    with tab2:
        team_stats = players_df.groupby("team").agg(
            valor_total=("price", "sum"),
            jugadores=("name", "count"),
            avg_valor=("price", "mean"),
        ).reset_index()

        team_stats = team_stats.merge(teams_df[["code", "full_name", "presi", "presupuesto"]],
                                      left_on="team", right_on="code", how="left")
        team_stats = team_stats.sort_values("valor_total", ascending=False)

        fig_teams = px.bar(
            team_stats, x="team", y="valor_total",
            color="presi", color_discrete_map=PRESI_COLORS,
            title="Valor total de plantilla por equipo",
            labels={"team": "Equipo", "valor_total": "Valor Total ($)", "presi": "Presidente"},
        )
        fig_teams.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                                font_color="#e2eaf4", title_font_color="#e8b84b", height=450)
        st.plotly_chart(fig_teams, use_container_width=True)

        # Scatter: valor vs presupuesto
        fig_scatter = px.scatter(
            team_stats, x="presupuesto", y="valor_total",
            size="jugadores", color="presi",
            color_discrete_map=PRESI_COLORS,
            hover_name="team",
            title="Presupuesto disponible vs Valor de plantilla",
            labels={"presupuesto": "Presupuesto ($)", "valor_total": "Valor Plantilla ($)", "presi": "Presidente"},
            text="team",
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter.update_layout(plot_bgcolor="#0d1520", paper_bgcolor="#060a0f",
                                  font_color="#e2eaf4", title_font_color="#e8b84b", height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        # Pie by contrato type
        contrato_counts = players_df["contrato"].value_counts().reset_index()
        fig_pie = px.pie(
            contrato_counts, values="count", names="contrato",
            title="Distribución de tipos de contrato",
            color_discrete_map=CONTRATO_COLORS,
        )
        fig_pie.update_layout(paper_bgcolor="#060a0f", font_color="#e2eaf4",
                              title_font_color="#e8b84b")
        st.plotly_chart(fig_pie, use_container_width=True)

        # By presi
        presi_val = players_df.merge(
            teams_df[["code", "presi"]], left_on="team", right_on="code", how="left"
        ).groupby("presi")["price"].sum().reset_index()
        presi_val.columns = ["Presidente", "Valor Total"]
        presi_val["Valor Total Fmt"] = presi_val["Valor Total"].apply(fmt_money)

        fig_presi = px.pie(
            presi_val, values="Valor Total", names="Presidente",
            title="Valor total de plantilla por presidente",
            color="Presidente", color_discrete_map=PRESI_COLORS,
        )
        fig_presi.update_layout(paper_bgcolor="#060a0f", font_color="#e2eaf4",
                                title_font_color="#e8b84b")
        st.plotly_chart(fig_presi, use_container_width=True)
