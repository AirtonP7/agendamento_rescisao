from config.firebase_config import init_firebase

db = init_firebase()

# Agendamentos
def criar_agendamento(dados):
    db.collection("agendamentos").add(dados)

def listar_agendamentos():
    return [doc.to_dict() for doc in db.collection("agendamentos").stream()]

# Feedback
def criar_feedback(dados):
    db.collection("feedback").add(dados)

def listar_feedback():
    return [doc.to_dict() for doc in db.collection("feedback").stream()]
