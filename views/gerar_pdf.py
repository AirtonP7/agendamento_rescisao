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

    # --- Gráficos ---
    # Agendamentos por Dia
    contagem_datas = df["data_agendamento"].dt.date.value_counts().sort_index()
    if not contagem_datas.empty:
        fig1 = px.bar(x=contagem_datas.index, y=contagem_datas.values,
                      labels={"x": "Data", "y": "Quantidade"}, title="Agendamentos por Dia")
        img_bytes = fig1.to_image(format="png")
        elementos.append(Image(BytesIO(img_bytes), width=450, height=250))
        elementos.append(Spacer(1, 12))

    # Demissões por Loja
    contagem_lojas = df["loja"].value_counts()
    if not contagem_lojas.empty:
        fig2 = px.pie(names=contagem_lojas.index, values=contagem_lojas.values, title="Demissões por Loja")
        img_bytes = fig2.to_image(format="png")
        elementos.append(Image(BytesIO(img_bytes), width=450, height=250))
        elementos.append(Spacer(1, 12))

    # Atendimentos por Responsável
    contagem_resp = df["responsavel"].value_counts()
    if not contagem_resp.empty:
        fig3 = px.bar(x=contagem_resp.index, y=contagem_resp.values,
                      labels={"x": "Responsável", "y": "Quantidade"}, title="Atendimentos por Responsável")
        img_bytes = fig3.to_image(format="png")
        elementos.append(Image(BytesIO(img_bytes), width=450, height=250))
        elementos.append(Spacer(1, 12))

    # --- Rodapé ---
    rodape = Paragraph("Sistema de Agendamento - Copyright © Airton Pereira 2025.", styles["Italic"])
    elementos.append(rodape)

    doc.build(elementos)
    buffer.seek(0)
    return buffer, f"agendamentos_{data_inicio}_{data_fim}.pdf"
