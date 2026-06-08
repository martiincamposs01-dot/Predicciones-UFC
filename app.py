import streamlit as st
import pandas as pd
import os
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="UFC Freedom 250 | Cokemma Edition", page_icon="🥊", layout="wide", initial_sidebar_state="collapsed")

# --- 📸 DICCIONARIO DE IMÁGENES Y DATOS OFICIALES ---
TRAILER_OFICIAL = "https://youtu.be/iNJIs5bXoAE?si=Lbes9bQDegv6vocd"
BANNER_PRINCIPAL = "https://images.daznservices.com/di/library/DAZN_News/38/dc/ufc-casa-blanca-ilia-topuria-vs-justin-gaethje_1lpqgt419yykc17egde0t8b3g1.jpg?t=-828957604"
URL_APP = "https://predicciones-ufc-87c5opnpg9pmnfjm9qqrkr.streamlit.app"

FIGHTER_IMAGES = {
    "Ilia Topuria": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2024-10/TOPURIA_ILIA_L_BELT_10-26.png?itok=0ZnoiqvU",
    "Justin Gaethje": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-01/GAETHJE_JUSTIN_L_BELTMOCK.png?itok=Ec57vAPj",
    "Alex Pereira": "https://gidstats.com/img/fighters/0/0/1-824.png",
    "Ciryl Gane": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-01/5/GANE_CIRYL_L_12-07.png?itok=RtxXOv1m",
    "Sean O'Malley": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-01/OMALLEY_SEAN_L_01-24.png?itok=GKNy0vLH",
    "Aiemann Zahabi": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-01/5/ZAHABI_AIEMANN_L_11-02.png?itok=7oV3Lazp",
    "Josh Hokit": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-01/HOKIT_JOSH_L_01-24.png?itok=q4AaxC15",
    "Derrick Lewis": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-07/LEWIS_DERRICK_L_07-12.png?itok=NW56kLpV",
    "Mauricio Ruffy": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-02/RUFFY_MAURICIO_L_01-31.png?itok=I_xrL9e4",
    "Michael Chandler": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-04/CHANDLER_MICHAEL_L_04-12.png?itok=a63uTG7H",
    "Bo Nickal": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-11/NICKAL_BO_L_11-15.png?itok=H_KDgWwL",
    "Kyle Daukaus": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-11/DAUKAUS_KYLE_L_11-15.png?itok=9rQVeQfZ",
    "Diego Lopes": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-02/LOPES_DIEGO_L_01-31.png?itok=m_ex383n",
    "Steve Garcia": "https://ufc.com/images/styles/athlete_bio_full_body/s3/2025-10/GARCIA_STEVE_L_11-01.png?itok=C9aRxxhd"
}

FIGHTER_STATS = {
    "Ilia Topuria": {"record": "17-0-0", "altura": "1.70 m", "alcance": "1.75 m", "odds": "-720"},
    "Justin Gaethje": {"record": "27-5-0", "altura": "1.81 m", "alcance": "1.78 m", "odds": "+450"},
    "Alex Pereira": {"record": "13-3-0", "altura": "1.93 m", "alcance": "2.01 m", "odds": "-113"},
    "Ciryl Gane": {"record": "13-2-0", "altura": "1.93 m", "alcance": "2.06 m", "odds": "-113"},
    "Sean O'Malley": {"record": "19-3-0 (1 NC)", "altura": "1.80 m", "alcance": "1.83 m", "odds": "-430"},
    "Aiemann Zahabi": {"record": "14-2-0", "altura": "1.73 m", "alcance": "1.74 m", "odds": "+300"},
    "Josh Hokit": {"record": "9-0-0", "altura": "1.85 m", "alcance": "1.87 m", "odds": "-340"},
    "Derrick Lewis": {"record": "29-13-0 (1 NC)", "altura": "1.88 m", "alcance": "2.01 m", "odds": "+250"},
    "Mauricio Ruffy": {"record": "13-2-0", "altura": "1.80 m", "alcance": "1.91 m", "odds": "-670"},
    "Michael Chandler": {"record": "23-10-0", "altura": "1.73 m", "alcance": "1.82 m", "odds": "+430"},
    "Bo Nickal": {"record": "6-0-0", "altura": "1.85 m", "alcance": "1.93 m", "odds": "-330"},
    "Kyle Daukaus": {"record": "17-4-0 (1 NC)", "altura": "1.88 m", "alcance": "1.93 m", "odds": "+240"},
    "Diego Lopes": {"record": "24-6-0", "altura": "1.80 m", "alcance": "1.84 m", "odds": "-160"},
    "Steve Garcia": {"record": "16-5-0", "altura": "1.83 m", "alcance": "1.91 m", "odds": "+135"}
}

# --- ESTILOS CSS (DISEÑO PREMIUM OPTIMIZADO PARA PC) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;600;800&display=swap');

/* Fondo Global */
.stApp { 
    background-color: #050505; 
    color: #ffffff; 
    font-family: 'Montserrat', sans-serif; 
    background-image: radial-gradient(circle at 50% 0%, #1a0505 0%, #050505 60%);
}

/* Tipografías Especiales */
h1, h2, h3, .fighter-name, .vs-text, .weight-class, .stat-title { 
    font-family: 'Bebas Neue', sans-serif !important; 
    letter-spacing: 1.5px;
}

/* Ocultar UI de Streamlit en Modo Directo */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Ticker ESPN Style Mejorado para PC */
.ticker-wrap { 
    width: 100%; 
    background-color: #DC2626; 
    color: white; 
    padding: 12px 0; 
    font-family: 'Bebas Neue', sans-serif; 
    font-size: 1.8rem; 
    letter-spacing: 2px; 
    border-radius: 8px; 
    margin-bottom: 30px; 
    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.6); 
    text-transform: uppercase;
}

/* ---------------------------------------------------
   Pestañas (Tabs) ULTRA VISIBLES PARA PC
--------------------------------------------------- */
div[data-baseweb="tab-list"] {
    gap: 12px;
    border-bottom: 3px solid #DC2626; 
    padding-bottom: 0px;
}

button[data-baseweb="tab"] {
    font-size: 1.6rem !important; 
    font-family: 'Bebas Neue', sans-serif !important; 
    text-transform: uppercase;
    padding: 15px 35px !important; 
    background-color: #111111 !important; 
    border: 2px solid #333333 !important; 
    border-bottom: none !important;
    border-radius: 12px 12px 0 0 !important; 
    color: #888888 !important; 
    letter-spacing: 2px;
    transition: all 0.3s ease;
}

/* Pestaña Activa (Seleccionada) */
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, #DC2626 0%, #8b0000 100%) !important;
    color: #ffffff !important; 
    border: 2px solid #ff4d4d !important;
    border-bottom: none !important;
    box-shadow: 0 -5px 20px rgba(220, 38, 38, 0.5);
    transform: translateY(-2px);
}

button[data-baseweb="tab"]:hover {
    background-color: #222222 !important;
    color: #ffffff !important;
}

/* Botones de Acción */
.stButton > button {
    background: linear-gradient(90deg, #DC2626 0%, #991B1B 100%); 
    color: #ffffff; 
    font-weight: 800; 
    font-family: 'Montserrat', sans-serif; 
    font-size: 1.2rem; 
    border: 1px solid #ff4d4d; 
    border-radius: 8px; 
    padding: 18px 30px; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
}
.stButton > button:hover { 
    transform: translateY(-3px); 
    box-shadow: 0 10px 25px rgba(220, 38, 38, 0.7); 
    border: 1px solid #ffffff; 
}

/* Tarjetas de Noticias Web */
.news-card {
    display: block;
    background-size: cover;
    background-position: center;
    height: 250px;
    border-radius: 12px;
    text-decoration: none;
    position: relative;
    overflow: hidden;
    border: 2px solid #333;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
}
.news-card:hover {
    transform: translateY(-5px);
    border-color: #D4AF37;
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4);
}
.news-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, rgba(0,0,0,1), transparent);
    padding: 30px 15px 15px 15px;
}
.news-title {
    color: white;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    margin: 0;
    text-shadow: 2px 2px 5px black;
    letter-spacing: 1px;
}

/* Tarjetas de Pelea */
.fight-card { 
    background: rgba(26, 26, 26, 0.8); 
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 35px; 
    border-radius: 16px; 
    text-align: center; 
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-top: 5px solid #D4AF37; 
    margin-bottom: 25px; 
    box-shadow: 0 15px 35px rgba(0,0,0,0.8); 
    position: relative; 
    overflow: hidden; 
    transition: transform 0.3s ease;
}
.fight-card:hover {
    transform: scale(1.01);
    border: 1px solid rgba(212, 175, 55, 0.4);
}

/* Imágenes de Peleadores */
.fighter-img { 
    width: 200px; 
    height: 200px; 
    object-fit: cover; 
    object-position: top; 
    border-radius: 50%; 
    border: 4px solid #D4AF37; 
    box-shadow: 0 0 20px rgba(212,175,55,0.4); 
    background-color: #000000;
    transition: all 0.3s ease;
}
.fighter-img:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(212,175,55,0.8);
}

.fighter-name { font-size: 3rem; font-weight: 400; color: #ffffff; text-transform: uppercase; margin-top: 15px; line-height: 1;}
.vs-text { font-size: 4.5rem; color: #DC2626; font-weight: 400; font-style: italic; text-shadow: 0 0 15px rgba(220,38,38,0.6); margin-top: 50px; }
.weight-class { color: #A1A1AA; font-size: 1.3rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 25px; font-weight: 600; font-family: 'Montserrat', sans-serif;}

/* Cajas personalizadas */
.custom-box { 
    background: rgba(20, 20, 20, 0.8); 
    border-radius: 12px; 
    padding: 30px; 
    border-left: 5px solid #D4AF37; 
    margin-bottom: 20px; 
    box-shadow: 0 8px 20px rgba(0,0,0,0.5); 
}
.share-box {
    background: linear-gradient(135deg, #111 0%, #1a1a1a 100%);
    border-radius: 12px;
    padding: 25px;
    border: 1px solid #333;
    border-top: 4px solid #25D366;
    margin-bottom: 30px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}
.quote-card {
    background-color: #111;
    border-left: 5px solid #DC2626;
    padding: 25px;
    border-radius: 8px;
    height: 100%;
}
.quote-text { font-style: italic; font-size: 1.2rem; color: #ddd; margin-bottom: 15px; }
.quote-author { color: #D4AF37; font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; letter-spacing: 1px; margin: 0; }

/* Tablas y Momios */
.odds-box { background-color: #111; border: 2px solid #333; border-radius: 10px; padding: 20px; text-align: center; }
.odds-fav { color: #10B981; font-weight: bold; font-size: 2.5rem; font-family: 'Bebas Neue', sans-serif;}
.odds-dog { color: #EF4444; font-weight: bold; font-size: 2.5rem; font-family: 'Bebas Neue', sans-serif;}
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.1rem !important;
}

/* 🥊 BANNER ENCUADRE TOP PARA DAZN 🥊 */
.banner-container {
    background-size: cover; 
    background-position: center top; 
    min-height: 520px; 
    display: flex; 
    flex-direction: column; 
    justify-content: flex-end; 
    align-items: center; 
    padding: 40px 20px; 
    border-radius: 16px; 
    margin-bottom: 25px; 
    border: 2px solid #333; 
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
}

/* Animación de vibración para el BOOM */
@keyframes shake {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -2px) rotate(-1deg); }
    20% { transform: translate(-3px, 0px) rotate(1deg); }
    30% { transform: translate(3px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(1deg); }
    50% { transform: translate(-1px, 2px) rotate(-1deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(3px, 1px) rotate(-1deg); }
    80% { transform: translate(-1px, -1px) rotate(1deg); }
    90% { transform: translate(1px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(-1deg); }
}

/* Responsivo para celulares */
@media (max-width: 768px) {
    .fighter-img { width: 110px; height: 110px; }
    .fighter-name { font-size: 1.8rem; }
    .vs-text { font-size: 2.5rem; margin-top: 30px; }
    .weight-class { font-size: 0.9rem; }
    .fight-card { padding: 15px; }
    button[data-baseweb="tab"] { font-size: 1.1rem !important; padding: 10px 5px !important; }
    .banner-container { min-height: 300px; background-position: top center; justify-content: flex-end; padding-bottom: 20px; }
    .banner-h1 { font-size: 3.5rem !important; }
    .banner-h2 { font-size: 1.8rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS ---
PELEAS_FILE = "ufc_peleas_broadcast.csv"
PREDICCONES_FILE = "ufc_preds_broadcast.csv"
LIGAS_FILE = "ufc_ligas_broadcast.csv" 
PASSWORD_ADMIN = "dana2050"

# --- INICIALIZACIÓN ---
if not os.path.exists(PELEAS_FILE):
    cartelera_inicial = [
        {"id": 1, "orden": "MAIN EVENT - 5 ROUNDS", "peso": "UFC Lightweight Championship", "fighter_a": "Ilia Topuria", "fighter_b": "Justin Gaethje", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 2, "orden": "CO-MAIN EVENT - 5 ROUNDS", "peso": "Interim Heavyweight Championship", "fighter_a": "Alex Pereira", "fighter_b": "Ciryl Gane", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 3, "orden": "MAIN CARD - 3 ROUNDS", "peso": "Bantamweight Bout", "fighter_a": "Sean O'Malley", "fighter_b": "Aiemann Zahabi", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 4, "orden": "MAIN CARD - 3 ROUNDS", "peso": "Lightweight Bout", "fighter_a": "Mauricio Ruffy", "fighter_b": "Michael Chandler", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 5, "orden": "PRELIMS - 3 ROUNDS", "peso": "Middleweight Bout", "fighter_a": "Bo Nickal", "fighter_b": "Kyle Daukaus", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 6, "orden": "PRELIMS - 3 ROUNDS", "peso": "Featherweight Bout", "fighter_a": "Diego Lopes", "fighter_b": "Steve Garcia", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 7, "orden": "PRELIMS - 3 ROUNDS", "peso": "Heavyweight Bout", "fighter_a": "Josh Hokit", "fighter_b": "Derrick Lewis", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
    ]
    pd.DataFrame(cartelera_inicial).to_csv(PELEAS_FILE, index=False)

if not os.path.exists(PREDICCONES_FILE): pd.DataFrame(columns=["usuario", "liga", "pelea_id", "pred_winner", "pred_method", "pred_round"]).to_csv(PREDICCONES_FILE, index=False)
if not os.path.exists(LIGAS_FILE): pd.DataFrame(columns=["nombre_liga", "clave_liga", "creador"]).to_csv(LIGAS_FILE, index=False)

df_peleas = pd.read_csv(PELEAS_FILE)
df_predicciones = pd.read_csv(PREDICCONES_FILE)
df_ligas = pd.read_csv(LIGAS_FILE)

OPCIONES_METODO = ["KO/TKO", "Sumisión", "Decisión"]
def get_opciones_round(rondas_max): return [str(i) for i in range(1, rondas_max + 1)] + ["Tarjetas (Decisión)"]

def calcular_tabla_ufc(df_p, df_preds, liga_filtro=None):
    if df_preds.empty: return pd.DataFrame(columns=["Peleador", "Cinturón 🎖️", "Puntos Totales", "Plenos (25pts)", "Aciertos Ganador"])
    if liga_filtro and liga_filtro.strip().upper() != "GLOBAL":
        df_preds = df_preds[df_preds["liga"].str.upper() == liga_filtro.strip().upper()]
        if df_preds.empty: return pd.DataFrame(columns=["Peleador", "Cinturón 🎖️", "Puntos Totales", "Plenos (25pts)", "Aciertos Ganador"])

    puntajes = {user: {"puntos": 0, "plenos": 0, "ganadores": 0} for user in df_preds["usuario"].unique()}
    peleas_jugadas = df_p[df_p["jugado"] == True]
    
    for _, pred in df_preds.iterrows():
        user = pred["usuario"]
        p_id = int(pred["pelea_id"])
        pelea_real_list = peleas_jugadas[peleas_jugadas["id"] == p_id].to_dict(orient="records")
        if not pelea_real_list: continue
        p_real = pelea_real_list[0]
        
        real_w, real_m, real_r = p_real["res_winner"], p_real["res_method"], str(p_real["res_round"])
        pred_w, pred_m, pred_r = pred["pred_winner"], pred["pred_method"], str(pred["pred_round"])
        
        if real_w == pred_w:
            puntos_pelea = 10
            puntajes[user]["ganadores"] += 1
            if real_m == pred_m: puntos_pelea += 5
            if real_r == pred_r: puntos_pelea += 5
            if real_m == pred_m and real_r == pred_r:
                puntos_pelea += 5 
                puntajes[user]["plenos"] += 1
            puntajes[user]["puntos"] += puntos_pelea

    tabla_data = []
    for u, stats in puntajes.items():
        p = stats["puntos"]
        rango = "En el Pesaje ⚖️"
        if p >= 120: rango = "Campeón Indiscutido 🏆"
        elif p >= 80: rango = "Retador #1 👊"
        elif p >= 40: rango = "Prospecto Letal 🔥"
        elif p > 0: rango = "Peleador Preliminar 🥊"
        tabla_data.append([u, rango, p, stats["plenos"], stats["ganadores"]])
        
    df_tabla = pd.DataFrame(tabla_data, columns=["Peleador", "Cinturón 🎖️", "Puntos Totales", "Plenos (25pts)", "Aciertos Ganador"])
    return df_tabla.sort_values(by=["Puntos Totales", "Plenos (25pts)"], ascending=[False, False]).reset_index(drop=True)

def get_fighter_img(name):
    if name in FIGHTER_IMAGES: 
        url = FIGHTER_IMAGES[name]
        if "ufc.com" in url:
            url_encoded = urllib.parse.quote(url)
            return f"https://wsrv.nl/?url={url_encoded}"
        return url
    return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=18181b&color=DC2626&size=200&font-size=0.33&bold=true"

def get_stat(name, stat_key):
    if name in FIGHTER_STATS: return FIGHTER_STATS[name].get(stat_key, "N/A")
    return "N/A"

# --- BANNER PRINCIPAL ANIMADO Y CORREGIDO PARA PC ---
st.markdown(f"""
<div class="banner-container" style="background-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.1) 0%, rgba(5, 5, 5, 0.95) 100%), url('{BANNER_PRINCIPAL}');">
    <h3 class="banner-sub" style="color: #D4AF37; margin:0; text-transform: uppercase; letter-spacing: 4px; font-family: 'Bebas Neue', sans-serif; text-shadow: 2px 2px 10px black; z-index: 2; font-size: 1.8rem;">🎙️ TRANSMISIÓN OFICIAL - COKEMMA DIRECTO</h3>
    <h1 class="banner-h1" style="color: #ffffff; font-size: 7rem; margin-top:10px; margin-bottom:0px; line-height: 1; text-transform: uppercase; letter-spacing: 6px; text-shadow: 4px 4px 15px rgba(220, 38, 38, 0.9); font-family: 'Bebas Neue', sans-serif; z-index: 2;">UFC FREEDOM <span style="color:#DC2626;">250</span></h1>
    <h2 class="banner-h2" style="color: #ffffff; font-size: 3.5rem; margin-top: 10px; font-weight: 400; letter-spacing: 4px; font-family: 'Bebas Neue', sans-serif; text-shadow: 2px 2px 10px black; z-index: 2;">TOPURIA <span style="color:#D4AF37; font-size: 2.5rem; font-family:'Montserrat', sans-serif; font-weight:800;">VS</span> GAETHJE</h2>
</div>
""", unsafe_allow_html=True)

# --- TICKER DE NOTICIAS (ESTILO ESPN) ---
st.markdown("""
<div class="ticker-wrap">
    <marquee scrollamount="12">🚨 EN VIVO: DIRECTO ESPECIAL COKEMMA | 🥊 ÚLTIMA HORA: Topuria promete un KO brutal en el 1er Round... 💰 MOMIOS: Gaethje paga +450 en Las Vegas, ¿habrá sorpresa hoy?... 🏆 Alex Pereira busca hacer historia en su debut en Peso Pesado... 📊 ¡Sella tu cartilla ahora mismo y compite contra el chat en el Ránking Global!</marquee>
</div>
""", unsafe_allow_html=True)

# --- PESTAÑAS NOMBRADAS EXPLÍCITAMENTE ---
t_lobby, t_jugar, t_stats, t_rankings, t_momios, t_admin = st.tabs(["🏠 LOBBY PRINCIPAL", "📝 PREDICCIONES 🥊", "📊 STATS EN VIVO", "🏆 RÁNKINGS", "🎲 MOMIOS & ANÁLISIS", "🔒 PANEL ADMIN"])

# --- PESTAÑA 0: LOBBY (CON ZONA DE COMPARTIR Y INFO) ---
with t_lobby:
    
    # NUEVA ZONA: INFO Y COMPARTIR DIRECTO EN EL LOBBY
    col_info, col_share = st.columns([1, 1])
    
    with col_info:
        st.markdown("""
        <div class="custom-box" style="height: 100%; border-left-color: #D4AF37;">
            <h3 style="color: #D4AF37; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; font-size: 2.2rem; margin-top:0;">ℹ️ INFO DEL EVENTO</h3>
            <p style="margin: 10px 0; font-size: 1.1rem; color: #eee;">📅 <strong>Fecha:</strong> Dom, Jun 07, 2026</p>
            <p style="margin: 10px 0; font-size: 1.1rem; color: #eee;">📍 <strong>Lugar:</strong> Casa Blanca Arena (DC)</p>
            <p style="margin: 10px 0; font-size: 1.1rem; color: #eee;">📺 <strong>Transmisión:</strong> ESPN+, PPV</p>
            <p style="margin: 10px 0; font-size: 1.1rem; color: #eee;">💸 <strong>Momios:</strong> Topuria (-720) vs Gaethje (+450)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_share:
        url_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote('🥊 Únete al directo de Cokemma y compite en el UFC 250: ' + URL_APP)}"
        st.markdown(f"""
        <div class="share-box" style="height: 100%;">
            <h3 style="color: #25D366; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; font-size: 2.2rem; margin-top:0; text-align: center;">🔗 COMPARTIR PÁGINA</h3>
            <p style="text-align: center; color: #aaa; margin-bottom: 15px;">Invita a tus amigos a predecir la cartelera.</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 20px;">
                <a href="{url_whatsapp}" target="_blank" style="text-decoration:none;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="45" style="transition: transform 0.2s;">
                </a>
                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" width="45" style="cursor:pointer; transition: transform 0.2s;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg" width="45" style="background: white; border-radius: 10px; padding: 4px; cursor:pointer; transition: transform 0.2s;">
            </div>
            <div style="background-color: #000; padding: 12px; border-radius: 8px; color: #25D366; border: 1px solid #333; text-align: center; font-weight: bold; font-family: monospace;">
                {URL_APP}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="custom-box">
        <h2 style="margin: 0; color: #D4AF37; font-size: 2.8rem;">¿CÓMO FUNCIONA ESTO? 🌍</h2>
        <p style="font-size: 1.2rem; color: #e4e4e7; line-height: 1.6; margin-top: 10px;">
            Esta es la <strong>Plataforma Oficial de Predicciones de la Comunidad MMA</strong>. Un espacio interactivo donde puedes predecir, competir y vivir la adrenalina de las mejores carteleras junto al stream. Crea tu liga privada con amigos o mídete contra el mismísimo Cokemma en el Ranking Global.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 📰 PORTADA DE NOTICIAS
    st.markdown("<h2 style='color: #ffffff; margin-top:40px; margin-bottom: 25px; font-size: 3rem;'><span style='color:#DC2626;'>📰</span> RUMBO A LA CASA BLANCA</h2>", unsafe_allow_html=True)
    
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        st.markdown(f"""
        <a href="https://www.mma.es/2026/02/25/ufc-white-house-mas-caro/" target="_blank" class="news-card" style="background-image: url('https://www.mma.es/wp-content/uploads/2026/02/UFC-Casa-Blanca.png');">
            <div class="news-overlay">
                <p class="news-title">El evento más caro de la historia de UFC</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col_n2:
        st.markdown(f"""
        <a href="https://www.diariodesantiago.es/deportes/ilia-topuria-peleara-en-la-casa-blanca-contra-justin-gaethje-por-el-titulo-ligero-de-la-ufc-en-una-cartelera-historica/" target="_blank" class="news-card" style="background-image: url('https://www.diariodesantiago.es/wp-content/uploads/2026/03/ilia-topuria-encabeza-la-historica-cartelera-de-ufc-en-la-casa-blanca-vs-justin-gaethje-2026-03-08-ilia-topuria-encabeza-la-historica-cartelera-de-ufc-en-la-casa-blanca-vs-justin-gaethje.jpg');">
            <div class="news-overlay">
                <p class="news-title">Topuria vs Gaethje: Choque de Titanes por el Oro</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
    with col_n3:
        st.markdown(f"""
        <a href="https://www.dazn.com/es-MX/news/mma/la-casa-blanca-ya-huele-a-ufc-arranca-la-construccion-de-la-jaula-del-freedom-250/1tph2u2jt7z7nzu48cs89688b" target="_blank" class="news-card" style="background-image: url('https://cms-images.acc.indazn.com/di/library/DAZN_News/75/aa/ufc-freedom-250-topuria-vs-gaethje_rarhj63rmuf114nwefy7rmf0v.jpg?t=-2004902675&quality=80&w=750&h=422');">
            <div class="news-overlay">
                <p class="news-title">Inicia la construcción del Octágono en la Casa Blanca</p>
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
    
    col_reglas, col_trailer = st.columns([1, 1])
    with col_reglas:
        st.markdown("""
        <div class="custom-box" style="border-left-color: #DC2626; height: 100%;">
            <h2 style="color: #DC2626; font-size: 2.8rem; margin-top:0;">📝 REGLAS DE PUNTUACIÓN</h2>
            <ul style="font-size: 1.2rem; color: #ddd; line-height: 1.8;">
                <li><strong style="color: #10B981;">+10 Puntos:</strong> Acertar al ganador de la pelea.</li>
                <li><strong style="color: #60EFFF;">+5 Puntos:</strong> Acertar el método (KO, Sumisión, Decisión).</li>
                <li><strong style="color: #FBBF24;">+5 Puntos:</strong> Acertar el Round exacto.</li>
            </ul>
            <div style="background-color: #111; padding: 15px; border-radius: 8px; border: 1px solid #D4AF37; text-align: center; margin-top: 20px;">
                <p style="margin:0; font-weight:bold; color: #D4AF37; font-size: 1.2rem;">🏆 BONO PERFECTO (+5 PTS EXTRA)</p>
                <p style="margin:0; font-size: 1rem; color: #aaa;">Si aciertas los 3 resultados exactos te llevas 25 pts por pelea.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_trailer:
        st.markdown("<h2 style='color: #ffffff; font-size: 2.8rem;'>🎬 TRAILER OFICIAL (HYPE)</h2>", unsafe_allow_html=True)
        st.video(TRAILER_OFICIAL)
        
    st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
    
    # HYPE ROOM (DECLARACIONES Y DATOS)
    st.markdown("<h2 style='color: #ffffff; font-size: 3rem;'><span style='color:#D4AF37;'>🎙️</span> HYPE ROOM: LA PREVIA</h2>", unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("""
        <div class="quote-card">
            <p class="quote-text">"Le voy a apagar las luces en el primer asalto. El estilo de Justin está hecho a la medida para que yo brille. No está a mi nivel de boxeo."</p>
            <p class="quote-author">— Ilia Topuria</p>
        </div>
        <br>
        <div class="quote-card" style="border-left-color: #10B981;">
            <p class="quote-text">"He roto a los mejores de esta división. Topuria no sabe lo que es estar en aguas profundas y sentir que te quitan el alma a patadas."</p>
            <p class="quote-author">— Justin Gaethje</p>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown("""
        <div class="custom-box" style="border-left-color: #60EFFF; height: 100%;">
            <h3 style="color: #60EFFF; font-size: 2.2rem; margin-top:0;">🧠 DATOS CURIOSOS DEL EVENTO</h3>
            <ul style="font-size: 1.1rem; color: #ddd; line-height: 1.8;">
                <li><strong>Haciendo Historia:</strong> Freedom 250 es el primer evento numerado en la historia de la UFC celebrado en los terrenos de la Casa Blanca.</li>
                <li><strong>El Rey del Bono:</strong> Justin Gaethje posee la mayor cantidad de bonos por 'Pelea de la Noche' en la historia de los pesos ligeros.</li>
                <li><strong>El Matador Invicto:</strong> Ilia Topuria llega con un récord inmaculado de 17-0, buscando defender su título por segunda vez.</li>
                <li><strong>Chama en Heavyweight:</strong> Alex Pereira busca cimentar su legado debutando oficialmente en el Peso Pesado ante el peligroso Ciryl Gane.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# --- PESTAÑA 1: JUGAR (PREDICCIONES) ---
with t_jugar:
    st.markdown("<h2 style='color: #ffffff; text-align:center; font-size: 3.5rem;'>🔥 PREDICCIONES OFICIALES</h2>", unsafe_allow_html=True)
    
    usuario_input = st.text_input("👤 INGRESA TU APODO PARA EL STREAM:", placeholder="Ej. El Especialista")
    usuario_limpio = usuario_input.strip().title()
    
    opcion_liga = st.selectbox("🤝 ¿DÓNDE QUIERES COMPETIR?", ["🌍 Ranking Global (Recomendado para el Directo)", "➕ Crear Liga Privada", "🔐 Unirse a Liga Existente"])
    liga_limpia, clave_ingresada, clave_creada, liga_nueva = "GLOBAL", "", "", ""
    
    if opcion_liga == "➕ Crear Liga Privada":
        col_nl, col_cl = st.columns(2)
        with col_nl: liga_nueva = st.text_input("Nombre de Liga:")
        with col_cl: clave_creada = st.text_input("Clave Secreta:")
        liga_limpia = liga_nueva.strip().upper()
    elif opcion_liga == "🔐 Unirse a Liga Existente":
        ligas_disp = df_ligas["nombre_liga"].tolist()
        if ligas_disp:
            col_sel, col_pass = st.columns(2)
            with col_sel: liga_seleccionada = st.selectbox("Selecciona Liga:", ligas_disp)
            with col_pass: clave_ingresada = st.text_input("Contraseña:", type="password")
            liga_limpia = liga_seleccionada
        else: st.error("No hay ligas privadas aún.")

    if usuario_limpio:
        st.markdown("---")
        
        # --- BOTÓN DE ALARDEAR (WHATSAPP) ---
        pred_main = df_predicciones[(df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == 1)]
        if not pred_main.empty:
            w_main = pred_main.iloc[0]["pred_winner"]
            m_main = pred_main.iloc[0]["pred_method"]
            r_main = pred_main.iloc[0]["pred_round"]
            
            texto_wa = f"🥊 ¡Sellé mi cartilla para el UFC Freedom 250! Mi pronóstico estelar: {w_main} gana por {m_main} (Round {r_main}). 🔥 ¿Crees que sabes más que yo? Entra al directo de Cokemma y supérame aquí: {URL_APP}"
            link_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_wa)}"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10B981 0%, #047857 100%); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 30px; border: 2px solid #34D399; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);">
                <h3 style="color: white; margin-top: 0; font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; letter-spacing: 1px;">✅ ¡CARTILLA GUARDADA CON ÉXITO!</h3>
                <p style="color: #ecfdf5; font-size: 1.2rem; margin-bottom: 20px; font-family: 'Montserrat', sans-serif;">Tus predicciones ya están en el sistema. ¡Desafía a tus amigos por WhatsApp y que arda el chat!</p>
                <a href="{link_wa}" target="_blank" style="text-decoration: none; display: inline-block; background-color: #ffffff; color: #047857; padding: 15px 30px; border-radius: 8px; font-weight: 800; font-family: 'Montserrat', sans-serif; font-size: 1.1rem; text-transform: uppercase; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: transform 0.2s;">
                    📲 ALARDEAR MI PRONÓSTICO EN WHATSAPP
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("form_preds_ufc"):
            for _, row in df_peleas.iterrows():
                p_id_f = int(row["id"])
                pred_existente = df_predicciones[(df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == p_id_f)]
                def_w, def_m, def_r = row["fighter_a"], "Decisión", "Tarjetas (Decisión)"
                if not pred_existente.empty:
                    def_w, def_m, def_r = pred_existente.iloc[0]["pred_winner"], pred_existente.iloc[0]["pred_method"], str(pred_existente.iloc[0]["pred_round"])

                ops_w = [row["fighter_a"], row["fighter_b"]]
                idx_w = ops_w.index(def_w) if def_w in ops_w else 0
                idx_m = OPCIONES_METODO.index(def_m) if def_m in OPCIONES_METODO else 2
                ops_r = get_opciones_round(row["rondas_max"])
                idx_r = ops_r.index(def_r) if def_r in ops_r else len(ops_r)-1
                
                img_a = get_fighter_img(row["fighter_a"])
                img_b = get_fighter_img(row["fighter_b"])

                st.markdown(f"""
                <div class='fight-card'>
                    <div class='weight-class'>{row['orden']} | {row['peso']}</div>
                    <div style='display:flex; justify-content:space-around; align-items:center;'>
                        <div style='width:35%;'>
                            <img src='{img_a}' class='fighter-img'>
                            <div class='fighter-name'>{row['fighter_a']}</div>
                        </div>
                        <div style='width:30%;' class='vs-text'>VS</div>
                        <div style='width:35%;'>
                            <img src='{img_b}' class='fighter-img'>
                            <div class='fighter-name'>{row['fighter_b']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                esta_bloqueado = bool(row["jugado"])
                if esta_bloqueado: st.markdown("<p style='text-align:center; color:#DC2626; font-weight:bold; font-size:1.2rem;'>🛑 PELEA FINALIZADA</p>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1: st.selectbox("GANADOR", ops_w, index=idx_w, key=f"w_{p_id_f}", disabled=esta_bloqueado)
                with col2: st.selectbox("MÉTODO", OPCIONES_METODO, index=idx_m, key=f"m_{p_id_f}", disabled=esta_bloqueado)
                with col3: st.selectbox("ROUND", ops_r, index=idx_r, key=f"r_{p_id_f}", disabled=esta_bloqueado)
                st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
                
            if st.form_submit_button("🔒 CONFIRMAR MIS PREDICCIONES"):
                acceso = True
                if opcion_liga == "➕ Crear Liga Privada":
                    if not liga_nueva or not clave_creada: st.error("Faltan datos de la liga."); acceso = False
                    else:
                        df_ligas = pd.concat([df_ligas, pd.DataFrame([{"nombre_liga": liga_limpia, "clave_liga": clave_creada, "creador": usuario_limpio}])], ignore_index=True)
                        df_ligas.to_csv(LIGAS_FILE, index=False)
                elif opcion_liga == "🔐 Unirse a Liga Existente" and ligas_disp:
                    if str(clave_ingresada) != str(df_ligas[df_ligas["nombre_liga"] == liga_limpia]["clave_liga"].values[0]):
                        st.error("Contraseña incorrecta."); acceso = False

                if acceso:
                    for _, row in df_peleas.iterrows():
                        p_id_s = int(row["id"])
                        if row["jugado"]: continue
                        df_predicciones = df_predicciones[~((df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == p_id_s))]
                        df_predicciones = pd.concat([df_predicciones, pd.DataFrame([{"usuario": usuario_limpio, "liga": liga_limpia, "pelea_id": p_id_s, "pred_winner": st.session_state[f"w_{p_id_s}"], "pred_method": st.session_state[f"m_{p_id_s}"], "pred_round": st.session_state[f"r_{p_id_s}"]}])], ignore_index=True)
                    df_predicciones.to_csv(PREDICCONES_FILE, index=False)
                    
                    st.toast('¡Cartilla asegurada en la base de datos!', icon='🏆')
                    st.markdown("""
                    <div style="text-align:center; animation: shake 0.5s;">
                        <h1 style="color: #DC2626; font-size: 6rem; font-family: 'Bebas Neue', sans-serif;">¡BOOM! 💥</h1>
                        <p style="font-size: 1.8rem; color:white; font-family:'Bebas Neue', sans-serif; letter-spacing:2px;">¡CARTILLA OFICIAL EN LA JAULA!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.snow()
                    time.sleep(2)
                    st.rerun()

# --- PESTAÑA 2: STATS EN VIVO (BARÓMETRO DEL DIRECTO) ---
with t_stats:
    st.markdown("<h2 class='stat-title' style='font-size: 3.5rem;'>📊 EL TERMÓMETRO DEL DIRECTO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #ddd;'>Así se están inclinando las predicciones de todos los jugadores en vivo. ¡Perfecto para debatir en el stream!</p>", unsafe_allow_html=True)
    
    if st.button("🔄 ACTUALIZAR GRÁFICOS AHORA"):
        st.rerun()
        
    st.markdown("---")
    
    if df_predicciones.empty:
        st.info("Aún no hay suficientes predicciones registradas para calcular las probabilidades.")
    else:
        for _, row in df_peleas.iterrows():
            f_a = row["fighter_a"]
            f_b = row["fighter_b"]
            preds_pelea = df_predicciones[df_predicciones["pelea_id"] == row["id"]]
            
            if not preds_pelea.empty:
                total_votos = len(preds_pelea)
                votos_a = len(preds_pelea[preds_pelea["pred_winner"] == f_a])
                pct_a = int((votos_a / total_votos) * 100) if total_votos > 0 else 0
                pct_b = 100 - pct_a if total_votos > 0 else 0
                
                st.markdown(f"""
                <div style="background-color: #111; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #D4AF37; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                    <p style="color: #A1A1AA; font-size: 1.1rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; font-family: 'Bebas Neue', sans-serif;">{row['peso']}</p>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="font-size: 1.8rem; font-weight: bold; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px;">{f_a} <span style="color:#DC2626;">({pct_a}%)</span></span>
                        <span style="font-size: 1.8rem; font-weight: bold; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px;"><span style="color:#D4AF37;">({pct_b}%)</span> {f_b}</span>
                    </div>
                    <div style="width: 100%; background-color: #333; height: 30px; border-radius: 15px; display: flex; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);">
                        <div style="width: {pct_a}%; background-color: #DC2626; transition: width 0.5s;"></div>
                        <div style="width: {pct_b}%; background-color: #D4AF37; transition: width 0.5s;"></div>
                    </div>
                    <p style="text-align: center; color: #777; font-size: 1rem; margin-top: 10px; margin-bottom: 0;">Basado en {total_votos} predicciones de la comunidad</p>
                </div>
                """, unsafe_allow_html=True)

# --- PESTAÑA 3: RÁNKINGS ---
with t_rankings:
    st.markdown("<h2 style='color: #D4AF37; font-size: 3.5rem;'>🏅 TABLA DE POSICIONES OFICIAL</h2>", unsafe_allow_html=True)
    opciones_ligas = ["GLOBAL"]
    if not df_ligas.empty: opciones_ligas.extend(sorted(df_ligas["nombre_liga"].unique().tolist()))
    liga_busqueda = st.selectbox("🔍 Filtrar por Gimnasio (Liga):", opciones_ligas).strip().upper()
    
    df_ranking = calcular_tabla_ufc(df_peleas, df_predicciones, liga_busqueda)
    if not df_ranking.empty: 
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else: 
        st.info("Aún no hay peleadores registrados en esta categoría.")

# --- PESTAÑA 4: MOMIOS Y TALE OF THE TAPE ---
with t_momios:
    st.markdown("<h2 style='color: #ffffff; font-size: 3.5rem;'><span style='color:#10B981;'>🎲</span> MOMIOS Y TALE OF THE TAPE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #ddd;'>Estudia los números fríos antes de lanzar tus predicciones.</p>", unsafe_allow_html=True)
    
    lista_combates = [f"{row['fighter_a']} vs {row['fighter_b']}" for _, row in df_peleas.iterrows()]
    pelea_seleccionada = st.selectbox("🔍 Combate a analizar en Las Vegas:", lista_combates)
    
    if pelea_seleccionada:
        f_a = pelea_seleccionada.split(" vs ")[0]
        f_b = pelea_seleccionada.split(" vs ")[1]
        
        col_img1, col_vs, col_img2 = st.columns([2, 1, 2])
        with col_img1: st.markdown(f"<div style='text-align:center;'><img src='{get_fighter_img(f_a)}' class='fighter-img' style='width:160px; height:160px; border-color:#333;'><h3 style='color:white; margin-top:10px; font-size: 2.5rem;'>{f_a}</h3></div>", unsafe_allow_html=True)
        with col_vs: st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top: 40px; font-size: 4rem;'>VS</h1>", unsafe_allow_html=True)
        with col_img2: st.markdown(f"<div style='text-align:center;'><img src='{get_fighter_img(f_b)}' class='fighter-img' style='width:160px; height:160px; border-color:#333;'><h3 style='color:white; margin-top:10px; font-size: 2.5rem;'>{f_b}</h3></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <table style="width:100%; text-align:center; background: rgba(20,20,20,0.8); border-radius:12px; overflow:hidden; border: 1px solid #333;">
            <tr style="background-color:#111; color:#D4AF37; font-family:'Bebas Neue', sans-serif;">
                <td style="padding:15px; width:33%; font-size:2rem;">{get_stat(f_a, 'record')}</td>
                <td style="padding:15px; width:33%; font-size:1.6rem; letter-spacing:1px;">RÉCORD</td>
                <td style="padding:15px; width:33%; font-size:2rem;">{get_stat(f_b, 'record')}</td>
            </tr>
            <tr>
                <td style="padding:15px; border-bottom:1px solid #222; font-weight:600; font-size:1.2rem;">{get_stat(f_a, 'altura')}</td>
                <td style="padding:15px; border-bottom:1px solid #222; color:#A1A1AA; font-family:'Bebas Neue', sans-serif; font-size:1.6rem;">ESTATURA</td>
                <td style="padding:15px; border-bottom:1px solid #222; font-weight:600; font-size:1.2rem;">{get_stat(f_b, 'altura')}</td>
            </tr>
            <tr>
                <td style="padding:15px; font-weight:600; font-size:1.2rem;">{get_stat(f_a, 'alcance')}</td>
                <td style="padding:15px; color:#A1A1AA; font-family:'Bebas Neue', sans-serif; font-size:1.6rem;">ALCANCE</td>
                <td style="padding:15px; font-weight:600; font-size:1.2rem;">{get_stat(f_b, 'alcance')}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        odds_a = get_stat(f_a, 'odds')
        odds_b = get_stat(f_b, 'odds')
        color_a = "odds-fav" if "-" in odds_a else "odds-dog"
        color_b = "odds-fav" if "-" in odds_b else "odds-dog"
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_odds1, col_odds2 = st.columns(2)
        with col_odds1:
            st.markdown(f"<div class='odds-box'><p style='color:#A1A1AA; margin:0; font-weight:600; font-size:1.2rem; text-transform:uppercase;'>{f_a}</p><p class='{color_a}' style='margin:0; font-size:3rem;'>{odds_a}</p></div>", unsafe_allow_html=True)
        with col_odds2:
            st.markdown(f"<div class='odds-box'><p style='color:#A1A1AA; margin:0; font-weight:600; font-size:1.2rem; text-transform:uppercase;'>{f_b}</p><p class='{color_b}' style='margin:0; font-size:3rem;'>{odds_b}</p></div>", unsafe_allow_html=True)

# --- PESTAÑA 5: ADMIN ---
with t_admin:
    st.markdown("<h2 style='color: #DC2626; font-size: 3.5rem;'>🔒 MESA DE CONTROL (OFFICIALS ONLY)</h2>", unsafe_allow_html=True)
    if st.text_input("Ingresa la credencial de acceso:", type="password") == PASSWORD_ADMIN:
        with st.form("admin_form"):
            for idx, row in df_peleas.iterrows():
                st.write(f"**{row['fighter_a']} vs {row['fighter_b']}**")
                ops_w, ops_r = [row['fighter_a'], row['fighter_b'], "Empate/No Contest"], get_opciones_round(row["rondas_max"])
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1: w_r = st.selectbox("Ganador", ops_w, index=ops_w.index(row['res_winner']) if row['res_winner'] in ops_w else 0, key=f"rw_{row['id']}")
                with c2: m_r = st.selectbox("Método", OPCIONES_METODO, index=OPCIONES_METODO.index(row['res_method']) if row['res_method'] in OPCIONES_METODO else 0, key=f"rm_{row['id']}")
                with c3: r_r = st.selectbox("Round", ops_r, index=ops_r.index(str(row['res_round'])) if str(row['res_round']) in ops_r else 0, key=f"rr_{row['id']}")
                with c4: jugado = st.checkbox("¿Oficial?", value=row["jugado"], key=f"rj_{row['id']}")
                st.markdown("---")
            if st.form_submit_button("CERRAR RESULTADOS DE LA NOCHE"):
                for idx, row in df_peleas.iterrows():
                    df_peleas.at[idx, "res_winner"], df_peleas.at[idx, "res_method"], df_peleas.at[idx, "res_round"], df_peleas.at[idx, "jugado"] = st.session_state[f"rw_{row['id']}"], st.session_state[f"rm_{row['id']}"], st.session_state[f"rr_{row['id']}"], bool(st.session_state[f"rj_{row['id']}"])
                df_peleas.to_csv(PELEAS_FILE, index=False)
                st.success('Resultados Guardados Oficialmente.')
                time.sleep(1)
                st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div style="text-align: center; margin-top: 60px; padding: 25px; border-top: 1px solid #333;">
    <p style="color: #666; font-size: 1.1rem; font-weight:600;">UFC Freedom 250 Predictions © 2026 | Desarrollado por <a href="https://tiktok.com/@martincampos.mma" target="_blank" style="color:#D4AF37; text-decoration:none; font-family:'Bebas Neue', sans-serif; font-size:1.8rem; letter-spacing:1px;">@martincampos.mma</a></p>
</div>
""", unsafe_allow_html=True)
