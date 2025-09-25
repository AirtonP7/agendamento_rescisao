# cadastro.py
import streamlit as st
from datetime import date, datetime, timedelta, time
import locale
from config.firebase_config import init_firebase
import time as tm

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except Exception:
    pass

db = init_firebase()

def gerar_horarios_30min():
    lista = []
    cur = datetime.combine(date.today(), time(7, 0))
    end = datetime.combine(date.today(), time(22, 0))
    while cur <= end:
        lista.append(cur.time().strftime("%H:%M"))
        cur += timedelta(minutes=30)
    return lista


def cadastrar_agendamento():
    st.title("📅 Novo Agendamento de Rescisão")
    st.write("Preencha os dados abaixo para cadastrar um novo agendamento.")

    # --- session_state defaults / flags ---
    if "form_enviado" not in st.session_state:
        st.session_state["form_enviado"] = False
    if "reset_on_next_run" not in st.session_state:
        st.session_state["reset_on_next_run"] = False

    if st.session_state.get("reset_on_next_run", False):
        st.session_state["nome"] = ""
        st.session_state["sindicato"] = " "
        st.session_state["data_demissao"] = date.today()
        st.session_state["data_agendamento"] = date.today()
        st.session_state["hora_agendamento"] = gerar_horarios_30min()[0]
        st.session_state["loja"] = " "
        st.session_state["responsavel"] = ""
        st.session_state["reset_on_next_run"] = False

    # garante chaves
    if "nome" not in st.session_state:
        st.session_state["nome"] = ""
    if "sindicato" not in st.session_state:
        st.session_state["sindicato"] = " "
    if "data_demissao" not in st.session_state:
        st.session_state["data_demissao"] = date.today()
    if "data_agendamento" not in st.session_state:
        st.session_state["data_agendamento"] = date.today()
    if "hora_agendamento" not in st.session_state:
        st.session_state["hora_agendamento"] = gerar_horarios_30min()[0]
    if "loja" not in st.session_state:
        st.session_state["loja"] = " "
    if "responsavel" not in st.session_state:
        st.session_state["responsavel"] = ""

    horarios = gerar_horarios_30min()

    # --- Coloca a Data da Demissão FORA do form para ser reativa ---
    data_demissao = st.date_input("📆 Data da Demissão", key="data_demissao")
    data_limite = data_demissao + timedelta(days=9)
    st.info(f"⚠️ Data limite para agendamento: **{data_limite.strftime('%d/%m/%Y')}**")

    # Se o valor atual de data_agendamento no session_state estiver fora do novo intervalo,
    # ajusta (clamp) para evitar inconsistências no widget dentro do form.
    da_session = st.session_state.get("data_agendamento")
    if isinstance(da_session, date):
        if da_session < data_demissao or da_session > data_limite:
            st.session_state["data_agendamento"] = data_demissao

    # --- Formulário (contendo o campo de agendamento e demais campos) ---
    with st.form("form_agendamento", clear_on_submit=False):
        nome = st.text_input("👤 Nome do colaborador", key="nome")
        sindicato = st.selectbox(
            "🏢 Sindicato",
            [" ", "Sindicato Fortaleza", "Sindicato Caucaia", "Não"],
            index=0
            if st.session_state.get("sindicato", " ")
            not in ["Sindicato Fortaleza", "Sindicato Caucaia", "Não"]
            else [" ", "Sindicato Fortaleza", "Sindicato Caucaia", "Não"].index(
                st.session_state.get("sindicato")
            ),
            key="sindicato",
        )

        # Data do agendamento (agora dentro do form) — usa min/max dinâmicos
        data_agendamento = st.date_input(
            "📌 Data do Agendamento",
            min_value=data_demissao,
            max_value=data_limite,
            key="data_agendamento",
        )

        try:
            idx = horarios.index(st.session_state.get("hora_agendamento", horarios[0]))
        except ValueError:
            idx = 0
        hora_agendamento = st.selectbox(
            "⏰ Hora do Agendamento (intervalo 30 min)",
            horarios,
            index=idx,
            key="hora_agendamento",
        )

        loja = st.selectbox(
            "🏬 Loja do colaborador",
            [
                " ",
                "Sargento",
                "Mister Hull",
                "Jurema",
                "Mondubim",
                "Pecem",
                "Metropole",
                "Caucaia",
                "Canindé",
                "Pindoretama",
                "Icaraí",
                "Novo Metropole",
                "Escritorio",
                "Operação",
                "CD",
            ],
            key="loja",
        )

        responsavel = st.text_input("👨‍💼 Responsável", key="responsavel")

        submitted = st.form_submit_button("✅ Salvar Agendamento")

    # --- Após submit ---
    if submitted:
        def esta_vazio(x):
            if isinstance(x, str):
                return x.strip() == "" or x == " "
            return x is None

        if any(
            esta_vazio(v)
            for v in [
                nome,
                sindicato,
                data_demissao,
                data_agendamento,
                hora_agendamento,
                loja,
                responsavel,
            ]
        ):
            st.error("⚠️ Todos os campos são obrigatórios!")
            st.stop()

        if not (data_demissao <= data_agendamento <= data_limite):
            st.error("❌ Data do agendamento fora do limite permitido.")
            st.stop()

        try:
            agendamentos_ref = db.collection("agendamentos")
            query = agendamentos_ref.where(
                "data_agendamento", "==", data_agendamento.strftime("%d/%m/%Y")
            ).stream()
            qtd = len(list(query))
            if qtd >= 5:
                st.error("⚠️ Já existem 5 agendamentos neste dia. Escolha outro.")
                st.stop()
        except Exception as e:
            st.error(f"Erro ao verificar agendamentos: {e}")
            st.stop()

        dados = {
            "nome": nome,
            "sindicato": sindicato,
            "data_demissao": data_demissao.strftime("%d/%m/%Y"),
            "data_limite": data_limite.strftime("%d/%m/%Y"),
            "data_agendamento": data_agendamento.strftime("%d/%m/%Y"),
            "hora_agendamento": hora_agendamento,
            "loja": loja,
            "responsavel": responsavel,
            "status": "Pendente",
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

        try:
            db.collection("agendamentos").add(dados)
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
            st.stop()

        st.session_state["form_enviado"] = True
        st.session_state["reset_on_next_run"] = True
        st.rerun()

    if st.session_state.get("form_enviado", False):
        placeholder = st.empty()
        placeholder.success("✅ Agendamento salvo com sucesso!")
        tm.sleep(1)
        placeholder.empty()
        st.session_state["form_enviado"] = False


if __name__ == "__main__":
    cadastrar_agendamento()

# alias
tela_agendamento = cadastrar_agendamento
