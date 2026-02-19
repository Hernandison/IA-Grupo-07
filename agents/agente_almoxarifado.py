from aima.agents import Agent
from aima.search import astar_search
from problems.problema_almoxarifado import ProblemaAlmoxarifado


class AgenteAlmoxarifado(Agent):
    def __init__(self, pos_inicial, dados_prateleiras, pos_entrega, largura_grid, altura_grid):
        super().__init__(self.programa_agente)
        self.largura_grid = largura_grid
        self.altura_grid = altura_grid
        self.memoria_prateleiras = dados_prateleiras.copy()
        self.pos_entrega = pos_entrega
        self.plano = []

    def traduzir_plano(self, pos_atual, acao):
        movimentos = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}
        if acao in movimentos:
            return (pos_atual[0] + movimentos[acao][0], pos_atual[1] + movimentos[acao][1])
        return pos_atual

    def _buscar_caminho(self, estado_inicial, obstaculos, alvo, pos_entrega, goal_pos):
        """
        Centraliza a criação do problema e a busca A*.
        Recebe goal_pos como valor fixo — evita o bug de closure do lambda.
        """
        prob = ProblemaAlmoxarifado(
            estado_inicial, obstaculos, alvo, pos_entrega,
            self.largura_grid, self.altura_grid
        )
        # Captura goal_pos por valor no argumento padrão — closure segura
        prob.goal_test = lambda state, _gp=goal_pos: state[0:2] == _gp
        return astar_search(prob)

    def programa_agente(self, percepcao):
        pos_atual    = percepcao['posicao']
        tem_caixa    = percepcao['tem_caixa']
        bateria      = percepcao['bateria']
        guardas      = percepcao['guardas_visiveis']
        baterias_chao = percepcao['baterias_visiveis']

        # ── Zona de perigo: células com guarda + adjacentes ──────────────────
        zona_perigo = set(guardas)
        for gx, gy in guardas:
            zona_perigo.update([(gx+1, gy), (gx-1, gy), (gx, gy+1), (gx, gy-1)])

        # ── Aborta rota se bloqueada ou bateria crítica com recarga disponível
        if self.plano:
            prox_pos = self.traduzir_plano(pos_atual, self.plano[0])
            if prox_pos in zona_perigo or (bateria <= 15 and baterias_chao):
                self.plano = []

        if self.plano:
            return self.plano.pop(0)

        # ── Obstáculos base: prateleiras + zona de perigo ────────────────────
        obstaculos = set(self.memoria_prateleiras.keys()) | zona_perigo

        # ── MODO SOBREVIVÊNCIA: ir buscar bateria ────────────────────────────
        if bateria <= 15 and baterias_chao:
            baterias_chao_sorted = sorted(
                baterias_chao,
                key=lambda p: abs(p[0] - pos_atual[0]) + abs(p[1] - pos_atual[1])
            )
            alvo = baterias_chao_sorted[0]
            solucao = self._buscar_caminho(
                (pos_atual[0], pos_atual[1], 0),
                obstaculos, alvo, self.pos_entrega, alvo
            )
            if solucao:
                self.plano = solucao.solution()
                return self.plano.pop(0) if self.plano else 'NoOp'

        # ── MODO TRABALHO: Entregar caixa ────────────────────────────────────
        if tem_caixa:
            destino = self.pos_entrega
            solucao = self._buscar_caminho(
                (pos_atual[0], pos_atual[1], 1),
                obstaculos, destino, destino, destino
            )
            if solucao:
                self.plano = solucao.solution()
                self.plano.append('Entregar')
                return self.plano.pop(0) if self.plano else 'NoOp'

        # ── MODO TRABALHO: Buscar caixa na prateleira ────────────────────────
        else:
            caixas = [pos for pos, qtd in self.memoria_prateleiras.items() if qtd > 0]
            if not caixas:
                return 'NoOp'

            caixas_sorted = sorted(
                caixas,
                key=lambda p: abs(p[0] - pos_atual[0]) + abs(p[1] - pos_atual[1])
            )
            alvo = caixas_sorted[0]
            obstaculos_busca = obstaculos - {alvo}  # permite pisar no alvo
            solucao = self._buscar_caminho(
                (pos_atual[0], pos_atual[1], 0),
                obstaculos_busca, alvo, self.pos_entrega, alvo
            )
            if solucao:
                self.plano = solucao.solution()
                self.plano.append('Pegar')
                return self.plano.pop(0) if self.plano else 'NoOp'

        # Sem saída (cercado ou sem caixas)
        return 'NoOp'