from models import Usuario
from repository import UsuarioRepository

repository = UsuarioRepository()


def selecionar_todos_usuarios():
    usuario = repository.findall()
    for usuario in usuario:
        print(usuario.nome)

def cadastrar_usuario(nome, email, senha, tipo):
    usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
    repository.save(usuario)
    print(f"Usuário {nome} cadastrado com sucesso!")

id = cadastrar_usuario(
    nome="João Silva",
    email="joao.silva@email.com",
    senha="senha123",
    tipo="arquivista"
)
print(id)