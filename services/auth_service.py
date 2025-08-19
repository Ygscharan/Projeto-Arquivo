import firebase_admin
from firebase_admin import credentials, auth
import os


CREDENTIALS_FILE = CREDENTIALS_FILE = "projetocoamo-67073-firebase-adminsdk-fbsvc-1468609e87.json"

def initialize_firebase():
    """Inicializa o SDK do Firebase."""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Erro: Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado.")
            return False
        
        cred = credentials.Certificate(CREDENTIALS_FILE)
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao inicializar o Firebase: {e}")
        return False

def login_with_email_password(email, password):
    try:
        user = auth.get_user_by_email(email)
        print(f"Login bem-sucedido para o usuário: {user.email}")
        return user
        
    except auth.UserNotFoundError:
        print("Erro de login: E-mail não encontrado.")
    except Exception as e:
        print(f"Erro de login: {e}")
    return None