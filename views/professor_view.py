from dadosMocados import dados_alunos
from auth import logout
def painel_professor(st,pd):
    st.title("📘 Painel do Professor")

    st.subheader("📊 Indicadores dos Alunos")
    df = pd.DataFrame(dados_alunos)

    st.dataframe(df)
    st.bar_chart(df.set_index("nome")[["nota"]])
    st.line_chart(df.set_index("nome")[["frequencia"]])

    st.sidebar.button("Sair", on_click=logout)

