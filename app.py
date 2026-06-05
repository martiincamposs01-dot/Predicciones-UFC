import streamlit as st
import pandas as pd
import os
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="UFC Freedom 250", page_icon="🥊", layout="wide")

# --- ESTILOS CSS (ESTÉTICA UFC - ROJO, NEGRO Y DORADO) ---
st.markdown("""
<style>
    .stApp { background-color: #09090b; color: #ffffff; }
    
    @keyframes pulseRed {
        0% { box-shadow: 0 0 15px rgba(220, 38, 38, 0.4); }
        50% { box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
        100% { box-shadow: 0 0 15px rgba(220, 38, 38, 0.4); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        color: #ffffff; font-weight: 900; border: none; border-radius: 8px;
        padding: 12px 24px; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 2px; width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(220, 38, 38, 0.6); color: #fff; border: 1px solid #ff4d4d; }
    
    .fight-card { 
        background: linear-gradient(180deg, #18181b 0%, #09090b 100%); 
        padding: 20px; border-radius: 12px; text-align: center; 
        border-top: 4px solid #D4AF37; margin-bottom: 25px; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.6); position: relative; overflow: hidden;
    }
    .fight-card::before { content: '🛑'; position: absolute; font-size: 6rem; opacity: 0.02; right: -15px; bottom: -30px; }
    
    .fighter-name { font-size: 1.4rem; font-weight: 900; color: #ffffff; text-transform: uppercase; margin-top: 10px; }
    .vs-text { font-size: 2.5rem; color: #D4AF37; font-weight: 900; font-style: italic; text-shadow: 0 0 15px rgba(212,175,55,0.4); margin-top: 10px; }
    .weight-class { color: #A1A1AA; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 15px; font-weight: bold; }
    
    .stSelectbox > div > div > div { background-color: #27272a; color: white; border-radius: 6px; font-weight: bold; }
    .lobby-box { background-color: #18181b; border-radius: 12px; padding: 20px; text-align: center; border-bottom: 3px solid #DC2626; }
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS OFICIALES ---
PELEAS_FILE = "ufc_peleas_final.csv"
PREDICCONES_FILE = "ufc_preds_final.csv"
LIGAS_FILE = "ufc_ligas_final.csv" 
PASSWORD_ADMIN = "dana2050"

# --- INICIALIZACIÓN DE LA CARTELERA (UFC FREEDOM 250) ---
if not os.path.exists(PELEAS_FILE):
    cartelera_inicial = [
        {"id": 1, "orden": "MAIN EVENT - 5 ROUNDS", "peso": "UFC Lightweight Championship", "fighter_a": "Ilia Topuria", "fighter_b": "Justin Gaethje", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
        {"id": 2, "orden": "CO-MAIN EVENT - 5 ROUNDS", "peso": "Interim UFC Heavyweight Championship", "fighter_a": "Alex Pereira", "fighter_b": "Ciryl Gane", "rondas_max": 5, "res_winner": "-", "res_method": "-", "res_round": "-", "jugado": False},
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

# --- LISTAS DE OPCIONES ---
OPCIONES_METODO = ["KO/TKO", "Sumisión", "Decisión"]
def get_opciones_round(rondas_max):
    return [str(i) for i in range(1, rondas_max + 1)] + ["Tarjetas (Decisión)"]

# --- FUNCIÓN DE PUNTUACIÓN UFC ---
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
        
        real_w = p_real["res_winner"]
        real_m = p_real["res_method"]
        real_r = str(p_real["res_round"])
        
        pred_w = pred["pred_winner"]
        pred_m = pred["pred_method"]
        pred_r = str(pred["pred_round"])
        
        if real_w == pred_w:
            puntos_pelea = 10
            puntajes[user]["ganadores"] += 1
            if real_m == pred_m: puntos_pelea += 5
            if real_r == pred_r: puntos_pelea += 5
            if real_m == pred_m and real_r == pred_r:
                puntos_pelea += 5 # Bono Pleno Perfecto
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

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h1 style="font-size: 4rem; margin: 0; filter: drop-shadow(0px 0px 10px rgba(220,38,38,0.8));">🥊</h1>
        <h2 style="color: #DC2626; margin-top: 10px; text-transform: uppercase; letter-spacing: 2px;">Fight Week</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 Asegúrate de instalar la app en tu pantalla de inicio para la experiencia completa.")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: white;'>🔗 Invita a tus amigos</h3>", unsafe_allow_html=True)
    
    # ⚠️ IMPORTANTE: CAMBIA ESTE LINK CUANDO DESPLIEGUES TU NUEVA APP
    url_de_tu_app = "https://PON_TU_NUEVO_LINK_AQUI.streamlit.app"
    
    st.code(url_de_tu_app, language="text")
    mensaje_whatsapp = f"🥊 ¡Únete a nuestra liga de pronósticos para UFC FREEDOM 250! Deja tus predicciones aquí: {url_de_tu_app}"
    url_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensaje_whatsapp)}"
    
    st.markdown(f"""
    <a href="{url_whatsapp}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            📲 Enviar por WhatsApp
        </div>
    </a>
    """, unsafe_allow_html=True)

# --- BANNER PRINCIPAL ---
st.markdown("""
<div style="animation: pulseRed 3s infinite; background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.9)), url('https://images.unsplash.com/photo-1599586120429-48281b6f0ece?auto=format&fit=crop&w=1200&q=80'); background-size: cover; background-position: center; padding: 40px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 2px solid #D4AF37;">
    <h1 style="color: #D4AF37; margin:0; text-transform: uppercase; letter-spacing: 4px; text-shadow: 0 0 20px rgba(212,175,55,1);">UFC FREEDOM 250</h1>
    <p style="color: #e5e7eb; font-size: 1.3em; margin-top: 10px; font-weight: 900; letter-spacing: 5px;">TOPURIA VS GAETHJE</p>
</div>
""", unsafe_allow_html=True)

tab0, tab1, tab2, tab3, tab4 = st.tabs(["🏠 Lobby", "📊 Ránking", "📝 Cartelera", "📺 Estadísticas", "🎙️ Bruce Buffer"])

# --- PESTAÑA 0: LOBBY ---
with tab0:
    st.markdown("""
    <div style="background-color: #18181b; padding: 25px; border-radius: 12px; border-left: 5px solid #DC2626; margin-bottom: 20px;">
        <h2 style="color: white; margin-top: 0;">🔥 Entra al Octágono</h2>
        <p style="color: #A1A1AA; font-size: 1.1rem;">Arma tu cartilla de predicciones para la velada. Adivina ganadores, métodos de finalización y el round exacto para coronarte campeón.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("✅ Resultados Oficiales de la Noche")
    peleas_jugadas = df_peleas[df_peleas["jugado"] == True]
    if not peleas_jugadas.empty:
        for _, row in peleas_jugadas.iterrows():
            st.markdown(f"<div style='background-color:#18181b; padding:15px; border-radius:8px; margin-bottom:10px; border-left: 4px solid #D4AF37;'><p style='color:#A1A1AA; font-size:0.8rem; margin:0;'>{row['peso']}</p><p style='font-size:1.2rem; margin:5px 0; color:white;'>👑 <strong>{row['res_winner']}</strong> vence por <strong>{row['res_method']}</strong> (Round {row['res_round']})</p></div>", unsafe_allow_html=True)
    else:
        st.info("⏱️ Aún no hay resultados. ¡Bruce Buffer se está preparando!")

# --- PESTAÑA 1: RÁNKING ---
with tab1:
    st.markdown("""
    <div style="background-color: #18181b; padding: 20px; border-radius: 12px; border-left: 5px solid #DC2626; margin-bottom: 20px;">
        <h3 style="color: white; margin-top: 0;">🏆 Tabla de Posiciones</h3>
        <p style="color: #A1A1AA; margin-bottom: 0;">Selecciona 'GLOBAL' o busca la liga privada de tu gimnasio.</p>
    </div>
    """, unsafe_allow_html=True)
    
    opciones_ligas = ["GLOBAL"]
    if not df_ligas.empty: opciones_ligas.extend(sorted(df_ligas["nombre_liga"].unique().tolist()))
    liga_busqueda = st.selectbox("🔍 Buscar Liga:", opciones_ligas).strip().upper()
    
    df_ranking = calcular_tabla_ufc(df_peleas, df_predicciones, liga_busqueda)
    if not df_ranking.empty:
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay predicciones registradas aún en esta liga.")

# --- PESTAÑA 2: CARTELERA (PREDICCIONES) ---
with tab2:
    usuario_input = st.text_input("👤 Nombre del Peleador (Tu Apodo):", placeholder="Ej. The Notorious")
    usuario_limpio = usuario_input.strip().title()
    
    opcion_liga = st.selectbox("🤝 Modalidad:", ["🌍 Ranking Global", "➕ Crear Liga Privada", "🔐 Unirse a Liga Existente"])
    liga_limpia = "GLOBAL"
    clave_ingresada, clave_creada, liga_nueva = "", "", ""
    
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
                
                def_w = row["fighter_a"]
                def_m = "Decisión"
                def_r = "Tarjetas (Decisión)"
                
                if not pred_existente.empty:
                    def_w = pred_existente.iloc[0]["pred_winner"]
                    def_m = pred_existente.iloc[0]["pred_method"]
                    def_r = str(pred_existente.iloc[0]["pred_round"])

                opciones_fighters = [row["fighter_a"], row["fighter_b"]]
                idx_w = opciones_fighters.index(def_w) if def_w in opciones_fighters else 0
                idx_m = OPCIONES_METODO.index(def_m) if def_m in OPCIONES_METODO else 2
                
                ops_r = get_opciones_round(row["rondas_max"])
                idx_r = ops_r.index(def_r) if def_r in ops_r else len(ops_r)-1

                st.markdown(f"""
                <div class='fight-card'>
                    <div class='weight-class'>{row['orden']} | {row['peso']}</div>
                    <div style='display:flex; justify-content:space-around; align-items:center;'>
                        <div style='width:40%;' class='fighter-name'>{row['fighter_a']}</div>
                        <div style='width:20%;' class='vs-text'>VS</div>
                        <div style='width:40%;' class='fighter-name'>{row['fighter_b']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                esta_bloqueado = bool(row["jugado"])
                
                if esta_bloqueado:
                     st.markdown("<p style='text-align:center; color:#DC2626; font-weight:bold;'>🛑 PELEA FINALIZADA</p>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1: p_w = st.selectbox("Ganador", opciones_fighters, index=idx_w, key=f"w_{row['id']}", disabled=esta_bloqueado)
                with col2: p_m = st.selectbox("Método", OPCIONES_METODO, index=idx_m, key=f"m_{row['id']}", disabled=esta_bloqueado)
                with col3: p_r = st.selectbox("Round", ops_r, index=idx_r, key=f"r_{row['id']}", disabled=esta_bloqueado)
                st.markdown("<br>", unsafe_allow_html=True)
                
            if st.form_submit_button("🔥 SELLAR PREDICCIONES"):
                acceso = True
                if opcion_liga == "➕ Crear Liga Privada":
                    if not liga_nueva or not clave_creada: st.error("Faltan datos de la liga."); acceso = False
                    else:
                        nueva_l = {"nombre_liga": liga_limpia, "clave_liga": clave_creada, "creador": usuario_limpio}
                        df_ligas = pd.concat([df_ligas, pd.DataFrame([nueva_l])], ignore_index=True)
                        df_ligas.to_csv(LIGAS_FILE, index=False)
                elif opcion_liga == "🔐 Unirse a Liga Existente" and ligas_disp:
                    if str(clave_ingresada) != str(df_ligas[df_ligas["nombre_liga"] == liga_limpia]["clave_liga"].values[0]):
                        st.error("Contraseña incorrecta."); acceso = False

                if acceso:
                    for _, row in df_peleas.iterrows():
                        p_id = row["id"]
                        if row["jugado"]: continue
                        df_predicciones = df_predicciones[~((df_predicciones["usuario"] == usuario_limpio) & (df_predicciones["pelea_id"] == p_id))]
                        nueva_p = {"usuario": usuario_limpio, "liga": liga_limpia, "pelea_id": p_id, 
                                   "pred_winner": st.session_state[f"w_{p_id}"], 
                                   "pred_method": st.session_state[f"m_{p_id}"], 
                                   "pred_round": st.session_state[f"r_{p_id}"]}
                        df_predicciones = pd.concat([df_predicciones, pd.DataFrame([nueva_p])], ignore_index=True)
                    df_predicciones.to_csv(PREDICCONES_FILE, index=False)
                    st.toast('¡Predicciones enviadas al Octágono!', icon='🥊')
                    time.sleep(1.5)
                    st.rerun()

# --- PESTAÑA 3: ESTADÍSTICAS ---
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
    st.info("Las estadísticas globales de los peleadores más apostados aparecerán aquí cuando hayan más predicciones.")

# --- PESTAÑA 4: ADMIN (BRUCE BUFFER) ---
with tab4:
    st.markdown("### 🎙️ Panel Oficial de Resultados")
    if st.text_input("Contraseña de Dana White:", type="password") == PASSWORD_ADMIN:
        with st.form("admin_form"):
            for idx, row in df_peleas.iterrows():
                st.write(f"**{row['fighter_a']} vs {row['fighter_b']}**")
                
                ops_w = [row['fighter_a'], row['fighter_b'], "Empate/No Contest"]
                idx_w_real = ops_w.index(row['res_winner']) if row['res_winner'] in ops_w else 0
                idx_m_real = OPCIONES_METODO.index(row['res_method']) if row['res_method'] in OPCIONES_METODO else 0
                ops_r = get_opciones_round(row["rondas_max"])
                idx_r_real = ops_r.index(str(row['res_round'])) if str(row['res_round']) in ops_r else 0

                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1: w_r = st.selectbox("Ganador", ops_w, index=idx_w_real, key=f"rw_{row['id']}")
                with c2: m_r = st.selectbox("Método", OPCIONES_METODO, index=idx_m_real, key=f"rm_{row['id']}")
                with c3: r_r = st.selectbox("Round", ops_r, index=idx_r_real, key=f"rr_{row['id']}")
                with c4: jugado = st.checkbox("¿Oficial?", value=row["jugado"], key=f"rj_{row['id']}")
                st.markdown("---")
            if st.form_submit_button("Confirmar Noche de Peleas"):
                for idx, row in df_peleas.iterrows():
                    p_id = row["id"]
                    df_peleas.at[idx, "res_winner"] = st.session_state[f"rw_{p_id}"] if st.session_state[f"rj_{p_id}"] else "-"
                    df_peleas.at[idx, "res_method"] = st.session_state[f"rm_{p_id}"] if st.session_state[f"rj_{p_id}"] else "-"
                    df_peleas.at[idx, "res_round"] = st.session_state[f"rr_{p_id}"] if st.session_state[f"rj_{p_id}"] else "-"
                    df_peleas.at[idx, "jugado"] = bool(st.session_state[f"rj_{p_id}"])
                df_peleas.to_csv(PELEAS_FILE, index=False)
                st.toast('Resultados Guardados', icon='✅')
                time.sleep(1)
                st.rerun()
