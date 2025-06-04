from auth import logout
import streamlit as st
import pandas as pd
import os

def painel_professor(st, os,pd):
    # Configuração da sidebar
    configurar_sidebar()
    
    # Título principal
    st.title("🔐 Painel do Professor")
    
    # Seção de visualização dos dados
    secao_visualizacao_dados(pd)
    secao_tabela_consolidada_filtrada(st, pd,path="dataset/dataSetSintetico1.csv")
    
    
    st.markdown("---")
    
    # Seção de comparação
    secao_comparacao_aluno(st, pd)
    
    st.markdown("---")
    
    # Seção de evolução do aluno
    secao_evolucao_aluno(st, pd)

def configurar_sidebar():
    """Configura a barra lateral com informações e controles"""
    st.sidebar.title("🎯 Menu de Controle")
    st.sidebar.markdown("---")
    
    # Informações do sistema
    st.sidebar.markdown("### ℹ️ Informações")
    st.sidebar.info("Sistema de Gestão Acadêmica")
    
    # Estatísticas rápidas
    if os.path.exists("dataset/dataSetSintetico.csv"):
        df = pd.read_csv("dataset/dataSetSintetico.csv")
        total_alunos = len(df)
        st.sidebar.metric("👥 Total de Alunos", total_alunos)
    
    st.sidebar.markdown("---")
    
    # Botão de logout
    if st.sidebar.button("🚪 Sair", type="primary", use_container_width=True):
        logout()


def secao_visualizacao_dados(pd):
    """Seção para visualização dos dados atuais"""
    st.header("📊 Base de Dados Atual")
    
    if os.path.exists("dataset/dataSetSintetico.csv"):
        planilhaCerta = pd.read_csv("dataset/dataSetSintetico.csv")
        
        # Informações resumidas - só contagem, sem cálculos de média para evitar erro
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total de Alunos", len(planilhaCerta))
        with col2:
            st.metric("📊 Colunas", len(planilhaCerta.columns))
        with col3:
            st.metric("📋 Registros", len(planilhaCerta))
        
      
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



def comparar_aluno_com_media(st, pd, path="dataset/dataSetSintetico.csv"):
    """Interface para comparação de aluno com média"""
    if not os.path.exists(path):
        st.error("❌ Arquivo de dados não encontrado.")
        return
    
    df = pd.read_csv(path)
    
    # Limpeza e conversão dos dados (como no código original)
    col_numericas = [
        "nota_disciplina1", "nota_disciplina2", "media_notas",
        "frequencia", "taxa_aprovacao", "tempo_permanencia",
        "total_semestres_cursados", "semestre_atual"
    ]
    
    for col in col_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Interface de seleção
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
        
        # Calcular médias
        medias = {}
        for col in col_numericas:
            if col in df.columns:
                medias[col] = df[col].mean()
        
        # Exibir resultados em containers organizados
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
        
        # Análise comparativa
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
        
        # Alerta de risco
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

    # Converter valores corretamente
    for col in ["media_notas", "frequencia", "taxa_aprovacao"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    alunos_disponiveis = sorted(df["id_aluno"].unique())
    id_aluno = st.selectbox("🎯 Selecione o ID do aluno para visualizar a evolução", alunos_disponiveis)

    dados_aluno = df[df["id_aluno"] == id_aluno].sort_values(by="semestre")

    if dados_aluno.empty:
        st.info("🔍 Nenhum dado encontrado para esse aluno.")
        return

    st.subheader(f"📈 Evolução do Aluno {id_aluno} ao Longo dos Semestres")

    # Plotagem com line_chart
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

    # Filtros interativos
    cursos = sorted(df["curso"].unique())
    semestres = sorted(df["semestre_atual"].unique())

    col1, col2 = st.columns(2)
    with col1:
        curso_selecionado = st.selectbox("🎓 Selecione o curso", options=["Todos"] + cursos)
    with col2:
        semestre_selecionado = st.selectbox("📚 Selecione o semestre", options=["Todos"] + [str(s) for s in semestres])

    # Aplicar filtros
    if curso_selecionado != "Todos":
        df = df[df["curso"] == curso_selecionado]
    if semestre_selecionado != "Todos":
        df = df[df["semestre_atual"] == int(semestre_selecionado)]

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return

    # Agrupamento por curso e semestre
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

    # Exibir tabela final com curso e semestre
    st.dataframe(df_grouped.set_index(["curso", "semestre_atual"]), use_container_width=True)


