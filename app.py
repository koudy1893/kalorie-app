import streamlit as st
import pandas as pd
import plotly.express as px

# Nastavení vzhledu
st.set_page_config(page_title="Moje Kalorické Tabulky", layout="wide")

st.title("🍎 Kalorické Tabulky V2")

# Simulace propojení s Google Sheets (v reálu použijeme st.connection)
# Pro začátek vytvoříme testovací data
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Datum', 'Jídlo', 'Kalorie', 'Bílkoviny', 'Sacharidy', 'Tuky'])

# Boční panel pro zadávání dat
st.sidebar.header("Přidat nové jídlo")
with st.sidebar.form("add_form", clear_on_submit=True):
    date = st.date_input("Datum")
    food = st.text_input("Název jídla")
    kcal = st.number_input("Kalorie (kcal)", min_value=0)
    prot = st.number_input("Bílkoviny (g)", min_value=0)
    carb = st.number_input("Sacharidy (g)", min_value=0)
    fat = st.number_input("Tuky (g)", min_value=0)
    submit = st.form_submit_button("Uložit do tabulky")

    if submit:
        new_row = {'Datum': date, 'Jídlo': food, 'Kalorie': kcal, 'Bílkoviny': prot, 'Sacharidy': carb, 'Tuky': fat}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Uloženo!")

# Hlavní přehled
col1, col2, col3 = st.columns(3)
total_kcal = st.session_state.data['Kalorie'].sum()
col1.metric("Celkem Kalorie", f"{total_kcal} kcal")
col2.metric("Bílkoviny celkem", f"{st.session_state.data['Bílkoviny'].sum()} g")
col3.metric("Počet záznamů", len(st.session_state.data))

# Grafy
st.subheader("Vizualizace příjmu")
if not st.session_state.data.empty:
    fig = px.bar(st.session_state.data, x='Datum', y='Kalorie', color='Jídlo', title="Kalorie podle dní")
    st.plotly_chart(fig, use_container_width=True)

# Tabulka dat
st.subheader("Detailní záznamy")
st.dataframe(st.session_state.data, use_container_width=True)