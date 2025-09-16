import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from config.firebase_config import init_firebase

db = init_firebase()


def carregar_agendamentos(data_inicio, data_fim):
    """Carrega agendamentos do Firebase no período informado"""
    inicio = datetime.combine(data_inicio, datetime.min.time())
    fim = datetime.combine(data_fim, datetime.max.time())
    query = db.collection("agendamentos").where("data_agendamento", ">=", inicio).where("data_agendamento", "<=", fim)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


def gerar_pdf_tabelado(agendamentos, data_inicio, data_fim):
    """Gera PDF tabelado com cabeçalho premium"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Cabeçalho
    titulo = Paragraph("📄 Relatório de Agendamentos", styles["Title"])
    periodo = Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}", styles["Normal"])
    elements.extend([titulo, periodo, Spacer(1, 12)])

    # Tabela de agendamentos
    dados_tabela = [["Nome", "Sindicato", "Loja", "Responsável", "Data Demissão", "Data Limite", "Data Agendamento", "Hora"]]
    for ag in agendamentos:
        dados_tabela.append([
            ag.get("nome", "-"),
            ag.get("sindicato", "-"),
            ag.get("loja", "-"),
            ag.get("responsavel", "-"),
            ag.get("data_demissao", "-"),
            ag.get("data_limite", "-"),
            ag.get("data_agendamento", "-"),
            ag.get("hora_agendamento", "-")
        ])

    tabela = Table(dados_tabela, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 9)
    ]))
    elements.append(tabela)
    elements.append(Spacer(1, 20))

    # Rodapé
    rodape = Paragraph("Sistema de Agendamento - Copyright © Airton Pereira 2025.", styles["Italic"])
    elements.append(rodape)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def relatorios_tabelados():
    st.title("📋 Relatório de Agendamentos")

    # Filtros de período (pré-seleção do dia atual)
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", value=date.today())
    with col2:
        data_fim = st.date_input("Data Fim", value=date.today())

    agendamentos = carregar_agendamentos(data_inicio, data_fim)

    if not agendamentos:
        st.warning("⚠️ Nenhum agendamento encontrado nesse período.")
        return

    # DataFrame para exibição na tela
    df = pd.DataFrame(agendamentos)
    st.subheader("📑 Lista de Agendamentos")
    st.dataframe(df)

    # Botão para download PDF
    pdf_buffer = gerar_pdf_tabelado(agendamentos, data_inicio, data_fim)
    st.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_buffer,
        file_name=f"relatorio_agendamentos_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )


if __name__ == "__main__":
    relatorios_tabelados()
