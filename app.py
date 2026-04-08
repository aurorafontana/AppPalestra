import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16U2wd-3GfeH-oqL5C-iA_ewQdkScEHShTA0HwVpOXgA/edit?usp=sharing"

st.set_page_config(page_title="Gym Tracker PRO", page_icon="🏋️", layout="centered")

# --- CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LISTA COMPLETA ESERCIZI (Aggiornata con la tua lista) ---
DEFAULT_EXERCISES = [
    # Giorno 1 – Upper A
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Panca piana bilanciere"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Lat machine / trazioni"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Panca inclinata manubri"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Rematore chest-supported"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Shoulder press"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Alzate laterali"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Curl bilanciere EZ"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Pushdown corda"},
    # Giorno 2 – Lower A
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Squat"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Romanian deadlift"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Leg press"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Leg curl"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Calf raise"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Crunch cavo"},
    # Giorno 3 – Upper B
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Panca inclinata multipower / chest press"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Pulldown presa neutra"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Rematore manubrio"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Dip assistite / panca stretta"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Alzate laterali"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Rear delt fly / face pull"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Curl manubri alternati"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "French press / estensioni tricipiti"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Hammer curl"},
    # Giorno 4 – Lower B
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Hack squat / front squat"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Hip thrust"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Bulgarian split squat"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Leg extension"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Leg curl"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Calf press"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Farmer carry / reverse curl"}
]

@st.cache_data(ttl=2)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Storico")
        if df.empty:
            return pd.DataFrame(columns=["Data", "Giorno", "Esercizio", "Peso_S1", "Reps_S1", "Peso_S2", "Reps_S2", "Peso_S3", "Reps_S3", "Peso_S4", "Reps_S4", "Note"])
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df.dropna(subset=['Data']).sort_values("Data")
    except:
        return pd.DataFrame(columns=["Data", "Giorno", "Esercizio", "Peso_S1", "Reps_S1", "Peso_S2", "Reps_S2", "Peso_S3", "Reps_S3", "Peso_S4", "Reps_S4", "Note"])

@st.cache_data(ttl=2)
def load_exercises():
    try:
        df_ex = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi")
        if df_ex is None or df_ex.empty:
            df_default = pd.DataFrame(DEFAULT_EXERCISES)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_default)
            return df_default
        return df_ex
    except:
        return pd.DataFrame(DEFAULT_EXERCISES)

# Caricamento
df_storico = load_data()
df_esercizi = load_exercises()

giorni_disponibili = ["Giorno 1 - Upper A", "Giorno 2 - Lower A", "Giorno 3 - Upper B", "Giorno 4 - Lower B"]
exercises_dict = {g: df_esercizi[df_esercizi['Giorno'] == g]['Esercizio'].tolist() for g in giorni_disponibili}

st.title("🏋️ Workout Tracker PRO")

col1, col2 = st.columns(2)
with col1:
    giorno_sel = st.selectbox("Seleziona Giorno", giorni_disponibili)
with col2:
    es_disponibili = exercises_dict.get(giorno_sel, [])
    es_sel = st.selectbox("Seleziona Esercizio", es_disponibili) if es_disponibili else None

if es_sel:
    st.divider()
    # Filtro e preparazione dati grafico
    storico_es = df_storico[df_storico["Esercizio"] == es_sel].copy()
    
    if not storico_es.empty:
        # Calcolo peso max per il grafico
        cols_p = ['Peso_S1', 'Peso_S2', 'Peso_S3', 'Peso_S4']
        storico_es[cols_p] = storico_es[cols_p].apply(pd.to_numeric, errors='coerce').fillna(0)
        storico_es['Peso_Max'] = storico_es[cols_p].max(axis=1)
        
        # Info ultimo allenamento
        ultimo = storico_es.sort_values("Data", ascending=False).iloc[0]
        st.info(f"**Ultimo allenamento ({ultimo['Data'].strftime('%d/%m/%Y')}):**\n"
                f"S1: {ultimo['Peso_S1']}kg x {ultimo['Reps_S1']} | S2: {ultimo['Peso_S2']}kg x {ultimo['Reps_S2']}")
        
        # Grafico
        chart = alt.Chart(storico_es).mark_line(point=True, color='#FF4B4B').encode(
            x=alt.X('Data:T', title='Data'),
            y=alt.Y('Peso_Max:Q', title='Carico Max (kg)'),
            tooltip=['Data', 'Peso_Max']
        ).properties(height=250)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Nessun dato registrato per questo esercizio.")

    # Form registrazione
    with st.form("new_workout", clear_on_submit=True):
        st.subheader("Registra l'allenamento di oggi")
        c1, c2, c3, c4 = st.columns(4)
        p1 = c1.number_input("P1 (kg)", min_value=0.0, step=0.5)
        r1 = c1.number_input("R1", min_value=0, step=1)
        p2 = c2.number_input("P2 (kg)", min_value=0.0, step=0.5)
        r2 = c2.number_input("R2", min_value=0, step=1)
        p3 = c3.number_input("P3 (kg)", min_value=0.0, step=0.5)
        r3 = c3.number_input("R3", min_value=0, step=1)
        p4 = c4.number_input("P4 (kg)", min_value=0.0, step=0.5)
        r4 = c4.number_input("R4", min_value=0, step=1)
        
        note = st.text_input("Note/Sensazioni")
        
        if st.form_submit_button("💾 SALVA ALLENAMENTO", use_container_width=True):
            nuovo = pd.DataFrame([{
                "Data": datetime.now().strftime("%Y-%m-%d"),
                "Giorno": giorno_sel, "Esercizio": es_sel,
                "Peso_S1": p1, "Reps_S1": r1, "Peso_S2": p2, "Reps_S2": r2,
                "Peso_S3": p3, "Reps_S3": r3, "Peso_S4": p4, "Reps_S4": r4,
                "Note": note
            }])
            # Ricarichiamo i dati freschi prima di concatenare per evitare di perdere dati di altri esercizi
            df_attuale = load_data()
            df_final = pd.concat([df_attuale, nuovo], ignore_index=True)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Storico", data=df_final)
            st.cache_data.clear()
            st.success("Allenamento salvato con successo!")
            st.rerun()

# Espander per gestione manuale
with st.expander("⚙️ Gestione Avanzata Esercizi"):
    st.write("Puoi aggiungere esercizi extra non presenti nella lista iniziale.")
    n_es = st.text_input("Nome nuovo esercizio")
    g_es = st.selectbox("Aggiungi a:", giorni_disponibili, key="config_g")
    if st.button("Aggiungi Esercizio"):
        if n_es:
            nuovo_df = pd.concat([df_esercizi, pd.DataFrame([{"Giorno": g_es, "Esercizio": n_es}])])
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=nuovo_df)
            st.cache_data.clear()
            st.rerun()
