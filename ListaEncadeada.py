class No:
    def __init__(self, valor):
        self.valor = valor
        self.proximo = None

class ListaEncadeada:
    def __init__(self):
        self.cabeca = None

    def vazia(self):
        return self.cabeca is None

    def inserir_no_inicio(self, valor):
        novo_no = No(valor)
        novo_no.proximo = self.cabeca
        self.cabeca = novo_no

    def inserir_no_fim(self, valor):
        novo_no = No(valor)
        if self.cabeca is None:
            self.cabeca = novo_no
        else:
            atual = self.cabeca
            while atual.proximo is not None:
                atual = atual.proximo
            atual.proximo = novo_no

    def inserir_ordenado(self, valor):
        novo_no = No(valor)
        if self.vazia() or valor < self.cabeca.valor:
            self.inserir_no_inicio(valor)
            return
        atual = self.cabeca
        while atual.proximo and atual.proximo.valor < valor:
            atual = atual.proximo
        novo_no.proximo = atual.proximo
        atual.proximo = novo_no

    def remover(self, valor):
        atual = self.cabeca
        anterior = None
        while atual:
            if atual.valor == valor:
                if anterior is None:
                    self.cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def buscar(self, valor):
        atual = self.cabeca
        while atual:
            if atual.valor == valor:
                return True
            atual = atual.proximo
        return False

    def imprimir(self):
        atual = self.cabeca
        if atual is None:
            print("Lista vazia")
            return
        while atual:
            print(atual.valor, end=" -> ")
            atual = atual.proximo
        print("None")
