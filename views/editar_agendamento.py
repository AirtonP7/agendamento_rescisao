import streamlit as st
from datetime import datetime, date
from config.firebase_config import init_firebase

db = init_firebase()

def carregar_agendamentos(data_inicio, data_fim):
    """Carregar agendamentos no intervalo"""
    agendamentos_ref = db.collection("agendamentos")
    docs = agendamentos_ref.stream()

    resultados = []
    for doc in docs:
        dados = doc.to_dict()
        try:
            data_agendamento = datetime.strptime(dados["data_agendamento"], "%d/%m/%Y").date()
            if data_inicio <= data_agendamento <= data_fim:
                resultados.append(doc)
        except Exception:
            pass
    return resultados


def editar_agendamento():
    st.title("✏️ Editar Agendamento")

    # Filtro de datas (padrão: dia atual)
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data início", value=date.today())
    with col2:
        data_fim = st.date_input("Data fim", value=date.today())

    agendamentos = carregar_agendamentos(data_inicio, data_fim)

    if not agendamentos:
        st.warning("⚠️ Nenhum agendamento encontrado nesse período.")
        return

    # Mostrar nomes + data em vez de IDs
    opcoes = {
        f"{doc.to_dict().get('nome', 'Sem nome')} — {doc.to_dict().get('data_agendamento', '??/??/????')}": doc.id
        for doc in agendamentos
    }

    # Adiciona opção vazia no início
    lista_opcoes = [""] + list(opcoes.keys())

    escolha = st.selectbox(
        "Selecione o agendamento para editar:",
        lista_opcoes,
        key="opcao_editar",
        index=0
    )

    if escolha and escolha in opcoes:
        doc_id = opcoes[escolha]
        doc_ref = db.collection("agendamentos").document(doc_id)
        dados = doc_ref.get().to_dict()

        with st.form("editar_form"):
            novo_nome = st.text_input("Nome", value=dados.get("nome", ""))
            nova_loja = st.text_input("Loja", value=dados.get("loja", ""))
            novo_responsavel = st.text_input("Responsável", value=dados.get("responsavel", ""))

            # Converter para date
            try:
                data_atual = datetime.strptime(dados.get("data_agendamento", ""), "%d/%m/%Y").date()
            except:
                data_atual = date.today()

            nova_data = st.date_input("Data do Agendamento", value=data_atual)

            # Campo de status (novo)
            novo_status = st.selectbox(
                "📌 Status",
                ["Pendente", "Atendido"],
                index=0 if dados.get("status", "Pendente") == "Pendente" else 1
            )

            salvar = st.form_submit_button("💾 Salvar Alterações")

            if salvar:
                # --- Validação: limite de 5 agendamentos por dia ---
                agendamentos_ref = db.collection("agendamentos")
                agendamentos_dia = agendamentos_ref.where(
                    "data_agendamento", "==", nova_data.strftime("%d/%m/%Y")
                ).stream()
                agendamentos_dia = list(agendamentos_dia)

                # Excluir o próprio agendamento da contagem
                agendamentos_dia = [a for a in agendamentos_dia if a.id != doc_id]

                if len(agendamentos_dia) >= 5:
                    st.error("⚠️ Já existem 5 agendamentos neste dia. Escolha outro.")
                    return

                # --- Atualização permitida ---
                doc_ref.update({
                    "nome": novo_nome,
                    "loja": nova_loja,
                    "responsavel": novo_responsavel,
                    "data_agendamento": nova_data.strftime("%d/%m/%Y"),
                    "status": novo_status,  # <- Novo campo atualizado
                    "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                })
                st.success("✅ Agendamento atualizado com sucesso!")

                # Limpar seleção após edição
                del st.session_state["opcao_editar"]
                st.rerun()


if __name__ == "__main__":
    editar_agendamento()

# Compatibilidade com app.py
tela_edicao = editar_agendamento
