# Arquivo: problems/problema_almoxarifado.py

from aima.search import Problem

class ProblemaAlmoxarifado(Problem):
    def __init__(self, estado_inicial, obstaculos, alvo, pos_entrega, largura=10, altura=10):
        # Herdando do AIMA
        # Por padrão, o objetivo (goal) do subproblema de navegação é chegar na coordenada do alvo.
        # O programa do agente muda o alvo (prateleira/balcão) criando uma nova instância do problema.
        super().__init__(estado_inicial, goal=alvo)
        self.obstaculos = obstaculos # Posições que bloqueiam (ex: outras prateleiras)
        self.alvo = alvo             # Onde queremos chegar (Prateleira ou Balcão)
        self.pos_entrega = pos_entrega
        self.largura = largura
        self.altura = altura

    def actions(self, state):
        """Retorna as ações possíveis a partir do estado atual."""
        acoes_possiveis = []
        x, y, status = state 
        
        # Movimentos: Norte, Sul, Oeste, Leste
        movimentos = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}
        
        for nome_acao, (dx, dy) in movimentos.items():
            nx, ny = x + dx, y + dy
            # Verifica limites do mapa
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                # Pode andar se não for obstáculo OU se for o próprio alvo
                if (nx, ny) not in self.obstaculos or (nx, ny) == self.alvo:
                    acoes_possiveis.append(nome_acao)

        # Ações de interação com o cenário
        if (x, y) == self.alvo:
            if status == 0: acoes_possiveis.append('Pegar')    # Pegar na prateleira
            if status == 1: acoes_possiveis.append('Entregar') # Entregar no balcão
            
        return acoes_possiveis

    def result(self, state, action):
        """Retorna o novo estado após a execução de uma ação."""
        x, y, status = state
        if action == 'N': y -= 1
        elif action == 'S': y += 1
        elif action == 'O': x -= 1
        elif action == 'L': x += 1
        elif action == 'Pegar': return (x, y, 1)
        elif action == 'Entregar': return (x, y, 2)
        
        return (x, y, status)

    def goal_test(self, state):
        """Retorna True quando o agente chega na coordenada objetivo do subproblema."""
        return state[0:2] == self.goal

    def h(self, node):
        """Heurística simples: Distância Manhattan até o alvo atual."""
        x, y, status = node.state
        def distancia(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        return distancia((x, y), self.alvo)