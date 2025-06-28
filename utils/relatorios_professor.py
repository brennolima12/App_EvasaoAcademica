from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.platypus import Image

def gerar_grafico_barras_top_alunos(df_nivel, titulo):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))

    top = df_nivel.sort_values(by="Probabilidade", ascending=False).head(10)
    nomes = top["nome_aluno"] if "nome_aluno" in top.columns else top["id_aluno"].astype(str)
    valores = (top["Probabilidade"] * 100).round(1)

    ax.barh(nomes[::-1], valores[::-1], color="blue")
    ax.set_title(titulo)
    ax.set_xlabel("Probabilidade de Evasão (%)")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)
    return buffer

def gerar_pdf_risco_alunos(df, titulo="Relatório de Alunos em Risco"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    bold = styles["Heading2"]

    # Personalizações adicionais
    bold_left = ParagraphStyle("BoldLeft", parent=styles["Heading3"], alignment=0, spaceAfter=6)

    elements = []

    # Cabeçalho
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elements.append(Paragraph(f"Gerado em: {data}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    niveis = ["🔴 Alto", "🟠 Médio", "🟢 Baixo"]
    cores = {"🔴 Alto": colors.red, "🟠 Médio": colors.orange, "🟢 Baixo": colors.green}

    # Adiciona o gráfico de pizza
    try:
        img_buffer = gerar_grafico_barras_top_alunos(df, "Gráfico com Top 10 Alunos")
        img = Image(img_buffer, width=200, height=200)
        elements.append(img)
        elements.append(Spacer(1, 16))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erro ao gerar gráfico: {e}</i>", styles["Normal"]))
        elements.append(Spacer(1, 12))

    for nivel in niveis:
        grupo = df[df["Nível de Risco"] == nivel]
        if grupo.empty:
            continue

        # Título da seção
        elements.append(Paragraph(f"<b>Grupo: {nivel}</b>", ParagraphStyle(name="Secao", textColor=cores[nivel], fontSize=14)))
        elements.append(Spacer(1, 6))

        # Tabela com sugestões
        headers = ["ID", "Nome", "Probabilidade (%)", "Recomendação", "Notas", "Frequência", "Aprovação"]
        dados = [headers]
        for _, row in grupo.iterrows():
            prob = round(row.get("Probabilidade", 0) * 100, 1)
            nome = row.get("nome_aluno", f"Aluno {row['id_aluno']}")
            recomendacao = row.get("Situação Sugerida", "")
            nota = round(row.get("media_notas", 0), 2)
            freq = round(row.get("frequencia", 0), 2)
            aprov = round(row.get("taxa_aprovacao", 0), 2)

            dados.append([row["id_aluno"], nome, f"{prob}%", recomendacao, nota, freq, aprov])

        tabela = Table(dados, colWidths=[50, 130, 70, 170, 50, 50, 60])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), cores[nivel]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        elements.append(tabela)
        elements.append(Spacer(1, 16))
        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer
