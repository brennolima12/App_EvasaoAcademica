from dadosMocados import dados_alunos
from auth import logout
def painel_coordenador(st,os,pd):
    st.title("🔐 Painel do Coordenador")
    


    st.subheader("📁 Enviar CSV para o Sistema")
    os.makedirs("dataset", exist_ok=True)

    uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])

    if uploaded_file is not None:
        file_path = os.path.join("dataset", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Arquivo salvo com sucesso na pasta: {file_path}")
    
    st.subheader("📊 Dados atuais dos alunos")
    df = pd.DataFrame(dados_alunos)
    st.dataframe(df)


    st.sidebar.button("Sair", on_click=logout)

