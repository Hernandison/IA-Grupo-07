import sys
# Certifique-se que a pasta 'aima' está acessível ou os arquivos search.py/agents.py estão no mesmo diretório
sys.path.append('./aima')

from search import Problem, astar_search
from agents import Agent, Environment

# =============================================================================
# 1. PROBLEMA DE BUSCA (A*)
# =============================================================================

class WarehouseProblem(Problem):
    def __init__(self, initial, obstacles, target, delivery_pos, width=10, height=10):
        super().__init__(initial, goal=None)
        self.obstacles = obstacles # Posições que não são o alvo, mas bloqueiam
        self.target = target       # Onde queremos chegar (Prateleira ou Balcão)
        self.delivery_pos = delivery_pos
        self.width, self.height = width, height

    def actions(self, state):
        actions_list = []
        x, y, status = state 
        
        # Norte, Sul, Oeste, Leste
        moves = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}
        
        for action_name, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            # Verifica limites
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Pode andar se não for obstáculo OU se for o próprio alvo
                if (nx, ny) not in self.obstacles or (nx, ny) == self.target:
                    actions_list.append(action_name)

        # Ações de interação
        if (x, y) == self.target:
            if status == 0: actions_list.append('PickUp') # Pegar na prateleira
            if status == 1: actions_list.append('DropOff') # Entregar no balcão
            
        return actions_list

    def result(self, state, action):
        x, y, status = state
        if action == 'N': y -= 1
        elif action == 'S': y += 1
        elif action == 'W': x -= 1
        elif action == 'E': x += 1
        elif action == 'PickUp': return (x, y, 1)
        elif action == 'DropOff': return (x, y, 2)
        return (x, y, status)

    def goal_test(self, state):
        # O objetivo é ter realizado a ação final (status 2 = entregue ou status 1 = pegou, depende do sub-objetivo)
        # Mas para simplificar, o A* busca o caminho até chegar na posição.
        # A lógica do agente decide quando parar o A* e executar a ação.
        return False # Não usado diretamente no loop simples, usamos pathing

    def h(self, node):
        x, y, status = node.state
        def dist(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        # Heurística simples: Distância Manhattan até o alvo atual
        return dist((x, y), self.target)

# =============================================================================
# 2. O AGENTE
# =============================================================================

class WarehouseAgent(Agent):
    def __init__(self, start_pos, shelves_data, delivery_pos, grid_w, grid_h):
        super().__init__(self.agent_program)
        self.grid_w = grid_w
        self.grid_h = grid_h
        # shelves_data é um dict {(x,y): quantidade}
        self.shelves_memory = shelves_data.copy() 
        self.delivery_pos = delivery_pos
        self.plan = []
        self.current_target = None

    def agent_program(self, percept):
        current_pos = percept['pos']
        has_box = percept['has_box']
        
        # Se tem plano, executa
        if self.plan:
            return self.plan.pop(0)

        # Se não tem plano, decide o que fazer
        if has_box:
            # 1. Levar ao balcão
            # Obstáculos são todas as prateleiras (exceto o balcão se fosse obstáculo)
            obstacles = set(self.shelves_memory.keys())
            prob = WarehouseProblem((current_pos[0], current_pos[1], 1), obstacles, self.delivery_pos, self.delivery_pos, self.grid_w, self.grid_h)
            prob.goal_test = lambda state: state[0:2] == self.delivery_pos
            
            node = astar_search(prob)
            if node:
                self.plan = node.solution()
                self.plan.append('DropOff')
                return self.plan.pop(0) if self.plan else 'NoOp'
                
        else:
            # 2. Buscar item
            # Filtrar prateleiras com itens > 0
            available_shelves = [pos for pos, count in self.shelves_memory.items() if count > 0]
            
            if not available_shelves:
                return 'NoOp' # Acabou o trabalho

            # Escolher a mais próxima
            available_shelves.sort(key=lambda p: abs(p[0]-current_pos[0]) + abs(p[1]-current_pos[1]))
            target = available_shelves[0]
            
            # Obstáculos são todas as prateleiras MENOS a alvo (precisamos entrar nela/ficar em cima)
            obstacles = set(self.shelves_memory.keys()) - {target}
            
            prob = WarehouseProblem((current_pos[0], current_pos[1], 0), obstacles, target, self.delivery_pos, self.grid_w, self.grid_h)
            prob.goal_test = lambda state: state[0:2] == target
            
            node = astar_search(prob)
            if node:
                self.plan = node.solution()
                self.plan.append('PickUp')
                self.current_target = target # Memoriza onde está indo
                return self.plan.pop(0) if self.plan else 'NoOp'

        return 'NoOp'

# =============================================================================
# 3. O AMBIENTE
# =============================================================================

class WarehouseEnvironment(Environment):
    def __init__(self, width, height, shelves_data, delivery_pos):
        super().__init__()
        self.width, self.height = width, height
        # shelves_data: {(x,y): int_quantidade}
        self.shelves = shelves_data 
        self.delivery_pos = delivery_pos
        self.agents_data = {}

    def add_thing(self, agent, location=(0,0)):
        super().add_thing(agent, location)
        self.agents_data[agent] = {'pos': location, 'has_box': False, 'items_delivered': 0, 'last_action': None}

    def percept(self, agent):
        # O agente precisa saber o estado atualizado das prateleiras para decidir
        # (Em uma simulação real, ele teria que ver, aqui passamos a memória atualizada)
        agent.shelves_memory = self.shelves.copy()
        return self.agents_data[agent]

    def execute_action(self, agent, action):
        data = self.agents_data[agent]
        x, y = data['pos']
        data['last_action'] = action

        moves = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}
        
        if action in moves:
            dx, dy = moves[action]
            nx, ny = x + dx, y + dy
            # Checagem básica de colisão (o A* deve evitar, mas o ambiente garante)
            # Permitimos entrar na prateleira para pegar o item (abstração de "ficar na frente")
            if 0 <= nx < self.width and 0 <= ny < self.height:
                data['pos'] = (nx, ny)

        elif action == 'PickUp':
            if data['pos'] in self.shelves and self.shelves[data['pos']] > 0 and not data['has_box']:
                self.shelves[data['pos']] -= 1
                data['has_box'] = True

        elif action == 'DropOff':
            if data['pos'] == self.delivery_pos and data['has_box']:
                data['has_box'] = False
                data['items_delivered'] += 1

    def is_done(self):
        total_items_left = sum(self.shelves.values())
        agents_carrying = any(d['has_box'] for d in self.agents_data.values())
        return total_items_left == 0 and not agents_carrying