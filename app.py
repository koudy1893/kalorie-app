import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalorická Appka - Lukáš", layout="wide")
st.title("🍎 Kalorické Tabulky: Lukáš")

# Upravený odkaz s gid=0 (pro první list)
URL = "https://docs.google.com/spreadsheets/d/1-2iZnGaecjr2scBPQPETz4M6Ymw9B8NjaFM0cafouqE/export?format=csv&gid=0"

try:
    # 1. Načteme data "nanečisto" bez hlavičky
    raw_df = pd.read_csv(URL, header=None)
    
    # 2. Najdeme řádek, kde se poprvé vyskytuje slovo "Datum"
    header_row = None
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('Datum').any():
            header_row = i
            break
            
    if header_row is not None:
        # 3. Načteme tabulku znovu, ale tentokrát přeskočíme prázdné řádky nad hlavičkou
        df = pd.read_csv(URL, skiprows=header_row)
        
        # Vyčistíme názvy sloupců (odstraníme mezery na začátku/konci)
        df.columns = [c.strip() for c in df.columns]
        
        # Odstraníme úplně prázdné řádky
        df = df.dropna(subset=['Datum'])

        # --- ZOBRAZENÍ ---
        # Definujeme názvy (zkusíme najít nejpodobnější, pokud by se jmenovaly trochu jinak)
        def get_col(options):
            for opt in options:
                for col in df.columns:
                    if opt.lower() in col.lower(): return col
            return None

        vaha_col = get_col(['Váha', 'Vaha'])
        prijem_col = get_col(['Příjem', 'Prijem', 'kcal'])
        deficit_col = get_col(['Deficit'])
        kroky_col = get_col(['Kroky', 'Step'])

        st.subheader("Dnešní přehled")
        m1, m2, m3 = st.columns(3)
        
        if vaha_col:
            vaha = df[vaha_col].dropna().iloc[-1]
            m1.metric("Aktuální váha", f"{vaha} kg")
        
        if prijem_col:
            prijem = df[prijem_col].dropna().iloc[-1]
            m2.metric("Naposledy snědeno", f"{prijem} kcal")
            
        if deficit_col:
            def_avg = df[deficit_col].mean()
            m3.metric("Průměrný deficit", f"{def_avg:.0f} kcal")

        # Graf
        if vaha_col:
            st.divider()
            st.subheader("Vývoj váhy")
            fig = px.line(df, x='Datum', y=vaha_col, markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("Zobrazit celá data"):
            st.dataframe(df)
            
    else:
        st.error("V tabulce jsem nenašel sloupec 'Datum'.")
        st.write("Takhle vypadá začátek tvé tabulky, jak ho vidí Python:")
        st.table(raw_df.head(5))

except Exception as e:
    st.error(f"Chyba: {e}")