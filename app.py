import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from datetime import datetime

# 1. Nastavenie stránky
st.set_page_config(page_title="Kalórie Lukáš", layout="wide")

# 2. Autorizácia (Secrets)
def get_gsheet_client():
    credentials = {
        "type": "service_account",
        "project_id": st.secrets["gspread"]["project_id"],
        "private_key_id": st.secrets["gspread"]["private_key_id"],
        "private_key": st.secrets["gspread"]["private_key"],
        "client_email": st.secrets["gspread"]["client_email"],
        "client_id": st.secrets["gspread"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"]
    }
    gc = gspread.service_account_from_dict(credentials)
    return gc

# --- SIDEBAR: KOMPLETNÝ FORMULÁR ---
with st.sidebar:
    st.header("📝 Pridať nový deň")
    with st.form("add_form", clear_on_submit=True):
        f_date = st.date_input("Dátum", datetime.now()).strftime('%-d.%-m.%Y')
        f_prijem = st.number_input("Príjem (kcal)", step=10)
        f_vydaj = st.number_input("Výdaj (kcal)", step=10)
        f_vaha = st.number_input("Váha(kg)", step=0.1, format="%.1f")
        f_aktivita = st.selectbox("Aktivita", ["Rest day", "Silový tréning", "Fotbal", "Chůze na pásu", "Hike"])
        f_kroky = st.number_input("Počet kroků", step=100)
        
        submit = st.form_submit_button("Uložiť do tabuľky")

    if submit:
        try:
            client = get_gsheet_client()
            sh = client.open_by_key("1-2iZnGaecjr2scBPQPETz4M6Ymw9B8NjaFM0cafouqE")
            worksheet = sh.worksheet("Lukáš")
            
            # Výpočet deficitu (Prijem - Vydaj)
            f_deficit = f_prijem - f_vydaj
            
            # Zápis riadku presne podľa poradia v tvojej tabuľke (Stĺpce B až H)
            # Poradie: Dátum, Príjem, Výdaj, Deficit, Váha, Aktivita, Počet krokov
            worksheet.append_row([f_date, f_prijem, f_vydaj, f_deficit, f_vaha, f_aktivita, f_kroky], 
                                 value_input_option='USER_ENTERED')
            
            st.success("Dáta uložené!")
            st.balloons()
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Chyba pri zápise: {e}")

# --- HLAVNÁ STRÁNKA ---
st.title("🍎 Kalorické Tabulky: Lukáš")

URL_CSV = "https://docs.google.com/spreadsheets/d/1-2iZnGaecjr2scBPQPETz4M6Ymw9B8NjaFM0cafouqE/export?format=csv&gid=0"

try:
    # Načítanie a hľadanie hlavičky
    raw_df = pd.read_csv(URL_CSV, header=None)
    header_row = None
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('Datum').any():
            header_row = i
            break
    
    if header_row is not None:
        df = pd.read_csv(URL_CSV, skiprows=header_row)
        df.columns = [c.strip() for c in df.columns]
        # Odstránime riadky kde nie je dátum
        df = df[df['Datum'].notna()]

        # Oprava NaN hodnôt: vezmeme posledný riadok, kde je reálne zadaná váha/príjem
        valid_vaha = df[df['Váha(kg)'].notna() & (df['Váha(kg)'] != 0)]
        valid_prijem = df[df['Příjem (kcal)'].notna() & (df['Příjem (kcal)'] != 0)]

        m1, m2 = st.columns(2)
        if not valid_vaha.empty:
            m1.metric("Posledná váha", f"{valid_vaha['Váha(kg)'].iloc[-1]} kg")
        if not valid_prijem.empty:
            m2.metric("Posledný príjem", f"{valid_prijem['Příjem (kcal)'].iloc[-1]} kcal")

        # Graf vývoja váhy (otočený pre lepšiu čitateľnosť, ak chceš)
        st.subheader("Vývoj váhy")
        # Pre istotu prevedieme váhu na čísla
        df['Váha(kg)'] = pd.to_numeric(df['Váha(kg)'], errors='coerce')
        fig = px.line(df.dropna(subset=['Váha(kg)']), x='Datum', y='Váha(kg)', 
                      markers=True, template="plotly_dark", color_discrete_sequence=['#00f2ff'])
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Zobraziť kompletné dáta"):
            st.dataframe(df)
    else:
        st.warning("Hľadám dáta v tabuľke...")

except Exception as e:
    st.error(f"Chyba: {e}")
