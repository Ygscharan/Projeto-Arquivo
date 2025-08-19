import datetime
from models.models import Usuario, Caixa, Documento, Prateleira, Unidade, Movimentacao

from repository.CaixaRepository import CaixaRepository
from repository.DocumentoRepository import DocumentoRepository
from repository.MovimentacaoRepository import MovimentacaoRepository
from repository.PrateleiraRepository import PrateleiraRepository
from repository.UnidadeRepository import UnidadeRepository
from repository.UsuarioRepository import UsuarioRepository


repo_usuario = UsuarioRepository()
repo_caixa = CaixaRepository()
repo_documento = DocumentoRepository()
repo_movimentacao = MovimentacaoRepository()
repo_prateleira = PrateleiraRepository()
repo_unidade = UnidadeRepository()


def parse_data_flexivel(data_str):
    formatos_para_tentar = [
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y-%m-%d'
    ]
    for fmt in formatos_para_tentar:
        try:
            return datetime.datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    return None


def criar_dados_iniciais():
    print("Verificando dados iniciais...")

    unidades = repo_unidade.get_all()
    if not unidades:
        print("Criando Unidade padrão...")
        unidade_padrao = Unidade(nome="Sede Campo Mourão", codigo=101)
        repo_unidade.add(unidade_padrao)

    prateleiras = repo_prateleira.get_all()
    if not prateleiras:
        print("Criando Prateleira padrão...")
        prateleira_padrao = Prateleira(setor="Arquivo Morto", corredor=1, coluna=1, nivel=1)
        repo_prateleira.add(prateleira_padrao)
    print("Dados iniciais prontos!")


# ---------------- MENU USUÁRIO ----------------
def menu_usuario():
    while True:
        print("\n--- Menu Usuário ---")
        print("1. Listar todos")
        print("2. Buscar por ID")
        print("3. Buscar por E-mail")
        print("4. Cadastrar novo")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            usuarios = repo_usuario.get_all()
            for u in usuarios:
                print(f"ID: {u.id}, Nome: {u.nome}, E-mail: {u.email}, Tipo: {u.tipo}")

        elif opcao == '2':
            id_busca = int(input("Digite o ID do usuário: "))
            usuario = repo_usuario.get_by_id(id_busca)
            if usuario:
                print(f"Encontrado: ID: {usuario.id}, Nome: {usuario.nome}")
            else:
                print("Usuário não encontrado.")

        elif opcao == '3':
            email_busca = input("Digite o e-mail do usuário: ")
            usuario = repo_usuario.get_by_email(email_busca)
            if usuario:
                print(f"Encontrado: ID: {usuario.id}, Nome: {usuario.nome}")
            else:
                print("Usuário não encontrado.")

        elif opcao == '4':
            nome = input("Nome: ")
            email = input("E-mail: ")
            senha = input("Senha: ")
            tipo = input("Tipo (arquivista, comum): ")
            novo_usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
            repo_usuario.add(novo_usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso!")

        elif opcao == '5':
            break


# ---------------- MENU CAIXA ----------------
def menu_caixa():
    while True:
        print("\n--- Menu Caixa ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            caixas = repo_caixa.get_all()
            for c in caixas:
                if getattr(c, "data_eliminacao", None):
                    data_elim_str = c.data_eliminacao.strftime("%Y-%m-%d")
                else:
                    data_elim_str = "CAIXA PERMANENTE"
                docs = getattr(c, "documentos", None) or []
                docs_str = "; ".join(f"{d.id}:{d.titulo}" for d in docs) if docs else "Nenhum documento"
                print(f"ID: {c.id}, Número: {c.numero_caixa}, Unidade: {c.unidade_id}, Eliminação: {data_elim_str}, Prateleira: {c.prateleira_id}, Documentos: {docs_str}")

        elif opcao == '2':
            try:
                id_busca = int(input("Digite o ID da caixa: "))
            except ValueError:
                print("ID inválido.")
                continue
            caixa = repo_caixa.get_by_id(id_busca)
            if caixa:
                de = caixa.data_eliminacao.strftime("%Y-%m-%d") if getattr(caixa, "data_eliminacao", None) else "CAIXA PERMANENTE"
                docs = getattr(caixa, "documentos", None) or []
                docs_str = "; ".join(f"{d.id}:{d.titulo}" for d in docs) if docs else "Nenhum documento"
                print(f"Encontrado: ID {caixa.id}, Número {caixa.numero_caixa}, Eliminação: {de}, Unidade: {caixa.unidade_id}, Prateleira: {caixa.prateleira_id}, Documentos: {docs_str}")
            else:
                print("Caixa não encontrada.")

        elif opcao == '3':
            try:
                numero = int(input("Número da Caixa: "))
            except ValueError:
                print("Número inválido.")
                continue

            data_input = input("Data de eliminação (enter para CAIXA PERMANENTE) [dd-mm-YYYY | dd/mm/YYYY | YYYY-mm-dd]: ").strip()
            data_elim = None if data_input == "" else parse_data_flexivel(data_input)
            if data_input and data_elim is None:
                print("Formato de data inválido. Tente novamente.")
                continue

            unidades = repo_unidade.get_all()
            prateleiras = repo_prateleira.get_all()
            if not unidades or not prateleiras:
                print("Unidade ou prateleira padrão não encontrada. Crie antes de adicionar caixas.")
                continue

            # escolher unidade explicitamente
            print("\nUnidades disponíveis:")
            for u in unidades:
                print(f"ID: {u.id} - Nome: {u.nome} - Código: {u.codigo}")
            unidade_input = input("ID da unidade para associar (enter para usar a primeira): ").strip()
            if unidade_input == "":
                unidade = unidades[0]
            else:
                try:
                    uid = int(unidade_input)
                except ValueError:
                    print("ID de unidade inválido.")
                    continue
                unidade = repo_unidade.get_by_id(uid)
                if not unidade:
                    print("Unidade não encontrada.")
                    continue

            # escolher prateleira explicitamente (melhora confiabilidade)
            print("\nPrateleiras disponíveis:")
            for p in prateleiras:
                print(f"ID: {p.id} - Setor: {p.setor} - Corredor: {p.corredor} - Coluna: {p.coluna} - Nível: {p.nivel}")
            pr_input = input("ID da prateleira para associar (enter para usar a primeira): ").strip()
            if pr_input == "":
                prateleira = prateleiras[0]
            else:
                try:
                    pid = int(pr_input)
                except ValueError:
                    print("ID de prateleira inválido.")
                    continue
                prateleira = repo_prateleira.get_by_id(pid)
                if not prateleira:
                    print("Prateleira não encontrada.")
                    continue

            # lista documentos disponíveis
            documentos = repo_documento.get_all()
            selected_docs = []
            print("\nDocumentos disponíveis:")
            if documentos:
                for d in documentos:
                    print(f"ID: {d.id} - Título: {d.titulo} - Tipo: {d.tipo}")
            else:
                print("  (nenhum documento cadastrado)")
            ids_input = input("IDs dos documentos para associar (vírgula-separados, enter para nenhum): ").strip()
            if ids_input:
                for part in ids_input.split(','):
                    part = part.strip()
                    if not part:
                        continue
                    try:
                        did = int(part)
                    except ValueError:
                        print(f"Ignorando ID inválido: {part}")
                        continue
                    doc = repo_documento.get_by_id(did)
                    if doc:
                        selected_docs.append(doc)
                    else:
                        print(f"Documento com ID {did} não encontrado; ignorado.")

            # DEBUG: verificar ids antes de criar
            print(f"DEBUG: unidade.id={getattr(unidade, 'id', None)} prateleira.id={getattr(prateleira, 'id', None)}")

            nova_caixa = Caixa(
                numero_caixa=numero,
                data_criacao=datetime.datetime.now(),
                data_eliminacao=data_elim,
                unidade_id=int(unidade.id) if getattr(unidade, 'id', None) is not None else None,
                prateleira_id=int(prateleira.id) if getattr(prateleira, 'id', None) is not None else None
            )

            if selected_docs:
                nova_caixa.documentos = selected_docs

            # usa repo_caixa.add que faz flush/commit (ver arquivo do repo)
            repo_caixa.add(nova_caixa)
            print(f"Caixa {numero} criada com sucesso!")

        elif opcao == '4':
            break


# ---------------- MENU DOCUMENTO ----------------
def menu_documento():
    while True:
        print("\n--- Menu Documento ---")
        print("1. Listar todos")
        print("2. Cadastrar novo")
        print("3. Excluir")
        print("4. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            documentos = repo_documento.get_all()
            for d in documentos:
                print(f"ID: {d.id}, Título: {d.titulo}, Tipo: {d.tipo}")

        elif opcao == '2':
            titulo = input("Título: ")
            tipo = input("Tipo: ")
            data_emissao = datetime.datetime.now()
            novo_doc = Documento(titulo=titulo, tipo=tipo)
            repo_documento.add(novo_doc)
            print("Documento criado com sucesso!")

        elif opcao == '3':
            id_del = int(input("ID do documento para excluir: "))
            repo_documento.delete(id_del)
            print("Documento excluído.")

        elif opcao == '4':
            break

# ---------------- MENU PRATELEIRA ----------------
def menu_prateleira():
    while True:
        print("\n--- Menu Prateleira ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Excluir")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            prateleiras = repo_prateleira.get_all()
            for p in prateleiras:
                print(f"ID: {p.id}, Setor: {p.setor}, Corredor: {p.corredor}, Coluna: {p.coluna}, Nível: {p.nivel}")

        elif opcao == '2':
            id_busca = int(input("Digite o ID da prateleira: "))
            prateleira = repo_prateleira.get_by_id(id_busca)
            if prateleira:
                print(f"Encontrado: ID {prateleira.id}, Setor {prateleira.setor}")
            else:
                print("Prateleira não encontrada.")

        elif opcao == '3':
            setor = input("Setor: ")
            corredor = input("Corredor: ")
            coluna = int(input("Coluna: "))
            nivel = int(input("Nível: "))
            nova_prateleira = Prateleira(setor=setor, corredor=corredor, coluna=coluna, nivel=nivel)
            repo_prateleira.add(nova_prateleira)
            print("Prateleira criada com sucesso!")

        elif opcao == '4':
            id_del = int(input("ID da prateleira para excluir: "))
            repo_prateleira.delete(id_del)
            print("Prateleira excluída.")

        elif opcao == '5':
            break

# ---------------- MENU UNIDADE ----------------
def menu_unidade():
    while True:
        print("\n--- Menu Unidade ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Excluir")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            unidades = repo_unidade.get_all()
            for u in unidades:
                print(f"ID: {u.id}, Nome: {u.nome}, Código: {u.codigo}")

        elif opcao == '2':
            id_busca = int(input("Digite o ID da unidade: "))
            unidade = repo_unidade.get_by_id(id_busca)
            if unidade:
                print(f"Encontrado: ID {unidade.id}, Nome {unidade.nome}")
            else:
                print("Unidade não encontrada.")

        elif opcao == '3':
            nome = input("Nome: ")
            codigo = int(input("Código: "))
            nova_unidade = Unidade(nome=nome, codigo=codigo)
            repo_unidade.add(nova_unidade)
            print("Unidade criada com sucesso!")

        elif opcao == '4':
            id_del = int(input("ID da unidade para excluir: "))
            repo_unidade.delete(id_del)
            print("Unidade excluída.")

        elif opcao == '5':
            break

# ---------------- MENU MOVIMENTAÇÃO ----------------
def menu_movimentacao():
    while True:
        print("\n--- Menu Movimentação ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Excluir")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            movimentacoes = repo_movimentacao.get_all()
            for m in movimentacoes:
                print(f"ID: {m.id}, Tipo: {m.tipo}, Data: {m.data}, Usuário: {m.usuario_id}, Caixa: {m.caixa_id}")

        elif opcao == '2':
            id_busca = int(input("Digite o ID da movimentação: "))
            movimentacao = repo_movimentacao.get_by_id(id_busca)
            if movimentacao:
                print(f"Encontrado: ID {movimentacao.id}, Tipo {movimentacao.tipo}")
            else:
                print("Movimentação não encontrada.")

        elif opcao == '3':
            tipo = input("Tipo: ")
            data = datetime.datetime.now()
            usuario = repo_usuario.get_all()[0]
            caixa = repo_caixa.get_all()[0]
            nova_mov = Movimentacao(tipo=tipo, data=data, usuario_id=usuario.id, caixa_id=caixa.id)
            repo_movimentacao.add(nova_mov)
            print("Movimentação criada com sucesso!")

        elif opcao == '4':
            id_del = int(input("ID da movimentação para excluir: "))
            repo_movimentacao.delete(id_del)
            print("Movimentação excluída.")

        elif opcao == '5':
            break

def menu_principal():
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. Usuários")
        print("2. Caixas")
        print("3. Documentos")
        print("4. Prateleiras")
        print("5. Unidades")
        print("6. Movimentações")
        print("7. Sair")
        opcao = input("Escolha: ")

        if opcao == '1':
            menu_usuario()
        elif opcao == '2':
            menu_caixa()
        elif opcao == '3':
            menu_documento()
        elif opcao == '4':
            menu_prateleira()
        elif opcao == '5':
            menu_unidade()
        elif opcao == '6':
            menu_movimentacao()
        elif opcao == '7':
            break

def main():
    criar_dados_iniciais()
    menu_principal()


if __name__ == "__main__":
    main()
