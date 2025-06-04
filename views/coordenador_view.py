from auth import logout
import streamlit as st
import pandas as pd
import os
import time

def painel_coordenador(st, os, pd):
    st.title("🔐 Painel do Coordenador")

    col_form, col_upload = st.columns([2, 1])
    with col_form:
        inserir_dados_aluno()

    with col_upload:
        inserir_planilha()

    st.markdown("---")

    st.subheader("📊 Dados atuais dos alunos")
    planilhaCerta = pd.read_csv("dataset/dataSetSintetico.csv")
    st.dataframe(planilhaCerta.set_index("id_aluno"))

    comparar_aluno_com_media(st, pd)

    st.sidebar.button("🚪 Sair", on_click=logout)

def inserir_dados_aluno():
    st.header("📝 Inserir Novo Aluno")

    with st.form("form_aluno"):
        col1, col2 = st.columns([1,1])

        with col1:
            id_aluno = st.number_input("ID do Aluno", min_value=1, step=1)
            total_semestres_cursados = st.number_input("Total de Semestres Cursados", min_value=1, step=1)
            nota_disciplina1 = st.number_input("Nota Disciplina 1", min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            taxa_aprovacao = st.slider("Taxa de Aprovação", min_value=0.0, max_value=1.0, step=0.01, format="%.2f")

        with col2:
            semestre_atual = st.number_input("Semestre Atual", min_value=1, step=1)
            tempo_permanencia = st.number_input("Tempo de Permanência (semestres)", min_value=1, step=1)
            nota_disciplina2 = st.number_input("Nota Disciplina 2", min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            frequencia = st.number_input("Frequência (%)", min_value=0, max_value=100, step=1)



        media_notas = st.number_input("Média das notas", min_value=1, step=1)

        enviado = st.form_submit_button("💾 Salvar")

        if enviado:
            novo_aluno = {
                "id_aluno": id_aluno,
                "semestre_atual": semestre_atual,
                "total_semestres_cursados": total_semestres_cursados,
                "nota_disciplina1": round(nota_disciplina1, 2),
                "nota_disciplina2": round(nota_disciplina2, 2),
                "media_notas": round(media_notas, 2),
                "taxa_aprovacao": round(taxa_aprovacao, 2),
                "tempo_permanencia": tempo_permanencia,
                "frequencia": frequencia
            }
            inserir_dado_na_planilha(novo_aluno, "dataset/dataSetSintetico.csv")


def inserir_planilha():
    st.header("📁 Upload de CSV")
    st.write("Selecione um arquivo CSV para atualizar os dados.")

    os.makedirs("dataset", exist_ok=True)

    # uploaded_file = st.file_uploader("", type=["csv"])
    uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])


    if uploaded_file is not None:
        backup_path = "dataset/dataSetSintetico_backup.csv"
        file_path = os.path.join("dataset", "dataSetSintetico.csv")

        if os.path.exists(file_path):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(file_path, backup_path)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        ## ta com bug aqui , tem q fechar a caixinha la no x e dps poder adicionar aluno novo

        ##########################IGNORAR###################################
        #st.success(f"✅ Arquivo salvo com sucesso: `{file_path}`")
        # msg = st.empty()
        # msg.success("✅ Novo dado inserido com sucesso!")
        # time.sleep(2)
        # msg.empty()

        #time.sleep(2)
        #st.rerun()
        ##########################IGNORAR###################################

def inserir_dado_na_planilha(novo_aluno,path):
    df = pd.read_csv(path)
    df = pd.concat([df, pd.DataFrame([novo_aluno])], ignore_index=True)
    df.to_csv("dataset/dataSetSintetico.csv", index=False)
    ##########################IGNORAR###################################
    #st.success("✅ Novo dado inserido com sucesso!")
    #time.sleep(2)
    #st.rerun()
    ##########################IGNORAR###################################
def comparar_aluno_com_media(st, pd, path="dataset/dataSetSintetico.csv"):
    st.header("📈 Comparação do Aluno com a Média do Curso")

    df = pd.read_csv(path)

    col_numericas = [
        "nota_disciplina1", "nota_disciplina2", "media_notas",
        "frequencia", "taxa_aprovacao", "tempo_permanencia",
        "total_semestres_cursados", "semestre_atual"
    ]

    for col in col_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    id_aluno = st.number_input("Digite o ID do aluno para comparar", min_value=1, step=1)

    if st.button("Comparar"):
        if id_aluno not in df["id_aluno"].values:
            st.error("Aluno não encontrado na base de dados.")
            return

        aluno = df[df["id_aluno"] == id_aluno].iloc[0]

        medias = {
            "nota_disciplina1": df["nota_disciplina1"].mean(),
            "nota_disciplina2": df["nota_disciplina2"].mean(),
            "media_notas": df["media_notas"].mean(),
            "frequencia": df["frequencia"].mean(),
            "taxa_aprovacao": df["taxa_aprovacao"].mean(),
            "tempo_permanencia": df["tempo_permanencia"].mean(),
            "total_semestres_cursados": df["total_semestres_cursados"].mean(),
            "semestre_atual": df["semestre_atual"].mean()
        }

        st.subheader(f"Dados do aluno {id_aluno}")
        aluno_dados = aluno[col_numericas]
        aluno_dados.name = "Dados do Aluno"
        aluno_df = pd.DataFrame({
            "Métricas": aluno_dados.index,
            "Valores do Aluno": aluno_dados.values
        })
        st.table(aluno_df.set_index("Métricas"))

        st.subheader("Médias da Curso")
        st.write(medias)

        st.subheader("Comparação")
        comparacao = {}
        abaixo_da_media = []
        for chave, media_valor in medias.items():
            valor_aluno = aluno[chave]
            diferenca = valor_aluno - media_valor
            situacao = "Acima da média" if diferenca > 0 else ("Normal" if diferenca == 0 else "Abaixo da média")
            comparacao[chave] = {
                "Valor Aluno": valor_aluno,
                "Média Curso": round(media_valor, 2),
                "Diferença": round(diferenca, 2),
                "Situação": situacao
            }
            if situacao == "Abaixo da média":
                abaixo_da_media.append(chave)

        comparacao_df = pd.DataFrame(comparacao).T
        comparacao_df.index.name = 'Métricas'
        st.table(comparacao_df)

        if len(abaixo_da_media) >= 4:
            atributos_str = ", ".join(abaixo_da_media)
            st.warning(
                f"⚠️ Alerta: O aluno apresenta desempenho abaixo da média nos seguintes parâmetros de possível evasão: {atributos_str}. Recomenda-se acompanhamento, pois pode haver risco de evasão.")
        else:
            st.info("Aluno com desempenho satisfatório ou risco baixo de evasão baseado nas métricas atuais.")

