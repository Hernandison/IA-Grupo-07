from aima.agents import Environment
import random

class AmbienteAlmoxarifado(Environment):
    def __init__(self, largura, altura, dados_prateleiras, pos_entrega):
        super().__init__()
        self.largura = largura
        self.altura = altura
        self.prateleiras = dados_prateleiras
        self.pos_entrega = pos_entrega
        self.dados_agentes = {}

        # Lista que guarda as posições dos funcionários que invadiram o armazém
        self.funcionarios_corredor = []   
        self.pos_inicio_agente = (0, 0)

    def add_thing(self, agent, location=(0, 0)):
        super().add_thing(agent, location)
        self.pos_inicio_agente = location
        self.dados_agentes[agent] = {
            'posicao': location, 
            'tem_caixa': False, 
            'itens_entregues': 0,
            'ultima_acao': None, 
            'bateria': 100, 
            'paralisado': False,       # Status crítico de Game Over
            'motivo_gameover': ''      # Mensagem a ser enviada para a interface
        }

    def percept(self, agent):
        dados = self.dados_agentes[agent]
        return {
            'posicao': dados['posicao'],
            'tem_caixa': dados['tem_caixa'],
            'bateria': dados['bateria'],
            'guardas_visiveis': self.funcionarios_corredor.copy(),
            'baterias_visiveis': []
        }

    def invadir(self, pos_x, pos_y):
        """Método chamado pela interface quando a paciência de um funcionário chega a zero."""
        self.funcionarios_corredor.append((pos_x, pos_y))

    def mover_invasores(self):
        """Move os funcionários furiosos pelo armazém à procura do robô."""
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        posicoes_ocupadas = set()
        novos = []

        # Tenta localizar o robô para que os invasores o possam perseguir
        pos_robo = None
        for d in self.dados_agentes.values():
            pos_robo = d['posicao']
            break

        for (fx, fy) in self.funcionarios_corredor:
            candidatos = []
            for dx, dy in movimentos:
                nx, ny = fx + dx, fy + dy
                # Invasores não sobem nas prateleiras nem voltam para a zona de atendimento (y = altura - 1)
                if (0 <= nx < self.largura and 0 <= ny < self.altura - 1 and
                    (nx, ny) not in self.prateleiras and (nx, ny) not in posicoes_ocupadas):
                    candidatos.append((nx, ny))

            escolha = (fx, fy)
            if candidatos:
                # 50% de probabilidade de o invasor tentar andar ativamente na direção do robô
                if pos_robo and random.random() < 0.5:
                    candidatos.sort(key=lambda p: abs(p[0]-pos_robo[0]) + abs(p[1]-pos_robo[1]))
                    escolha = candidatos[0]
                else:
                    escolha = random.choice(candidatos)

            posicoes_ocupadas.add(escolha)
            novos.append(escolha)

        self.funcionarios_corredor = novos

    def verificar_se_preso(self, agent):
        """Verifica se o robô foi encurralado num canto ou diretamente capturado."""
        dados = self.dados_agentes[agent]
        if dados['paralisado']: return
        
        x, y = dados['posicao']
        
        # Condição 1: Um invasor tocou fisicamente no robô
        if (x, y) in self.funcionarios_corredor:
            dados['paralisado'] = True
            dados['motivo_gameover'] = 'DESTRUÍDO PELOS INVASORES!'
            return

        # Condição 2: O robô está encurralado contra prateleiras sem via de fuga
        movimentos = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        caminhos_livres = 0
        tem_invasor_perto = False

        for dx, dy in movimentos:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                if (nx, ny) in self.funcionarios_corredor:
                    tem_invasor_perto = True
                elif (nx, ny) not in self.prateleiras:
                    caminhos_livres += 1

        if caminhos_livres == 0 and tem_invasor_perto:
            dados['paralisado'] = True
            dados['motivo_gameover'] = 'ROBÔ ENCURRALADO! SEM SAÍDA!'

    def execute_action(self, agent, action):
        dados = self.dados_agentes[agent]
        
        # O robô deixa de funcionar se ficar sem bateria ou for destruído
        if dados['bateria'] <= 0 or dados['paralisado']:
            return

        x, y = dados['posicao']
        dados['ultima_acao'] = action
        movimentos = {'N': (0, -1), 'S': (0, 1), 'O': (-1, 0), 'L': (1, 0)}

        if action in movimentos:
            nx, ny = x + movimentos[action][0], y + movimentos[action][1]

            if not (0 <= nx < self.largura and 0 <= ny < self.altura):
                return  

            # Se o robô tentar andar acidentalmente para cima de um invasor
            if (nx, ny) in self.funcionarios_corredor:
                dados['paralisado'] = True
                dados['motivo_gameover'] = 'BATEU NUM INVASOR!'
                return

            dados['posicao'] = (nx, ny)

        elif action == 'Pegar':
            pos = dados['posicao']
            if pos in self.prateleiras and self.prateleiras[pos] > 0:
                self.prateleiras[pos] -= 1
                dados['tem_caixa'] = True

        elif action == 'Entregar':
            if dados['posicao'] == self.pos_entrega and dados['tem_caixa']:
                dados['tem_caixa'] = False
                dados['itens_entregues'] += 1

    def is_done(self):
        if not self.dados_agentes: return False
        todas_caixas = sum(self.prateleiras.values()) == 0
        todos_paralisados = all(d['paralisado'] for d in self.dados_agentes.values())
        return todas_caixas or todos_paralisados

    def step(self):
        # A cada "turno" da simulação, os invasores patrulham e o ambiente verifica o robô
        self.mover_invasores()
        super().step()
        for agent in self.dados_agentes:
            self.verificar_se_preso(agent)