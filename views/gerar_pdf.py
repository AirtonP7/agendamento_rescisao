import plotly.express as px
from io import BytesIO
from reportlab.platypus import Image

def gerar_pdf(df, data_inicio, data_fim):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []

    # --- Estilos ---
    styles = getSampleStyleSheet()
    titulo = Paragraph("📄 Relatório de Agendamentos", styles["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    # Data de geração e período
    data_geracao = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"])
    periodo = Paragraph(f"Período: {data_inicio} até {data_fim}", styles["Normal"])
    elementos.append(data_geracao)
    elementos.append(periodo)
    elementos.append(Spacer(1, 20))

    # --- Tabela ---
    colunas = ["Data Agendamento", "Colaborador", "Sindicato", "Loja", "Responsável"]
    dados = [colunas] + [
        [
            row["data_agendamento"].strftime("%d/%m/%Y") if pd.notna(row["data_agendamento"]) else "",
            row["nome_colaborador"],
            row["sindicato"],
            row["loja"],
            row["responsavel"],
        ]
        for _, row in df.iterrows()
    ]
    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 20))


    # --- Rodapé ---
    rodape = Paragraph("Sistema de Agendamento - Copyright © Airton Pereira 2025.", styles["Italic"])
    elementos.append(rodape)

    doc.build(elementos)
    buffer.seek(0)
    return buffer, f"agendamentos_{data_inicio}_{data_fim}.pdf"
