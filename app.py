import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from datetime import datetime

# 1. Nastavení stránky
st.set_page_config(page_title="Kalorie Lukáš", layout="wide")

# 2. Funkce pro autorizaci do Google Sheets (používá tvoje Secrets)
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

# --- SIDEBAR: FORMULÁŘ PRO ZÁPIS ---
with st.sidebar:
    st.header("📝 Přidat nový den")
    with st.form("add_form", clear_on_submit=True):
        new_date = st.date_input("Datum", datetime.now()).strftime('%d.%m.%Y')
        new_weight = st.number_input("Váha (kg)", step=0.1, format="%.1f")
        new_prijem = st.number_input("Příjem (kcal)", step=10)
        new_steps = st.number_input("Kroky", step=100)
        submit = st.form_submit_button("Uložit do tabulky")

    if submit:
        try:
            client = get_gsheet_client()
            # Otevře tabulku podle ID
            sh = client.open_by_key("1-2iZnGaecjr2scBPQPETz4M6Ymw9B8NjaFM0cafouqE")
            worksheet = sh.worksheet("Lukáš")
            
            # ZDE ZKONTROLUJ POŘADÍ SLOUPCŮ! 
            # Pokud máš v tabulce nejdřív Datum, pak Váhu, pak Příjem a pak Kroky, je to takto:
            worksheet.append_row([new_date, new_weight, new_prijem, new_steps])
            
            st.success("Data byla úspěšně uložena do Google Sheets!")
            st.balloons() # Malá oslava
            st.cache_data.clear() # Smaže stará data, aby se hned načetla nová
        except Exception as e:
            st.error(f"Chyba při zápisu: {e}")

# --- HLAVNÍ STRÁNKA: DASHBOARD ---
st.title("🍎 Kalorické Tabulky: Lukáš")

# Použijeme odkaz pro čtení (nejrychlejší způsob)
URL_CSV = "https://docs.google.com/spreadsheets/d/1-2iZnGaecjr2scBPQPETz4M6Ymw9B8NjaFM0cafouqE/export?format=csv&gid=0"

try:
    # Inteligentní načtení dat (najde řádek Datum)
    raw_df = pd.read_csv(URL_CSV, header=None)
    header_row = None
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('Datum').any():
            header_row = i
            break
    
    if header_row is not None:
        df = pd.read_csv(URL_CSV, skiprows=header_row)
        df.columns = [c.strip() for c in df.columns]
        df = df.dropna(subset=['Datum'])

        # Metriky
        m1, m2 = st.columns(2)
        vaha_col = 'Váha(kg)' # Uprav podle potřeby
        prijem_col = 'Příjem (kcal)'
        
        if vaha_col in df.columns:
            m1.metric("Poslední váha", f"{df[vaha_col].iloc[-1]} kg")
        if prijem_col in df.columns:
            m2.metric("Poslední příjem", f"{df[prijem_col].iloc[-1]} kcal")

        # Graf
        st.subheader("Vývoj váhy")
        fig = px.line(df, x='Datum', y=vaha_col, markers=True, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Zobrazit kompletní data"):
            st.dataframe(df)
    else:
        st.warning("Čekám na data z tabulky...")

except Exception as e:
    st.error(f"Chyba při načítání: {e}")
