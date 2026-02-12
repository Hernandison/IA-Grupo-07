import sys
import math

# Ajuste de caminho para garantir importação se rodado isoladamente ou via main
sys.path.append('./aima')

from search import Problem, astar_search
from agents import Agent, Environment

# =============================================================================
# 1. A MODELAGEM DO PROBLEMA (BUSCA A*)
# =============================================================================

class WarehouseProblem(Problem):
    """
    Define o problema matemático de busca (Estados e Ações).
    
    Estados: Tupla (x, y, status_caixa)
        - x, y: Coordenadas na grade.
        - status_caixa: 
            0 = Caixa na prateleira (Precisa buscar)
            1 = Caixa com o robô (Carregando)
            2 = Caixa entregue (Objetivo final)
    """

    def __init__(self, initial, grid_map, box_pos, delivery_pos):
        # O objetivo é definido customizadamente em goal_test, então goal=None
        super().__init__(initial, goal=None)
        
        self.grid_map = grid_map
        self.box_pos = box_pos
        self.delivery_pos = delivery_pos
        self.width = 10  
        self.height = 10

    def actions(self, state):
        """Retorna a lista de ações válidas para o estado atual."""
        actions_list = []
        x, y, status = state

        # 1. Movimentos Básicos
        moves = {
            'Move(Norte)': (0, -1),
            'Move(Sul)':   (0, 1),
            'Move(Oeste)': (-1, 0),
            'Move(Leste)': (1, 0)
        }

        for action_name, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            # Verifica limites da grade (0-9) e se não é parede
            if (0 <= nx < self.width) and (0 <= ny < self.height) and ((nx, ny) not in self.grid_map):
                actions_list.append(action_name)

        # 2. Lógica de PEGAR (PickUp)
        # Condição: Estar no local da caixa E a caixa ainda estar lá (status 0)
        if (x, y) == self.box_pos and status == 0:
            actions_list.append('PickUp')

        # 3. Lógica de SOLTAR (DropOff)
        # Condição: Estar no local de entrega E estar carregando a caixa (status 1)
        if (x, y) == self.delivery_pos and status == 1:
            actions_list.append('DropOff')

        return actions_list

    def result(self, state, action):
        """Retorna o novo estado (simulado) após aplicar a ação."""
        x, y, status = state

        if 'Move' in action:
            if 'Norte' in action: y -= 1
            if 'Sul'   in action: y += 1
            if 'Oeste' in action: x -= 1
            if 'Leste' in action: x += 1
            return (x, y, status)

        elif action == 'PickUp':
            return (x, y, 1) # Robô agora tem a caixa

        elif action == 'DropOff':
            return (x, y, 2) # Caixa foi entregue

        return state

    def goal_test(self, state):
        """O objetivo é atingido apenas quando o status é 2 (Entregue)."""
        return state[2] == 2

    def h(self, node):
        """
        Função Heurística (Distância Manhattan).
        Guia o A* para ser inteligente e não apenas aleatório.
        """
        x, y, status = node.state
        
        def manhattan(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        if status == 0:
            # Se não pegou a caixa: Custo para ir até a caixa + custo da caixa até a entrega
            return manhattan((x, y), self.box_pos) + manhattan(self.box_pos, self.delivery_pos)
        
        elif status == 1:
            # Se já pegou: Custo para ir até a entrega
            return manhattan((x, y), self.delivery_pos)
        
        else:
            # Se entregou: Custo zero (chegou)
            return 0

# =============================================================================
# 2. O AGENTE (CÉREBRO)
# =============================================================================

class WarehouseAgent(Agent):
    """
    O Agente que vive no ambiente.
    Ciclo: Perceber -> Planejar (usando A*) -> Agir
    """
    def __init__(self, start_pos, grid_map, box_pos, delivery_pos):
        super().__init__()
        # Estado mental inicial do agente
        self.state = (start_pos[0], start_pos[1], 0)
        self.grid_map = grid_map
        self.box_pos = box_pos
        self.delivery_pos = delivery_pos
        
        self.plan = [] # Fila de ações para executar

    def execute(self, percept):
        """Chamado automaticamente pelo Environment a cada passo."""
        
        # 1. Interpretar Percepção (Atualizar onde estou)
        current_pos = percept['pos']
        has_box = percept['has_box']
        
        # Lógica para manter o estado 2 (Entregue) se já tiver entregue
        status = 1 if has_box else (2 if self.state[2] == 2 else 0)
        self.state = (current_pos[0], current_pos[1], status)

        # 2. Verificar Objetivo
        if status == 2:
            return 'NoOp' # Missão cumprida, descansa.

        # 3. Deliberação (Planejamento)
        # Se a fila de planos acabou, calcula uma nova rota
        if not self.plan:
            print(f"\n[Agente] Calculando rota A* a partir de {self.state}...")
            
            problem = WarehouseProblem(self.state, self.grid_map, self.box_pos, self.delivery_pos)
            solution_node = astar_search(problem)
            
            if solution_node:
                self.plan = solution_node.solution()
                print(f"[Agente] Plano gerado: {self.plan}")
            else:
                print("[Agente] ERRO: Caminho bloqueado ou impossível!")
                return 'NoOp'

        # 4. Ação
        if self.plan:
            action = self.plan.pop(0) # Pega a próxima ação da fila
            return action
        
        return 'NoOp'

# =============================================================================
# 3. O AMBIENTE (FÍSICA/SIMULAÇÃO)
# =============================================================================

class WarehouseEnvironment(Environment):
    """
    Representa o mundo real (Almoxarifado).
    Valida se o robô bateu na parede e se pegou a caixa de verdade.
    """
    def __init__(self, width, height, walls, box_pos, delivery_pos):
        super().__init__()
        self.width = width
        self.height = height
        self.walls = walls
        self.box_pos = box_pos
        self.delivery_pos = delivery_pos
        
        # Dicionário para guardar o estado real de cada agente no mundo
        self.agents_data = {} 

    def add_thing(self, agent, location=None):
        super().add_thing(agent, location)
        # Define estado inicial real no ambiente
        self.agents_data[agent] = {'pos': location, 'has_box': False}

    def percept(self, agent):
        """O que o agente consegue sentir/ver."""
        data = self.agents_data[agent]
        return {'pos': data['pos'], 'has_box': data['has_box']}

    def execute_action(self, agent, action):
        """Executa a ação física e printa o log."""
        data = self.agents_data[agent]
        x, y = data['pos']

        if action == 'NoOp':
            return

        elif 'Move' in action:
            nx, ny = x, y
            if 'Norte' in action: ny -= 1
            if 'Sul'   in action: ny += 1
            if 'Oeste' in action: nx -= 1
            if 'Leste' in action: nx += 1

            # Checagem de colisão real
            if (nx, ny) in self.walls:
                print(f"   [Ambiente] BLOQUEADO: Agente bateu na parede em ({nx}, {ny})")
            elif not (0 <= nx < self.width and 0 <= ny < self.height):
                print(f"   [Ambiente] BLOQUEADO: Agente tentou sair do mapa")
            else:
                data['pos'] = (nx, ny)
                print(f"   [Ambiente] Agente moveu para {data['pos']}")

        elif action == 'PickUp':
            if (x, y) == self.box_pos and not data['has_box']:
                data['has_box'] = True
                print("   [Ambiente] --- CAIXA COLETADA! ---")
            else:
                print("   [Ambiente] Ação PickUp ignorada (local incorreto).")

        elif action == 'DropOff':
            if (x, y) == self.delivery_pos and data['has_box']:
                data['has_box'] = False
                print("   [Ambiente] >>> CAIXA ENTREGUE COM SUCESSO! <<<")
            else:
                print("   [Ambiente] Ação DropOff ignorada.")