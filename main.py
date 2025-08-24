import datetime

from models.models import Usuario, Caixa, Documento, Prateleira, Unidade, Movimentacao
from services.auth_service import create_user_with_email_password, initialize_firebase, login_with_email_password
import getpass
import csv
import os
from tqdm import tqdm
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

def mostrar_prateleira(prateleira):
    """
    Exibe a prateleira em forma de tabela, mostrando apenas as caixas que pertencem a ela.
    """
    print(f"\nPrateleira: {prateleira.setor} | Corredor: {prateleira.corredor}")

    try:
        max_colunas = int(prateleira.max_colunas)
        max_niveis = int(prateleira.max_niveis)
    except (ValueError, TypeError):
        print("Erro: As dimensões (colunas/níveis) desta prateleira não são válidas.")
        return

    caixas_posicionadas = {}
    for caixa in getattr(prateleira, 'caixas', []):
        if caixa.nivel is not None and caixa.coluna is not None:
            try:
                nivel = int(caixa.nivel)
                coluna = int(caixa.coluna)
                caixas_posicionadas[(nivel, coluna)] = str(caixa.numero_caixa)
            except (ValueError, TypeError):
                continue 

    col_width = 8
    sep = "+" + "+".join(["-" * col_width for _ in range(max_colunas + 1)]) + "+"
    
    print(sep)
    header = ["Nível"] + [str(c) for c in range(1, max_colunas + 1)]
    print("|" + "|".join(f"{h:^{col_width}}" for h in header) + "|")
    print(sep)

    for n in range(1, max_niveis + 1):
        row = [f"{n:^{col_width}}"]
        for c in range(1, max_colunas + 1):
            valor = caixas_posicionadas.get((n, c), "-")
            row.append(f"{valor:^{col_width}}")
        print("|" + "|".join(row) + "|")
        print(sep)


def visualizar_prateleira_tabela(prateleira_id):
    prateleira = repo_prateleira.get_by_id(prateleira_id)
    if not prateleira:
        print("Prateleira não encontrada.")
        return
    
    mostrar_prateleira(prateleira)

def cadastrar_usuario():
    print("\n--- Cadastro de Novo Usuário ---")
    nome = input("Nome completo: ").strip()
    

    while True:
        email = input("E-mail: ").strip()
        try:
            nome_usuario, dominio = email.split('@')
            if nome_usuario and dominio:
                break
            else:
                print("Erro: Formato de e-mail inválido. Deve haver texto antes e depois do '@'. Tente novamente.")
        except ValueError:
            print("Erro: Formato de e-mail inválido. O e-mail deve conter um '@'. Tente novamente.")

    password = getpass.getpass("Senha: ")
    tipo = input("Função do usuário (ex: admin, normal): ").strip()
    
    if not all([nome, password, tipo]):
        print("Nome, senha e função são obrigatórios. Cadastro cancelado.")
        return

    create_user_with_email_password(nome, email, password, tipo)

def login():
    print("\n--- Autenticação ---")
    while True:
        email = input("E-mail (ou deixe em branco para cancelar): ").strip()
        if not email:
            print("Login cancelado.")
            return None

        password = getpass.getpass("Senha: ")
        
        usuario_logado = login_with_email_password(email, password)
        
        if usuario_logado:
            return usuario_logado 
        else:
            print("Por favor, tente novamente.")



# ---------------- MENU USUÁRIO ----------------
def menu_usuario():
    while True:
        print("\n--- Menu Usuário ---")
        print("1. Listar todos")
        print("2. Buscar por ID")
        print("3. Buscar por E-mail")
        print("4. Cadastrar novo")
        print("5. Alterar informações") 
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

def importar_caixas_csv():
    BATCH_SIZE = 100 
    csv_dir = "CSV"
    if not os.path.isdir(csv_dir):
        print(f"Erro: A pasta '{csv_dir}' não foi encontrada.")
        return
    csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"Nenhum arquivo .csv encontrado na pasta '{csv_dir}'.")
        return
    print("\nArquivos CSV disponíveis para importação:")
    for i, filename in enumerate(csv_files, 1):
        print(f"{i}. {filename}")
    try:
        choice = int(input("Escolha o número do arquivo (ou 0 para cancelar): "))
        if choice == 0:
            print("Importação cancelada."); return
        caminho_arquivo = os.path.join(csv_dir, csv_files[choice - 1])
    except (ValueError, IndexError):
        print("Escolha inválida."); return

    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8-sig') as f:
            total_rows = sum(1 for row in f) - 1

        with open(caminho_arquivo, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # --- LÓGICA DE IMPORTAÇÃO CORRIGIDA E MELHORADA ---
            print("Iniciando importação...")
            sucesso = 0
            falha = 0
            
            # Cache para documentos já buscados/criados, para evitar buscas repetidas no banco
            documentos_cache = {}

            for row_num, row in enumerate(tqdm(reader, total=total_rows, desc="Importando Caixas"), start=2):
                try:
                    # Validação de número de caixa (mantém a lógica anterior)
                    numero_caixa = int(row['numero_caixa'])
                    if repo_caixa.numero_exists(numero_caixa):
                        raise ValueError(f"Número de caixa {numero_caixa} já existe.")

                    # Processamento da data de eliminação
                    data_eliminacao_str = row.get('data_eliminacao', '').strip()
                    data_eliminacao = parse_data_flexivel(data_eliminacao_str) if data_eliminacao_str else None

                    # Processamento da unidade
                    unidade = repo_unidade.get_by_id(int(row['unidade_id']))
                    if not unidade:
                        raise ValueError(f"Unidade com ID '{row['unidade_id']}' não encontrada.")
                    
                    # Processamento da prateleira e posição
                    prateleira = repo_prateleira.get_by_id(int(row['prateleira_id'])) if row.get('prateleira_id') else None
                    if prateleira_id_str := row.get('prateleira_id', ''):
                        prateleira = repo_prateleira.get_by_id(int(prateleira_id_str))
                        if not prateleira:
                             tqdm.write(f"Aviso na linha {row_num}: Prateleira ID '{prateleira_id_str}' não encontrada. Caixa ficará avulsa.")
                    
                    # --- LÓGICA DE DOCUMENTOS CORRIGIDA ---
                    docs_associados = []
                    # Lê a coluna 'documento' do novo CSV
                    documentos_str = row.get('documento', '').strip()
                    if documentos_str:
                        # Separa múltiplos documentos que estão na mesma célula
                        documentos_no_csv = [d.strip() for d in documentos_str.split(';')]
                        for doc_info in documentos_no_csv:
                            if not doc_info: continue
                            
                            # Tenta extrair ID, Título e Tipo
                            try:
                                doc_id_str, doc_titulo, doc_tipo = doc_info.split('-', 2)
                                doc_id = int(doc_id_str)

                                # Verifica se o documento já está no cache
                                if doc_id in documentos_cache:
                                    docs_associados.append(documentos_cache[doc_id])
                                else:
                                    # Se não está no cache, busca no banco
                                    doc_existente = repo_documento.get_by_id(doc_id)
                                    if doc_existente:
                                        documentos_cache[doc_id] = doc_existente
                                        docs_associados.append(doc_existente)
                                    else:
                                        # Se não existe no banco, cria um novo
                                        tqdm.write(f"  -> Documento '{doc_titulo}' (ID: {doc_id}) não encontrado, criando novo.")
                                        novo_doc = Documento(id=doc_id, titulo=doc_titulo, tipo=doc_tipo, data_emissao=datetime.datetime.now())
                                        repo_documento.session.add(novo_doc)
                                        documentos_cache[doc_id] = novo_doc
                                        docs_associados.append(novo_doc)
                            except ValueError:
                                tqdm.write(f"Aviso na linha {row_num}: Formato de documento inválido ('{doc_info}'). Documento ignorado.")
                                continue

                    # Cria o objeto Caixa com todos os dados
                    nova_caixa = Caixa(
                        numero_caixa=numero_caixa,
                        data_criacao=datetime.datetime.now(),
                        data_eliminacao=data_eliminacao,
                        unidade=unidade,
                        prateleira=prateleira,
                        coluna=row.get('coluna'),
                        nivel=row.get('nivel'),
                        documentos=docs_associados # Adiciona a lista de documentos
                    )
                    repo_caixa.session.add(nova_caixa)
                    sucesso += 1

                except (ValueError, KeyError) as e:
                    tqdm.write(f"Erro na linha {row_num}: {e}. Caixa não importada.")
                    falha += 1
            
            # Commit final para salvar tudo no banco
            repo_caixa.session.commit()
            print(f"\nImportação concluída! {sucesso} caixas criadas, {falha} falhas.")

    except Exception as e:
        repo_caixa.session.rollback()
        print(f"Ocorreu um erro inesperado: {e}")



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
        print("7. Importar caixas")
        print("8. Voltar")        
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
                    prateleira_str = f"{pr.setor} - Corredor:{pr.corredor} Coluna:{caixa.coluna} Nível:{caixa.nivel}"
                else:
                    prateleira_str = f"ID:{getattr(caixa, 'prateleira_id', 'None')}"

                print(f"Encontrado: ID {caixa.id}, Número {caixa.numero_caixa}, Eliminação: {de}, Unidade: {unidade_str}, Prateleira: {prateleira_str}, Documentos: {docs_str}")
            else:
                print("Caixa não encontrada.")

        elif opcao == '3':
            while True:
                try:
                    numero_str = input("Número da Caixa (ou deixe em branco para cancelar): ").strip()
                    if not numero_str:
                        print("Cadastro cancelado.")
                        return 

                    numero = int(numero_str)

                    if repo_caixa.numero_exists(numero):
                        print(f"Erro: A caixa com o número {numero} já existe. Por favor, tente outro número.")
                    else:
                        break
                except ValueError:
                    print("Erro: Por favor, digite um número válido.")

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

            repo_caixa.update(caixa)
            print("Alterações salvas com sucesso.")

        elif opcao == '5':
            caixas_avulsas = [c for c in repo_caixa.get_all() if getattr(c, 'prateleira_id', None) is None]
            if not caixas_avulsas: print("Nenhuma caixa avulsa encontrada."); continue
            
            print(f"\nForam encontradas {len(caixas_avulsas)} caixas avulsas.")
            prateleiras = repo_prateleira.get_all()
            if not prateleiras: print("Nenhuma prateleira cadastrada para mover as caixas."); continue

            print("\nPrateleiras disponíveis:")
            for p in prateleiras: print(f"ID: {p.id} - Setor: {p.setor} - Corredor: {p.corredor}")

            try:
                prateleira_id = int(input("Digite o ID da prateleira de destino: "))
                prateleira_destino = repo_prateleira.get_by_id(prateleira_id)
                if not prateleira_destino: print("ID de prateleira inválido."); continue
            except ValueError: print("Entrada inválida. Digite um número."); continue

            caixas_na_prateleira = repo_caixa.get_by_prateleira(prateleira_destino.id)
            posicoes_ocupadas = set((int(c.coluna), int(c.nivel)) for c in caixas_na_prateleira if c.coluna is not None and c.nivel is not None)
            max_col, max_niv = int(prateleira_destino.max_colunas), int(prateleira_destino.max_niveis)
            
            caixas_para_mover = []

            for caixa in caixas_avulsas:
                slot_encontrado = False
                for nivel_atual in range(1, max_niv + 1):
                    for coluna_atual in range(1, max_col + 1):
                        if (coluna_atual, nivel_atual) not in posicoes_ocupadas:
                            # Prepara a caixa para ser movida (atualiza em memória)
                            caixa.prateleira = prateleira_destino
                            caixa.coluna = str(coluna_atual)
                            caixa.nivel = str(nivel_atual)
                            
                            # Adiciona à lista para salvar depois
                            caixas_para_mover.append(caixa)
                            
                            posicoes_ocupadas.add((coluna_atual, nivel_atual))
                            print(f"Caixa {caixa.numero_caixa} movida para Prateleira ID {prateleira_destino.id} (Coluna: {coluna_atual}, Nível: {nivel_atual})")
                            
                            slot_encontrado = True
                            break
                    if slot_encontrado: break
                
                if not slot_encontrado:
                    print(f"\nNão há mais espaço na prateleira de destino.")
                    break
            
            if caixas_para_mover:
                print(f"\nSalvando {len(caixas_para_mover)} caixas no banco de dados...")
                # O repo.update já lida com o merge, commit e remove.
                # Chamamos um por um, mas a sessão será renovada a cada chamada.
                for caixa_movida in caixas_para_mover:
                    repo_caixa.update(caixa_movida)
                print("Operação concluída com sucesso!")
            else:
                print("Nenhuma caixa foi movida.")

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
                confirmacao = input(f"Tem certeza que deseja excluir a caixa com ID {id_del}? (s/n): ").strip().lower()
                if confirmacao == 's':
                    repo_caixa.delete(id_del)
                    print(f"Caixa com ID {id_del} excluída com sucesso.")
                else:
                    print("Exclusão cancelada.")
            except ValueError:
                print("ID inválido. Apenas números são permitidos.")

        elif opcao == '7':    
            importar_caixas_csv()

        elif opcao == '8':
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
            
            setor = None 

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
            else: 
                print("Nenhum setor cadastrado ainda.")
                setor = input("Digite o nome do primeiro setor: ").strip()

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

            tipo = input("Tipo da movimentação: ")
            data = datetime.datetime.now()

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

# ---------------- MENU PRINCIPAL ----------------
def menu_principal():
    usuario_atual = None

    while True:
        if usuario_atual:
            print("\n===== MENU PRINCIPAL =====")
            print(f"Usuário: {usuario_atual.display_name}")
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
            print("\n===== BEM-VINDO AO SISTEMA DE ARQUIVO =====")
            print("1. Fazer Login")
            print("2. Cadastrar Novo Usuário") 
            print("3. Sair")                   
            opcao = input("Escolha: ")
            if opcao == '1':
                usuario_atual = login()
            elif opcao == '2':
                cadastrar_usuario() 
            elif opcao == '3':
                break

def main():
    if initialize_firebase():
        criar_dados_iniciais()
        menu_principal()


if __name__ == "__main__":
    main()