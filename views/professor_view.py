
from auth import logout

import streamlit as st
import pandas as pd
def painel_professor():
    st.title("📘 Painel do Professor")

    st.subheader("📊 Indicadores dos Alunos")
    
    df = pd.DataFrame(pd.read_csv("dataset/dataSetSintetico.csv"))

    st.dataframe(df.set_index("id_aluno"))
    st.bar_chart(df.set_index("id_aluno")[["frequencia"]])
    # Corrigir vírgulas e converter para float
    df["media_notas"] = df["media_notas"].astype(str).str.replace(",", ".", regex=False).astype(float)
    df["frequencia"] = df["frequencia"].astype(str).str.replace(",", ".", regex=False).astype(float)

    st.line_chart(df.set_index("id_aluno")[["frequencia", "media_notas"]])


    #st.sidebar.button("HOME", on_click=painel_professor)
    st.sidebar.button("dashboard")
    st.sidebar.button("Sair", on_click=logout)


# def dash():
#     st.title("Dashboard")
#     st.write("Aqui você pode visualizar os dados dos alunos.")

#     st.sidebar.button("Voltar", on_click=painel_professor)