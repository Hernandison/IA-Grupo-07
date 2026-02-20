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
        # Conjunto de prateleiras confirmadas como inacessíveis (cercadas de obstáculos)
        self._inacessiveis = set()
        # Sinaliza ao ambiente que não há mais nada a fazer (layout impossível)
        self.missao_impossivel = False

    def _buscar_caminho(self, estado_inicial, obstaculos, alvo):
        """Tenta encontrar caminho via A*. Retorna lista de ações ou None."""
        prob = ProblemaAlmoxarifado(
            estado_inicial, obstaculos, alvo,
            self.pos_entrega, self.largura_grid, self.altura_grid
        )
        no_solucao = astar_search(prob)
        return no_solucao.solution() if no_solucao else None

    def _vizinhos_livres(self, pos, obstaculos):
        """Retorna as células adjacentes à posição que não são obstáculos."""
        x, y = pos
        candidatos = [
            (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)
        ]
        return [
            p for p in candidatos
            if 0 <= p[0] < self.largura_grid
            and 0 <= p[1] < self.altura_grid
            and p not in obstaculos
        ]

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

        if tem_caixa:
            # ----------------------------------------------------------------
            # Sub-objetivo: Levar caixa ao balcão
            # ----------------------------------------------------------------
            obstaculos = set(self.memoria_prateleiras.keys())
            acoes = self._buscar_caminho(
                (pos_atual[0], pos_atual[1], 1), obstaculos, self.pos_entrega
            )

            if acoes is not None:
                self.plano = acoes
                self.plano.append('Entregar')
                return self.plano.pop(0)

            # ── Balcão inacessível diretamente: tenta chegar a um vizinho livre ──
            vizinhos = self._vizinhos_livres(self.pos_entrega, obstaculos)
            vizinhos.sort(key=lambda p: abs(p[0] - pos_atual[0]) + abs(p[1] - pos_atual[1]))
            for viz in vizinhos:
                acoes = self._buscar_caminho(
                    (pos_atual[0], pos_atual[1], 1), obstaculos, viz
                )
                if acoes is not None:
                    print(f"[AGENTE] Balcão cercado. Roteando para vizinho livre {viz}.")
                    self.plano = acoes
                    # Ao chegar no vizinho, tenta entrar no balcão pelo lado acessível
                    # na próxima chamada do programa_agente
                    return self.plano.pop(0)

            # Totalmente impossível entregar — encerra para não travar em loop
            print("[AGENTE] AVISO: balcão totalmente inacessível. Encerrando.")
            self.missao_impossivel = True
            return 'NoOp'

        else:
            # ----------------------------------------------------------------
            # Sub-objetivo: Buscar novo item
            # ----------------------------------------------------------------
            prateleiras_disponiveis = [
                pos for pos, qtd in self.memoria_prateleiras.items()
                if qtd > 0 and pos not in self._inacessiveis
            ]

            if not prateleiras_disponiveis:
                return 'NoOp'  # Sem itens restantes acessíveis

            # Tenta cada prateleira em ordem crescente de distância Manhattan
            prateleiras_disponiveis.sort(
                key=lambda p: abs(p[0] - pos_atual[0]) + abs(p[1] - pos_atual[1])
            )

            for alvo in prateleiras_disponiveis:
                obstaculos = set(self.memoria_prateleiras.keys()) - {alvo}
                acoes = self._buscar_caminho(
                    (pos_atual[0], pos_atual[1], 0), obstaculos, alvo
                )

                if acoes is not None:
                    self.plano = acoes
                    self.plano.append('Pegar')
                    self.alvo_atual = alvo
                    return self.plano.pop(0)

                # Sem caminho para este alvo: marca como inacessível
                print(f"[AGENTE] Prateleira {alvo} inacessível. Ignorando.")
                self._inacessiveis.add(alvo)

            # Todas as prateleiras com item estão cercadas
            print("[AGENTE] AVISO: nenhuma prateleira acessível. Encerrando missão.")
            self.missao_impossivel = True
            return 'NoOp'