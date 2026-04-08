import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
from streamlit_gsheets import GSheetsConnection

# --- INSERISCI QUI IL LINK DEL TUO FOGLIO GOOGLE ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16U2wd-3GfeH-oqL5C-iA_ewQdkScEHShTA0HwVpOXgA/edit?usp=sharing"

# --- SETUP PAGINA ---
st.set_page_config(page_title="Gym Tracker", page_icon="🏋️", layout="centered")

# --- CONNESSIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Esercizi predefiniti (in caso il foglio sia vuoto)
DEFAULT_EXERCISES = [
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Panca piana bilanciere"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Lat machine / trazioni"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Squat"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Romanian deadlift"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Panca inclinata multipower"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Hack squat / front squat"}
]

@st.cache_data(ttl=5)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Storico", usecols=list(range(12)))
        df = df.dropna(how='all') # Rimuove righe vuote
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Data", "Giorno", "Esercizio", "Peso_S1", "Reps_S1", "Peso_S2", "Reps_S2", "Peso_S3", "Reps_S3", "Peso_S4", "Reps_S4", "Note"])

@st.cache_data(ttl=5)
def load_exercises():
    try:
        df_ex = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", usecols=[0, 1])
        df_ex = df_ex.dropna(how='all')
        if df_ex.empty:
            df_default = pd.DataFrame(DEFAULT_EXERCISES)
            # Corretto: aggiunto spreadsheet=SPREADSHEET_URL
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_default)
            return df_default
        return df_ex
    except Exception:
        return pd.DataFrame(DEFAULT_EXERCISES)

df_storico = load_data()
df_esercizi = load_exercises()

giorni_disponibili = ["Giorno 1 - Upper A", "Giorno 2 - Lower A", "Giorno 3 - Upper B", "Giorno 4 - Lower B"]
exercises_dict = {giorno: df_esercizi[df_esercizi['Giorno'] == giorno]['Esercizio'].tolist() for giorno in giorni_disponibili}

# --- TITOLO ---
st.title("🏋️ Workout Tracker")

# --- SELEZIONE GIORNO E ESERCIZIO ---
col1, col2 = st.columns(2)
with col1:
    giorno_selezionato = st.selectbox("Seleziona Giorno", giorni_disponibili)

with col2:
    esercizi_giorno = exercises_dict.get(giorno_selezionato, [])
    if not esercizi_giorno:
        st.warning("Nessun esercizio per questo giorno. Aggiungine uno in basso!")
        esercizio_selezionato = None
    else:
        esercizio_selezionato = st.selectbox("Seleziona Esercizio", esercizi_giorno)

st.divider()

if esercizio_selezionato:
    # --- SEZIONE STORICO E GRAFICO ---
    st.subheader(f"📊 Dati per: {esercizio_selezionato}")

    storico_esercizio = df_storico[df_storico["Esercizio"] == esercizio_selezionato].copy()

    if not storico_esercizio.empty:
        storico_esercizio["Data"] = pd.to_datetime(storico_esercizio["Data"])
        storico_esercizio = storico_esercizio.sort_values(by="Data", ascending=False)
        
        ultimo_allenamento = storico_esercizio.iloc[0]
        
        st.info(f"**Ultimo allenamento ({ultimo_allenamento['Data'].strftime('%d/%m/%Y')}):**\n"
                f"- S1: {ultimo_allenamento['Peso_S1']}kg x {ultimo_allenamento['Reps_S1']} reps\n"
                f"- S2: {ultimo_allenamento['Peso_S2']}kg x {ultimo_allenamento['Reps_S2']} reps\n"
                f"- S3: {ultimo_allenamento['Peso_S3']}kg x {ultimo_allenamento['Reps_S3']} reps\n"
                f"- S4: {ultimo_allenamento['Peso_S4']}kg x {ultimo_allenamento['Reps_S4']} reps\n"
                f"- Note: {ultimo_allenamento['Note'] if pd.notna(ultimo_allenamento['Note']) else 'Nessuna nota'}")

        storico_esercizio['Peso_Max'] = storico_esercizio[['Peso_S1', 'Peso_S2', 'Peso_S3', 'Peso_S4']].apply(pd.to_numeric, errors='coerce').max(axis=1)
        
        chart = alt.Chart(storico_esercizio).mark_line(point=True).encode(
            x=alt.X('Data:T', title='Data'),
            y=alt.Y('Peso_Max:Q', title='Peso Massimo (kg)'),
            tooltip=['Data:T', 'Peso_Max:Q']
        ).properties(height=250)
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Nessun dato precedente per questo esercizio. Inizia a spingere! 💪")

    st.divider()

    # --- INSERIMENTO NUOVI DATI ---
    st.subheader("✍️ Registra Allenamento Oggi")

    oggi = datetime.now().strftime("%Y-%m-%d")

    with st.form("workout_form", clear_on_submit=True):
        cols_s1 = st.columns(2)
        with cols_s1[0]: p1 = st.number_input("Peso Serie 1 (kg)", min_value=0.0, step=1.0, format="%.1f")
        with cols_s1[1]: r1 = st.number_input("Reps Serie 1", min_value=0, step=1)
        
        cols_s2 = st.columns(2)
        with cols_s2[0]: p2 = st.number_input("Peso Serie 2 (kg)", min_value=0.0, step=1.0, format="%.1f")
        with cols_s2[1]: r2 = st.number_input("Reps Serie 2", min_value=0, step=1)
        
        cols_s3 = st.columns(2)
        with cols_s3[0]: p3 = st.number_input("Peso Serie 3 (kg)", min_value=0.0, step=1.0, format="%.1f")
        with cols_s3[1]: r3 = st.number_input("Reps Serie 3", min_value=0, step=1)
        
        cols_s4 = st.columns(2)
        with cols_s4[0]: p4 = st.number_input("Peso Serie 4 (kg)", min_value=0.0, step=1.0, format="%.1f")
        with cols_s4[1]: r4 = st.number_input("Reps Serie 4", min_value=0, step=1)
        
        note = st.text_area("Note (sensazioni, tecnica, fastidi...)", height=100)
        
        submitted = st.form_submit_button("💾 Salva Allenamento", use_container_width=True)
        
        if submitted:
            nuovo_dato = pd.DataFrame([{
                "Data": oggi,
                "Giorno": giorno_selezionato,
                "Esercizio": esercizio_selezionato,
                "Peso_S1": p1, "Reps_S1": r1,
                "Peso_S2": p2, "Reps_S2": r2,
                "Peso_S3": p3, "Reps_S3": r3,
                "Peso_S4": p4, "Reps_S4": r4,
                "Note": note
            }])
            
            df_aggiornato = pd.concat([df_storico, nuovo_dato], ignore_index=True)
            # Corretto: aggiunto spreadsheet=SPREADSHEET_URL
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Storico", data=df_aggiornato)
            st.cache_data.clear()
            st.success("Allenamento salvato su Google Sheets!")
            st.rerun()

st.divider()

# --- AGGIUNTA NUOVO ESERCIZIO ---
with st.expander("➕ Aggiungi un nuovo esercizio al database"):
    with st.form("add_exercise_form"):
        giorno_destinazione = st.selectbox("A quale giorno vuoi aggiungerlo?", giorni_disponibili)
        nuovo_nome = st.text_input("Nome del nuovo esercizio")
        add_submit = st.form_submit_button("Aggiungi alla lista")
        
        if add_submit and nuovo_nome:
            if nuovo_nome not in exercises_dict.get(giorno_destinazione, []):
                nuovo_es_df = pd.DataFrame([{"Giorno": giorno_destinazione, "Esercizio": nuovo_nome}])
                df_ex_aggiornato = pd.concat([df_esercizi, nuovo_es_df], ignore_index=True)
                # Corretto: aggiunto spreadsheet=SPREADSHEET_URL
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_ex_aggiornato)
                st.cache_data.clear()
                st.success(f"'{nuovo_nome}' aggiunto a {giorno_destinazione} su Google Sheets!")
                st.rerun()
            else:
                st.warning("Esercizio già presente in questo giorno.")
