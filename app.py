# app.py
import streamlit as st

# Importando telas
from views.cadastro import tela_agendamento
from views.editar_agendamento import tela_edicao
from views.excluir_agendamento import tela_exclusao
from views.dashboard import tela_dash
from falar_desenvolvedor.contato_dev import render

# depois você conecta a tela_feedback que já tem pronta

st.set_page_config(
    page_title="GrupoMax | Agendamento de Rescisão",
    page_icon="https://i.postimg.cc/CLBKzSSQ/file.jpg",
    layout="wide"
)

# --- CSS Premium ---
st.markdown("""
    <style>
    /* Sidebar geral */
    [data-testid="stSidebar"] {
        background-color: #1E1E2F;
        padding: 20px 15px;
    }

    /* Logo */
    .sidebar-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }

    /* Título */
    .sidebar-title {
        color: #FFFFFF;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    /* Subtítulo */
    .sidebar-subtitle {
        color: #A0A0B2;
        text-align: center;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Botões do menu */
    div[role="radiogroup"] > label {
        background-color: #2B2B40;
        color: #FFFFFF !important;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
        transition: all 0.3s ease-in-out;
        border: 1px solid #3C3C55;
    }

    /* Hover nos botões */
    div[role="radiogroup"] > label:hover {
        background-color: #3A3A55;
        border: 1px solid #5A5A7A;
    }

    /* Botão selecionado */
    div[role="radiogroup"] > label[data-selected="true"] {
        background-color: #6C63FF !important;
        border: 1px solid #857CFF;
        color: #FFFFFF !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; justify-content: space-around;">
            <img src="https://i.postimg.cc/Df5wFvD9/Design-sem-nome-2023-03-17-T165226-578.png" width="100">
            <img src="https://i.postimg.cc/CLBKzSSQ/file.jpg" width="100">
        </div>
    """, unsafe_allow_html=True)
    # substitua a URL pela sua logo em /assets/logo.png , https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg

    st.markdown("""
        <div style="margin-top: 30px; text-align: center;">
            <div style="font-size:20px; font-weight:bold; color:white;">DH | GrupoMax</div>
            <div style="font-size:16px; font-weight:bold; color:#cccccc; margin-top:5px;">
                Sistema de Agendamento de Rescisão
            </div>
        </div>
        <hr style="margin-top:15px; margin-bottom:10px; border:0px solid #444;">
    """, unsafe_allow_html=True)

    st.markdown("---")

    menu = st.radio(
        "Navegação",
        ["🌐 Painel Incial", "➕ Novo Agendamento", "✏️ Editar Agendamento", "🗑️ Excluir Agendamento", "👨🏽‍💻 Falar com Desenvolvedor"],
        label_visibility="collapsed"
    )

# --- ÁREA PRINCIPAL ---
if menu == "🌐 Painel Incial":
    tela_dash()

elif menu == "➕ Novo Agendamento":
    tela_agendamento()

elif menu == "✏️ Editar Agendamento":
    tela_edicao()

elif menu == "🗑️ Excluir Agendamento":
    tela_exclusao()

elif menu == "👨🏽‍💻 Falar com Desenvolvedor":
    render()

st.sidebar.markdown("---", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style="text-align: center; margin-top: 40px; color: #aaa;">
        <div style="font-size:16px; font-weight:bold;">v1.0.0</div>
        <div style="font-size:17px;">Airton Pereira © 2025</div>
    </div>
""", unsafe_allow_html=True)

    
