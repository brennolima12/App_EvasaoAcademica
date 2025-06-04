from auth import logout
import streamlit as st
import pandas as pd
import os
import time

def painel_coordenador(st, os, pd):
    configurar_sidebar()
    st.title("🔐 Painel do Coordenador")

    secao_insercao_dados()
    st.markdown("---")

    secao_visualizacao_dados(pd)
    st.markdown("---")

    secao_tabela_consolidada_filtrada(st, pd, path="dataset/dataSetSintetico1.csv")
    st.markdown("---")

    secao_comparacao_aluno(st, pd)
    st.markdown("---")

    secao_dashboard_individual(st, pd)
    st.markdown("---")

    secao_evolucao_aluno(st, pd)
    st.markdown("---")

    st.markdown("---")
    identificar_alunos_em_risco(st, pd)
def configurar_sidebar():
    """Configura a barra lateral com informações e controles"""
    st.sidebar.title("🎯 Menu de Controle")
    st.sidebar.markdown("---")

    st.sidebar.markdown("### ℹ️ Informações")
    st.sidebar.info("Sistema de Gestão Acadêmica")

    if os.path.exists("dataset/dataSetSintetico.csv"):
        df = pd.read_csv("dataset/dataSetSintetico.csv")
        total_alunos = len(df)
        st.sidebar.metric("👥 Total de Alunos", total_alunos)

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Sair", type="primary", use_container_width=True):
        logout()


def secao_insercao_dados():
    """Seção organizada para inserção de dados"""
    st.header("📝 Gerenciamento de Dados")

    tab_manual, tab_upload = st.tabs(["➕ Inserir Aluno", "📁 Upload CSV"])

    with tab_manual:
        inserir_dados_aluno()

    with tab_upload:
        inserir_planilha()


def secao_visualizacao_dados(pd):
    """Seção para visualização dos dados atuais"""
    st.header("📊 Base de Dados Atual")

    if os.path.exists("dataset/dataSetSintetico.csv"):
        planilhaCerta = pd.read_csv("dataset/dataSetSintetico.csv")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total de Alunos", len(planilhaCerta))
        with col2:
            st.metric("📊 Colunas", len(planilhaCerta.columns))
        with col3:
            st.metric("📋 Registros", len(planilhaCerta))

        # Tabela de dados
        # st.subheader("📋 Dados Detalhados")
        # st.dataframe(
        #    planilhaCerta.set_index("id_aluno"),
        #   use_container_width=True,
        #  height=400
        # )
    else:
        st.warning("⚠️ Nenhum arquivo de dados encontrado.")


def secao_evolucao_aluno(st, pd):
    """Seção para visualização da evolução do aluno"""
    st.header("📈 Evolução Acadêmica")

    with st.expander("🎯 Acompanhar Evolução do Aluno", expanded=False):
        mostrar_evolucao_aluno(st, pd)


def secao_comparacao_aluno(st, pd):
    """Seção para comparação de alunos"""
    st.header("📈 Análise Individual")

    with st.expander("🔍 Comparar Aluno com Média do Curso", expanded=False):
        comparar_aluno_com_media(st, pd)


def inserir_dados_aluno():
    """Interface organizada para inserção de dados de aluno"""
    st.subheader("✏️ Cadastrar Novo Aluno")

    with st.form("form_aluno"):
        st.markdown("**📋 Informações Básicas**")
        col1, col2 = st.columns(2)

        with col1:
            id_aluno = st.number_input("🆔 ID do Aluno", min_value=1, step=1)
            semestre_atual = st.number_input("📚 Semestre Atual", min_value=1, step=1)
            total_semestres_cursados = st.number_input("⏱️ Total de Semestres Cursados", min_value=1, step=1)

        with col2:
            tempo_permanencia = st.number_input("🕐 Tempo de Permanência (semestres)", min_value=1, step=1)
            frequencia = st.number_input("📅 Frequência (%)", min_value=0, max_value=100, step=1)
            taxa_aprovacao = st.slider("✅ Taxa de Aprovação", min_value=0.0, max_value=1.0, step=0.01, format="%.2f")

        st.markdown("---")
        st.markdown("**📊 Desempenho Acadêmico**")
        col3, col4, col5 = st.columns(3)

        with col3:
            nota_disciplina1 = st.number_input("📝 Nota Disciplina 1", min_value=0.0, max_value=10.0, step=0.1,
                                               format="%.2f")
        with col4:
            nota_disciplina2 = st.number_input("📝 Nota Disciplina 2", min_value=0.0, max_value=10.0, step=0.1,
                                               format="%.2f")
        with col5:
            media_notas = st.number_input("📈 Média das Notas", min_value=0.0, max_value=10.0, step=0.1, format="%.2f")

        st.markdown("---")
        enviado = st.form_submit_button("💾 Salvar Aluno", type="primary", use_container_width=True)

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
            st.success("✅ Aluno cadastrado com sucesso!")
            time.sleep(1)
            st.rerun()


def inserir_planilha():
    """Interface para upload de planilha"""
    st.subheader("📤 Importar Dados via CSV")

    os.makedirs("dataset", exist_ok=True)

    with st.expander("ℹ️ Formato do arquivo CSV"):
        st.markdown("""
        **Colunas necessárias:**
        - id_aluno
        - semestre_atual  
        - total_semestres_cursados
        - nota_disciplina1
        - nota_disciplina2
        - media_notas
        - taxa_aprovacao
        - tempo_permanencia
        - frequencia
        """)

    uploaded_file = st.file_uploader(
        "Selecione um arquivo CSV",
        type=["csv"],
        help="Arquivo CSV com os dados dos alunos"
    )

    if uploaded_file is not None:
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.subheader("👀 Preview do Arquivo")
            st.dataframe(preview_df.head(), use_container_width=True)

            if st.button("📥 Confirmar Import", type="primary"):
                backup_path = "dataset/dataSetSintetico_backup.csv"
                file_path = os.path.join("dataset", "dataSetSintetico.csv")

                if os.path.exists(file_path):
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(file_path, backup_path)
                    st.info("🔄 Backup do arquivo anterior criado")

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.success(f"✅ Arquivo importado com sucesso!")
                time.sleep(1)
                st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {str(e)}")


def inserir_dado_na_planilha(novo_aluno, path):
    """Insere um novo aluno na planilha"""
    try:
        df = pd.read_csv(path)
        df = pd.concat([df, pd.DataFrame([novo_aluno])], ignore_index=True)
        df.to_csv("dataset/dataSetSintetico.csv", index=False)
    except FileNotFoundError:
        df = pd.DataFrame([novo_aluno])
        df.to_csv("dataset/dataSetSintetico.csv", index=False)


def comparar_aluno_com_media(st, pd, path="dataset/dataSetSintetico.csv"):
    """Interface para comparação de aluno com média"""
    if not os.path.exists(path):
        st.error("❌ Arquivo de dados não encontrado.")
        return

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

    col_select, col_button = st.columns([3, 1])

    with col_select:
        id_aluno = st.selectbox(
            "🎯 Selecione o ID do aluno",
            options=sorted(df["id_aluno"].unique()),
            help="Escolha o aluno para comparar com a média"
        )

    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
        comparar = st.button("📊 Comparar", type="primary")

    if comparar:
        if id_aluno not in df["id_aluno"].values:
            st.error("❌ Aluno não encontrado na base de dados.")
            return

        aluno = df[df["id_aluno"] == id_aluno].iloc[0]

        medias = {}
        for col in col_numericas:
            if col in df.columns:
                medias[col] = df[col].mean()

        col_dados, col_medias = st.columns(2)

        with col_dados:
            st.subheader(f"👤 Dados do Aluno {id_aluno}")
            aluno_dados = aluno[col_numericas]
            aluno_df = pd.DataFrame({
                "Métrica": [col.replace('_', ' ').title() for col in aluno_dados.index],
                "Valor": [f"{val:.2f}" if isinstance(val, (int, float)) else str(val) for val in aluno_dados.values]
            })
            st.dataframe(aluno_df, hide_index=True, use_container_width=True)

        with col_medias:
            st.subheader("📊 Médias do Curso")
            medias_df = pd.DataFrame({
                "Métrica": [col.replace('_', ' ').title() for col in medias.keys()],
                "Média": [f"{val:.2f}" for val in medias.values()]
            })
            st.dataframe(medias_df, hide_index=True, use_container_width=True)

        st.subheader("🔍 Análise Comparativa")

        comparacao = {}
        abaixo_da_media = []

        for chave, media_valor in medias.items():
            valor_aluno = aluno[chave]
            diferenca = valor_aluno - media_valor

            if diferenca > 0:
                situacao = "🟢 Acima da média"
            elif diferenca == 0:
                situacao = "🟡 Na média"
            else:
                situacao = "🔴 Abaixo da média"
                abaixo_da_media.append(chave.replace('_', ' ').title())

            comparacao[chave.replace('_', ' ').title()] = {
                "Aluno": f"{valor_aluno:.2f}",
                "Média": f"{media_valor:.2f}",
                "Diferença": f"{diferenca:+.2f}",
                "Status": situacao
            }

        comparacao_df = pd.DataFrame(comparacao).T
        st.dataframe(comparacao_df, use_container_width=True)

        if len(abaixo_da_media) >= 4:
            st.error(
                f"⚠️ **ALERTA DE RISCO DE EVASÃO**\n\n"
                f"O aluno apresenta desempenho abaixo da média em {len(abaixo_da_media)} métricas: "
                f"{', '.join(abaixo_da_media)}.\n\n"
                f"**Recomendação:** Acompanhamento prioritário e ações de retenção."
            )
        elif len(abaixo_da_media) >= 2:
            st.warning(
                f"⚠️ **Atenção:** O aluno está abaixo da média em {len(abaixo_da_media)} métricas. "
                f"Recomenda-se monitoramento."
            )
        else:
            st.success("✅ **Situação Satisfatória:** Aluno com baixo risco de evasão baseado nas métricas atuais.")


def mostrar_evolucao_aluno(st, pd, path="dataset/historico_aluno.csv"):
    if not os.path.exists(path):
        st.warning("⚠️ Histórico de alunos não encontrado.")
        return

    df = pd.read_csv(path)

    for col in ["media_notas", "frequencia", "taxa_aprovacao"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    alunos_disponiveis = sorted(df["id_aluno"].unique())
    id_aluno = st.selectbox("🎯 Selecione o ID do aluno para visualizar a evolução", alunos_disponiveis)

    dados_aluno = df[df["id_aluno"] == id_aluno].sort_values(by="semestre")

    if dados_aluno.empty:
        st.info("🔍 Nenhum dado encontrado para esse aluno.")
        return

    st.subheader(f"📈 Evolução do Aluno {id_aluno} ao Longo dos Semestres")

    st.line_chart(
        data=dados_aluno.set_index("semestre")[["media_notas", "frequencia", "taxa_aprovacao"]],
        use_container_width=True,
        height=400
    )


def secao_tabela_consolidada_filtrada(st, pd, path="dataset/dataSetSintetico1.csv"):
    st.header("📋 Dados Consolidados por Semestre")

    if not os.path.exists(path):
        st.warning("⚠️ Arquivo de dados não encontrado.")
        return

    df = pd.read_csv(path)

    cursos = sorted(df["curso"].unique())
    semestres = sorted(df["semestre_atual"].unique())

    col1, col2 = st.columns(2)
    with col1:
        curso_selecionado = st.selectbox("🎓 Selecione o curso", options=["Todos"] + cursos)
    with col2:
        semestre_selecionado = st.selectbox("📚 Selecione o semestre", options=["Todos"] + [str(s) for s in semestres])

    if curso_selecionado != "Todos":
        df = df[df["curso"] == curso_selecionado]
    if semestre_selecionado != "Todos":
        df = df[df["semestre_atual"] == int(semestre_selecionado)]

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return

    df_grouped = df.groupby(["curso", "semestre_atual"]).agg({
        "id_aluno": "count",
        "media_notas": "mean",
        "frequencia": "mean",
        "taxa_aprovacao": "mean"
    }).reset_index()

    df_grouped = df_grouped.rename(columns={
        "id_aluno": "Total de Alunos",
        "media_notas": "Média das Notas",
        "frequencia": "Frequência Média (%)",
        "taxa_aprovacao": "Taxa de Aprovação Média"
    })

    st.dataframe(df_grouped.set_index(["curso", "semestre_atual"]), use_container_width=True)

def exibir_dashboard_individual(st, pd, path="dataset/dataSetSintetico.csv"):
    import plotly.graph_objects as go
    import os

    if not os.path.exists(path):
        st.error("❌ Arquivo de dados não encontrado.")
        return

    df = pd.read_csv(path)

    metricas_notas = ["nota_disciplina1", "nota_disciplina2", "media_notas"]
    metricas_frequencia = ["frequencia"]
    metricas_aprovacao = ["taxa_aprovacao"]

    todas_metricas = metricas_notas + metricas_frequencia + metricas_aprovacao

    for col in todas_metricas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=todas_metricas, how='any')

    if df.empty:
        st.warning("⚠️ Nenhum dado válido disponível para gerar gráfico.")
        return

    if "nome_aluno" in df.columns:
        df["label"] = df["nome_aluno"] + " (ID " + df["id_aluno"].astype(str) + ")"
        aluno_label = st.selectbox("📌 Selecione o aluno", options=df["label"].tolist())
        id_aluno = int(aluno_label.split("ID ")[-1].replace(")", ""))
    else:
        id_aluno = st.selectbox("📌 Escolha o aluno", options=df["id_aluno"].dropna().unique())

    if id_aluno not in df["id_aluno"].values:
        st.warning("Aluno não encontrado na base.")
        return

    aluno = df[df["id_aluno"] == id_aluno].iloc[0]
    media_geral = df[todas_metricas].mean(numeric_only=True)

    st.subheader(f"📊 Comparativo Gráfico - Aluno {id_aluno}")

    fig_notas = go.Figure([
        go.Bar(name='Aluno', x=metricas_notas, y=aluno[metricas_notas].values),
        go.Bar(name='Média Geral', x=metricas_notas, y=media_geral[metricas_notas].values)
    ])
    fig_notas.update_layout(barmode='group', title='Notas', height=300)
    st.plotly_chart(fig_notas, use_container_width=True)

    fig_freq = go.Figure([
        go.Bar(name='Aluno', x=metricas_frequencia, y=aluno[metricas_frequencia].values),
        go.Bar(name='Média Geral', x=metricas_frequencia, y=media_geral[metricas_frequencia].values)
    ])
    fig_freq.update_layout(barmode='group', title='Frequência (%)', height=250)
    st.plotly_chart(fig_freq, use_container_width=True)

    fig_aprov = go.Figure([
        go.Bar(name='Aluno', x=metricas_aprovacao, y=aluno[metricas_aprovacao].values),
        go.Bar(name='Média Geral', x=metricas_aprovacao, y=media_geral[metricas_aprovacao].values)
    ])
    fig_aprov.update_layout(barmode='group', title='Taxa de Aprovação', height=250)
    st.plotly_chart(fig_aprov, use_container_width=True)

def secao_dashboard_individual(st, pd):
    """Dashboard visual com gráficos para aluno individual"""
    st.header("📊 Painel Gráfico de Desempenho Individual")
    with st.expander("📈 Visualizar Gráficos de Desempenho", expanded=False):
        exibir_dashboard_individual(st, pd)

def identificar_alunos_em_risco(st, pd, path="dataset/dataSetSintetico.csv"):
    st.header("🚨 Identificação de Alunos em Risco de Evasão")

    if not os.path.exists(path):
        st.error("❌ Arquivo de dados não encontrado.")
        return

    df = pd.read_csv(path)

    metricas = [
        "nota_disciplina1", "nota_disciplina2", "media_notas",
        "frequencia", "taxa_aprovacao", "tempo_permanencia",
        "total_semestres_cursados", "semestre_atual"
    ]

    for col in metricas:
        df[col] = df[col].astype(str).str.replace(',', '.').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=metricas)

    if df.empty:
        st.warning("⚠️ Nenhum dado válido disponível.")
        return

    medias_gerais = df[metricas].mean()

    alunos_em_risco = []

    for _, row in df.iterrows():
        abaixo = []
        for m in metricas:
            if row[m] < medias_gerais[m]:
                abaixo.append(m)
        if len(abaixo) >= 2:
            nivel = "⚠️ Alerta Crítico" if len(abaixo) >= 4 else "🔎 Acompanhamento"
            alunos_em_risco.append({
                "ID": int(row["id_aluno"]),
                "Nome": row["nome_aluno"] if "nome_aluno" in df.columns else f"Aluno {int(row['id_aluno'])}",
                "Nº de Métricas Abaixo": len(abaixo),
                "Métricas Abaixo da Média": ", ".join([m.replace("_", " ").title() for m in abaixo]),
                "Nível de Alerta": nivel
            })

    if not alunos_em_risco:
        st.success("✅ Nenhum aluno em risco de evasão identificado com as métricas atuais.")
        return

    resultado_df = pd.DataFrame(alunos_em_risco)

    tipo_alerta = st.radio("Selecione o tipo de risco:", ["⚠️ Alerta Crítico", "🔎 Acompanhamento"], horizontal=True)

    filtrado = resultado_df[resultado_df["Nível de Alerta"] == tipo_alerta]

    if filtrado.empty:
        st.info("Nenhum aluno com esse nível de risco.")
    else:
        st.dataframe(filtrado, hide_index=True, use_container_width=True)
