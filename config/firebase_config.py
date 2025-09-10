import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from config.settings import FIREBASE_CREDENTIALS

def init_firebase():
    """
    Inicializa a conexão com o Firebase.
    - Ambiente local: usa o arquivo serviceAccountKey.json
    - Produção (Render/Deploy): usa variável de ambiente FIREBASE_CREDENTIALS_JSON
    """
    if not firebase_admin._apps:
        creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        if creds_json:
            try:
                cred_dict = json.loads(creds_json)
                cred = credentials.Certificate(cred_dict)
                print("DEBUG | Firebase inicializado com variável de ambiente JSON")
            except json.JSONDecodeError as e:
                raise ValueError("Erro ao decodificar JSON do FIREBASE_CREDENTIALS_JSON") from e

        elif FIREBASE_CREDENTIALS and os.path.exists(FIREBASE_CREDENTIALS):
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            print("DEBUG | Firebase inicializado com arquivo local")

        else:
            raise ValueError(
                "Credenciais do Firebase não encontradas. "
                "Configure a variável FIREBASE_CREDENTIALS_JSON no Render ou o arquivo local."
            )

        firebase_admin.initialize_app(cred)

    return firestore.client()
