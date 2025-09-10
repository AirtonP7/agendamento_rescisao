import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from config.settings import FIREBASE_CREDENTIALS

def init_firebase():
    """
    Inicializa a conexão com o Firebase.
    - Ambiente local: usa o arquivo serviceAccountKey.json
    - Produção: usa variável de ambiente FIREBASE_CREDENTIALS_JSON
    """
    if not firebase_admin._apps:
        # Tenta ler a variável de ambiente para produção
        creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        if creds_json:
            print("DEBUG | Usando Firebase via variável de ambiente JSON")
            cred = credentials.Certificate(json.loads(creds_json))
        elif FIREBASE_CREDENTIALS and os.path.exists(FIREBASE_CREDENTIALS):
            print("DEBUG | Usando Firebase via arquivo local")
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        else:
            raise ValueError(
                "Não foi possível encontrar credenciais do Firebase. "
                "Verifique o arquivo FIREBASE_CREDENTIALS ou a variável FIREBASE_CREDENTIALS_JSON."
            )

        firebase_admin.initialize_app(cred)

    return firestore.client()
