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
        print("4. Editar caixa")
        print("5. Voltar")
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

                unidade = getattr(c, "unidade", None)
                if unidade:
                    unidade_str = f"{unidade.nome} (Código: {unidade.codigo})"
                else:
                    unidade_str = f"ID:{getattr(c, 'unidade_id', 'None')}"

                pr = getattr(c, "prateleira", None)
                if pr:
                    prateleira_str = f"{pr.setor} - Corredor:{pr.corredor} Coluna:{pr.coluna} Nível:{pr.nivel}"
                else:
                    prateleira_str = f"ID:{getattr(c, 'prateleira_id', 'None')}"

                print(f"ID: {c.id}, Número: {c.numero_caixa}, Unidade: {unidade_str}, Eliminação: {data_elim_str}, Prateleira: {prateleira_str}, Documentos: {docs_str}")

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

                unidade = getattr(caixa, "unidade", None)
                if unidade:
                    unidade_str = f"{unidade.nome} (Código: {unidade.codigo})"
                else:
                    unidade_str = f"ID:{getattr(caixa, 'unidade_id', 'None')}"

                pr = getattr(caixa, "prateleira", None)
                if pr:
                    prateleira_str = f"{pr.setor} - Corredor:{pr.corredor} Coluna:{pr.coluna} Nível:{pr.nivel}"
                else:
                    prateleira_str = f"ID:{getattr(caixa, 'prateleira_id', 'None')}"

                print(f"Encontrado: ID {caixa.id}, Número {caixa.numero_caixa}, Eliminação: {de}, Unidade: {unidade_str}, Prateleira: {prateleira_str}, Documentos: {docs_str}")
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

            documentos = repo_documento.get_all()
            selected_docs = []
            print("\nDocumentos disponíveis:")
            if documentos:
                for d in documentos:
                    print(f"ID: {d.id} - Título: {d.titulo} - Tipo: {d.tipo}")
            else:
                print("  (nenhum documento cadastrado)")
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

            nova_caixa = Caixa(
                numero_caixa=numero,
                data_criacao=datetime.datetime.now(),
                data_eliminacao=data_elim
            )
            nova_caixa.unidade = unidade
            nova_caixa.prateleira = prateleira
            if selected_docs:
                nova_caixa.documentos = selected_docs
            repo_caixa.add(nova_caixa)
            print(f"Caixa {numero} criada com sucesso!")

        elif opcao == '4':
            ## CÓDIGO ADICIONADO AQUI
            caixas_disponiveis = repo_caixa.get_all()
            if not caixas_disponiveis:
                print("Nenhuma caixa cadastrada.")
                continue
            
            print("\nCaixas disponíveis para edição:")
            for c in caixas_disponiveis:
                print(f"ID: {c.id} - Número: {c.numero_caixa}")
            
            try:
                eid = int(input("Digite o ID da caixa a editar: ").strip())
            except ValueError:
                print("ID inválido.")
                continue
            caixa = repo_caixa.get_by_id(eid)
            if not caixa:
                print("Caixa não encontrada.")
                continue

            print(f"\nEditando Caixa ID {caixa.id} - Número atual: {caixa.numero_caixa}")
            print("1. Alterar número da caixa")
            print("2. Alterar unidade")
            print("3. Alterar prateleira")
            print("4. Adicionar documentos")
            print("5. Remover documentos")
            print("6. Alterar data de eliminação")
            print("7. Cancelar")
            escolha = input("Escolha a opção a alterar: ").strip()

            if escolha == '1':
                try:
                    novo_num = int(input("Novo número da caixa: "))
                except ValueError:
                    print("Número inválido.")
                    continue
                caixa.numero_caixa = novo_num

            elif escolha == '2':
                unidades = repo_unidade.get_all()
                print("\nUnidades disponíveis:")
                for u in unidades:
                    print(f"ID: {u.id} - Nome: {u.nome} - Código: {u.codigo}")
                uid_in = input("ID da nova unidade (enter para cancelar): ").strip()
                if uid_in == "":
                    print("Operação cancelada.")
                else:
                    try:
                        uid = int(uid_in)
                    except ValueError:
                        print("ID inválido.")
                        continue
                    unidade = repo_unidade.get_by_id(uid)
                    if not unidade:
                        print("Unidade não encontrada.")
                        continue
                    caixa.unidade = unidade

            elif escolha == '3':
                prateleiras = repo_prateleira.get_all()
                print("\nPrateleiras disponíveis:")
                for p in prateleiras:
                    print(f"ID: {p.id} - Setor: {p.setor} - Corredor: {p.corredor} - Coluna: {p.coluna} - Nível: {p.nivel}")
                pid_in = input("ID da nova prateleira (enter para cancelar): ").strip()
                if pid_in == "":
                    print("Operação cancelada.")
                else:
                    try:
                        pid = int(pid_in)
                    except ValueError:
                        print("ID inválido.")
                        continue
                    prateleira = repo_prateleira.get_by_id(pid)
                    if not prateleira:
                        print("Prateleira não encontrada.")
                        continue
                    caixa.prateleira = prateleira

            elif escolha == '4':
                documentos = repo_documento.get_all()
                print("\nDocumentos disponíveis para adicionar:")
                for d in documentos:
                    print(f"ID: {d.id} - Título: {d.titulo}")
                ids_in = input("IDs para adicionar (vírgula-separados, enter para cancelar): ").strip()
                if ids_in:
                    for part in ids_in.split(','):
                        part = part.strip()
                        if not part:
                            continue
                        try:
                            did = int(part)
                        except ValueError:
                            print(f"Ignorando ID inválido: {part}")
                            continue
                        doc = repo_documento.get_by_id(did)
                        if doc and doc not in (caixa.documentos or []):
                            caixa.documentos.append(doc)
                    print("Documentos adicionados (se válidos).")

            elif escolha == '5':
                docs = caixa.documentos or []
                if not docs:
                    print("Caixa não tem documentos associados.")
                else:
                    print("\nDocumentos atuais na caixa:")
                    for d in docs:
                        print(f"ID: {d.id} - Título: {d.titulo}")
                    ids_out = input("IDs para remover (vírgula-separados, enter para cancelar): ").strip()
                    if ids_out:
                        for part in ids_out.split(','):
                            part = part.strip()
                            if not part:
                                continue
                            try:
                                did = int(part)
                            except ValueError:
                                print(f"Ignorando ID inválido: {part}")
                                continue
                            caixa.documentos = [d for d in caixa.documentos if d.id != did]
                        print("Remoções aplicadas.")

            elif escolha == '6':
                di = input("Nova data de eliminação (enter para CAIXA PERMANENTE / vazio cancela): ").strip()
                if di == "":
                    caixa.data_eliminacao = None
                else:
                    nd = parse_data_flexivel(di)
                    if nd is None:
                        print("Formato de data inválido.")
                        continue
                    if hasattr(caixa, "data_eliminacao"):
                        caixa.data_eliminacao = nd

            elif escolha == '7':
                print("Edição cancelada.")
                continue

            # salvar alterações
            repo_caixa.update(caixa)
            print("Alterações salvas com sucesso.")

        elif opcao == '5':
            break


# ---------------- MENU DOCUMENTO ----------------
def menu_documento():
    while True:
        print("\n--- Menu Documento ---")
        print("1. Listar todos")
        print("2. Cadastrar novo")
        print("3. Editar documento")
        print("4. Excluir")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            documentos = repo_documento.get_all()
            for d in documentos:
                de_str = d.data_emissao.strftime("%Y-%m-%d") if getattr(d, "data_emissao", None) else "Sem data"
                print(f"ID: {d.id}, Título: {d.titulo}, Tipo: {d.tipo}, Data Emissão: {de_str}")

        elif opcao == '2':
            titulo = input("Título: ")
            tipo = input("Tipo: ")
            # opcional: pedir data de emissão
            data_input = input("Data de emissão (enter para usar data atual / vazio para sem data) [dd-mm-YYYY | dd/mm/YYYY | YYYY-mm-dd]: ").strip()
            if data_input == "":
                data_emissao = datetime.datetime.now()
            else:
                data_emissao = parse_data_flexivel(data_input)
                if data_emissao is None:
                    print("Formato de data inválido. Documento não criado.")
                    continue
            novo_doc = Documento(titulo=titulo, tipo=tipo)
            # atribuir data_emissao somente se modelo/tabela suportarem
            if hasattr(novo_doc, "data_emissao"):
                novo_doc.data_emissao = data_emissao
            repo_documento.add(novo_doc)
            print("Documento criado com sucesso!")

        elif opcao == '3':
            ## CÓDIGO ADICIONADO AQUI
            documentos_disponiveis = repo_documento.get_all()
            if not documentos_disponiveis:
                print("Nenhum documento cadastrado.")
                continue

            print("\nDocumentos disponíveis para edição:")
            for d in documentos_disponiveis:
                print(f"ID: {d.id} - Título: {d.titulo}")

            try:
                id_edit = int(input("ID do documento para editar: "))
            except ValueError:
                print("ID inválido.")
                continue
            doc = repo_documento.get_by_id(id_edit)
            if not doc:
                print("Documento não encontrado.")
                continue

            print(f"\nEditando Documento ID {doc.id}")
            print(f"1. Título (atual: {doc.titulo})")
            print(f"2. Tipo (atual: {doc.tipo})")
            current_de = doc.data_emissao.strftime('%Y-%m-%d') if getattr(doc, 'data_emissao', None) else 'Sem data'
            print(f"3. Data de Emissão (atual: {current_de})")
            print("4. Cancelar")
            opt = input("Escolha o campo a alterar: ").strip()

            if opt == '1':
                novo_titulo = input("Novo título (enter para manter atual): ").strip()
                if novo_titulo != "":
                    doc.titulo = novo_titulo
            elif opt == '2':
                novo_tipo = input("Novo tipo (enter para manter atual): ").strip()
                if novo_tipo != "":
                    doc.tipo = novo_tipo
            elif opt == '3':
                di = input("Nova data de emissão (enter para remover / vazio cancela) [dd-mm-YYYY | dd/mm/YYYY | YYYY-mm-dd]: ").strip()
                if di == "":
                    # remover data
                    if hasattr(doc, "data_emissao"):
                        doc.data_emissao = None
                else:
                    nd = parse_data_flexivel(di)
                    if nd is None:
                        print("Formato de data inválido. Alteração cancelada.")
                        continue
                    if hasattr(doc, "data_emissao"):
                        doc.data_emissao = nd
            else:
                print("Edição cancelada.")
                continue

            repo_documento.update(doc)
            print("Documento atualizado com sucesso.")

        elif opcao == '4':
            try:
                id_del = int(input("ID do documento para excluir: "))
            except ValueError:
                print("ID inválido.")
                continue
            repo_documento.delete(id_del)
            print("Documento excluído.")

        elif opcao == '5':
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
            try:
                id_busca = int(input("Digite o ID da movimentação: "))
            except ValueError:
                print("ID inválido.")
                continue
            movimentacao = repo_movimentacao.get_by_id(id_busca)
            if movimentacao:
                print(f"Encontrado: ID {movimentacao.id}, Tipo {movimentacao.tipo}")
            else:
                print("Movimentação não encontrada.")

        elif opcao == '3':
            # 1. Obter e listar usuários disponíveis
            usuarios_disp = repo_usuario.get_all()
            if not usuarios_disp:
                print("Erro: Nenhum usuário cadastrado para associar à movimentação. Crie um usuário primeiro.")
                continue

            print("\nUsuários disponíveis:")
            for u in usuarios_disp:
                print(f"ID: {u.id} - Nome: {u.nome}")

            try:
                usuario_id_input = int(input("ID do usuário para a movimentação: ").strip())
            except ValueError:
                print("ID de usuário inválido.")
                continue

            usuario = repo_usuario.get_by_id(usuario_id_input)
            if not usuario:
                print("Usuário não encontrado. Tente novamente.")
                continue

            # 2. Obter e listar caixas disponíveis
            caixas_disp = repo_caixa.get_all()
            if not caixas_disp:
                print("Erro: Nenhuma caixa cadastrada para associar à movimentação. Crie uma caixa primeiro.")
                continue

            print("\nCaixas disponíveis:")
            for c in caixas_disp:
                print(f"ID: {c.id} - Número: {c.numero_caixa}")

            try:
                caixa_id_input = int(input("ID da caixa para a movimentação: ").strip())
            except ValueError:
                print("ID de caixa inválido.")
                continue

            caixa = repo_caixa.get_by_id(caixa_id_input)
            if not caixa:
                print("Caixa não encontrada. Tente novamente.")
                continue

            # 3. Criar a nova movimentação com os IDs válidos
            tipo = input("Tipo da movimentação: ")
            data = datetime.datetime.now()

            # ESTA É A FORMA QUE DEVE FUNCIONAR AGORA, PASSANDO OS IDs.
            nova_mov = Movimentacao(
                tipo=tipo,
                data=data,
                usuario=usuario,
                caixa=caixa
            )

            repo_movimentacao.add(nova_mov)
            print("Movimentação criada com sucesso!")

        elif opcao == '4':
            try:
                id_del = int(input("ID da movimentação para excluir: "))
            except ValueError:
                print("ID inválido.")
                continue
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
