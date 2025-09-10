import os
from dotenv import load_dotenv

# Carrega o .env da raiz do projeto (mesmo se rodar dentro de scripts/)
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Caminho para o arquivo de credenciais local
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Máximo de agendamentos por dia
MAX_AGENDAMENTOS_DIA = int(os.getenv("MAX_AGENDAMENTOS_DIA", 5))

# Debug: confirmar leitura das variáveis
print("DEBUG | FIREBASE_CREDENTIALS:", FIREBASE_CREDENTIALS)
print("DEBUG | MAX_AGENDAMENTOS_DIA:", MAX_AGENDAMENTOS_DIA)
