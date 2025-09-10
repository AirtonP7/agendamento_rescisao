import streamlit as st
from datetime import datetime, date
from config.firebase_config import init_firebase

db = init_firebase()

def carregar_agendamentos(data_inicio, data_fim):
    """Carregar agendamentos no intervalo (strings DD/MM/YYYY)"""
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


def excluir_agendamento():
    st.title("🗑️ Excluir Agendamento")

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

    # Mostrar nomes + data + hora em vez de IDs
    opcoes = {
        f"{doc.to_dict().get('nome', 'Sem nome')} — {doc.to_dict().get('data_agendamento', '??/??/????')} às {doc.to_dict().get('hora_agendamento', '--:--')}": doc.id
        for doc in agendamentos
    }

    # Adiciona opção vazia no início
    lista_opcoes = [""] + list(opcoes.keys())

    escolha = st.selectbox(
        "Selecione o agendamento para excluir:",
        lista_opcoes,
        key="opcao_excluir",
        index=0  # começa vazio
    )

    if escolha and escolha in opcoes:  # só entra se não for vazio
        doc_id = opcoes[escolha]
        doc_ref = db.collection("agendamentos").document(doc_id)
        dados = doc_ref.get().to_dict()

        st.subheader("📋 Detalhes do Agendamento")
        st.write("**Nome:**", dados.get("nome"))
        st.write("**Loja:**", dados.get("loja"))
        st.write("**Responsável:**", dados.get("responsavel"))
        st.write("**Data do Agendamento:**", dados.get("data_agendamento"))

        if st.button("❌ Confirmar Exclusão"):
            doc_ref.delete()
            st.success("✅ Agendamento excluído com sucesso!")

            # Limpar seleção
            del st.session_state["opcao_excluir"]
            st.rerun()


if __name__ == "__main__":
    excluir_agendamento()

# Alias para compatibilidade com app.py
tela_exclusao = excluir_agendamento
