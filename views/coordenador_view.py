import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model.inferencia_modelo import prever_risco_evasao
from utils.relatorios import gerar_relatorio_pdf
from auth import logout
import datetime
import glob
import os

def painel_coordenador():
    st.title("📈 Previsão de Evasão Acadêmica - Coordenador")
    st.sidebar.title("🎯 Menu do Coordenador")
    st.sidebar.button("🚪 Sair", use_container_width=True, on_click=logout)

    tab1, tab2, tab3, tab4 = st.tabs(["📤 Análise por Lote", "🧪 Aluno Manual", "👤 Análise Individual", "📚 Histórico de Análises"])

    df_pred = None
    df_manual_pred = None

    # ==================== TAB 1: Inserção CSV ====================
    with tab1:
        st.subheader("📤 Upload de Arquivo CSV")
        arquivo_csv = st.file_uploader("Selecione um arquivo com os dados dos alunos", type=["csv"])

        if not arquivo_csv:
            st.info("📎 Envie um arquivo CSV para iniciar a análise.")
            return

        # 1. Processamento inicial
        df = pd.read_csv(arquivo_csv)
        st.success(f"✅ {len(df)} registros carregados com sucesso.")
        df_pred = prever_risco_evasao(df)

        if df_pred.empty:
            st.warning("⚠️ A análise gerou uma base vazia. Verifique os dados enviados.")
            return

        # 2. Filtros de visualização
        st.markdown("### 🎯 Filtros")
        col1, col2 = st.columns([2, 1])
        with col1:
            risco_opcao = st.radio("Filtrar por risco:", ["Todos", "🟢 Baixo", "🟠 Médio", "🔴 Alto"], horizontal=True)
            if risco_opcao != "Todos":
                df_pred = df_pred[df_pred["Nível de Risco"] == risco_opcao]
        with col2:
            risco_acima_90 = st.checkbox("🔎 Apenas alunos com risco > 90%")
            if risco_acima_90:
                df_pred = df_pred[df_pred["Probabilidade"] > 0.9]

        # 3. Tabela com resultados
        st.markdown("### 📋 Alunos Analisados")
        df_view = df_pred[["id_aluno", "Probabilidade", "Nível de Risco"]].copy()
        df_view["Probabilidade"] = (df_view["Probabilidade"] * 100).round(1).astype(str) + " %"
        st.write(f"**🎓 Total exibido:** {len(df_view)} aluno(s)")
        st.dataframe(df_view, use_container_width=True)

        # 4. Exportação e salvamento
        with st.expander("📥 Exportar ou Salvar Análise"):
            csv = df_pred.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV", csv, file_name="alunos_filtrados.csv", mime="text/csv")

            st.markdown("---")
            etiqueta = st.text_input("📝 Nome do lote (opcional)", value="analise")
            if st.button("💾 Salvar como Base Oficial"):
                agora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                nome_arquivo = f"dataset/base_{etiqueta}_{agora}.csv".replace(" ", "_")
                df_pred.to_csv(nome_arquivo, index=False)
                st.success(f"📁 Base salva como `{nome_arquivo}`.")

        # 5. Gráficos e análises visuais
        with st.expander("📊 Gráficos e Relatórios"):
            st.markdown("#### 📊 Distribuição por Risco")
            fig_risco = px.histogram(
                df_pred,
                x="Nível de Risco",
                color="Nível de Risco",
                category_orders={"Nível de Risco": ["🟢 Baixo", "🟠 Médio", "🔴 Alto"]},
                color_discrete_map={"🟢 Baixo": "green", "🟠 Médio": "gold", "🔴 Alto": "red"},
            )
            st.plotly_chart(fig_risco, use_container_width=True)

            st.markdown("#### 📈 Probabilidade de Evasão")
            fig_prob = px.histogram(df_pred, x="Probabilidade", nbins=20, marginal="rug")
            st.plotly_chart(fig_prob, use_container_width=True)

            if "semestre_atual" in df_pred.columns:
                st.markdown("#### 📈 Evolução do Risco por Semestre")
                media_risco = df_pred.groupby("semestre_atual")["Probabilidade"].mean().reset_index()
                fig_linha = px.line(media_risco, x="semestre_atual", y="Probabilidade", markers=True)
                st.plotly_chart(fig_linha, use_container_width=True)

            st.markdown("#### 📊 Média de Desempenho por Risco")
            media_risco = df_pred.groupby("Nível de Risco")[["media_notas", "frequencia", "taxa_aprovacao"]].mean().reset_index()
            fig_media = px.bar(
                media_risco.melt(id_vars="Nível de Risco", var_name="Métrica", value_name="Valor"),
                x="Métrica", y="Valor", color="Nível de Risco", barmode="group",
                category_orders={"Nível de Risco": ["🟢 Baixo", "🟠 Médio", "🔴 Alto"]},
                color_discrete_map={"🟢 Baixo": "green", "🟠 Médio": "gold", "🔴 Alto": "red"}
            )
            st.plotly_chart(fig_media, use_container_width=True)

            st.markdown("#### 📌 Resumo")
            contagem = df_pred["Nível de Risco"].value_counts().to_dict()
            for risco in ["🟢 Baixo", "🟠 Médio", "🔴 Alto"]:
                qtd = contagem.get(risco, 0)
                st.markdown(f"- {risco}: **{qtd} aluno(s)**")

            st.markdown("#### 📄 Relatório Geral")
            if st.button("📥 Baixar Relatório Geral"):
                relatorio = gerar_relatorio_pdf(df_pred, "Relatório de Risco Geral")
                st.download_button("⬇️ Download", relatorio.getvalue(), file_name="relatorio_geral.pdf", mime="application/pdf")

    # ==================== TAB 2: Inserção Manual ====================
    with tab2:
        st.subheader("🧪 Prever risco para um aluno manualmente")

        col1, col2, col3 = st.columns(3)
        with col1:
            id_manual = st.number_input("ID do Aluno", step=1)
            media_notas = st.number_input("Média das Notas", 0.0, 10.0)
            nota1 = st.number_input("Nota 1", 0.0, 10.0)
            nota2 = st.number_input("Nota 2", 0.0, 10.0)
            nota3 = st.number_input("Nota 3", 0.0, 10.0)
            nota4 = st.number_input("Nota 4", 0.0, 10.0)
        with col2:
            nota5 = st.number_input("Nota 5", 0.0, 10.0)
            nota6 = st.number_input("Nota 6", 0.0, 10.0)
            nota7 = st.number_input("Nota 7", 0.0, 10.0)
            nota8 = st.number_input("Nota 8", 0.0, 10.0)
            nota9 = st.number_input("Nota 9", 0.0, 10.0)
        with col3:
            nota10 = st.number_input("Nota 10", 0.0, 10.0)
            frequencia = st.slider("Frequência (%)", 0, 100, 75)
            taxa_aprovacao = st.slider("Taxa de Aprovação", 0.0, 1.0, 0.6, step=0.01)
            total_semestres = st.number_input("Semestres Cursados", 1)
            trancamentos = st.number_input("Qtd. de Trancamentos", 0)
            semestre_atual = st.number_input("Semestre Atual", 1)

        incluir = st.checkbox("➕ Incluir na análise geral")

        if st.button("🔍 Prever Risco"):
            aluno_manual = pd.DataFrame([{
                "id_aluno": id_manual,
                "media_notas": media_notas,
                "frequencia": frequencia,
                "taxa_aprovacao": taxa_aprovacao,
                "total_semestres_cursados": total_semestres,
                "qtd_trancamentos": trancamentos,
                "semestre_atual": semestre_atual,
                "nota_disciplina1": nota1, "nota_disciplina2": nota2, "nota_disciplina3": nota3,
                "nota_disciplina4": nota4, "nota_disciplina5": nota5, "nota_disciplina6": nota6,
                "nota_disciplina7": nota7, "nota_disciplina8": nota8, "nota_disciplina9": nota9,
                "nota_disciplina10": nota10
            }])
            df_manual_pred = prever_risco_evasao(aluno_manual)
            aluno = df_manual_pred.iloc[0]
            st.success(f"Previsão: {aluno['Nível de Risco']} ({aluno['Probabilidade']:.2%})")

            if incluir:
                if df_pred is not None:
                    df_pred = pd.concat([df_pred, df_manual_pred], ignore_index=True)
                    st.success("Aluno incluído na base de análise.")
                else:
                    df_pred = df_manual_pred.copy()
                    st.success("Base criada com o aluno inserido.")

    # ==================== TAB 3: Análise Individual ====================
    with tab3:
        st.subheader("👤 Análise de Aluno")

        if df_pred is not None and not df_pred.empty:
            aluno_id = st.selectbox("Selecione um aluno:", df_pred["id_aluno"].unique())
            aluno = df_pred[df_pred["id_aluno"] == aluno_id].iloc[0]
            media = df_pred[["media_notas", "frequencia", "taxa_aprovacao"]].mean()

            st.write(f"🧠 **Probabilidade de Evasão:** {aluno['Probabilidade']:.2%}")
            st.write(f"📊 **Nível de Risco:** {aluno['Nível de Risco']}")

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[aluno["media_notas"], aluno["frequencia"], aluno["taxa_aprovacao"]],
                theta=["Notas", "Frequência", "Aprovação"], fill='toself', name='Aluno'
            ))
            fig.add_trace(go.Scatterpolar(
                r=[media["media_notas"], media["frequencia"], media["taxa_aprovacao"]],
                theta=["Notas", "Frequência", "Aprovação"], fill='toself', name='Média'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            causas = []
            if aluno["frequencia"] < media["frequencia"]:
                causas.append("frequência abaixo da média")
            if aluno["media_notas"] < media["media_notas"]:
                causas.append("notas abaixo da média")
            if aluno.get("taxa_aprovacao", 0) < media.get("taxa_aprovacao", 0):
                causas.append("baixa taxa de aprovação")

            # Ações sugeridas
            if aluno['Nível de Risco'] == "🔴 Alto":
                acao = "Encaminhar para tutoria ou agendar reunião com a coordenação."
            elif aluno['Nível de Risco'] == "🟠 Médio":
                acao = "Acompanhar de perto o desempenho nos próximos semestres."
            else:
                acao = "Manter acompanhamento padrão."

            st.markdown(f"📌 **Recomendações:** {acao}")
            if causas:
                st.info("🧭 Possíveis fatores de risco: " + ", ".join(causas))

            st.markdown("---")
            st.subheader("📄 Relatório do Aluno Selecionado")
            if st.button(f"📥 Baixar Relatório de {aluno_id}"):
                df_individual = df_pred[df_pred["id_aluno"] == aluno_id]
                relatorio_ind = gerar_relatorio_pdf(df_individual, f"Relatório do Aluno {aluno_id}")
                st.download_button(f"⬇️ Download Aluno {aluno_id}", relatorio_ind.getvalue(), file_name=f"relatorio_aluno_{aluno_id}.pdf", mime="application/pdf")
        else:
            st.info("📎 Nenhum dado disponível. Envie um CSV em 'Análise por Lote' ou adicione manualmente um aluno em 'Aluno Manual'.")

    # ==================== TAB 4: Histórico de Análises ====================
    with tab4:
        st.subheader("📚 Histórico de Análises Salvas")

        arquivos = sorted(glob.glob("dataset/base_*.csv"), reverse=True)

        if not arquivos:
            st.info("📂 Nenhuma análise salva foi encontrada.")
        else:
            for arq in arquivos:
                nome = os.path.basename(arq)
                with st.expander(f"📄 {nome}", expanded=False):
                    try:
                        df_hist = pd.read_csv(arq)
                        st.markdown(f"**👥 Registros:** {len(df_hist)}")
                        st.dataframe(df_hist.head(10), use_container_width=True)

                        with open(arq, "rb") as f:
                            st.download_button(
                                label=f"⬇️ Baixar {nome}",
                                data=f,
                                file_name=nome,
                                mime="text/csv"
                            )

                        if st.button(f"📌 Definir como Base para Professores", key=nome):
                            df_hist.to_csv("dataset/dataSetSintetico.csv", index=False)
                            st.success("✅ Base atualizada com sucesso e liberada para o painel do professor.")

                    except Exception as e:
                        st.error(f"Erro ao ler {nome}: {e}")
