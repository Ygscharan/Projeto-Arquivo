import datetime

from models.models import Usuario, Caixa, Documento, Prateleira, Unidade, Movimentacao
from services.auth_service import initialize_firebase, login_with_email_password
import getpass
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
        prateleira_padrao = Prateleira(setor="Arquivo Morto", corredor="1", max_colunas=6, max_niveis=5)
        repo_prateleira.add(prateleira_padrao)
    print("Dados iniciais prontos!")


def listar_todas_prateleiras():
    prateleiras = repo_prateleira.get_all()
    for p in prateleiras:
        print(f"ID: {p.id}, Setor: {p.setor}, Corredor: {p.corredor}, Coluna: {p.max_colunas}, Nível: {p.max_niveis}")

def listar_todas_caixas():
    caixas = repo_caixa.get_all()
    print("\n--- Todas as Caixas ---")
    for c in caixas:
        # Verifica se a caixa tem uma prateleira associada
        if c.prateleira:
            localizacao = f"Prateleira ID {c.prateleira.id} (Nível: {c.nivel}, Coluna: {c.coluna})"
        else:
            localizacao = "Sem prateleira (Avulsa)"
        
        data_elim = c.data_eliminacao.strftime('%d/%m/%Y') if c.data_eliminacao else "Permanente"
        
        print(f"Número: {c.numero_caixa}, Localização: {localizacao}, Data Eliminação: {data_elim}")

def buscar_prateleira_por_id():
    id_busca = int(input("Digite o ID da prateleira: "))
    prateleira = repo_prateleira.get_by_id(id_busca)
    if prateleira:
        print(f"Encontrado: ID {prateleira.id}, Setor {prateleira.setor}, Corredor {prateleira.corredor}")
    else:
        print("Prateleira não encontrada.")

def listar_prateleiras_vazias():
    prateleiras = repo_prateleira.get_all()
    vazias = [p for p in prateleiras if not getattr(p, 'caixas', [])]
    if vazias:
        for p in vazias:
            print(f"ID: {p.id}, Setor: {p.setor}, Corredor: {p.corredor}")
    else:
        print("Não há prateleiras vazias.")

def listar_caixas_de_prateleira():
    id_prateleira = int(input("Digite o ID da prateleira: "))
    prateleira = repo_prateleira.get_by_id(id_prateleira)
    if not prateleira:
        print("Prateleira não encontrada.")
        return
        
    caixas = getattr(prateleira, 'caixas', [])
    print(f"\n--- Caixas na Prateleira ID {id_prateleira} ---")
    if caixas:
        for c in caixas:

            localizacao = f"Nível: {c.nivel}, Coluna: {c.coluna}"
            data_elim = c.data_eliminacao.strftime('%d/%m/%Y') if c.data_eliminacao else "Permanente"
            print(f"Número: {c.numero_caixa}, {localizacao}, Data Eliminação: {data_elim}")
    else:
        print("Esta prateleira não possui caixas.")

def contar_caixas_por_prateleira():
    prateleiras = repo_prateleira.get_all()
    for p in prateleiras:
        total_caixas = len(getattr(p, 'caixas', []))
        print(f"Prateleira ID {p.id} ({p.setor}): {total_caixas} caixa(s)")

def caixas_vencidas():
    hoje = datetime.datetime.now()
    caixas = repo_caixa.get_all()
    vencidas = [c for c in caixas if c.data_eliminacao and c.data_eliminacao < hoje]
    print("\n--- Caixas com Data de Eliminação Vencida ---")
    if vencidas:
        for c in vencidas:
            print(f"Número: {c.numero_caixa}, Prateleira ID: {c.prateleira_id}, Data Eliminação: {c.data_eliminacao.strftime('%d/%m/%Y')}")
    else:
        print("Nenhuma caixa vencida encontrada.")

def corredores_lotados():
    todas = repo_prateleira.get_all()
    corredores = {}
    for p in todas:
        key = f"{p.setor}-{p.corredor}"
        corredores.setdefault(key, []).append(len(getattr(p, 'caixas', [])))
    
    for key, ocupacoes in corredores.items():
        total_colunas = 6
        total_niveis = max(p.max_niveis for p in todas if f"{p.setor}-{p.corredor}" == key)
        capacidade = total_colunas * total_niveis
        ocupadas = sum(ocupacoes)
        print(f"Corredor {key}: {ocupadas}/{capacidade} ocupadas")

def ranking_prateleiras():
    todas = repo_prateleira.get_all()
    ranking = sorted(todas, key=lambda p: len(getattr(p, 'caixas', [])), reverse=True)
    for idx, p in enumerate(ranking, 1):
        total_caixas = len(getattr(p, 'caixas', []))
        print(f"{idx}. Prateleira ID {p.id} ({p.setor}-{p.corredor}): {total_caixas} caixa(s)")

def mostrar_prateleira(prateleira, prateleiras_mesmo_setor):
    """
    Exibe a prateleira em forma de tabela, no padrão solicitado.
    """

    max_colunas = max(p.max_colunas for p in prateleiras_mesmo_setor)
    max_niveis = max(p.max_niveis for p in prateleiras_mesmo_setor)

    
    caixas = {}
    for p in prateleiras_mesmo_setor:        
        for caixa in getattr(p, 'caixas', []):
            try:
                nivel = int(getattr(caixa, 'nivel', p.nivel))
                coluna = int(getattr(caixa, 'coluna', p.coluna))
                caixas[(nivel, coluna)] = str(caixa.numero_caixa)
            except Exception:
                continue

    
    print(f"\nPrateleira: {prateleira.setor} | Corredor: {prateleira.corredor}")
    col_width = 8

    
    sep = "+" + "+".join(["-" * col_width for _ in range(max_colunas + 1)]) + "+"

    
    print(sep)
    header = ["Nível"] + [str(c) for c in range(1, max_colunas + 1)]
    print("|" + "|".join(f"{h:^{col_width}}" for h in header) + "|")
    print(sep)

    
    for n in range(1, max_niveis + 1):
        row = [f"{n:^{col_width}}"]
        for c in range(1, max_colunas + 1):
            valor = caixas.get((n, c), "-")
            row.append(f"{valor:^{col_width}}")
        print("|" + "|".join(row) + "|")
        print(sep)



def visualizar_prateleira_tabela(prateleira_id):
    prateleira = repo_prateleira.get_by_id(prateleira_id)
    if not prateleira:
        print("Prateleira não encontrada.")
        return

    # Mesmas prateleiras do mesmo setor/corredor
    todas = repo_prateleira.get_all()
    mesmas = [p for p in todas if p.setor == prateleira.setor and str(p.corredor) == str(prateleira.corredor)]
    
    try:
        niveis_existentes = set(int(p.max_niveis) for p in mesmas)
        colunas_existentes = set(int(p.max_colunas) for p in mesmas)
        
        # Define 6 colunas como padrão se não houver um valor específico
        max_cols = max(colunas_existentes) if colunas_existentes else 6
        max_nivs = max(niveis_existentes) if niveis_existentes else 1

        colunas = list(range(1, max_cols + 1))
        
        tabela = {nivel: {col: '-' for col in colunas} for nivel in range(1, max_nivs + 1)}
        
        for p in mesmas:
            for c in getattr(p, 'caixas', []):
                # VERIFICAÇÃO ADICIONADA: Ignora caixas sem posição definida
                if c.nivel is not None and c.coluna is not None:
                    # Garante que a posição da caixa está dentro dos limites da tabela
                    nivel_caixa = int(c.nivel)
                    coluna_caixa = int(c.coluna)
                    if nivel_caixa in tabela and coluna_caixa in tabela[nivel_caixa]:
                        tabela[nivel_caixa][coluna_caixa] = str(c.numero_caixa)
    except (ValueError, TypeError) as e:
        print(f"Erro ao processar dimensões da prateleira: {e}")
        return
    
    col_width = 8
    header = ["Nível"] + [str(col) for col in colunas]
    sep = "+" + "+".join(["-"*col_width for _ in header]) + "+"
    print(f"\nPrateleira: {prateleira.setor} | Corredor: {prateleira.corredor}")
    print(sep)
    print("|" + "|".join(f"{h:^{col_width}}" for h in header) + "|")
    print(sep)
    for nivel in range(1, max_nivs + 1):
        row = [f"{nivel:^{col_width}}"]
        for col in colunas:
            row.append(f"{tabela[nivel][col]:^{col_width}}")
        print("|" + "|".join(row) + "|")
        print(sep)



# ---------------- MENU USUÁRIO ----------------
def menu_usuario():
    while True:
        print("\n--- Menu Usuário ---")
        print("1. Listar todos")
        print("2. Buscar por ID")
        print("3. Buscar por E-mail")
        print("4. Cadastrar novo")
        print("5. Alterar informações") # NOVA OPÇÃO
        print("6. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            usuarios = repo_usuario.get_all()
            for u in usuarios:
                print(f"ID: {u.id}, Nome: {u.nome}, E-mail: {u.email}, Tipo: {u.tipo}")
        
        elif opcao == '2':
            try:
                id_busca = int(input("Digite o ID do usuário: "))
            except ValueError:
                print("ID inválido.")
                continue
            usuario = repo_usuario.get_by_id(id_busca)
            if usuario:
                print(f"Encontrado: ID {usuario.id}, Nome {usuario.nome}")
            else:
                print("Usuário não encontrado.")

        elif opcao == '3':
            email_busca = input("Digite o e-mail do usuário: ")
            usuario = repo_usuario.get_by_email(email_busca)
            if usuario:
                print(f"Encontrado: ID {usuario.id}, Nome {usuario.nome}, E-mail {usuario.email}")
            else:
                print("Usuário não encontrado.")

        elif opcao == '4':
            nome = input("Nome do novo usuário: ")
            email = input("E-mail: ")
            senha = input("Senha: ")
            tipo = input("Tipo (Ex: admin, normal): ")
            novo_usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
            repo_usuario.add(novo_usuario)
            print("Usuário criado com sucesso!")

        elif opcao == '5':
            alterar_usuario() 

        elif opcao == '6':
            break

def alterar_usuario():
    """Função para alterar informações de um usuário existente."""
    try:
        id_alterar = int(input("Digite o ID do usuário que deseja alterar: "))
    except ValueError:
        print("ID inválido.")
        return

    usuario = repo_usuario.get_by_id(id_alterar)
    if not usuario:
        print("Usuário não encontrado.")
        return

    print(f"Alterando usuário: ID {usuario.id}, Nome {usuario.nome}")
    
    # Pergunta por novas informações, mantendo as antigas se o campo for deixado em branco
    novo_nome = input(f"Novo nome (atual: {usuario.nome}): ")
    if novo_nome:
        usuario.nome = novo_nome

    novo_email = input(f"Novo e-mail (atual: {usuario.email}): ")
    if novo_email:
        usuario.email = novo_email

    nova_senha = input(f"Nova senha (atual: {usuario.senha}): ")
    if nova_senha:
        usuario.senha = nova_senha

    novo_tipo = input(f"Novo tipo (atual: {usuario.tipo}): ")
    if novo_tipo:
        usuario.tipo = novo_tipo

    repo_usuario.update(usuario)
    print("Informações do usuário alteradas com sucesso!")


# ---------------- MENU CAIXA ----------------
def menu_caixa():
    while True:
        print("\n--- Menu Caixa ---")
        print("1. Listar todas")
        print("2. Buscar por ID")
        print("3. Cadastrar nova")
        print("4. Editar caixa")
        print("5. Mover caixas avulsas para prateleiras")
        print("6. Excluir caixa") 
        print("7. Voltar")        
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
                    prateleira_str = f"{pr.setor} - Corredor:{pr.corredor} Coluna:{c.coluna} Nível:{c.nivel}"
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
                print(f"ID: {p.id} - Setor: {p.setor} - Corredor: {p.corredor} - Max Colunas: {p.max_colunas} - Max Níveis: {p.max_niveis}")
            pr_input = input("ID da prateleira para associar (enter para deixar como avulsa): ").strip()
            
            prateleira = None
            if pr_input:
                try:
                    pid = int(pr_input)
                    prateleira = repo_prateleira.get_by_id(pid)
                    if not prateleira:
                        print("Prateleira não encontrada. A caixa será criada como avulsa.")
                except ValueError:
                    print("ID de prateleira inválido. A caixa será criada como avulsa.")

            coluna_alocar = None
            nivel_alocar = None

            if prateleira:
                print(f"Buscando espaço na prateleira ID {prateleira.id}...")
                caixas_na_prateleira = repo_caixa.get_by_prateleira(prateleira.id)
                posicoes_ocupadas = set(
                    (int(c.coluna), int(c.nivel)) 
                    for c in caixas_na_prateleira 
                    if c.coluna is not None and c.nivel is not None
                )

                max_col = int(prateleira.max_colunas)
                max_niv = int(prateleira.max_niveis)
                
                slot_encontrado = False
                for nivel_atual in range(1, max_niv + 1):
                    for coluna_atual in range(1, max_col + 1):
                        if (coluna_atual, nivel_atual) not in posicoes_ocupadas:
                            coluna_alocar = coluna_atual
                            nivel_alocar = nivel_atual
                            slot_encontrado = True
                            break
                    if slot_encontrado:
                        break
                
                if not slot_encontrado:
                    print(f"AVISO: A prateleira '{prateleira.setor}' está cheia! A caixa será criada como avulsa.")
                    prateleira = None 
            
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

            nova_caixa = Caixa(
                numero_caixa=numero,
                data_criacao=datetime.datetime.now(),
                data_eliminacao=data_elim,
                coluna=str(coluna_alocar) if coluna_alocar is not None else None,
                nivel=str(nivel_alocar) if nivel_alocar is not None else None
            )
            
            nova_caixa.unidade = unidade
            if prateleira:
                nova_caixa.prateleira = prateleira
            if selected_docs:
                nova_caixa.documentos = selected_docs
            repo_caixa.add(nova_caixa)

            if prateleira:
                print(f"Caixa {numero} criada e alocada AUTOMATICAMENTE na prateleira '{prateleira.setor}' (Coluna: {coluna_alocar}, Nível: {nivel_alocar})!")
            else:
                print(f"Caixa {numero} criada como avulsa (sem prateleira)!")

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
                    print(f"ID: {p.id} - Setor: {p.setor} - Corredor: {p.corredor} - Max Colunas: {p.max_colunas} - Max Níveis: {p.max_niveis}")
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
            caixas_avulsas = [c for c in repo_caixa.get_all() if getattr(c, 'prateleira', None) is None and (getattr(c, 'prateleira_id', None) is None or getattr(c, 'prateleira_id', 0) == 0)]
            if not caixas_avulsas:
                print("Nenhuma caixa avulsa encontrada.")
                return
            print(f"Foram encontradas {len(caixas_avulsas)} caixas avulsas.")
            
            prateleiras = repo_prateleira.get_all()
            setores = sorted(set(p.setor for p in prateleiras))
            if not setores:
                print("Nenhum setor cadastrado.")
                return
            print("Setores disponíveis:")
            for idx, setor in enumerate(setores, 1):
                print(f"{idx}. {setor}")
            while True:
                try:
                    setor_idx = int(input("Escolha o número do setor para mover as caixas: "))
                    if 1 <= setor_idx <= len(setores):
                        setor_escolhido = setores[setor_idx-1]
                        break
                    else:
                        print("Número inválido.")
                except ValueError:
                    print("Digite um número válido.")
            
            prateleiras_validas = []
            prateleiras_invalidas = []
            for p in prateleiras:
                if p.setor == setor_escolhido:
                    try:
                        _ = int(p.corredor)
                        _ = int(p.max_colunas)
                        _ = int(p.max_niveis)
                        prateleiras_validas.append(p)
                    except (ValueError, TypeError):
                        prateleiras_invalidas.append(p)
            if prateleiras_invalidas:
                print(f"Atenção: {len(prateleiras_invalidas)} prateleira(s) ignorada(s) por conterem valores não numéricos em corredor, coluna ou nível.")
            prateleiras_setor = sorted(prateleiras_validas, key=lambda p: (int(p.corredor), int(p.max_colunas), int(p.max_niveis)))
            if not prateleiras_setor:
                print("Nenhuma prateleira válida encontrada para o setor escolhido.")
                return
            for caixa in caixas_avulsas:
                alocada = False
                for p in prateleiras_setor:
                    
                    ocupada = False
                    for c in getattr(p, 'caixas', []):
                        if getattr(c, 'nivel', p.max_niveis) == p.max_niveis and getattr(c, 'coluna', p.max_colunas) == p.max_colunas:
                            ocupada = True
                            break
                    if not ocupada:
                        caixa.prateleira = p
                        caixa.nivel = p.max_niveis
                        caixa.coluna = p.max_colunas
                        repo_caixa.update(caixa)
                        print(f"Caixa {caixa.numero_caixa} movida para Prateleira ID {p.id} (Setor: {p.setor}, Corredor: {p.corredor}, Coluna: {p.max_colunas}, Nível: {p.max_niveis})")
                        alocada = True
                        break
                if not alocada:
                    print(f"Não há espaço disponível para a caixa {caixa.numero_caixa} no setor '{setor_escolhido}'.")

        elif opcao == '6':
            caixas_disponiveis = repo_caixa.get_all()
            if not caixas_disponiveis:
                print("Nenhuma caixa cadastrada para excluir.")
                continue

            print("\n--- Caixas Disponíveis para Exclusão ---")
            for c in caixas_disponiveis:
                print(f"ID: {c.id} - Número: {c.numero_caixa}")
            
            try:
                id_del = int(input("Digite o ID da caixa que deseja excluir: "))
                # Confirmação para segurança
                confirmacao = input(f"Tem certeza que deseja excluir a caixa com ID {id_del}? (s/n): ").strip().lower()
                if confirmacao == 's':
                    repo_caixa.delete(id_del)
                    print(f"Caixa com ID {id_del} excluída com sucesso.")
                else:
                    print("Exclusão cancelada.")
            except ValueError:
                print("ID inválido. Apenas números são permitidos.")

        elif opcao == '7':
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
            titulo = input("Título: ").strip()
            tipo = input("Tipo: ").strip()

            # data_emissao sempre começa como None (INDETERMINADO)
            novo_doc = Documento(titulo=titulo, tipo=tipo, data_emissao=None)
            data_input = input("Data de emissão (enter para usar data atual / vazio para sem data) [dd-mm-YYYY | dd/mm/YYYY | YYYY-mm-dd]: ").strip()
            if data_input == "":
                data_emissao = datetime.now()
            else:
                data_emissao = parse_data_flexivel(data_input)
                if data_emissao is None:
                    print("Formato de data inválido. Documento não criado.")
                    continue
            novo_doc = Documento(titulo=titulo, tipo=tipo, data_emissao=None)
            
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
        print("5. Visualizar prateleira (tabela de níveis e caixas)")
        print("6. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            prateleiras = repo_prateleira.get_all()
            for p in prateleiras:
                print(f"ID: {p.id}, Setor: {p.setor}, Corredor: {p.corredor}, Dimensões: {p.max_colunas} colunas x {p.max_niveis} níveis")

        elif opcao == '2':
            try:
                id_busca = int(input("Digite o ID da prateleira: "))
                prateleira = repo_prateleira.get_by_id(id_busca)
                if prateleira:
                    print(f"Encontrado: ID {prateleira.id}, Setor {prateleira.setor}, Corredor: {prateleira.corredor}")
                else:
                    print("Prateleira não encontrada.")
            except ValueError:
                print("ID inválido.")

        elif opcao == '3':
            prateleiras_existentes = repo_prateleira.get_all()
            setores_existentes = sorted(set(p.setor for p in prateleiras_existentes))
            
            setor = None # Inicializa a variável setor

            if setores_existentes:
                print("Setores já cadastrados:")
                for idx, setor_nome in enumerate(setores_existentes, 1):
                    print(f"{idx}. {setor_nome}")
                
                escolha_setor = input("Deseja usar um setor existente (E) ou cadastrar um novo (N)? [E/N]: ").strip().upper()
                
                if escolha_setor == 'E':
                    while True:
                        try:
                            idx_input = input("Digite o número do setor desejado: ")
                            idx = int(idx_input)
                            if 1 <= idx <= len(setores_existentes):
                                setor = setores_existentes[idx-1]
                                break
                            else:
                                print("Número inválido.")
                        except (ValueError, IndexError):
                            print("Entrada inválida. Por favor, digite um número da lista.")
                elif escolha_setor == 'N':
                    setor = input("Digite o nome do NOVO setor: ").strip()
                else:
                    print("Opção inválida. Voltando ao menu.")
                    continue
            else: # Se não existe nenhum setor, força a criação de um novo
                print("Nenhum setor cadastrado ainda.")
                setor = input("Digite o nome do primeiro setor: ").strip()

            # --- Bloco para criar a prateleira (executa para setor novo ou existente) ---
            if setor:
                try:
                    corredor = input(f"Digite o número do CORREDOR para o setor '{setor}': ")
                    max_colunas = int(input("Quantas COLUNAS a prateleira terá? "))
                    max_niveis = int(input("Quantos NÍVEIS a prateleira terá? "))

                    nova_prateleira = Prateleira(
                        setor=setor, 
                        corredor=corredor, 
                        max_colunas=str(max_colunas), 
                        max_niveis=str(max_niveis)
                    )
                    repo_prateleira.add(nova_prateleira)
                    print(f"Prateleira criada com sucesso no setor '{setor}', corredor {corredor}!")
                except ValueError:
                    print("Erro: Colunas e níveis devem ser números. Operação cancelada.")
            
        elif opcao == '4':
            try:
                id_del = int(input("Digite o ID da prateleira para excluir: "))
                repo_prateleira.delete(id_del)
                print("Prateleira excluída com sucesso (se o ID existia).")
            except ValueError:
                print("ID inválido.")

        elif opcao == '5':
            try:
                id_vis = int(input("Digite o ID da prateleira para visualizar: "))
                prateleira = repo_prateleira.get_by_id(id_vis)
                if not prateleira:
                    print("Prateleira não encontrada.")
                    continue

                todas_prateleiras = repo_prateleira.get_all()
                mesmas = [p for p in todas_prateleiras if p.setor == prateleira.setor and str(p.corredor) == str(prateleira.corredor)]

                mostrar_prateleira(prateleira, mesmas)
            except ValueError:
                print("ID inválido.")
        
        elif opcao == '6':
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
            data = datetime.now()

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

def menu_consultas():
    while True:
        print("\n--- Menu de Consultas ---")
        print("📌 Baixa Complexidade")
        print("1. Listar todas as prateleiras")
        print("2. Listar todas as caixas")
        print("3. Buscar prateleira por ID")
        print("\n📌 Média Complexidade")
        print("4. Listar prateleiras vazias")
        print("5. Listar todas as caixas de uma prateleira")
        print("6. Contar caixas por prateleira")
        print("\n📌 Alta Complexidade")
        print("7. Visualizar tabela completa de uma prateleira")
        print("8. Listar caixas com data de eliminação passada")
        print("9. Listar corredores lotados e com espaço")
        print("10. Ranking de prateleiras mais usadas")
        print("0. Voltar ao menu principal")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            listar_todas_prateleiras()
        elif opcao == '2':
            listar_todas_caixas()
        elif opcao == '3':
            buscar_prateleira_por_id()
        elif opcao == '4':
            listar_prateleiras_vazias()
        elif opcao == '5':
            listar_caixas_de_prateleira()
        elif opcao == '6':
            contar_caixas_por_prateleira()
        elif opcao == '7':
            prateleira_id = int(input("Digite o ID da prateleira: "))
            visualizar_prateleira_tabela(prateleira_id)
        elif opcao == '8':
            caixas_vencidas()
        elif opcao == '9':
            corredores_lotados()
        elif opcao == '10':
            ranking_prateleiras()
        elif opcao == '0':
            break
        else:
            print("Opção inválida, tente novamente.")

def login():
    print("\n--- Autenticação ---")
    email = input("E-mail: ")
    password = getpass.getpass("Senha: ")
    usuario_logado = login_with_email_password(email, password)
    
    return usuario_logado


def menu_principal():
    usuario_atual = None
    
    while True:
        if usuario_atual:
            print("\n===== MENU PRINCIPAL =====")
            print("1. Usuários")
            print("2. Caixas")
            print("3. Documentos")
            print("4. Prateleiras")
            print("5. Unidades")
            print("6. Movimentações")
            print("7. Consultas")
            print("8. Logout")
            print("9. Sair")
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
                menu_consultas()
            elif opcao == '8':
                usuario_atual = None
                print("Logout realizado.")
            elif opcao == '9':
                break
        else:
            print("\n===== MENU PRINCIPAL =====")
            print("1. Fazer Login")
            print("2. Sair")
            opcao = input("Escolha: ")
            if opcao == '1':
                usuario_atual = login()
            elif opcao == '2':
                break

def main():
    if initialize_firebase():
        criar_dados_iniciais()
        menu_principal()


if __name__ == "__main__":
    main()