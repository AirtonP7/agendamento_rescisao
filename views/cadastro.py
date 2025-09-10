import streamlit as st
from datetime import date, timedelta, datetime, time
import locale

from config.firebase_config import init_firebase

# Forçar formato de datas em PT-BR
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    pass  # no Windows pode dar problema, mas formatamos manualmente no strftime

db = init_firebase()

def cadastrar_agendamento():
    st.title("📅 Novo Agendamento de Rescisão")
    st.write("Preencha os dados abaixo para cadastrar um novo agendamento.")

    # inicialização do estado
    if "form_enviado" not in st.session_state:
        st.session_state.form_enviado = False

    with st.form("form_agendamento", clear_on_submit=True):
        nome = st.text_input("👤 Nome do colaborador")

        sindicato = st.selectbox(
            "🏢 Sindicato",
            [" ", "Sindicato Fortaleza", "Sindicato Caucaia", "Não"]
        )

        data_demissao = st.date_input("📆 Data da Demissão", min_value=date.today())
        data_limite = data_demissao + timedelta(days=10)

        st.info(f"⚠️ Data limite para agendamento: **{data_limite.strftime('%d/%m/%Y')}**")

        data_agendamento = st.date_input(
            "📌 Data do Agendamento",
            min_value=date.today(),
            max_value=data_limite
        )

        hora_agendamento = st.time_input("⏰ Hora do Agendamento")

        loja = st.selectbox(
            "🏬 Loja do colaborador",
            [
                " ", "Sargento", "Mister Hull", "Jurema", "Mondubim", "Pecem",
                "Metropole", "Caucaia", "Canindé", "Pindoretama",
                "Icaraí", "Novo Metropole", "CD"
            ]
        )

        responsavel = st.text_input("👨‍💼 Responsável")

        submitted = st.form_submit_button("✅ Salvar Agendamento")

        if submitted:
            if data_agendamento > data_limite:
                st.error("❌ O agendamento deve ser até a data limite!")
                return

            # Verificar limite de 5 agendamentos no mesmo dia
            agendamentos_ref = db.collection("agendamentos")
            agendamentos_dia = agendamentos_ref.where(
                "data_agendamento", "==", data_agendamento.strftime("%d/%m/%Y")
            ).stream()
            agendamentos_dia = list(agendamentos_dia)

            if len(agendamentos_dia) >= 5:
                st.error("⚠️ Já existem 5 agendamentos neste dia. Escolha outro.")
                return

            dados = {
                "nome": nome,
                "sindicato": sindicato,
                "data_demissao": data_demissao.strftime("%d/%m/%Y"),
                "data_limite": data_limite.strftime("%d/%m/%Y"),
                "data_agendamento": data_agendamento.strftime("%d/%m/%Y"),
                "hora_agendamento": hora_agendamento.strftime("%H:%M"),
                "loja": loja,
                "responsavel": responsavel,
                "status": "Pendente",  # <- NOVO CAMPO PADRÃO
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }

            db.collection("agendamentos").add(dados)
            st.session_state.form_enviado = True

    # Mensagem de sucesso fora do form (assim não some ao limpar)
    if st.session_state.form_enviado:
        st.success("✅ Agendamento salvo com sucesso!")
        st.session_state.form_enviado = False


if __name__ == "__main__":
    cadastrar_agendamento()

# Alias para compatibilidade com o app.py
tela_agendamento = cadastrar_agendamento
