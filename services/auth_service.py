import firebase_admin
from firebase_admin import credentials, auth
import os

from repository.UsuarioRepository import UsuarioRepository
from models.models import Usuario

CREDENTIALS_FILE = "projetocoamo-67073-firebase-adminsdk-fbsvc-1468609e87.json"

def initialize_firebase():
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Erro: Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado.")
            return False
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred)
            print("Firebase inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao inicializar o Firebase: {e}")
        return False


def create_user_with_email_password(nome, email, password, tipo):
    repo_usuario = UsuarioRepository()

    if repo_usuario.get_by_email(email):
        print("Erro: Este e-mail já está cadastrado.")
        return False

    try:
        user_firebase = auth.create_user(
            email=email,
            password=password,
            display_name=nome
        )
        print(f"Usuário criado com sucesso no Firebase: {user_firebase.email}")
        novo_usuario_local = Usuario(
            nome=nome,
            email=email,
            senha=password,
            tipo=tipo
        )
        repo_usuario.add(novo_usuario_local)
        print("Usuário salvo com sucesso no banco de dados local.")
        return True

    except auth.EmailAlreadyExistsError:
        print("Erro: O e-mail já está cadastrado no Firebase, mas não localmente. Contate o suporte.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o cadastro: {e}")
        return False
def login_with_email_password(email, password):
    repo_usuario = UsuarioRepository()
    
    try:
        usuario_local = repo_usuario.get_by_email(email)

        if usuario_local and usuario_local.senha == password:
            user_firebase = auth.get_user_by_email(email)
            if not user_firebase.display_name and usuario_local.nome:
                print("Sincronizando nome de exibição com o Firebase...")
                auth.update_user(user_firebase.uid, display_name=usuario_local.nome)
                user_firebase = auth.get_user(user_firebase.uid)

            print(f"Login bem-sucedido para o usuário: {user_firebase.email}")
            return user_firebase
        else:
            print("Erro de login: E-mail ou senha incorretos.")
            return None
            
    except auth.UserNotFoundError:
        print("Erro de consistência: O usuário não foi encontrado no Firebase.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o login: {e}")
        return None