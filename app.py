import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import altair as alt

# --- COSTANTI E PERCORSI FILE ---
DATA_FILE = "workout_data.csv"
EXERCISES_FILE = "exercises.json"

# --- ESERCIZI PREDEFINITI ---
DEFAULT_EXERCISES = {
    "Giorno 1 - Upper A": ["Panca piana bilanciere", "Lat machine / trazioni", "Panca inclinata manubri", "Rematore chest-supported", "Shoulder press", "Alzate laterali", "Curl bilanciere EZ", "Pushdown corda"],
    "Giorno 2 - Lower A": ["Squat", "Romanian deadlift", "Leg press", "Leg curl", "Calf raise", "Crunch cavo"],
    "Giorno 3 - Upper B": ["Panca inclinata multipower / chest press", "Pulldown presa neutra", "Rematore manubrio", "Dip assistite / panca stretta", "Alzate laterali", "Rear delt fly / face pull", "Curl manubri alternati", "French press / estensioni tricipiti", "Hammer curl"],
    "Giorno 4 - Lower B": ["Hack squat / front squat", "Hip thrust", "Bulgarian split squat", "Leg extension", "Leg curl", "Calf press", "Farmer carry / reverse curl"]
}

# --- FUNZIONI DI INIZIALIZZAZIONE ---
def init_files():
    if not os.path.exists(EXERCISES_FILE):
        with open(EXERCISES_FILE, "w") as f:
            json.dump(DEFAULT_EXERCISES, f)
    if not os.path.exists(DATA_FILE):
        cols = ["Data", "Giorno", "Esercizio", "Peso_S1", "Reps_S1", "Peso_S2", "Reps_S2", 
                "Peso_S3", "Reps_S3", "Peso_S4", "Reps_S4", "Note"]
        df = pd.DataFrame(columns=cols)
        df.to_csv(DATA_FILE, index=False)

def load_exercises():
    with open(EXERCISES_FILE, "r") as f:
        return json.load(f)

def save_exercises(exercises_dict):
    with open(EXERCISES_FILE, "w") as f:
        json.dump(exercises_dict, f)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_workout(data_row):
    df = pd.DataFrame([data_row])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- SETUP PAGINA ---
st.set_page_config(page_title="Gym Tracker", page_icon="🏋️", layout="centered")

# Inizializza i file se non esistono
init_files()
exercises_dict = load_exercises()
df_storico = load_data()

# --- TITOLO ---
st.title("🏋️ Workout Tracker")

# --- SELEZIONE GIORNO E ESERCIZIO ---
col1, col2 = st.columns(2)
with col1:
    giorni_disponibili = list(exercises_dict.keys())
    giorno_selezionato = st.selectbox("Seleziona Giorno", giorni_disponibili)

with col2:
    esercizi_giorno = exercises_dict[giorno_selezionato]
    esercizio_selezionato = st.selectbox("Seleziona Esercizio", esercizi_giorno)

st.divider()

# --- SEZIONE STORICO E GRAFICO ---
st.subheader(f"📊 Dati per: {esercizio_selezionato}")

storico_esercizio = df_storico[df_storico["Esercizio"] == esercizio_selezionato].copy()

if not storico_esercizio.empty:
    storico_esercizio["Data"] = pd.to_datetime(storico_esercizio["Data"])
    storico_esercizio = storico_esercizio.sort_values(by="Data", ascending=False)
    
    ultimo_allenamento = storico_esercizio.iloc[0]
    
    # Mostra l'ultimo allenamento in un box in evidenza
    st.info(f"**Ultimo allenamento ({ultimo_allenamento['Data'].strftime('%d/%m/%Y')}):**\n"
            f"- S1: {ultimo_allenamento['Peso_S1']}kg x {ultimo_allenamento['Reps_S1']} reps\n"
            f"- S2: {ultimo_allenamento['Peso_S2']}kg x {ultimo_allenamento['Reps_S2']} reps\n"
            f"- S3: {ultimo_allenamento['Peso_S3']}kg x {ultimo_allenamento['Reps_S3']} reps\n"
            f"- S4: {ultimo_allenamento['Peso_S4']}kg x {ultimo_allenamento['Reps_S4']} reps\n"
            f"- Note: {ultimo_allenamento['Note'] if pd.notna(ultimo_allenamento['Note']) else 'Nessuna nota'}")

    # Calcolo Peso Max e Volume per il grafico
    storico_esercizio['Peso_Max'] = storico_esercizio[['Peso_S1', 'Peso_S2', 'Peso_S3', 'Peso_S4']].max(axis=1)
    
    # Grafico Andamento (Altair per un look pulito in dark mode)
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
        nuovo_dato = {
            "Data": oggi,
            "Giorno": giorno_selezionato,
            "Esercizio": esercizio_selezionato,
            "Peso_S1": p1, "Reps_S1": r1,
            "Peso_S2": p2, "Reps_S2": r2,
            "Peso_S3": p3, "Reps_S3": r3,
            "Peso_S4": p4, "Reps_S4": r4,
            "Note": note
        }
        save_workout(nuovo_dato)
        st.success("Allenamento salvato con successo!")
        st.rerun() # Ricarica per aggiornare subito grafico e storico

st.divider()

# --- AGGIUNTA NUOVO ESERCIZIO ---
with st.expander("➕ Aggiungi un nuovo esercizio al database"):
    with st.form("add_exercise_form"):
        giorno_destinazione = st.selectbox("A quale giorno vuoi aggiungerlo?", giorni_disponibili)
        nuovo_nome = st.text_input("Nome del nuovo esercizio")
        add_submit = st.form_submit_button("Aggiungi alla lista")
        
        if add_submit and nuovo_nome:
            if nuovo_nome not in exercises_dict[giorno_destinazione]:
                exercises_dict[giorno_destinazione].append(nuovo_nome)
                save_exercises(exercises_dict)
                st.success(f"'{nuovo_nome}' aggiunto a {giorno_destinazione}!")
                st.rerun()
            else:
                st.warning("Esercizio già presente in questo giorno.")