# Arquivo: env/ambiente_almoxarifado.py

from aima.agents import Environment

class AmbienteAlmoxarifado(Environment):
    def __init__(self, largura, altura, dados_prateleiras, pos_entrega):
        super().__init__()
        self.largura = largura
        self.altura = altura
        # dados_prateleiras: {(x,y): int_quantidade}
        self.prateleiras = dados_prateleiras 
        self.pos_entrega = pos_entrega
        self.dados_agentes = {}

    def add_thing(self, agent, location=(0,0)):
        super().add_thing(agent, location)
        self.dados_agentes[agent] = {'posicao': location, 'tem_caixa': False, 'itens_entregues': 0, 'ultima_acao': None}

    def percept(self, agent):
        """Fornece a perceção atual ao agente."""
        # O agente "olha" e atualiza a sua memória sobre onde ainda tem caixas
        agent.memoria_prateleiras = self.prateleiras.copy()
        return self.dados_agentes[agent]

    def execute_action(self, agent, action):
        """Aplica a ação física do agente no mundo real (ambiente)."""
        dados = self.dados_agentes[agent]
        x, y = dados['posicao']
        dados['ultima_acao'] = action

        movimentos = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}
        
        if action in movimentos:
            dx, dy = movimentos[action]
            nx, ny = x + dx, y + dy
            # Checagem básica de colisão
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                dados['posicao'] = (nx, ny)

        elif action == 'Pegar':
            if dados['posicao'] in self.prateleiras and self.prateleiras[dados['posicao']] > 0 and not dados['tem_caixa']:
                self.prateleiras[dados['posicao']] -= 1
                dados['tem_caixa'] = True

        elif action == 'Entregar':
            if dados['posicao'] == self.pos_entrega and dados['tem_caixa']:
                dados['tem_caixa'] = False
                dados['itens_entregues'] += 1

    def is_done(self):
        """O ambiente encerra quando não há mais itens."""
        total_itens_restantes = sum(self.prateleiras.values())
        agentes_carregando = any(d['tem_caixa'] for d in self.dados_agentes.values())
        return total_itens_restantes == 0 and not agentes_carregando

    def step(self):
        """Executa um passo temporal e desenha o estado atual."""
        super().step()
        self.render()

    def render(self):
        """Imprime o estado atual do Almoxarifado no terminal."""
        print("\n" + "="*35)
        print(" ESTADO ATUAL DO ALMOXARIFADO")
        print("="*35)
        for y in range(self.altura):
            linha = ""
            for x in range(self.largura):
                pos = (x, y)
                simbolo = ". "
                
                # Renderiza o cenário
                if pos == self.pos_entrega:
                    simbolo = "B "  # Balcão
                elif pos in self.prateleiras:
                    qtd = self.prateleiras[pos]
                    simbolo = f"[{qtd}]" if qtd > 0 else "[ ]"

                # Sobrepõe com o robô (se estiver nesta posição)
                for agente, dados in self.dados_agentes.items():
                    if dados['posicao'] == pos:
                        simbolo = "🤖*" if dados['tem_caixa'] else "🤖 "
                
                linha += f"{simbolo:^4}"
            print(linha)
        
        # Mostra o status do(s) agente(s)
        for agente, dados in self.dados_agentes.items():
            print(f" -> Ação tomada: {dados['ultima_acao']}")
            print(f" -> Itens entregues no Balcão: {dados['itens_entregues']}")
        print("="*35 + "\n")