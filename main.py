import datetime
from repository import (
    UsuarioRepository,
    CaixaRepository,
    DocumentoRepository,
    MovimentacaoRepository,
    PrateleiraRepository,
    UnidadeRepository
)
from models.models import (
    Usuario,
    Caixa,
    Documento,
    Movimentacao,
    Prateleira,
    Unidade
)


repo_usuario = UsuarioRepository()
repo_caixa = CaixaRepository()
repo_documento = DocumentoRepository()
repo_movimentacao = MovimentacaoRepository()
repo_prateleira = PrateleiraRepository()
repo_unidade = UnidadeRepository()


def criar_dados_iniciais():
    print("Verificando dados iniciais...")
    if not repo_unidade.get_unidades():
        print("Criando Unidade padrão...")
        unidade_padrao = Unidade(nome="Sede Campo Mourão", codigo=101)
        repo_unidade.add_unidade(unidade_padrao)

    if not repo_prateleira.get_prateleiras():
        print("Criando Prateleira padrão...")
        prateleira_padrao = Prateleira(setor="Arquivo Morto", corredor="A", coluna=1, nivel=1)
        repo_prateleira.add_prateleira(prateleira_padrao)
    print("Dados iniciais prontos!")


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
            usuarios = repo_usuario.get_usuarios()
            print("\n--- Lista de Usuários ---")
            for u in usuarios:
                print(f"ID: {u.id}, Nome: {u.nome}, E-mail: {u.email}, Tipo: {u.tipo}")
        elif opcao == '2':
            id_busca = int(input("Digite o ID do usuário: "))
            usuario = repo_usuario.get_usuario_by_id(id_busca)
            if usuario:
                print(f"Encontrado: ID: {usuario.id}, Nome: {usuario.nome}")
            else:
                print("Usuário não encontrado.")
        elif opcao == '3':
            email_busca = input("Digite o e-mail do usuário: ")
            usuario = repo_usuario.find_by_email(email_busca)
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
            repo_usuario.add_usuario(novo_usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso!")
        elif opcao == '5':
            break
        else:
            print("Opção inválida!")


def menu_caixa():
    while True:
        print("\n--- Menu Caixa ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Buscar por Número da Caixa")
        print("4. Cadastrar nova")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            caixas = repo_caixa.get_caixas()
            print("\n--- Lista de Caixas ---")
            for c in caixas:
                print(f"ID: {c.id}, Número: {c.numero_caixa}, Prateleira ID: {c.prateleira_id}")
        elif opcao == '2':
            id_busca = int(input("Digite o ID da caixa: "))
            caixa = repo_caixa.get_caixa_by_id(id_busca)
            if caixa:
                print(f"Encontrado: ID: {caixa.id}, Número: {caixa.numero_caixa}")
            else:
                print("Caixa não encontrada.")
        elif opcao == '3':
            num_busca = int(input("Digite o número da caixa: "))
            caixa = repo_caixa.find_by_numero_caixa(num_busca)
            if caixa:
                print(f"Encontrado: ID: {caixa.id}, Número: {caixa.numero_caixa}")
            else:
                print("Caixa não encontrada.")
        elif opcao == '4':
            numero = int(input("Número da Caixa: "))
            unidade = repo_unidade.get_unidades()[0]
            prateleira = repo_prateleira.get_prateleiras()[0]
            data_eliminacao_str = input("Data de eliminação (AAAA-MM-DD) ou deixe em branco: ")

            nova_caixa = Caixa(
                numero_caixa=numero,
                data_criacao=datetime.datetime.now(),
                unidade_id=unidade.id,
                prateleira_id=prateleira.id
            )
            if data_eliminacao_str:
                nova_caixa.data_eliminacao = datetime.datetime.strptime(data_eliminacao_str, "%Y-%m-%d")

            repo_caixa.add_caixa(nova_caixa)
            print(f"Caixa número '{numero}' cadastrada com sucesso!")
        elif opcao == '5':
            break
        else:
            print("Opção inválida!")


def menu_documento():
    while True:
        print("\n--- Menu Documento ---")
        print("1. Listar todos")
        print("2. Buscar por ID")
        print("3. Buscar por Título")
        print("4. Cadastrar novo")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            documentos = repo_documento.get_documentos()
            print("\n--- Lista de Documentos ---")
            for d in documentos:
                print(f"ID: {d.id}, Título: {d.titulo}, Tipo: {d.tipo}, Caixa ID: {d.caixa_id}")
        elif opcao == '2':
            id_busca = int(input("Digite o ID do documento: "))
            documento = repo_documento.get_documento_by_id(id_busca)
            if documento:
                print(f"Encontrado: ID: {documento.id}, Título: {documento.titulo}")
            else:
                print("Documento não encontrado.")
        elif opcao == '3':
            titulo_busca = input("Digite parte do título do documento: ")
            documentos = repo_documento.find_by_titulo(titulo_busca)
            if documentos:
                for doc in documentos:
                    print(f"Encontrado: ID: {doc.id}, Título: {doc.titulo}")
            else:
                print("Nenhum documento encontrado com esse título.")
        elif opcao == '4':
            caixas = repo_caixa.get_caixas()
            if not caixas:
                print("\nERRO: Nenhuma caixa disponível. Cadastre uma caixa primeiro.")
                continue

            print("\nCaixas disponíveis:")
            for c in caixas:
                print(f"ID: {c.id}, Número: {c.numero_caixa}")

            try:
                caixa_id = int(input("Digite o ID da Caixa onde o documento será armazenado: "))
                if not repo_caixa.get_caixa_by_id(caixa_id):
                    print("ERRO: ID da caixa inválido.")
                    continue

                titulo = input("Título do documento: ")
                tipo = input("Tipo (e.g., Relatório, Contrato): ")

                novo_documento = Documento(
                    titulo=titulo,
                    tipo=tipo,
                    caixa_id=caixa_id
                )
                repo_documento.add_documento(novo_documento)
                print(f"Documento '{titulo}' cadastrado com sucesso na caixa ID {caixa_id}!")
            except ValueError:
                print("ERRO: Entrada inválida. Por favor, insira um número para o ID.")

        elif opcao == '5':
            break
        else:
            print("Opção inválida!")


def menu_prateleira():
    while True:
        print("\n--- Menu Prateleira ---")
        print("1. Listar todas")
        print("2. Listar prateleiras vazias")
        print("3. Cadastrar nova")
        print("4. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            prateleiras = repo_prateleira.get_prateleiras()
            print("\n--- Lista de Prateleiras ---")
            for p in prateleiras:
                print(f"ID: {p.id}, Setor: {p.setor}, Corredor: {p.corredor}-{p.coluna}-{p.nivel}")
        elif opcao == '2':
            vazias = repo_prateleira.find_prateleiras_vazias()
            print("\n--- Prateleiras Vazias ---")
            if not vazias:
                print("Nenhuma prateleira vazia encontrada.")
            for p in vazias:
                print(f"ID: {p.id}, Local: {p.setor}, {p.corredor}-{p.coluna}-{p.nivel}")
        elif opcao == '3':
            setor = input("Setor: ")
            corredor = input("Corredor: ")
            coluna = int(input("Coluna: "))
            nivel = int(input("Nível: "))
            nova_prateleira = Prateleira(setor=setor, corredor=corredor, coluna=coluna, nivel=nivel)
            repo_prateleira.add_prateleira(nova_prateleira)
            print("Prateleira cadastrada com sucesso!")
        elif opcao == '4':
            break
        else:
            print("Opção inválida!")


def menu_movimentacao():
    while True:
        print("\n--- Menu Movimentação ---")
        print("1. Listar todas")
        print("2. Registrar nova movimentação (retirada)")
        print("3. Buscar movimentações de uma caixa")
        print("4. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            movs = repo_movimentacao.get_movimentacoes()
            print("\n--- Histórico de Movimentações ---")
            for m in movs:
                print(f"ID: {m.id}, Tipo: {m.tipo}, Data: {m.data.strftime('%d/%m/%Y %H:%M')}, Caixa ID: {m.caixa_id}")
        elif opcao == '2':
            usuarios = repo_usuario.get_usuarios()
            caixas = repo_caixa.get_caixas()
            if not usuarios or not caixas:
                print("\nERRO: É necessário ter pelo menos um usuário e uma caixa cadastrados.")
                continue

            print("\nUsuários disponíveis:")
            for u in usuarios: print(f"ID: {u.id}, Nome: {u.nome}")
            usuario_id = int(input("Digite o ID do usuário que está fazendo a retirada: "))

            print("\nCaixas disponíveis:")
            for c in caixas: print(f"ID: {c.id}, Número: {c.numero_caixa}")
            caixa_id = int(input("Digite o ID da caixa a ser retirada: "))

            usuario_obj = repo_usuario.get_usuario_by_id(usuario_id)
            caixa_obj = repo_caixa.get_caixa_by_id(caixa_id)

            if not usuario_obj or not caixa_obj:
                print("ERRO: ID de usuário ou caixa inválido.")
                continue

            nova_movimentacao = Movimentacao(
                tipo='retirada',
                caixa_id=caixa_obj.id
            )
            nova_movimentacao.usuarios.append(usuario_obj)

            repo_movimentacao.add_movimentacao(nova_movimentacao)
            print("Movimentação de retirada registrada com sucesso!")
        elif opcao == '3':
            caixa_id = int(input("Digite o ID da caixa para ver seu histórico: "))
            movs = repo_movimentacao.find_by_caixa_id(caixa_id)
            print(f"\n--- Histórico da Caixa ID {caixa_id} ---")
            if not movs:
                print("Nenhuma movimentação encontrada para esta caixa.")
            for m in movs:
                print(f"ID: {m.id}, Tipo: {m.tipo}, Data: {m.data.strftime('%d/%m/%Y')}")
        elif opcao == '4':
            break
        else:
            print("Opção inválida!")


def main():
    criar_dados_iniciais()
    while True:
        print("\n" + "=" * 15 + " MENU PRINCIPAL " + "=" * 15)
        print("1. Gerenciar Usuários")
        print("2. Gerenciar Caixas")
        print("3. Gerenciar Documentos")
        print("4. Gerenciar Prateleiras")
        print("5. Gerenciar Movimentações")
        print("6. Gerenciar Unidades (Simplificado)")
        print("7. Sair")
        print("=" * 48)
        opcao = input("Escolha uma área para testar: ")

        if opcao == '1':
            menu_usuario()
        elif opcao == '2':
            menu_caixa()
        elif opcao == '3':
            menu_documento()
        elif opcao == '4':
            menu_prateleira()
        elif opcao == '5':
            menu_movimentacao()
        elif opcao == '6':
            print("\n--- Lista de Unidades ---")
            unidades = repo_unidade.get_unidades()
            for u in unidades:
                print(f"ID: {u.id}, Nome: {u.nome}, Código: {u.codigo}")
            input("Pressione Enter para voltar ao menu...")
        elif opcao == '7':
            print("Saindo do sistema de testes.")
            break
        else:
            print("Opção inválida, tente novamente.")


if __name__ == "__main__":
    main()