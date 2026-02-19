# Arquivo: agents/agente_almoxarifado.py

from aima.agents import Agent
from aima.search import astar_search
from problems.problema_almoxarifado import ProblemaAlmoxarifado

class AgenteAlmoxarifado(Agent):
    def __init__(self, pos_inicial, dados_prateleiras, pos_entrega, largura_grid, altura_grid):
        super().__init__(self.programa_agente)
        self.largura_grid = largura_grid
        self.altura_grid = altura_grid
        # dados_prateleiras é um dicionário {(x,y): quantidade}
        self.memoria_prateleiras = dados_prateleiras.copy() 
        self.pos_entrega = pos_entrega
        self.plano = []
        self.alvo_atual = None

    def programa_agente(self, percepcao):
        """Decide qual ação tomar com base no que percebe do ambiente."""
        pos_atual = percepcao['posicao']
        tem_caixa = percepcao['tem_caixa']
        
        # Se tem um plano na memória, apenas executa o próximo passo
        if self.plano:
            return self.plano.pop(0)

        # -----------------------------------------------------------------------------------
        # USO DO ALGORITMO A* (A-Star):
        # O agente utiliza o A* porque o problema exige encontrar o caminho mais curto
        # (menor custo) contornando obstáculos (prateleiras). O A* é ideal aqui pois é
        # completo e ótimo, utilizando a heurística de Manhattan definida na classe
        # ProblemaAlmoxarifado para guiar a busca de forma eficiente até o objetivo.
        # -----------------------------------------------------------------------------------

        # Se não tem plano, aciona a IA para decidir o que fazer
        if tem_caixa:
            # 1. Sub-objetivo: Levar caixa ao balcão
            obstaculos = set(self.memoria_prateleiras.keys())
            prob = ProblemaAlmoxarifado((pos_atual[0], pos_atual[1], 1), obstaculos, self.pos_entrega, self.pos_entrega, self.largura_grid, self.altura_grid)
            
            # Executa a busca A* para encontrar a melhor rota até o ponto de entrega
            no_solucao = astar_search(prob)
            
            if no_solucao:
                self.plano = no_solucao.solution() # solution() retorna a lista de ações (o plano)
                self.plano.append('Entregar')      # Adiciona a ação final de interação
                return self.plano.pop(0) if self.plano else 'NoOp'
                
        else:
            # 2. Sub-objetivo: Buscar novo item
            prateleiras_disponiveis = [pos for pos, qtd in self.memoria_prateleiras.items() if qtd > 0]
            
            if not prateleiras_disponiveis:
                return 'NoOp' # Acabou o trabalho, não há mais itens!

            # Escolher a prateleira mais próxima (Heurística Gulosa simples para escolher o alvo)
            prateleiras_disponiveis.sort(key=lambda p: abs(p[0]-pos_atual[0]) + abs(p[1]-pos_atual[1]))
            alvo = prateleiras_disponiveis[0]
            
            # Obstáculos são todas as prateleiras MENOS a alvo
            obstaculos = set(self.memoria_prateleiras.keys()) - {alvo}
            
            prob = ProblemaAlmoxarifado((pos_atual[0], pos_atual[1], 0), obstaculos, alvo, self.pos_entrega, self.largura_grid, self.altura_grid)
            
            # Executa a busca A* para encontrar a melhor rota até a prateleira escolhida
            no_solucao = astar_search(prob)
            
            if no_solucao:
                self.plano = no_solucao.solution() # Extrai a sequência de movimentos do A*
                self.plano.append('Pegar')         # Adiciona a ação final de interação
                self.alvo_atual = alvo 
                return self.plano.pop(0) if self.plano else 'NoOp'

        return 'NoOp'