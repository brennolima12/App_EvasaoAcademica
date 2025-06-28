from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

def gerar_relatorio_pdf(df_risco, titulo="Relatório de Risco Acadêmico"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    estilo_titulo = ParagraphStyle('titulo', fontSize=16, leading=20, alignment=1)
    estilo_normal = styles["Normal"]
    estilo_subtitulo = ParagraphStyle('sub', fontSize=12, leading=14, spaceBefore=12)

    elementos.append(Paragraph(titulo, estilo_titulo))
    elementos.append(Spacer(1, 16))

    if len(df_risco) == 1:
        aluno = df_risco.iloc[0]
        elementos.append(Paragraph(f"<b>ID do Aluno:</b> {aluno['id_aluno']}", estilo_normal))
        elementos.append(Paragraph(f"<b>Probabilidade de Evasão:</b> {aluno['Probabilidade']:.2%}", estilo_normal))
        elementos.append(Paragraph(f"<b>Nível de Risco:</b> {aluno['Nível de Risco']}", estilo_normal))

        # Causas prováveis (explicação simples)
        causas = []
        for col, limiar, nome in [
            ("frequencia", 75, "frequência baixa"),
            ("media_notas", 6.0, "média de notas abaixo"),
            ("taxa_aprovacao", 0.6, "taxa de aprovação reduzida")
        ]:
            if col in aluno and aluno[col] < limiar:
                causas.append(nome)
        if causas:
            explicacao = "Possíveis fatores de risco: " + ", ".join(causas)
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph(explicacao, estilo_normal))
    else:
        # Relatório geral com distribuição
        elementos.append(Paragraph(f"<b>Total de alunos:</b> {len(df_risco)}", estilo_subtitulo))
        risco_counts = df_risco["Nível de Risco"].value_counts().to_dict()
        for risco, qtd in risco_counts.items():
            elementos.append(Paragraph(f"{risco}: {qtd} aluno(s)", estilo_normal))
        elementos.append(Spacer(1, 12))

        # Tabela com os dados principais
        tabela_dados = [["ID", "Probabilidade", "Nível de Risco"]]
        for _, row in df_risco.iterrows():
            tabela_dados.append([
                str(row.get("id_aluno", "")),
                f"{row['Probabilidade']:.2%}",
                row["Nível de Risco"]
            ])

        tabela = Table(tabela_dados, repeatRows=1, colWidths=[70, 110, 130])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elementos.append(tabela)

    doc.build(elementos)
    buffer.seek(0)
    return buffer
