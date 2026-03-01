# ⚽ MMJ League — Mercado

Dashboard interactivo para gestionar el mercado de la **MMJ League Season V**, una liga de fantasy football con 30 equipos y 317 jugadores.

## 🚀 Demo en Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tu-app.streamlit.app)

---

## 📦 Instalación local

### 1. Clona el repositorio
```bash
git clone https://github.com/tu-usuario/mmj-league.git
cd mmj-league
```

### 2. Instala dependencias
```bash
pip install -r requirements.txt
```

### 3. Corre la app
```bash
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501`

---

## 🌐 Deploy en Streamlit Cloud (gratis)

1. Sube este repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repo y el archivo `app.py`
5. Haz clic en **Deploy** — ¡listo!

> El archivo `JUGADORES.xlsx` debe estar en la raíz del repositorio.

---

## 📊 Features

| Sección | Descripción |
|---|---|
| ⚽ **Jugadores** | Tabla filtrable con búsqueda, orden y filtros de contrato/equipo |
| 🏟️ **Equipos** | Info de cada club: DT, estadio, plantilla, presupuesto |
| 💰 **Presupuestos** | Ranking visual con gráfico de barras por presidente |
| 🔄 **Cedidos** | Lista de cesiones cortas y largas + diagrama Sankey |
| 📊 **Estadísticas** | Histogramas, rankings, scatter plots y gráficos de distribución |

---

## 🗂️ Estructura del proyecto

```
mmj-league/
├── app.py              # App principal de Streamlit
├── JUGADORES.xlsx      # Base de datos (Players + Teams)
├── requirements.txt    # Dependencias Python
└── README.md
```

---

## 📋 Formato del Excel

### Hoja `Players`
| Jugador | Price | Renovation | Clausula | Contrato | Cesion |
|---|---|---|---|---|---|
| M. Salah | 104000000 | 52000000 | 468000000 | 1 Season | |

### Hoja `Teams`
| Equipo | Estadio | Presi | DT | Presupuesto |
|---|---|---|---|---|
| Atlanta United | Mercedes-Benz Stadium | JNKA | Sérgio Conceição | 28000000 |

---

## 🛠️ Tecnologías

- [Streamlit](https://streamlit.io) — Framework web
- [Pandas](https://pandas.pydata.org) — Manejo de datos
- [Plotly](https://plotly.com/python/) — Gráficos interactivos
- [OpenPyXL](https://openpyxl.readthedocs.io) — Lectura de Excel

---

*MMJ League Season V*
