import streamlit as st
import pandas as pd
import os
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="UFC Freedom 250", page_icon="🥊", layout="wide")

# --- 📸 ENLACES DE IMÁGENES Y VIDEOS (INTEGRADOS) ---
TRAILER_OFICIAL = "https://youtu.be/iNJIs5bXoAE?si=Lbes9bQDegv6vocd" 

URL_FOTO_TOPURIA = "https://ufc.com/images/styles/athlete_bio_full_body/s3/2024-10/TOPURIA_ILIA_L_BELT_10-26.png?itok=0ZnoiqvU" 
URL_FOTO_GAETHJE = "https://ufc.com/images/styles/athlete_bio_full_body/s3/2026-01/GAETHJE_JUSTIN_L_BELTMOCK.png?itok=Ec57vAPj"

# --- ESTILOS CSS (MODO PPV EXTREMO CON BORDES DE CAMPEONATO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;700;900&family=Roboto:wght@400;700&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; font-family: 'Roboto', sans-serif; }
    
    h1, h2, h3, .fighter-name, .vs-text, .weight-class { font-family: 'Oswald', sans-serif !important; }
    
    /* PESTAÑAS GIGANTES */
    button[data-baseweb="tab"] {
        font-size: 1.5rem !important; 
        font-family: 'Oswald', sans-serif !important;
        text-transform: uppercase;
        padding: 15px 30px !important;
        background-color: #18181b;
        border: 1px solid #333;
        border-bottom: none;
        border-radius: 10px 10px 0 0;
        color: #71717A !important;
        letter-spacing: 1px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #DC2626 0%, #7F1D1D 100%) !important;
        color: white !important;
        border: 1px solid #EF4444;
        border-bottom: none;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        color: #ffffff; font-weight: 900; font-family: 'Oswald', sans-serif; font-size: 1.2rem;
        border: none; border-radius: 8px; padding: 15px 30px; text-transform: uppercase; letter-spacing: 2px; width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(220, 38, 38, 0.6); border: 1px solid #ff4d4d; }
    
    .fight-card { 
        background: linear-gradient(180deg, #1f1f1f 0%, #0a0a0a 100%); 
        padding: 30px; border-radius: 15px; text-align: center; 
        border-top: 5px solid #D4AF37; margin-bottom: 20px; 
        box-shadow: 0 15px 30px rgba(0,0,0,0.8); position: relative; overflow: hidden; border-bottom: 1px solid #333;
    }
    .fight-card::before { content: '🤼‍♂️'; position: absolute; font-size: 10rem; opacity: 0.03; right: -20px; bottom: -40px; }
    
    /* ESTILO DE FOTOS DE PELEADORES (Ajustado para PNG transparentes de UFC) */
    .fighter-img { 
        width: 170px; 
        height: 170px; 
        object-fit: cover; 
        object-position: top; /* Enfoca la cabeza y el cinturón */
        border-radius: 50%; 
        border: 4px solid #D4AF37; /* Borde de Campeonato */
        box-shadow: 0 0 25px rgba(212,175,55,0.5); 
        background-color: #000000; /* Fondo negro para que resalte el PNG */
    }
    
    .fighter-name { font-size: 2.2rem; font-weight: 900; color: #ffffff; text-transform: uppercase; margin-top: 15px; line-height: 1.1;}
    .vs-text { font-size: 3.5rem; color: #D4AF37; font-weight: 900; font-style: italic; text-shadow: 0 0 20px rgba(212,175,55,0.5); margin-top: 50px; }
    .weight-class { color: #DC2626; font-size: 1.1rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 20px; font-weight: bold; }
    
    .stSelectbox > div > div > div { background-color: #27272a; color: white; border-radius: 6px; font-weight: bold; font-family: 'Roboto', sans-serif;}
    .lobby-box { background-color: #18181b; border-radius: 12px; padding: 20px; text-align: center; border-bottom: 3px solid #DC2626; }
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS OFICIALES ---
PELEAS_FILE = "ufc_peleas_final.csv"
PREDICCONES_FILE = "ufc_preds_final.csv"
LIGAS_FILE = "ufc_ligas_final.csv" 
PASSWORD_ADMIN = "dana2050"

# --- INICIALIZACIÓN DE LA CARTELERA ---
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

def get_fighter_img(name, url_personalizada=""):
    if url_personalizada: return url_personalizada
    return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=18181b&color=DC2626&size=200&font-size=0.33&bold=true"

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

# --- BANNER PRINCIPAL (NUEVO OCTÁGONO) ---
st.markdown("""
<div style="background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.95)), url('https://images.unsplash.com/photo-1614081325785-35db209e5309?auto=format&fit=crop&w=1200&q=80'); background-size: cover; background-position: center; padding: 60px 20px; border-radius: 15px; text-align: center; margin-bottom: 35px; border: 2px solid #DC2626; box-shadow: 0 0 40px rgba(220, 38, 38, 0.4);">
    <h1 style="color: #ffffff; font-size: 4.5rem; margin:0; text-transform: uppercase; letter-spacing: 6px; text-shadow: 3px 3px 15px #DC2626; font-family: 'Oswald', sans-serif;">UFC FREEDOM 250</h1>
    <h2 style="color: #D4AF37; font-size: 2.5rem; margin-top: 5px; font-weight: 900; letter-spacing: 4px; font-family: 'Oswald', sans-serif;">TOPURIA <span style="color:white; font-size: 1.5rem;">VS</span> GAETHJE</h2>
</div>
""", unsafe_allow_html=True)

tab0, tab1, tab2, tab3, tab4 = st.tabs(["🏠 Lobby Oficial", "📊 Ránkings", "📝 Jugar (Cartelera)", "📺 Stats", "🎙️ Bruce Buffer"])

# --- PESTAÑA 0: LOBBY ---
with tab0:
    col_vid, col_info = st.columns([2, 1])
    with col_vid:
        st.markdown("<h3 style='color: #D4AF37; margin-top: 0;'>🎬 Promo Oficial de la Velada</h3>", unsafe_allow_html=True)
        st.video(TRAILER_OFICIAL)
    with col_info:
        st.markdown("""
        <div style="background-color: #18181b; padding: 25px; border-radius: 12px; border-left: 5px solid #DC2626; height: 100%;">
            <h2 style="color: white; margin-top: 0;">🔥 Entra al Octágono</h2>
            <p style="color: #A1A1AA; font-size: 1.1rem;">La cartelera más brutal del año te espera. Ve a la pestaña de <strong>JUGAR</strong>, arma tu cartilla de predicciones y demuestra que eres el Oráculo de las MMA.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("✅ Resultados de la Noche")
    peleas_jugadas = df_peleas[df_peleas["jugado"] == True]
    if not peleas_jugadas.empty:
        for _, row in peleas_jugadas.iterrows():
            st.markdown(f"<div style='background-color:#18181b; padding:15px; border-radius:8px; margin-bottom:10px; border-left: 4px solid #D4AF37;'><p style='color:#A1A1AA; font-size:0.8rem; margin:0;'>{row['peso']}</p><p style='font-size:1.2rem; margin:5px 0; color:white;'>👑 <strong>{row['res_winner']}</strong> vence por <strong>{row['res_method']}</strong> (Round {row['res_round']})</p></div>", unsafe_allow_html=True)
    else:
        st.info("⏱️ Aún no hay resultados. ¡Bruce Buffer se está preparando!")

# --- PESTAÑA 1: RÁNKING ---
with tab1:
    opciones_ligas = ["GLOBAL"]
    if not df_ligas.empty: opciones_ligas.extend(sorted(df_ligas["nombre_liga"].unique().tolist()))
    liga_busqueda = st.selectbox("🔍 Selecciona tu Liga:", opciones_ligas).strip().upper()
    df_ranking = calcular_tabla_ufc(df_peleas, df_predicciones, liga_busqueda)
    if not df_ranking.empty: st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else: st.warning("No hay predicciones registradas aún en esta liga.")

# --- PESTAÑA 2: CARTELERA (PREDICCIONES CON FACE-OFF) ---
with tab2:
    usuario_input = st.text_input("👤 Nombre del Peleador (Tu Apodo):", placeholder="Ej. Tesla Jr.")
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
                
                # Sistema de Fotos Face-off (Si es el Main Event carga las fotos de UFC)
                img_a = get_fighter_img(row["fighter_a"], URL_FOTO_TOPURIA if row["id"]==1 else "")
                img_b = get_fighter_img(row["fighter_b"], URL_FOTO_GAETHJE if row["id"]==1 else "")

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
                
                # TALE OF THE TAPE (Solo para el Main Event)
                if row["id"] == 1:
                    with st.expander("📊 Ver Tale of the Tape (Estadísticas)"):
                        st.markdown("""
                        | Estadística | Ilia Topuria | Justin Gaethje |
                        | :--- | :---: | :---: |
                        | **Récord** | 15 - 0 - 0 | 25 - 5 - 0 |
                        | **Altura** | 1.70 m | 1.80 m |
                        | **Alcance** | 1.75 m | 1.80 m |
                        | **Estilo** | Lucha / Boxeo | Wrestling / Kickboxing |
                        """)
                
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

# --- PESTAÑA 3 y 4 ---
with tab3:
    st.header("📊 Las Matemáticas del Octágono")
    st.markdown("""
    <div style="background-color: #18181b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #DC2626;">
        <h3 style="color: white; margin-top: 0;">📜 Reglas de Puntuación</h3>
        <ul style="color: #A1A1AA; font-size: 1.1rem;">
            <li><strong>+10 pts:</strong> Acertar al ganador de la pelea.</li>
            <li><strong>+5 pts extra:</strong> Acertar el Método (KO/TKO, Sumisión, Decisión).</li>
            <li><strong>+5 pts extra:</strong> Acertar el Round exacto.</li>
            <li>🏆 <strong>Bono Perfecto (+5 pts):</strong> Achuntar a TODO en la misma pelea (Máximo 25 puntos por combate).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with tab4:
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
