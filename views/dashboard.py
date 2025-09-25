import streamlit as st
from data.database import listar_agendamentos
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas

# ------------------- Funções de Exportação -------------------

def gerar_excel(df, data_inicio, data_fim):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Agendamentos")
    output.seek(0)
    return output, f"agendamentos_{data_inicio}_{data_fim}.xlsx"


def gerar_pdf(df, data_inicio, data_fim):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),  # formato horizontal
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=40,  # espaço maior p/ rodapé
    )
    elementos = []
    styles = getSampleStyleSheet()

    # --- Logos centralizadas lado a lado ---
    logo1 = Image("assets/logo.png", width=80, height=80)
    logo2 = Image("assets/dh.png", width=60, height=60)

    tabela_logos = Table([[logo1, logo2]], colWidths=[80, 80])
    tabela_logos.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    wrapper = Table([[tabela_logos]], colWidths=[doc.width])
    wrapper.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elementos.append(wrapper)
    elementos.append(Spacer(1, 10))
    elementos.append(Table([[""]], colWidths=[doc.width], rowHeights=[0.5],
                           style=[("LINEBELOW",(0, 0), (-1, -1), 0.5, colors.darkgreen)]))
    elementos.append(Spacer(1, 15))

    # --- Título ---
    elementos.append(Paragraph("📄 Relatório de Agendamentos", styles["Title"]))
    elementos.append(Spacer(1, 12))

    # --- Infos do relatório ---
    elementos.append(Paragraph(f"📌 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elementos.append(Paragraph(f"📌 Período: {data_inicio} até {data_fim}", styles["Normal"]))
    elementos.append(Spacer(1, 15))

    # --- Tabela principal ---
    colunas = [
        "Data Agendamento", "Hora Agendamento",
        "Loja", "Nome", "Data Demissão", "Data Limite", "Sindicato", 
        "Responsável", "Status"
    ]

    dados = [colunas]
    for _, row in df.iterrows():
        dados.append([
            row.get("data_agendamento", ""),
            row.get("hora_agendamento", ""),
            row.get("loja", ""),
            row.get("nome", ""),
            row.get("data_demissao", ""),
            row.get("data_limite", ""),
            row.get("sindicato", ""),
            row.get("responsavel", ""),
            row.get("status", ""),
        ])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
    ]))

    elementos.append(tabela)
    elementos.append(Spacer(1, 15))

    #elementos.append(Paragraph("Sistema de Agendamento - Copyright © Airton Pereira 2025.", styles["Italic"]))

    # --- Função para rodapé com numeração ---
    def add_footer(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(800, 20, text)  # ajusta posição (x, y)
        canvas.drawString(40, 20, "Sistema de Agendamento - Copyright © Airton Pereira 2025.")

    # Gera o PDF com rodapé
    doc.build(elementos, onFirstPage=add_footer, onLaterPages=add_footer)

    buffer.seek(0)
    return buffer, f"agendamentos_{data_inicio}_{data_fim}.pdf"



# ------------------- Dashboard -------------------

def tela_dash():
    from datetime import date
    hoje = date.today()

    agendamentos = listar_agendamentos()
    df = pd.DataFrame(agendamentos) if agendamentos else pd.DataFrame()

    # Ajustar datas
    for col in ["data_agendamento", "data_demissao", "data_limite"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

    # ------------------- FILTROS -------------------
    st.subheader("📌 Painel de Filtros")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    with col1:
        data_inicio = st.date_input("Data Início Agendamento", hoje)
    with col2:
        data_fim = st.date_input("Data Fim Agendamento", hoje)
    with col3:
        nome = st.text_input("Nome do Colaborador")
    with col4:
        sindicatos = st.multiselect(
            "Sindicato",
            df["sindicato"].dropna().unique().tolist() if not df.empty else [],
            default=df["sindicato"].dropna().unique().tolist() if not df.empty else [],
        )
    with col5:
        lojas = st.multiselect(
            "Loja",
            df["loja"].dropna().unique().tolist() if not df.empty else [],
            default=df["loja"].dropna().unique().tolist() if not df.empty else [],
        )

    col6, col7 = st.columns([2, 2])
    with col6:
        status = st.multiselect(
            "Status",
            df["status"].dropna().unique().tolist() if not df.empty else [],
            default=df["status"].dropna().unique().tolist() if not df.empty else [],
        )
    with col7:
        responsaveis = st.multiselect(
            "Responsável",
            df["responsavel"].dropna().unique().tolist() if not df.empty else [],
            default=df["responsavel"].dropna().unique().tolist() if not df.empty else [],
        )

    # ------------------- APLICA FILTROS -------------------
    if not df.empty:
        df_filtrado = df[
            (df["data_agendamento"] >= pd.to_datetime(data_inicio))
            & (df["data_agendamento"] <= pd.to_datetime(data_fim))
            & (df["sindicato"].isin(sindicatos))
            & (df["loja"].isin(lojas))
            & (df["responsavel"].isin(responsaveis))
            & (df["status"].isin(status))
        ]

        if nome:
            df_filtrado = df_filtrado[df_filtrado["nome"].str.contains(nome, case=False, na=False)]
    else:
        df_filtrado = pd.DataFrame()

    st.markdown("---")

    # ------------------- RESULTADOS -------------------
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum agendamento encontrado para os filtros aplicados.")
        return

    # ------------------- RELATÓRIO TABELADO -------------------
    st.subheader("📑 Relatório Tabelado | Agendamentos Filtrados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Agendamentos", len(df_filtrado))
    col2.metric("Lojas Atendidas", df_filtrado["loja"].nunique())
    col3.metric("Responsáveis", df_filtrado["responsavel"].nunique())

    colunas_ordem = [
        "criado_em",
        "data_agendamento",
        "hora_agendamento",
        "loja",
        "nome",
        "data_demissao",
        "data_limite",
        "sindicato",
        "responsavel",
        "status",
    ]
    df_filtrado_display = df_filtrado[
        [col for col in colunas_ordem if col in df_filtrado.columns]
    ].copy()

    for col in ["data_agendamento", "data_demissao", "data_limite"]:
        if col in df_filtrado_display.columns:
            df_filtrado_display[col] = df_filtrado_display[col].dt.strftime("%d/%m/%Y")

    st.dataframe(df_filtrado_display.reset_index(drop=True))

    # ------------------- EXPORTAÇÃO -------------------
    excel_file, excel_name = gerar_excel(df_filtrado_display, data_inicio, data_fim)
    pdf_file, pdf_name = gerar_pdf(df_filtrado_display, data_inicio, data_fim)

    st.download_button(
        "🟢 Exportar para Excel",
        data=excel_file,
        file_name=excel_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
        "🔴 Exportar para PDF",
        data=pdf_file,
        file_name=pdf_name,
        mime="application/pdf",
    )

    st.markdown("---")

    # ------------------- GRÁFICOS -------------------
    st.subheader("📊 Painel | Dashboards")

    contagem_datas = df_filtrado["data_agendamento"].dt.date.value_counts().sort_index()
    if not contagem_datas.empty:
        fig1 = px.bar(
            x=contagem_datas.index,
            y=contagem_datas.values,
            labels={"x": "Data", "y": "Quantidade"},
            title="Agendamentos por Dia",
            text=contagem_datas.values,
        )
        fig1.update_traces(textfont_size=20)
        st.plotly_chart(fig1, use_container_width=True)

    contagem_lojas = df_filtrado["loja"].value_counts()
    if not contagem_lojas.empty:
        fig2 = px.pie(
            names=contagem_lojas.index,
            values=contagem_lojas.values,
            title="Demissões por Loja",
            hole=0.3,
        )
        fig2.update_traces(textinfo="value", textfont_size=20)
        st.plotly_chart(fig2, use_container_width=True)

    contagem_resp = df_filtrado["responsavel"].value_counts()
    if not contagem_resp.empty:
        fig3 = px.bar(
            x=contagem_resp.index,
            y=contagem_resp.values,
            labels={"x": "Responsável", "y": "Quantidade"},
            title="Atendimentos por Responsável",
            text=contagem_resp.values,
        )
        fig3.update_traces(textfont_size=20)
        st.plotly_chart(fig3, use_container_width=True)

    contagem_status = df_filtrado["status"].value_counts()
    if not contagem_status.empty:
        fig4 = px.pie(
            names=contagem_status.index,
            values=contagem_status.values,
            title="Agendamentos por Status",
        )
        fig4.update_traces(textinfo="value", textfont_size=20)
        st.plotly_chart(fig4, use_container_width=True)




# Alias para compatibilidade com app.py
tela_dash = tela_dash
