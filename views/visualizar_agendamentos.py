import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from config.firebase_config import init_firebase
import plotly.express as px

db = init_firebase()

def carregar_agendamentos(data_inicio=None, data_fim=None, loja=None, responsavel=None, nome=None):
    """Carrega agendamentos filtrados do Firestore"""
    query = db.collection("agendamentos")

    # Filtro por intervalo de datas
    if data_inicio and data_fim:
        inicio = datetime.combine(data_inicio, datetime.min.time())
        fim = datetime.combine(data_fim, datetime.max.time())
        query = query.where("data_agendamento", ">=", inicio).where("data_agendamento", "<=", fim)
    else:
        # Puxa apenas o dia atual
        hoje = datetime.combine(date.today(), datetime.min.time())
        amanha = datetime.combine(date.today(), datetime.max.time())
        query = query.where("data_agendamento", ">=", hoje).where("data_agendamento", "<=", amanha)

    agendamentos = [doc.to_dict() for doc in query.stream()]
    df = pd.DataFrame(agendamentos)

    if df.empty:
        return df

    # Converter datas para datetime
    for campo in ["data_demissao", "data_limite", "data_agendamento"]:
        if campo in df.columns:
            df[campo] = pd.to_datetime(df[campo], errors="coerce")

    # Filtros adicionais
    if nome:
        df = df[df["nome"].str.contains(nome, case=False, na=False)]
    if loja and loja != "Todas":
        df = df[df["loja"] == loja]
    if responsavel and responsavel != "Todos":
        df = df[df["responsavel"] == responsavel]

    return df

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Agendamentos")
    output.seek(0)
    return output.getvalue()

def exportar_pdf(df, data_inicio, data_fim):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []

    styles = getSampleStyleSheet()
    elementos.append(Paragraph("📄 Relatório de Agendamentos", styles["Title"]))
    elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Spacer(1, 12))

    # Tabela
    colunas = ["Data Agendamento", "Nome", "Sindicato", "Loja", "Responsável"]
    dados = [colunas] + [
        [
            row["data_agendamento"].strftime("%d/%m/%Y") if pd.notna(row["data_agendamento"]) else "",
            row["nome"],
            row["sindicato"],
            row["loja"],
            row["responsavel"]
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
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,1), (-1,-1), 9),
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("Sistema de Agendamento - Copyright © Airton Pereira 2025.", styles["Italic"]))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

def visualizar_agendamentos():
    st.title("📅 Visualizar Agendamentos")

    # --- FILTROS NA TELA ---
    st.subheader("🔍 Filtros")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do colaborador")
        loja = st.selectbox(
            "Loja",
            [
                "Todas", "Sargento", "Mister Hull", "Jurema", "Mondubim", "Pecem",
                "Metropole", "Caucaia", "Canindé", "Pindoretama", "Icaraí",
                "Novo Metropole", "Escritorio", "Operação", "CD"
            ]
        )
    with col2:
        responsavel = st.selectbox("Responsável", ["Todos"] + [])
        data_inicio = st.date_input("Data Início", value=date.today())
        data_fim = st.date_input("Data Fim", value=date.today())

    # Carregar dados
    df = carregar_agendamentos(data_inicio, data_fim, loja, responsavel, nome)

    if df.empty:
        st.warning("⚠️ Nenhum agendamento encontrado para os filtros aplicados.")
    else:
        # Mostrar tabela
        st.subheader("📋 Resultados")
        df_display = df.copy()
        for campo in ["data_agendamento", "data_demissao", "data_limite"]:
            if campo in df_display.columns:
                df_display[campo] = df_display[campo].dt.strftime("%d/%m/%Y")
        st.dataframe(df_display, use_container_width=True)

        # Exportações
        st.subheader("📂 Exportar Resultados")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            excel_data = exportar_excel(df_display)
            st.download_button(
                "⬇️ Exportar para Excel",
                excel_data,
                "agendamentos.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with col_exp2:
            pdf_data = exportar_pdf(df_display, data_inicio, data_fim)
            st.download_button(
                "⬇️ Exportar para PDF",
                pdf_data,
                f"agendamentos_{data_inicio}_{data_fim}.pdf",
                "application/pdf",
            )

        # Gráficos
        st.subheader("📊 Gráficos")
        contagem_datas = df["data_agendamento"].dt.date.value_counts().sort_index()
        fig1 = px.bar(
            x=contagem_datas.index, y=contagem_datas.values,
            labels={"x": "Data", "y": "Quantidade"},
            title="Agendamentos por Dia"
        )
        st.plotly_chart(fig1, use_container_width=True)

        contagem_lojas = df["loja"].value_counts()
        fig2 = px.pie(
            names=contagem_lojas.index, values=contagem_lojas.values,
            title="Demissões por Loja"
        )
        st.plotly_chart(fig2, use_container_width=True)

        contagem_resp = df["responsavel"].value_counts()
        fig3 = px.bar(
            x=contagem_resp.index, y=contagem_resp.values,
            labels={"x": "Responsável", "y": "Quantidade"},
            title="Atendimentos por Responsável"
        )
        st.plotly_chart(fig3, use_container_width=True)


if __name__ == "__main__":
    visualizar_agendamentos()
