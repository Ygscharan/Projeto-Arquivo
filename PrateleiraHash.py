from ListaEncadeada import ListaEncadeada
from datetime import datetime

class Prateleira:
    def __init__(self, setor, corredor, coluna, nivel):
        self.id = None 
        self.setor = setor
        self.corredor = corredor
        self.coluna = coluna
        self.nivel = nivel
        self.caixas = PrateleiraHash(tamanho=nivel, limite_por_indice=coluna)


class PrateleiraHash:
    def __init__(self):
        self.caixas = []

    def inserir_caixa(self, caixa):
        if caixa in self.caixas:
            print(f"Caixa {caixa.numero_caixa} já está na prateleira!")
            return False
        self.caixas.append(caixa)
        return True

    def exibir_tabela(self):
        print(f"{'Posição':<10} | {'Caixa':<10}")
        print("-" * 25)
        for i, caixa in enumerate(self.caixas):
            print(f"{i:<10} | {caixa.numero_caixa:<10}")
        if not self.caixas:
            print("Vazio")

    def remover_caixa(self, caixa_id):
        for i, caixa in enumerate(self.caixas):
            if caixa.id == caixa_id:
                del self.caixas[i]
                return True
        return False

    def buscar_caixa_por_id(self, caixa_id):
        for caixa in self.caixas:
            if caixa.id == caixa_id:
                return caixa
        return None

    def listar_caixas(self):
        return list(self.caixas)

    def __str__(self):
        if not self.caixas:
            return "Vazio"
        return ", ".join(str(caixa.numero_caixa) for caixa in self.caixas)


repo_prateleira_hash = []

def menu_prateleira():
    while True:
        print("\n--- Menu Prateleira ---")
        print("1. Listar prateleiras")
        print("2. Cadastrar nova prateleira")
        print("3. Inserir caixa em prateleira")
        print("4. Buscar caixa por ID")
        print("5. Remover caixa por ID")
        print("6. Sair do menu")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            if not repo_prateleira_hash:
                print("Nenhuma prateleira cadastrada.")
            for p in repo_prateleira_hash:
                print(f"ID: {p.id}, Setor: {p.setor}, Local: {p.corredor}-{p.coluna}-{p.nivel}")
                print("Caixas na prateleira:")
                print(p.caixas)

        elif opcao == '2':
            setor = input("Setor: ")
            corredor = input("Corredor: ")
            coluna = int(input("Coluna: "))
            nivel = int(input("Nível: "))
            nova = Prateleira(setor, corredor, coluna, nivel)
            nova.id = len(repo_prateleira_hash) + 1
            repo_prateleira_hash.append(nova)
            print(f"Prateleira cadastrada com ID {nova.id}")

        elif opcao == '3':
            if not repo_prateleira_hash:
                print("Cadastre primeiro uma prateleira.")
                continue
            for p in repo_prateleira_hash:
                print(f"ID: {p.id}, Setor: {p.setor}, Local: {p.corredor}-{p.coluna}-{p.nivel}")
            pid = int(input("Escolha o ID da prateleira para inserir a caixa: "))
            prateleira = next((p for p in repo_prateleira_hash if p.id == pid), None)
            if not prateleira:
                print("ID inválido.")
                continue
            numero_caixa = int(input("Número da caixa: "))
            caixa_id = sum(len(p.caixas.listar_caixas()) for p in repo_prateleira_hash) + 1
            caixa = type('Caixa', (), {})()
            caixa.id = caixa_id
            caixa.numero_caixa = numero_caixa
            caixa.data_criacao = datetime.now()
            prateleira.caixas.inserir_caixa(caixa)
            print(f"Caixa {numero_caixa} inserida na prateleira {pid}")

        elif opcao == '4':
            busca_id = int(input("Digite o ID da caixa a buscar: "))
            encontrada = None
            for p in repo_prateleira_hash:
                encontrada = p.caixas.buscar_caixa_por_id(busca_id)
                if encontrada:
                    print(f"Caixa encontrada na prateleira {p.id}! ID: {encontrada.id}, Número: {encontrada.numero_caixa}")
                    break
            if not encontrada:
                print("Caixa não encontrada.")

        elif opcao == '5':
            remove_id = int(input("Digite o ID da caixa a remover: "))
            removida = False
            for p in repo_prateleira_hash:
                if p.caixas.remover_caixa(remove_id):
                    print(f"Caixa removida da prateleira {p.id}")
                    removida = True
                    break
            if not removida:
                print("ID não encontrado.")

        elif opcao == '6':
            break

        else:
            print("Opção inválida!")
