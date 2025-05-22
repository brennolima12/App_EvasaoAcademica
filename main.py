import streamlit as st
import pandas as pd
import os
from  views.coordenador_view import painel_coordenador 
from auth import login,logout
from views.professor_view import painel_professor


def main():
    st.set_page_config(page_title="DashBoard Acompanhamento Academico", layout="wide")
    st.logo(image="assets/logo_upe.png", 
        icon_image="assets/logo_upe.png")
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if not st.session_state.logado:
        login()
    else:
        if st.session_state.tipo_usuario == "coordenador":
            painel_coordenador(st,os,pd)
        elif st.session_state.tipo_usuario == "professor":
            painel_professor(st,pd)
        else:
            st.error("Tipo de usuário desconhecido.")
            logout()


if __name__ == "__main__":
    main()
