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
        print("2. Buscar por Número da Caixa")
        print("3. Cadastrar nova (vazia)")
        print("4. Gerenciar conteúdo da caixa")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            caixas = repo_caixa.get_caixas()
            print("\n" + "=" * 60)
            print("--- Lista Completa de Caixas ---")
            print("=" * 60)
            for c in caixas:
                if c.prateleira:
                    localizacao = f"Local: {c.prateleira.setor} - Corredor {c.prateleira.corredor}, Coluna {c.prateleira.coluna}, Nível {c.prateleira.nivel}"
                else:
                    localizacao = "Sem prateleira associada."

                eliminacao_str = f" | Eliminar em: {c.data_eliminacao.strftime('%d/%m/%Y')}" if c.data_eliminacao else " | Eliminação: Indeterminada"

                print(f"\n[ CAIXA ID: {c.id} | NÚMERO: {c.numero_caixa}{eliminacao_str} ]")
                print(f"  {localizacao}")

                if c.documento:
                    print("  Conteúdo:")
                    print(f"    - ID: {c.documento.id}, Título: {c.documento.titulo} (Tipo: {c.documento.tipo})")
                else:
                    print("  Conteúdo: A caixa está vazia.")
                print("-" * 60)

        elif opcao == '2':
            num_busca = int(input("Digite o NÚMERO da caixa a ser buscada: "))
            caixa = repo_caixa.find_by_numero_caixa(num_busca)

            if caixa:
                print("\n" + "=" * 50)
                print("--- Detalhes da Caixa Encontrada ---")
                print("=" * 50)

                if caixa.prateleira:
                    localizacao = f"Local: {caixa.prateleira.setor} - Corredor {caixa.prateleira.corredor}, Coluna {caixa.prateleira.coluna}, Nível {caixa.prateleira.nivel}"
                else:
                    localizacao = "Sem prateleira associada."

                eliminacao_str = f" | Eliminar em: {caixa.data_eliminacao.strftime('%d/%m/%Y')}" if caixa.data_eliminacao else ""

                print(f"\n[ CAIXA ID: {caixa.id} | NÚMERO: {caixa.numero_caixa}{eliminacao_str} ]")
                print(f"  {localizacao}")
                print(f"  Data de Criação: {caixa.data_criacao.strftime('%d/%m/%Y')}")

                if caixa.documento:
                    print("  Conteúdo:")
                    print(
                        f"    - ID: {caixa.documento.id}, Título: {caixa.documento.titulo} (Tipo: {caixa.documento.tipo})")
                else:
                    print("  Conteúdo: A caixa está vazia.")
                print("-" * 50)
            else:
                print("Caixa com este número não foi encontrada.")

        elif opcao == '3':
            numero = int(input("Número da Caixa: "))
            unidade = repo_unidade.get_unidades()[0]
            prateleira = repo_prateleira.get_prateleiras()[0]
            data_eliminacao_str = input("Data de eliminação da caixa (ex: 10/12/2026) ou deixe em branco: ")

            nova_caixa = Caixa(
                numero_caixa=numero,
                data_criacao=datetime.datetime.now(),
                unidade_id=unidade.id,
                prateleira_id=prateleira.id
            )
            if data_eliminacao_str:
                data_convertida = parse_data_flexivel(data_eliminacao_str)
                if data_convertida:
                    nova_caixa.data_eliminacao = data_convertida
                else:
                    print("\nERRO: Formato de data inválido! A caixa foi salva sem data de eliminação.")

            repo_caixa.add_caixa(nova_caixa)
            print(f"Caixa VAZIA número '{numero}' cadastrada com sucesso!")

        elif opcao == '4':
            id_gerenciar = int(input("Digite o ID da caixa que deseja gerenciar: "))
            caixa = repo_caixa.get_caixa_by_id(id_gerenciar)
            if caixa:
                while True:
                    print("\n" + "=" * 50)
                    print(f"--- Gerenciando Caixa Nº {caixa.numero_caixa} (ID: {caixa.id}) ---")
                    print("  Conteúdo Atual:")
                    if caixa.documento:
                        print(f"    - ID: {caixa.documento.id}, Título: {caixa.documento.titulo}")
                    else:
                        print("    A caixa está vazia.")
                    print("=" * 50)

                    print("\nOpções de Gerenciamento de Conteúdo:")
                    print("1. Atribuir ou Trocar Documento")
                    print("2. Desvincular Documento (esvaziar caixa)")
                    print("3. Concluir gerenciamento")
                    sub_opcao = input("Escolha uma opção: ")

                    if sub_opcao == '1':
                        docs = repo_documento.get_documentos()
                        if not docs:
                            print("\nNão há documentos cadastrados no sistema para atribuir.")
                            continue

                        print("\n--- Documentos Disponíveis ---")
                        for doc in docs:
                            caixas_associadas = [str(c.numero_caixa) for c in doc.caixas]
                            local = f"Nas Caixas: {', '.join(caixas_associadas)}" if caixas_associadas else "Sem caixa"
                            print(f"ID: {doc.id}, Título: {doc.titulo} ({local})")

                        try:
                            doc_id = int(input("Digite o ID do documento para colocar nesta caixa: "))
                            doc_atribuir = repo_documento.get_documento_by_id(doc_id)

                            if doc_atribuir:
                                caixa.documento_id = doc_atribuir.id
                                repo_caixa.update_caixa(caixa)
                                print("Documento atribuído com sucesso!")
                                caixa = repo_caixa.get_caixa_by_id(id_gerenciar)
                            else:
                                print("ID de documento inválido.")
                        except ValueError:
                            print("ERRO: Entrada inválida.")

                    elif sub_opcao == '2':
                        if caixa.documento:
                            caixa.documento_id = None
                            repo_caixa.update_caixa(caixa)
                            print("Documento desvinculado. A caixa agora está vazia.")
                            caixa = repo_caixa.get_caixa_by_id(id_gerenciar)
                        else:
                            print("A caixa já está vazia.")

                    elif sub_opcao == '3':
                        break
                    else:
                        print("Opção inválida.")
            else:
                print("Caixa não encontrada.")
        elif opcao == '5':
            break
        else:
            print("Opção inválida!")


def menu_documento():
    while True:
        print("\n--- Menu Documento ---")
        print("1. Listar todos")
        print("2. Cadastrar novo documento")
        print("3. Ver em quais caixas um documento está")
        print("4. Excluir um documento permanentemente")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            docs = repo_documento.get_documentos()
            print("\n--- Lista de Documentos ---")
            for d in docs:
                print(f"ID: {d.id}, Título: {d.titulo} (Tipo: {d.tipo})")
        elif opcao == '2':
            titulo = input("Título do novo documento: ")
            tipo = input("Tipo (e.g., Relatório, Contrato): ")
            novo_documento = Documento(titulo=titulo, tipo=tipo)
            repo_documento.add_documento(novo_documento)
            print(f"Documento '{titulo}' cadastrado com sucesso.")
        elif opcao == '3':
            doc_id = int(input("Digite o ID do documento para verificar: "))
            doc = repo_documento.get_documento_by_id(doc_id)
            if doc:
                print(f"\n--- O documento '{doc.titulo}' está nas seguintes caixas: ---")
                if doc.caixas:
                    for c in doc.caixas: print(f" - Caixa Nº {c.numero_caixa} (ID: {c.id})")
                else:
                    print("O documento não está em nenhuma caixa.")
            else:
                print("Documento não encontrado.")
        elif opcao == '4':
            doc_id = int(input("Digite o ID do documento a ser EXCLUÍDO PERMANENTEMENTE: "))
            doc_excluir = repo_documento.get_documento_by_id(doc_id)
            if doc_excluir:
                confirmar = input(
                    f"Tem certeza que deseja apagar para sempre o documento '{doc_excluir.titulo}'? Esta ação não pode ser desfeita. (s/n): ").lower()
                if confirmar == 's':
                    repo_documento.delete_documento(doc_id)
                    print("Documento excluído com sucesso!")
            else:
                print("Documento não encontrado.")
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
        print("4. Alterar prateleira")
        print("5. Voltar ao menu principal")
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
            id_alterar = int(input("Digite o ID da prateleira que deseja alterar: "))
            prateleira = repo_prateleira.get_prateleira_by_id(id_alterar)
            if prateleira:
                print(f"Alterando prateleira ID {prateleira.id}")
                novo_setor = input(f"Novo setor (atual: {prateleira.setor}): ")
                novo_corredor = input(f"Novo corredor (atual: {prateleira.corredor}): ")
                nova_coluna = int(input(f"Nova coluna (atual: {prateleira.coluna}): "))
                novo_nivel = int(input(f"Novo nível (atual: {prateleira.nivel}): "))

                prateleira.setor = novo_setor
                prateleira.corredor = novo_corredor
                prateleira.coluna = nova_coluna
                prateleira.nivel = novo_nivel

                repo_prateleira.update_prateleira(prateleira)
                print("Prateleira alterada com sucesso!")
            else:
                print("Prateleira não encontrada.")
        elif opcao == '5':
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
                nome_usuario = m.usuario.nome if m.usuario else "Usuário Desconhecido"
                print(
                    f"ID: {m.id}, Tipo: {m.tipo}, Data: {m.data.strftime('%d/%m/%Y %H:%M')}, Caixa ID: {m.caixa_id}, Usuário: {nome_usuario}")
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

            if not repo_usuario.get_usuario_by_id(usuario_id) or not repo_caixa.get_caixa_by_id(caixa_id):
                print("ERRO: ID de usuário ou caixa inválido.")
                continue

            nova_movimentacao = Movimentacao(
                tipo='retirada',
                data=datetime.datetime.now(),
                caixa_id=caixa_id,
                usuario_id=usuario_id
            )

            repo_movimentacao.add_movimentacao(nova_movimentacao)
            print("Movimentação de retirada registrada com sucesso!")
        elif opcao == '3':
            caixa_id = int(input("Digite o ID da caixa para ver seu histórico: "))
            movs = repo_movimentacao.find_by_caixa_id(caixa_id)
            print(f"\n--- Histórico da Caixa ID {caixa_id} ---")
            if not movs:
                print("Nenhuma movimentação encontrada para esta caixa.")
            for m in movs:
                nome_usuario = m.usuario.nome if m.usuario else "Usuário Desconhecido"
                print(f"ID: {m.id}, Tipo: {m.tipo}, Data: {m.data.strftime('%d/%m/%Y')}, Usuário: {nome_usuario}")
        elif opcao == '4':
            break
        else:
            print("Opção inválida!")


def menu_unidade():
    while True:
        print("\n--- Menu Unidade ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Alterar unidade")
        print("5. Excluir unidade")
        print("6. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            unidades = repo_unidade.get_unidades()
            print("\n--- Lista de Unidades ---")
            for u in unidades:
                print(f"ID: {u.id}, Nome: {u.nome}, Código: {u.codigo}")
        elif opcao == '2':
            id_busca = int(input("Digite o ID da unidade: "))
            unidade = repo_unidade.get_unidade_by_id(id_busca)
            if unidade:
                print(f"Encontrado: ID: {unidade.id}, Nome: {unidade.nome}, Código: {unidade.codigo}")
            else:
                print("Unidade não encontrada.")
        elif opcao == '3':
            nome = input("Nome da nova unidade: ")
            codigo = int(input("Código da nova unidade: "))
            nova_unidade = Unidade(nome=nome, codigo=codigo)
            repo_unidade.add_unidade(nova_unidade)
            print("Unidade cadastrada com sucesso!")
        elif opcao == '4':
            id_alterar = int(input("Digite o ID da unidade que deseja alterar: "))
            unidade = repo_unidade.get_unidade_by_id(id_alterar)
            if unidade:
                print(f"Alterando dados da unidade: {unidade.nome}")
                novo_nome = input(f"Novo nome (atual: {unidade.nome}): ")
                novo_codigo = int(input(f"Novo código (atual: {unidade.codigo}): "))

                unidade.nome = novo_nome
                unidade.codigo = novo_codigo

                repo_unidade.update_unidade(unidade)
                print("Unidade alterada com sucesso!")
            else:
                print("Unidade não encontrada.")
        elif opcao == '5':
            id_deletar = int(input("Digite o ID da unidade que deseja excluir: "))

            caixas_na_unidade = repo_caixa.find_by_unidade_id(id_deletar)
            if caixas_na_unidade:
                print("\nERRO: Esta unidade não pode ser excluída, pois existem caixas associadas a ela.")
                print("Mova ou exclua as caixas antes de excluir a unidade.")
                continue

            if repo_unidade.delete_unidade(id_deletar):
                print("Unidade excluída com sucesso!")
            else:
                print("Erro: Unidade não encontrada.")
        elif opcao == '6':
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
        print("6. Gerenciar Unidades")
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
            menu_unidade()
        elif opcao == '7':
            print("Saindo do sistema de testes.")
            break
        else:
            print("Opção inválida, tente novamente.")


if __name__ == "__main__":
    main()