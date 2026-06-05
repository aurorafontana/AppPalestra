import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
from streamlit_gsheets import GSheetsConnection

# --- LINK DEL TUO FOGLIO GOOGLE ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16U2wd-3GfeH-oqL5C-iA_ewQdkScEHShTA0HwVpOXgA/edit?usp=sharing"

# --- SETUP PAGINA ---
st.set_page_config(page_title="Gym Tracker", page_icon="🏋️", layout="centered")

# --- CONNESSIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DIZIONARIO IMMAGINI ESERCIZI (NUOVI LINK STABILI) ---
IMMAGINI_ESERCIZI = {
    # GIORNO 1
    "Panca piana bilanciere": "https://static.strengthlevel.com/images/illustrations/bench-press-1.jpg",
    "Lat machine / trazioni": "https://static.strengthlevel.com/images/illustrations/lat-pulldown-1.jpg",
    "Panca inclinata manubri": "https://static.strengthlevel.com/images/illustrations/incline-dumbbell-bench-press-1.jpg",
    "Rematore chest-supported": "https://static.strengthlevel.com/images/illustrations/dumbbell-row-1.jpg",
    "Shoulder press": "https://static.strengthlevel.com/images/illustrations/dumbbell-shoulder-press-1.jpg",
    "Alzate laterali": "https://static.strengthlevel.com/images/illustrations/lateral-raise-1.jpg",
    "Curl bilanciere EZ": "https://static.strengthlevel.com/images/illustrations/ez-bar-curl-1.jpg",
    "Pushdown corda": "https://static.strengthlevel.com/images/illustrations/tricep-pushdown-1.jpg",
    "Pectoral machine": "https://static.strengthlevel.com/images/illustrations/pec-deck-1.jpg",
    
    # GIORNO 2
    "Squat": "https://static.strengthlevel.com/images/illustrations/squat-1.jpg",
    "Romanian deadlift": "https://static.strengthlevel.com/images/illustrations/romanian-deadlift-1.jpg",
    "Leg press": "https://static.strengthlevel.com/images/illustrations/leg-press-1.jpg",
    "Leg curl": "https://static.strengthlevel.com/images/illustrations/leg-curl-1.jpg",
    "Calf raise": "https://static.strengthlevel.com/images/illustrations/calf-raise-1.jpg",
    "Crunch cavo": "https://static.strengthlevel.com/images/illustrations/cable-crunch-1.jpg",
    
    # GIORNO 3
    "Panca inclinata multipower / chest press": "https://static.strengthlevel.com/images/illustrations/smith-machine-incline-bench-press-1.jpg",
    "Pulldown presa neutra": "https://static.strengthlevel.com/images/illustrations/v-bar-pulldown-1.jpg",
    "Rematore manubrio": "https://static.strengthlevel.com/images/illustrations/dumbbell-row-1.jpg",
    "Dip assistite / panca stretta": "https://static.strengthlevel.com/images/illustrations/tricep-dips-1.jpg",
    "Alzate laterali": "https://static.strengthlevel.com/images/illustrations/lateral-raise-1.jpg",
    "Rear delt fly / face pull": "https://static.strengthlevel.com/images/illustrations/face-pull-1.jpg",
    "Curl manubri alternati": "https://static.strengthlevel.com/images/illustrations/dumbbell-curl-1.jpg",
    "French press / estensioni tricipiti": "https://static.strengthlevel.com/images/illustrations/lying-tricep-extension-1.jpg",
    "Hammer curl": "https://static.strengthlevel.com/images/illustrations/hammer-curl-1.jpg",
    
    # GIORNO 4
    "Hack squat / front squat": "https://static.strengthlevel.com/images/illustrations/hack-squat-1.jpg",
    "Hip thrust": "https://static.strengthlevel.com/images/illustrations/hip-thrust-1.jpg",
    "Bulgarian split squat": "https://static.strengthlevel.com/images/illustrations/bulgarian-split-squat-1.jpg",
    "Leg extension": "https://static.strengthlevel.com/images/illustrations/leg-extension-1.jpg",
    "Calf press": "https://static.strengthlevel.com/images/illustrations/calf-press-1.jpg",
    "Farmer carry": "https://static.strengthlevel.com/images/illustrations/farmers-walk-1.jpg",
    "Reverse curl": "https://static.strengthlevel.com/images/illustrations/reverse-curl-1.jpg"
}

# --- LISTA ESERCIZI COMPLETA E AGGIORNATA ---
DEFAULT_EXERCISES_LIST = [
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Panca piana bilanciere"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Lat machine / trazioni"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Panca inclinata manubri"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Rematore chest-supported"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Shoulder press"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Alzate laterali"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Curl bilanciere EZ"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Pushdown corda"},
    {"Giorno": "Giorno 1 - Upper A", "Esercizio": "Pectoral machine"}, # Aggiunto
    
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Squat"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Romanian deadlift"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Leg press"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Leg curl"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Calf raise"},
    {"Giorno": "Giorno 2 - Lower A", "Esercizio": "Crunch cavo"},
    
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Panca inclinata multipower / chest press"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Pulldown presa neutra"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Rematore manubrio"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Dip assistite / panca stretta"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Alzate laterali"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Rear delt fly / face pull"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Curl manubri alternati"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "French press / estensioni tricipiti"},
    {"Giorno": "Giorno 3 - Upper B", "Esercizio": "Hammer curl"},
    
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Hack squat / front squat"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Hip thrust"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Bulgarian split squat"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Leg extension"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Leg curl"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Calf press"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Farmer carry"},
    {"Giorno": "Giorno 4 - Lower B", "Esercizio": "Reverse curl"}
]

# --- FUNZIONI DI CARICAMENTO ---
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Storico", ttl=0)
        df = df.dropna(how='all')
        return df
    except Exception:
        return pd.DataFrame(columns=["Data", "Giorno", "Esercizio", "Peso_S1", "Reps_S1", "Peso_S2", "Reps_S2", "Peso_S3", "Reps_S3", "Peso_S4", "Reps_S4", "Note"])

def load_exercises():
    try:
        df_ex = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", ttl=0)
        df_ex = df_ex.dropna(how='all')
        if df_ex.empty or "Giorno" not in df_ex.columns:
            df_default = pd.DataFrame(DEFAULT_EXERCISES_LIST)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_default)
            return df_default
        
        # Logica per inserire automaticamente i nuovi esercizi (come Pectoral)
        esercizi_presenti = df_ex["Esercizio"].tolist()
        nuovi_da_aggiungere = []
        for default_ex in DEFAULT_EXERCISES_LIST:
            if default_ex["Esercizio"] not in esercizi_presenti:
                nuovi_da_aggiungere.append(default_ex)
                
        if nuovi_da_aggiungere:
            df_aggiornato = pd.concat([df_ex, pd.DataFrame(nuovi_da_aggiungere)], ignore_index=True)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_aggiornato)
            return df_aggiornato
            
        return df_ex
    except Exception:
        return pd.DataFrame(DEFAULT_EXERCISES_LIST)

# --- AVVIO DATI ---
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
        st.warning("Nessun esercizio. Aggiorna o aggiungine uno in basso!")
        esercizio_selezionato = None
    else:
        esercizio_selezionato = st.selectbox("Seleziona Esercizio", esercizi_giorno)
        
        # --- MOSTRA IMMAGINE ESERCIZIO ---
        if esercizio_selezionato in IMMAGINI_ESERCIZI:
            try:
                st.image(IMMAGINI_ESERCIZI[esercizio_selezionato], use_container_width=True)
            except Exception:
                st.write("*(Immagine temporaneamente non disponibile)*")

st.divider()

if esercizio_selezionato:
    # --- PROMEMORIA REPS ---
    if esercizio_selezionato == "Hammer curl":
        st.caption("💡 **Obiettivo Consigliato:** 3 serie x 10–12 reps")
    elif esercizio_selezionato == "Reverse curl":
        st.caption("💡 **Obiettivo Consigliato:** 2 serie x 12–15 reps")
    elif esercizio_selezionato == "Farmer carry":
        st.caption("💡 **Obiettivo Consigliato:** 2 serie (usa le note per segnare distanza/tempo)")

    # --- SEZIONE STORICO E GRAFICO ---
    st.subheader(f"📊 Dati per: {esercizio_selezionato}")

    if not df_storico.empty and "Esercizio" in df_storico.columns:
        storico_esercizio = df_storico[df_storico["Esercizio"] == esercizio_selezionato].copy()
    else:
        storico_esercizio = pd.DataFrame()

    if not storico_esercizio.empty:
        storico_esercizio["Data"] = pd.to_datetime(storico_esercizio["Data"], errors='coerce')
        storico_esercizio = storico_esercizio.dropna(subset=["Data"])
        
        if not storico_esercizio.empty:
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
            nuova_riga = pd.DataFrame([{
                "Data": oggi, "Giorno": giorno_selezionato, "Esercizio": esercizio_selezionato,
                "Peso_S1": p1, "Reps_S1": r1, "Peso_S2": p2, "Reps_S2": r2,
                "Peso_S3": p3, "Reps_S3": r3, "Peso_S4": p4, "Reps_S4": r4, "Note": note
            }])
            
            df_aggiornato_fresco = load_data()
            if df_aggiornato_fresco.empty:
                df_finale = nuova_riga
            else:
                df_finale = pd.concat([df_aggiornato_fresco, nuova_riga], ignore_index=True)
                
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Storico", data=df_finale)
            st.success("Allenamento salvato e protetto su Google Sheets!")
            st.rerun()

st.divider()

# --- AGGIUNTA NUOVO ESERCIZIO ---
with st.expander("➕ Aggiungi un nuovo esercizio al database"):
    with st.form("add_exercise_form"):
        giorno_destinazione = st.selectbox("A quale giorno vuoi aggiungerlo?", giorni_disponibili)
        nuovo_nome = st.text_input("Nome del nuovo esercizio")
        add_submit = st.form_submit_button("Aggiungi alla lista")
        
        if add_submit and nuovo_nome:
            df_ex_fresco = load_exercises()
            if nuovo_nome not in df_ex_fresco[df_ex_fresco['Giorno'] == giorno_destinazione]['Esercizio'].tolist():
                nuovo_es_df = pd.DataFrame([{"Giorno": giorno_destinazione, "Esercizio": nuovo_nome}])
                df_ex_aggiornato = pd.concat([df_ex_fresco, nuovo_es_df], ignore_index=True)
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Esercizi", data=df_ex_aggiornato)
                st.success(f"'{nuovo_nome}' aggiunto a {giorno_destinazione}!")
                st.rerun()
            else:
                st.warning("Esercizio già presente.")
