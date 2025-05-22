import streamlit as st
from datetime import datetime
import pandas as pd
import os
from dadosMocados import USUARIOS

def registrar_acesso(usuario):
    log_path = "log_acessos.xlsx"
    novo_log = {
        "usuario": usuario,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S")
    }

    
    if os.path.exists(log_path):
        df_existente = pd.read_excel(log_path)
        df_atualizado = pd.concat([df_existente, pd.DataFrame([novo_log])], ignore_index=True)
    else:
        df_atualizado = pd.DataFrame([novo_log])

    df_atualizado.to_excel(log_path, index=False)

def login():
    st.title("🎓 Sistema Previsão de Evasão")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        for user in USUARIOS:
            if user["usuario"] == usuario and user["senha"] == senha:
                st.session_state.logado = True
                st.session_state.tipo_usuario = user["tipo"]
                registrar_acesso(usuario)
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()
                return
        st.error("Usuário ou senha incorretos.")


def logout():
    st.session_state.clear()

