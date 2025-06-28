import streamlit as st
from views.coordenador_view import painel_coordenador
from views.professor_view import painel_professor
from auth import login, logout

st.set_page_config(page_title="Dashboard Acompanhamento Acadêmico", layout="wide")

def main():
    st.sidebar.image("assets/logo_upe.png", use_container_width=True)

    if "logado" not in st.session_state:
        st.session_state.logado = False

    if not st.session_state.logado:
        login()
    else:
        if st.session_state.tipo_usuario == "coordenador":
            painel_coordenador()
        elif st.session_state.tipo_usuario == "professor":
            painel_professor()
        else:
            st.error("Tipo de usuário desconhecido.")
            logout()

if __name__ == "__main__":
    main()
