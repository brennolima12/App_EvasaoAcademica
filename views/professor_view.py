import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from auth import logout
from utils.relatorios_professor import gerar_pdf_risco_alunos

# ================== Função Principal ==================
def painel_professor():
    
    configurar_sidebar()

    st.title("📘 Painel do Professor")

    path_base = "dataset/dataSetSintetico.csv"
    if not os.path.exists(path_base):
        st.warning("⚠️ Nenhuma base oficial disponível. Aguarde o coordenador salvar uma análise.")
        return

    df = pd.read_csv(path_base)
    nome_base = os.path.basename(path_base)
    st.info(f"📂 Base oficial em uso: `{nome_base}` com {len(df)} aluno(s)")

    tab1, tab2, tab3 = st.tabs([
        "📋 Dados Consolidados",
        "📊 Desempenho Individual",
        "🚨 Alunos em Risco"
    ])

    with tab1:
        exibir_consolidados(df)

    with tab2:
        exibir_dashboard(df)

    with tab3:
        identificar_alunos_em_risco(df)

# ================== Sidebar ==================
def configurar_sidebar():
    st.sidebar.title("🎯 Menu de Controle")
    st.sidebar.markdown("Sistema de Gestão Acadêmica")

    path = "dataset/dataSetSintetico.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        st.sidebar.metric("👥 Total de Alunos", len(df))
    else:
        st.sidebar.info("Base oficial ainda não disponível.")

    if st.sidebar.button("🚪 Sair", type="primary", use_container_width=True):
        logout()

# ================== TAB 1 — Consolidados + Análises Gerais ==================
def exibir_consolidados(df):
    st.header("📋 Consolidados por Semestre")

    if "semestre_atual" not in df.columns:
        st.info("A coluna 'semestre_atual' não existe nesta base.")
        return

    semestres = sorted(df["semestre_atual"].dropna().unique())
    semestre = st.selectbox("📚 Semestre", ["Todos"] + [str(s) for s in semestres])

    if semestre != "Todos":
        df = df[df["semestre_atual"] == int(semestre)]

    if df.empty:
        st.warning("Sem registros disponíveis.")
        return

    resumo = df.groupby("semestre_atual").agg({
        "id_aluno": "count",
        "media_notas": "mean",
        "frequencia": "mean",
        "taxa_aprovacao": "mean",
        "Probabilidade": "mean"
    }).reset_index()

    resumo.columns = ["Semestre", "Total de Alunos", "Média das Notas", "Frequência Média (%)", "Taxa de Aprovação Média", "Probabilidade de Evasão"]
    st.dataframe(resumo.set_index("Semestre"), use_container_width=True)

# ================== TAB 2 — Desempenho Individual ==================
def exibir_dashboard(df):
    st.header("📊 Análise Gráfica de Desempenho")

    metricas = ["media_notas", "frequencia", "taxa_aprovacao"]
    for m in metricas:
        df[m] = pd.to_numeric(df[m], errors="coerce")
    df.dropna(subset=metricas, inplace=True)

    if df.empty:
        st.warning("Sem dados numéricos disponíveis para análise.")
        return

    id_aluno = st.selectbox("👤 Selecione o aluno", sorted(df["id_aluno"].unique()))
    aluno = df[df["id_aluno"] == id_aluno].iloc[0]
    media_geral = df[metricas].mean()

    col1, col2 = st.columns(2)

    # Radar Chart
    with col1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[aluno[m] for m in metricas], theta=metricas, fill='toself', name='Aluno'))
        fig_radar.add_trace(go.Scatterpolar(r=[media_geral[m] for m in metricas], theta=metricas, fill='toself', name='Média'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

    # Mostrar situação de risco e ação sugerida
    if "Probabilidade" in aluno and "Nível de Risco" in aluno:
        risco = aluno["Nível de Risco"]
        prob = round(aluno["Probabilidade"] * 100, 1)
        st.markdown(f"### 🎯 Situação Atual: {risco} ({prob}%)")

        if risco == "🔴 Alto":
            st.error("Recomendação: Encaminhar para tutoria ou contato com coordenação.")
        elif risco == "🟠 Médio":
            st.warning("Recomendação: Acompanhar de perto nos próximos meses.")
        else:
            st.success("Recomendação: Manter acompanhamento regular.")

    # Dispersão Risco x Frequência
    with col2:
        st.markdown("#### 🔎 Frequência x Risco de Evasão")
        if "Probabilidade" in df.columns:
            fig_disp = px.scatter(df, x="frequencia", y="Probabilidade", color="Probabilidade",
                                  color_continuous_scale="RdYlBu", title="Relação entre Frequência e Risco")
            st.plotly_chart(fig_disp, use_container_width=True)
        else:
            st.info("Coluna 'Probabilidade' não encontrada.")

# ================== TAB 3 — Alunos em Risco ==================
def identificar_alunos_em_risco(df):
    st.header("🚨 Análise por Nível de Risco de Evasão")

    if "Nível de Risco" not in df.columns or "Probabilidade" not in df.columns:
        st.warning("A base precisa conter as colunas 'Nível de Risco' e 'Probabilidade'.")
        return

    niveis_padrao = ["🟢 Baixo", "🟠 Médio", "🔴 Alto"]
    niveis = [n for n in niveis_padrao if n in df["Nível de Risco"].unique()]

    if not niveis:
        st.info("Nenhum aluno categorizado por nível de risco.")
        return

    nivel_escolhido = st.radio("🎯 Selecione o nível de risco:", niveis, horizontal=True)
    filtrado = df[df["Nível de Risco"] == nivel_escolhido].copy()

    if filtrado.empty:
        st.info("Nenhum aluno nesse nível de risco.")
        return

    st.markdown(f"**👥 Total de alunos com risco {nivel_escolhido}:** {len(filtrado)}")

    # Gráfico de pizza com proporção de alunos por risco
    st.markdown("### 📊 Distribuição Geral por Nível de Risco")
    dist_risco = df["Nível de Risco"].value_counts().reset_index()
    dist_risco.columns = ["Nível de Risco", "Total de Alunos"]
    fig_pie = px.pie(dist_risco, names="Nível de Risco", values="Total de Alunos",
                    color="Nível de Risco",
                    color_discrete_map={"🟢 Baixo": "green", "🟠 Médio": "orange", "🔴 Alto": "red"},
                    title="Distribuição dos Alunos por Nível de Risco")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### 🔍 Dispersão: Média das Notas x Probabilidade de Evasão")
    if "media_notas" in df.columns and "Probabilidade" in df.columns:
        fig_disp = px.scatter(
            df,
            x="media_notas",
            y="Probabilidade",
            color="Nível de Risco",
            hover_data=["id_aluno", "frequencia", "taxa_aprovacao"],
            color_discrete_map={"🟢 Baixo": "green", "🟠 Médio": "orange", "🔴 Alto": "red"},
            title="Dispersão de Alunos por Nota Média e Risco"
        )
        st.plotly_chart(fig_disp, use_container_width=True)
        
    st.markdown("### 📈 Dispersão: Frequência x Probabilidade no grupo selecionado")
    if "frequencia" in filtrado.columns and "Probabilidade" in filtrado.columns:
        fig_disp = px.scatter(
            filtrado,
            x="frequencia",
            y="Probabilidade",
            color="Nível de Risco",
            size="media_notas" if "media_notas" in filtrado.columns else None,
            hover_data=["id_aluno", "media_notas", "frequencia", "taxa_aprovacao"],
            color_discrete_map={"🔴 Alto": "red", "🟠 Médio": "orange", "🟢 Baixo": "green"},
            title="Risco por Frequência e Desempenho no Grupo Selecionado"
        )
        fig_disp.update_layout(height=400)
        st.plotly_chart(fig_disp, use_container_width=True)
    else:
        st.info("Colunas 'frequencia' e/ou 'Probabilidade' ausentes.")


    filtrado.loc[:, "Probabilidade (%)"] = (filtrado["Probabilidade"] * 100).round(1)
    filtrado.loc[:, "Situação Sugerida"] = filtrado["Nível de Risco"].map({
        "🔴 Alto": "Encaminhar para tutoria urgente",
        "🟠 Médio": "Acompanhar de perto com professor tutor",
        "🟢 Baixo": "Manter acompanhamento regular"
    })

    tabela = filtrado[["id_aluno", "Probabilidade (%)", "Nível de Risco", "Situação Sugerida"]]
    st.dataframe(tabela, use_container_width=True)

    csv = tabela.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar análise com recomendações (CSV)", data=csv, file_name="alunos_risco_com_recomendacoes.csv", mime="text/csv")

    pdf = gerar_pdf_risco_alunos(filtrado, titulo="Relatório de Risco com Recomendações")
    st.download_button("📄 Baixar PDF com Recomendações", data=pdf, file_name="relatorio_alunos_em_risco.pdf", mime="application/pdf")
