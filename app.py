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

# Base de datos de Stats Reales para el Tale of the Tape
FIGHTER_STATS = {
    "Ilia Topuria": {"record": "15-0-0", "altura": "1.70 m", "alcance": "1.75 m", "odds": "-150"},
    "Justin Gaethje": {"record": "25-5-0", "altura": "1.80 m", "alcance": "1.80 m", "odds": "+125"},
    "Alex Pereira": {"record": "10-2-0", "altura": "1.93 m", "alcance": "2.00 m", "odds": "-130"},
    "Ciryl Gane": {"record": "12-2-0", "altura": "1.93 m", "alcance": "2.06 m", "odds": "+110"},
    "Sean O'Malley": {"record": "18-1-0", "altura": "1.80 m", "alcance": "1.83 m", "odds": "-200"},
    "Aiemann Zahabi": {"record": "11-2-0", "altura": "1.73 m", "alcance": "1.73 m", "odds": "+170"},
    "Josh Hokit": {"record": "8-1-0", "altura": "1.85 m", "alcance": "1.88 m", "odds": "-110"},
    "Derrick Lewis": {"record": "27-12-0", "altura": "1.91 m", "alcance": "2.01 m", "odds": "-110"},
    "Mauricio Ruffy": {"record": "10-1-0", "altura": "1.80 m", "alcance": "1.83 m", "odds": "-140"},
    "Michael Chandler": {"record": "23-8-0", "altura": "1.73 m", "alcance": "1.80 m", "odds": "+120"},
    "Bo Nickal": {"record": "6-0-0", "altura": "1.85 m", "alcance": "1.93 m", "odds": "-450"},
    "Kyle Daukaus": {"record": "13-4-0", "altura": "1.91 m", "alcance": "1.93 m", "odds": "+320"},
    "Diego Lopes": {"record": "24-6-0", "altura": "1.80 m", "alcance": "1.84 m", "odds": "-160"},
    "Steve Garcia": {"record": "16-5-0", "altura": "1.83 m", "alcance": "1.91 m", "odds": "+135"}
}

# --- ESTILOS CSS ---
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
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS ---
PELEAS_FILE = "ufc_peleas_final.csv"
PREDICCONES_FILE = "ufc_preds_final.csv"
LIGAS_FILE = "ufc_ligas_final.csv" 
PASSWORD_ADMIN = "dana2050"

# --- INICIALIZACIÓN ---
if not os.path.exists(PELEAS_FILE):
    cartelera_inicial = [
        {"id": 1, "orden": "MAIN EVENT - 5 ROUNDS", "peso": "UFC Lightweight Championship", "fighter_a": "Ilia Topuria", "fighter_b": "Justin Gaethje", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 2, "orden": "CO-MAIN EVENT - 5 ROUNDS", "peso": "Interim Heavyweight Championship", "fighter_a": "Alex Pereira", "fighter_b": "Ciryl Gane", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 3, "orden": "MAIN CARD - 3 ROUNDS", "peso": "Bantamweight Bout", "fighter_a": "Sean O'Malley", "fighter_b": "Aiemann Zahabi", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 4, "orden": "MAIN CARD - 3 ROUNDS", "peso": "Heavyweight Bout", "fighter_a": "Josh Hokit", "fighter_b": "Derrick Lewis", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 5, "orden": "MAIN CARD - 3 ROUNDS", "peso": "Lightweight Bout", "fighter_a": "Mauricio Ruffy", "fighter_b": "Michael Chandler", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 6, "orden": "PRELIMS - 3 ROUNDS", "peso": "Middleweight Bout", "fighter_a": "Bo Nickal", "fighter_b": "Kyle Daukaus", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 7, "orden": "PRELIMS - 3 ROUNDS", "peso": "Featherweight Bout", "fighter_a": "Diego Lopes", "fighter_b": "Steve Garcia", "rondas_max": 3, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
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
    url_de_tu_app = "https://predicciones-ufc-87c5opnpg9pmnfjm9qqrkr.streamlit.app"
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
    <h1 style="color: #ffffff; font-size: 4.5rem; margin:0; text-transform: uppercase; letter-spacing: 6px; text-shadow: 3px 3px 15px #DC2626; font-family: 'Oswald', sans-serif;">UFC FREEDOM 250</h1>
    <h2 style="color: #D4AF37; font-size: 2.5rem; margin-top: 5px; font-weight: 900; letter-spacing: 4px; font-family: 'Oswald', sans-serif;">TOPURIA <span style="color:white; font-size: 1.5rem;">VS</span> GAETHJE</h2>
</div>
""", unsafe_allow_html=True)

# --- PESTAÑAS (AHORA SON 6) ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Lobby", "📊 Ránkings", "📝 Jugar", "🎲 Momios", "📺 Stats", "🎙️ Bruce"])

# --- PESTAÑA 0: LOBBY ---
with tab0:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #DC2626 0%, #7F1D1D 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #ff4d4d; box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4);">
        <h3 style="margin-top: 0; color: white; display: flex; align-items: center; font-family: 'Oswald', sans-serif;">📲 ¡Lleva el Octágono en tu Bolsillo!</h3>
        <p style="font-weight: 700; font-size: 1.05rem; margin-bottom: 12px;">Instala esta web como una App nativa para no perderte ningún resultado ni estadística:</p>
        <ul style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0;">
            <li><strong>🍏 iPhone (Safari):</strong> Toca 'Compartir' (📤) abajo ➔ <strong>➕ Agregar a inicio</strong>.</li>
            <li><strong>🤖 Android (Chrome):</strong> Toca los 3 puntos (⋮) arriba ➔ <strong>📱 Agregar a la pantalla principal</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color: #D4AF37; font-family: \"Oswald\", sans-serif; margin-bottom: 20px; font-size: 2.5rem;'>📜 MANUAL DEL ORÁCULO: ¿CÓMO SE JUEGA?</h2>", unsafe_allow_html=True)
    
    col_inst1, col_inst2, col_inst3 = st.columns(3)
    with col_inst1:
        st.markdown("<div class='lobby-box'><h1 style='font-size: 3rem; margin: 0;'>1️⃣</h1><h3 style='color: white; font-family: \"Oswald\", sans-serif;'>Elige tu Esquina</h3><p style='color: #A1A1AA;'>Ve a la pestaña <strong>JUGAR</strong>. Crea tu propio Gimnasio (Liga Privada) o únete al Ranking Global.</p></div>", unsafe_allow_html=True)
    with col_inst2:
        st.markdown("<div class='lobby-box'><h1 style='font-size: 3rem; margin: 0;'>2️⃣</h1><h3 style='color: white; font-family: \"Oswald\", sans-serif;'>Sella tu Cartilla</h3><p style='color: #A1A1AA;'>Predice 3 cosas por pelea: <strong>Ganador</strong>, <strong>Método</strong> y el <strong>Round</strong> exacto.</p></div>", unsafe_allow_html=True)
    with col_inst3:
        st.markdown("<div class='lobby-box'><h1 style='font-size: 3rem; margin: 0;'>3️⃣</h1><h3 style='color: white; font-family: \"Oswald\", sans-serif;'>Cobra tus Puntos</h3><p style='color: #A1A1AA;'>Revisa la pestaña <strong>RÁNKINGS</strong> para ver tu posición. Demuestra quién sabe más de MMA.</p></div>", unsafe_allow_html=True)
        
    st.markdown("""
    <div style="background-color: #111; padding: 20px; border-radius: 12px; margin-top: 25px; margin-bottom: 30px; border: 2px dashed #D4AF37; text-align: center;">
        <h3 style="color: #D4AF37; margin-top: 0; font-family: 'Oswald', sans-serif; text-transform: uppercase;">💰 Bolsa de Puntos (Cómo Ganar)</h3>
        <p style="color: #ddd; font-size: 1.1rem; margin-bottom: 5px;"><strong>+10 pts:</strong> Acertar al ganador.</p>
        <p style="color: #ddd; font-size: 1.1rem; margin-bottom: 5px;"><strong>+5 pts extra:</strong> Acertar el Método.</p>
        <p style="color: #ddd; font-size: 1.1rem; margin-bottom: 5px;"><strong>+5 pts extra:</strong> Acertar el Round.</p>
        <p style="color: #DC2626; font-size: 1.2rem; font-weight: bold; margin-top: 10px;">🏆 BONO PERFECTO (+5 pts): ¡Acierta TODO y llévate 25 PUNTOS POR PELEA!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_vid, col_info = st.columns([2, 1])
    with col_vid:
        st.markdown("<h3 style='color: #D4AF37; margin-top: 0;'>🎬 Promo Oficial de la Velada</h3>", unsafe_allow_html=True)
        st.video(TRAILER_OFICIAL)
    with col_info:
        st.markdown("""
        <div style="background-color: #18181b; padding: 25px; border-radius: 12px; border-left: 5px solid #DC2626; height: 100%;">
            <h2 style="color: white; margin-top: 0;">🔥 Hype Room</h2>
            <div class='quote-box'>
                "Voy a noquear a Justin Gaethje. No tiene ni la velocidad ni el IQ de pelea para aguantarme."<br><strong>— Ilia Topuria</strong>
            </div>
            <div class='quote-box' style='border-left-color: #DC2626;'>
                "Me encanta cuando hablan mucho. Cae más duro cuando le apague las luces en el octágono."<br><strong>— Justin Gaethje</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- PESTAÑA 1: RÁNKING ---
with tab1:
    opciones_ligas = ["GLOBAL"]
    if not df_ligas.empty: opciones_ligas.extend(sorted(df_ligas["nombre_liga"].unique().tolist()))
    liga_busqueda = st.selectbox("🔍 Selecciona tu Liga:", opciones_ligas).strip().upper()
    df_ranking = calcular_tabla_ufc(df_peleas, df_predicciones, liga_busqueda)
    if not df_ranking.empty: st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else: st.warning("No hay predicciones registradas aún en esta liga.")

# --- PESTAÑA 2: CARTELERA ---
with tab2:
    usuario_input = st.text_input("👤 Nombre del Peleador (Tu Apodo):", placeholder="Ej. The Specialist")
    usuario_limpio = usuario_input.strip().title()
    opcion_liga = st.selectbox("🤝 Modalidad:", ["🌍 Ranking Global", "➕ Crear Liga Privada", "🔐 Unirse a Liga Existente"])
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
        with st.form("form_preds_ufc"):
            for _, row in df_peleas.iterrows():
                pred_existente = df_predicciones[(df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == row["id"])]
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
                if esta_bloqueado: st.markdown("<p style='text-align:center; color:#DC2626; font-weight:bold;'>🛑 PELEA FINALIZADA</p>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1: st.selectbox("Ganador", ops_w, index=idx_w, key=f"w_{row['id']}", disabled=esta_bloqueado)
                with col2: st.selectbox("Método", OPCIONES_METODO, index=idx_m, key=f"m_{row['id']}", disabled=esta_bloqueado)
                with col3: st.selectbox("Round", ops_r, index=idx_r, key=f"r_{row['id']}", disabled=esta_bloqueado)
                st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
                
            if st.form_submit_button("🔥 SELLAR CARTILLA OFICIAL"):
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
                        p_id = row["id"]
                        if row["jugado"]: continue
                        df_predicciones = df_predicciones[~((df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == p_id))]
                        df_predicciones = pd.concat([df_predicciones, pd.DataFrame([{"usuario": usuario_limpio, "liga": liga_limpia, "pelea_id": p_id, "pred_winner": st.session_state[f"w_{p_id}"], "pred_method": st.session_state[f"m_{p_id}"], "pred_round": st.session_state[f"r_{p_id}"]}])], ignore_index=True)
                    df_predicciones.to_csv(PREDICCONES_FILE, index=False)
                    st.toast('¡Predicciones enviadas al Octágono!', icon='🥊')
                    time.sleep(1.5)
                    st.rerun()

# --- PESTAÑA 3: NUEVO CENTRO DE ANÁLISIS Y MOMIOS ---
with tab3:
    st.markdown("<h2 class='stat-title'>🎲 Centro de Apuestas & Análisis (Las Vegas)</h2>", unsafe_allow_html=True)
    st.markdown("Revisa los datos de los peleadores y los momios oficiales antes de lanzar tus predicciones.")
    
    lista_combates = [f"{row['fighter_a']} vs {row['fighter_b']}" for _, row in df_peleas.iterrows()]
    pelea_seleccionada = st.selectbox("🔍 Selecciona un Combate para Analizar:", lista_combates)
    
    if pelea_seleccionada:
        f_a = pelea_seleccionada.split(" vs ")[0]
        f_b = pelea_seleccionada.split(" vs ")[1]
        
        col_img1, col_vs, col_img2 = st.columns([2, 1, 2])
        with col_img1: st.markdown(f"<div style='text-align:center;'><img src='{get_fighter_img(f_a)}' class='fighter-img' style='width:120px; height:120px;'><h3 style='color:white; margin-top:10px;'>{f_a}</h3></div>", unsafe_allow_html=True)
        with col_vs: st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top: 30px;'>VS</h1>", unsafe_allow_html=True)
        with col_img2: st.markdown(f"<div style='text-align:center;'><img src='{get_fighter_img(f_b)}' class='fighter-img' style='width:120px; height:120px;'><h3 style='color:white; margin-top:10px;'>{f_b}</h3></div>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#DC2626; margin-top:20px;'>📊 TALE OF THE TAPE</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <table style="width:100%; text-align:center; background-color:#18181b; border-radius:10px; overflow:hidden;">
            <tr style="background-color:#333; color:#D4AF37; font-weight:bold;">
                <td style="padding:10px; width:33%; font-size:1.2rem;">{get_stat(f_a, 'record')}</td>
                <td style="padding:10px; width:33%; font-size:1.1rem; text-transform:uppercase;">Récord</td>
                <td style="padding:10px; width:33%; font-size:1.2rem;">{get_stat(f_b, 'record')}</td>
            </tr>
            <tr>
                <td style="padding:10px; border-bottom:1px solid #333;">{get_stat(f_a, 'altura')}</td>
                <td style="padding:10px; border-bottom:1px solid #333; color:#A1A1AA;">Estatura</td>
                <td style="padding:10px; border-bottom:1px solid #333;">{get_stat(f_b, 'altura')}</td>
            </tr>
            <tr>
                <td style="padding:10px;">{get_stat(f_a, 'alcance')}</td>
                <td style="padding:10px; color:#A1A1AA;">Alcance</td>
                <td style="padding:10px;">{get_stat(f_b, 'alcance')}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#10B981; margin-top:30px;'>💰 MOMIOS DE LAS VEGAS</h3>", unsafe_allow_html=True)
        
        odds_a = get_stat(f_a, 'odds')
        odds_b = get_stat(f_b, 'odds')
        color_a = "odds-fav" if "-" in odds_a else "odds-dog"
        color_b = "odds-fav" if "-" in odds_b else "odds-dog"
        
        col_odds1, col_odds2 = st.columns(2)
        with col_odds1:
            st.markdown(f"<div class='odds-box'><p style='color:#A1A1AA; margin:0;'>Apuesta por {f_a}</p><p class='{color_a}' style='margin:0;'>{odds_a}</p></div>", unsafe_allow_html=True)
        with col_odds2:
            st.markdown(f"<div class='odds-box'><p style='color:#A1A1AA; margin:0;'>Apuesta por {f_b}</p><p class='{color_b}' style='margin:0;'>{odds_b}</p></div>", unsafe_allow_html=True)

# --- PESTAÑA 4: STATS EN VIVO (GRÁFICOS DE TRANSMISIÓN) ---
with tab4:
    st.markdown("<h2 class='stat-title'>📊 Tendencias de la Audiencia</h2>", unsafe_allow_html=True)
    st.markdown("Así se están inclinando las apuestas globales en tiempo real. ¿Con quién va la mayoría?")
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
                votos_b = len(preds_pelea[preds_pelea["pred_winner"] == f_b])
                
                pct_a = int((votos_a / total_votos) * 100) if total_votos > 0 else 0
                pct_b = 100 - pct_a if total_votos > 0 else 0
                
                st.markdown(f"""
                <div style="background-color: #111; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid #D4AF37;">
                    <p style="color: #A1A1AA; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">{row['peso']}</p>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 1.2rem; font-weight: bold; font-family: 'Oswald', sans-serif;">{f_a} <span style="color:#DC2626;">({pct_a}%)</span></span>
                        <span style="font-size: 1.2rem; font-weight: bold; font-family: 'Oswald', sans-serif;"><span style="color:#D4AF37;">({pct_b}%)</span> {f_b}</span>
                    </div>
                    <div style="width: 100%; background-color: #333; height: 18px; border-radius: 10px; display: flex; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);">
                        <div style="width: {pct_a}%; background-color: #DC2626; transition: width 0.5s;"></div>
                        <div style="width: {pct_b}%; background-color: #D4AF37; transition: width 0.5s;"></div>
                    </div>
                    <p style="text-align: center; color: #777; font-size: 0.8rem; margin-top: 5px; margin-bottom: 0;">Basado en {total_votos} apuestas</p>
                </div>
                """, unsafe_allow_html=True)

# --- PESTAÑA 5: ADMIN ---
with tab5:
    st.markdown("### 🎙️ Panel Oficial de Resultados")
    if st.text_input("Contraseña de Dana White:", type="password") == PASSWORD_ADMIN:
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
            if st.form_submit_button("Confirmar Noche de Peleas"):
                for idx, row in df_peleas.iterrows():
                    df_peleas.at[idx, "res_winner"], df_peleas.at[idx, "res_method"], df_peleas.at[idx, "res_round"], df_peleas.at[idx, "jugado"] = st.session_state[f"rw_{row['id']}"], st.session_state[f"rm_{row['id']}"], st.session_state[f"rr_{row['id']}"], bool(st.session_state[f"rj_{row['id']}"])
                df_peleas.to_csv(PELEAS_FILE, index=False)
                st.toast('Resultados Guardados', icon='✅')
                time.sleep(1)
                st.rerun()
