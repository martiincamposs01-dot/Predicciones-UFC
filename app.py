import streamlit as st
import pandas as pd
import os
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="UFC Freedom 250", page_icon="🥊", layout="wide")

# --- 📸 DICCIONARIO DE IMÁGENES Y DATOS OFICIALES ---
TRAILER_OFICIAL = "https://youtu.be/iNJIs5bXoAE?si=Lbes9bQDegv6vocd"

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

# Base de datos de Stats ACTUALIZADAS (Récords, Medidas y Momios Reales)
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
    "Bo Nickal": {"record": "8-1-0", "altura": "1.85 m", "alcance": "1.93 m", "odds": "-330"},
    "Kyle Daukaus": {"record": "17-4-0 (1 NC)", "altura": "1.88 m", "alcance": "1.93 m", "odds": "+240"},
    "Diego Lopes": {"record": "27-8-0", "altura": "1.80 m", "alcance": "1.84 m", "odds": "-192"},
    "Steve Garcia": {"record": "19-5-0", "altura": "1.83 m", "alcance": "1.91 m", "odds": "+148"}
}

# --- ESTILOS CSS (CON OPTIMIZACIÓN EXTREMA PARA CELULARES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;700;900&family=Roboto:wght@400;700&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; font-family: 'Roboto', sans-serif; }
    h1, h2, h3, .fighter-name, .vs-text, .weight-class, .stat-title { font-family: 'Oswald', sans-serif !important; }
    
    button[data-baseweb="tab"] {
        font-size: 1.3rem !important; font-family: 'Oswald', sans-serif !important; text-transform: uppercase;
        padding: 12px 20px !important; background-color: #18181b; border: 1px solid #333; border-bottom: none;
        border-radius: 10px 10px 0 0; color: #71717A !important; letter-spacing: 1px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #DC2626 0%, #7F1D1D 100%) !important; color: white !important; border: 1px solid #EF4444; border-bottom: none;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: #ffffff; font-weight: 900; font-family: 'Oswald', sans-serif; 
        font-size: 1.2rem; border: none; border-radius: 8px; padding: 15px 30px; text-transform: uppercase; letter-spacing: 2px; width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(220, 38, 38, 0.6); border: 1px solid #ff4d4d; }
    
    .fight-card { 
        background: linear-gradient(180deg, #1f1f1f 0%, #0a0a0a 100%); padding: 30px; border-radius: 15px; text-align: center; 
        border-top: 5px solid #D4AF37; margin-bottom: 20px; box-shadow: 0 15px 30px rgba(0,0,0,0.8); position: relative; overflow: hidden; border-bottom: 1px solid #333;
    }
    
    .fighter-img { width: 170px; height: 170px; object-fit: cover; object-position: top; border-radius: 50%; border: 4px solid #D4AF37; box-shadow: 0 0 25px rgba(212,175,55,0.5); background-color: #000000; }
    .fighter-name { font-size: 2.2rem; font-weight: 900; color: #ffffff; text-transform: uppercase; margin-top: 15px; line-height: 1.1;}
    .vs-text { font-size: 3.5rem; color: #D4AF37; font-weight: 900; font-style: italic; text-shadow: 0 0 20px rgba(212,175,55,0.5); margin-top: 50px; }
    .weight-class { color: #DC2626; font-size: 1.1rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 20px; font-weight: bold; }
    
    .stSelectbox > div > div > div { background-color: #27272a; color: white; border-radius: 6px; font-weight: bold; font-family: 'Roboto', sans-serif;}
    .lobby-box { background-color: #18181b; border-radius: 12px; padding: 25px; text-align: center; border-bottom: 3px solid #DC2626; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
    .quote-box { background-color: #111; border-left: 4px solid #D4AF37; padding: 15px; font-style: italic; color: #ddd; margin-bottom: 10px; border-radius: 0 8px 8px 0; }
    
    .odds-box { background-color: #111; border: 2px solid #333; border-radius: 10px; padding: 15px; text-align: center; }
    .odds-fav { color: #10B981; font-weight: bold; font-size: 1.8rem; font-family: 'Oswald', sans-serif;}
    .odds-dog { color: #EF4444; font-weight: bold; font-size: 1.8rem; font-family: 'Oswald', sans-serif;}

    /* REGLAS EXCLUSIVAS PARA CELULARES (RESPONSIVE) */
    @media (max-width: 768px) {
        .fighter-img { width: 100px; height: 100px; border-width: 2px; }
        .fighter-name { font-size: 1.2rem; margin-top: 5px; }
        .vs-text { font-size: 2rem; margin-top: 25px; }
        .weight-class { font-size: 0.8rem; letter-spacing: 1px; }
        .fight-card { padding: 15px; }
        .banner-h1 { font-size: 2.5rem !important; letter-spacing: 2px !important; }
        .banner-h2 { font-size: 1.5rem !important; }
        button[data-baseweb="tab"] { font-size: 0.9rem !important; padding: 10px 5px !important; }
        .lobby-box h1 { font-size: 2rem !important; }
        .lobby-box h3 { font-size: 1.2rem !important; }
        table { font-size: 0.75rem !important; }
        td { padding: 5px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS (NUEVOS NOMBRES PARA REINICIAR LAS PRUEBAS) ---
PELEAS_FILE = "ufc_peleas_lanzamiento.csv"
PREDICCONES_FILE = "ufc_preds_lanzamiento.csv"
LIGAS_FILE = "ufc_ligas_lanzamiento.csv" 
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
        pelea_real = list(peleas_jugadas[peleas_jugadas["id"] == p_id].to_dict(orient="index").values())
        if not pelea_real: continue
        p_real = pelea_real[0]
        
        real_w, real_m, real_r = p_real["res_winner"], p_real["res_method"], str(p_real["res_round"])
        pred_w, pred_m, pred_r = pred["pred_winner"], pred["pred_method"], str(pred["pred_round"])
        
        if real_w == pred_w:
            puntos_pelea = 10
            puntajes[user]["ganadores"] += 1
            if real_m == pred_m: puntos_pelea += 5
            if real_r == pred_r: puntos_pelea += 5
            if real_m == pred_m and real_r == pred_r:
                puntos_pelea += 5 # Bono Pleno
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
    if name in FIGHTER_IMAGES: return FIGHTER_IMAGES[name]
    return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=18181b&color=DC2626&size=200&font-size=0.33&bold=true"

def get_stat(name, stat_key):
    if name in FIGHTER_STATS: return FIGHTER_STATS[name].get(stat_key, "N/A")
    return "N/A"

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h1 style="font-size: 4rem; margin: 0; filter: drop-shadow(0px 0px 10px rgba(220,38,38,0.8));">🥊</h1>
        <h2 style="color: #DC2626; margin-top: 10px; text-transform: uppercase; letter-spacing: 2px;">Fight Week</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: white;'>🔗 Invita a tus amigos</h3>", unsafe_allow_html=True)
    url_de_tu_app = "https://predicciones-ufc-87c5opnpg9pmnfjm9qqrkr.streamlit.app/#momios-de-las-vegas"
    st.code(url_de_tu_app, language="text")
    mensaje_whatsapp = f"🥊 ¡Únete a nuestra liga de pronósticos para UFC FREEDOM 250! Deja tus predicciones aquí: {url_de_tu_app}"
    url_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensaje_whatsapp)}"
    st.markdown(f"""<a href="{url_whatsapp}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            📲 Enviar por WhatsApp
        </div></a>""", unsafe_allow_html=True)

# --- BANNER PRINCIPAL ---
st.markdown("""
<div style="background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.8)), url('https://aulanews.uao.es/wp-content/uploads/2020/05/ufc-octagono.jpg'); background-size: cover; background-position: center; padding: 60px 20px; border-radius: 15px; text-align: center; margin-bottom: 35px; border: 2px solid #DC2626; box-shadow: 0 0 40px rgba(220, 38, 38, 0.4);">
    <h1 class="banner-h1" style="color: #ffffff; font-size: 4.5rem; margin:0; text-transform: uppercase; letter-spacing: 6px; text-shadow: 3px 3px 15px #DC2626; font-family: 'Oswald', sans-serif;">UFC FREEDOM 250</h1>
    <h2 class="banner-h2" style="color: #D4AF37; font-size: 2.5rem; margin-top: 5px; font-weight: 900; letter-spacing: 4px; font-family: 'Oswald', sans-serif;">TOPURIA <span style="color:white; font-size: 1.5rem;">VS</span> GAETHJE</h2>
</div>
""", unsafe_allow_html=True)

# --- PESTAÑAS ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Lobby", "📊 Ránkings", "📝 Jugar", "🎲 Momios", "📺 Stats", "🎙️ Bruce"])

# --- PESTAÑA 0: LOBBY ---
with tab0:
    st.markdown("""
<div style="background: linear-gradient(135deg, #DC2626 0%, #7F1D1D 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #ff4d4d; box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4);">
<h3 style="margin-top: 0; color: white; display: flex; align-items: center; font-family: 'Oswald', sans-serif;">📲 ¡Lleva el Octágono en tu Bolsillo!</h3>
<p style="font-weight: 700; font-size: 1.05rem; margin-bottom: 8px;">Instala esta web como una App nativa para no perderte nada:</p>
<div style="background-color: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #D4AF37;">
<span style="font-size: 0.9rem; color: #fbbf24; font-weight: bold;">⚠️ ¿Atrapado en el navegador de TikTok o Instagram?</span><br>
<span style="font-size: 0.85rem; color: #ddd;">Las redes sociales bloquean la instalación de apps. Para solucionarlo:</span><br>
<ol style="font-size: 0.85rem; color: #ddd; margin-top: 5px; margin-bottom: 0; padding-left: 20px;">
<li>Toca la barra superior blanca que dice <em>"Estás en..."</em> o busca los 3 puntitos.</li>
<li>Copia el enlace de la página.</li>
<li>Abre <strong>Safari</strong> (iPhone) o <strong>Chrome</strong> (Android) y pega el enlace ahí.</li>
</ol>
</div>
<ul style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0;">
<li><strong>🍏 Una vez en Safari:</strong> Toca 'Compartir' (📤) abajo ➔ <strong>➕ Agregar a inicio</strong>.</li>
<li><strong>🤖 Una vez en Chrome:</strong> Toca los 3 puntos (⋮) arriba ➔ <strong>📱 Agregar a la pantalla principal</strong>.</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color: #D4AF37; font-family: \"Oswald\", sans-serif; margin-bottom: 20px; font-size: 2.5rem;'>📜 MANUAL DEL ORÁCULO: ¿CÓMO SE JUEGA?</h2>", unsafe_allow_html=True)
    
    col_inst1, col_inst2, col_inst3 = st.columns(3)
    with col_inst1:
        st.markdown("<div class='
