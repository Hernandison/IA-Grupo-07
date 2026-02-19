from aima.search import Problem


class ProblemaAlmoxarifado(Problem):
    def __init__(
        self,
        estado_inicial,
        obstaculos,
        alvo,
        pos_entrega,
        largura=10,
        altura=10,
        areas_radioativas=None,
    ):
        super().__init__(estado_inicial, goal=None)
        self.obstaculos = obstaculos   # Posições que bloqueiam (ex: prateleiras)
        self.alvo = alvo               # Destino da busca (prateleira ou balcão)
        self.pos_entrega = pos_entrega
        self.largura = largura
        self.altura = altura
        self.areas_radioativas = areas_radioativas or set()

    # ------------------------------------------------------------------
    # Movimentos disponíveis a partir de um estado
    # ------------------------------------------------------------------

    def actions(self, state):
        """Retorna os movimentos cardinais válidos a partir do estado atual.

        Ações de interação ('Pegar', 'Entregar') são excluídas intencionalmente:
        o A* só planeja o CAMINHO até o alvo; o agente acrescenta a ação de
        interação manualmente ao final do plano (veja AgenteAlmoxarifado).
        Incluí-las aqui duplicaria estados e aumentaria o espaço de busca
        sem nenhum benefício para o planejamento de rota.
        """
        acoes = []
        x, y, _ = state
        movimentos = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}

        for acao, (dx, dy) in movimentos.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                # Permite pisar no alvo mesmo que esteja na lista de obstáculos
                if (nx, ny) not in self.obstaculos or (nx, ny) == self.alvo:
                    acoes.append(acao)

        return acoes

    # ------------------------------------------------------------------
    # Transição de estados
    # ------------------------------------------------------------------

    def result(self, state, action):
        """Retorna o novo estado após executar uma ação de movimento."""
        x, y, status = state
        deltas = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}
        if action in deltas:
            dx, dy = deltas[action]
            return (x + dx, y + dy, status)
        # Ação desconhecida — mantém estado (não deveria ocorrer com actions() correto)
        return state

    # ------------------------------------------------------------------
    # Teste de objetivo — DEVE ser injetado pelo agente antes do A*
    # ------------------------------------------------------------------

    def goal_test(self, state):
        """Substituído pelo agente via argumento padrão no lambda.

        Falha explicitamente se chamado sem substituição, evitando que o A*
        rode silenciosamente sem nunca encontrar o objetivo.
        """
        raise NotImplementedError(
            "goal_test não foi injetado. Use _buscar_caminho() em AgenteAlmoxarifado, "
            "que define:\n"
            "  prob.goal_test = lambda state, _gp=goal_pos: state[0:2] == _gp"
        )

    # ------------------------------------------------------------------
    # Heurística A* — distância Manhattan até o alvo
    # ------------------------------------------------------------------

    def h(self, node):
        x, y, _ = node.state
        return abs(x - self.alvo[0]) + abs(y - self.alvo[1])

    # ------------------------------------------------------------------
    # Custo de caminho — penaliza áreas radioativas
    # ------------------------------------------------------------------

    def path_cost(self, c, state1, action, state2):
        """Terreno limpo custa 1; áreas radioativas custam 5.

        O A* contornará a radiação automaticamente se houver rota alternativa
        com custo total menor.
        """
        x_novo, y_novo, _ = state2
        penalidade = 5 if (x_novo, y_novo) in self.areas_radioativas else 1
        return c + penalidade