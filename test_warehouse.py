import pytest
import sys
import os

# Garante que o diretório atual e a pasta aima estejam no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'aima')))

from warehouse import WarehouseProblem, WarehouseEnvironment, WarehouseAgent
from aima.search import astar_search, Node

# =============================================================================
# FIXTURES (Cenários Automáticos)
# =============================================================================

@pytest.fixture
def default_setup():
    """Configuração padrão: Mapa 10x10, Paredes em L, Caixa em (2,2), Destino em (4,4)"""
    walls = [(1, 0), (1, 1), (1, 2)] # Uma barreira vertical
    box_pos = (2, 2)
    delivery_pos = (4, 4)
    return walls, box_pos, delivery_pos

# =============================================================================
# TESTES DE MODELAGEM (WarehouseProblem)
# =============================================================================

def test_movement_restrictions(default_setup):
    """Garante que o robô não atravesse prateleiras (paredes)"""
    walls, box_pos, delivery_pos = default_setup
    # Inicia em (0,1). Com paredes em (1,1), a ação 'Move(Leste)' deve ser proibida.
    initial_state = (0, 1, 0)
    problem = WarehouseProblem(initial_state, walls, box_pos, delivery_pos)
    
    actions = problem.actions(initial_state)
    assert 'Move(Leste)' not in actions
    assert 'Move(Norte)' in actions # Caminho livre

def test_pickup_logic(default_setup):
    """Verifica se a ação PickUp só aparece no local correto"""
    walls, box_pos, delivery_pos = default_setup
    
    # Caso 1: Fora do local da caixa
    state_away = (0, 0, 0)
    prob1 = WarehouseProblem(state_away, walls, box_pos, delivery_pos)
    assert 'PickUp' not in prob1.actions(state_away)
    
    # Caso 2: No local da caixa
    state_at_box = (2, 2, 0)
    prob2 = WarehouseProblem(state_at_box, walls, box_pos, delivery_pos)
    assert 'PickUp' in prob2.actions(state_at_box)

def test_heuristic_admissibility(default_setup):
    """Verifica se a Heurística de Manhattan nunca é negativa e diminui ao chegar no alvo"""
    walls, box_pos, delivery_pos = default_setup
    
    # Robô longe da caixa
    node_far = Node((0, 0, 0))
    # Robô mais perto da caixa
    node_near = Node((1, 1, 0))
    
    problem = WarehouseProblem((0,0,0), walls, box_pos, delivery_pos)
    
    h_far = problem.h(node_far)
    h_near = problem.h(node_near)
    
    assert h_far > h_near
    assert h_near >= 0

# =============================================================================
# TESTES DE INTEGRAÇÃO (Agente + Ambiente + Busca)
# =============================================================================

def test_complete_mission_solve(default_setup):
    """Teste de fôlego: Verifica se o A* encontra uma solução válida em um cenário com paredes"""
    walls, box_pos, delivery_pos = default_setup
    # Estado: (0,0) sem caixa. Alvo: (4,4) com status 2 (entregue).
    initial_state = (0, 0, 0)
    problem = WarehouseProblem(initial_state, walls, box_pos, delivery_pos)
    
    solution = astar_search(problem)
    
    assert solution is not None
    assert 'PickUp' in solution.solution()
    assert 'DropOff' in solution.solution()

def test_environment_execution(default_setup):
    """Verifica se o Ambiente atualiza corretamente a posição física do agente"""
    walls, box_pos, delivery_pos = default_setup
    env = WarehouseEnvironment(10, 10, walls, box_pos, delivery_pos)
    agent = WarehouseAgent((0, 0), walls, box_pos, delivery_pos)
    env.add_thing(agent, location=(0, 0))
    
    # Executa uma ação de movimento manual no ambiente
    env.execute_action(agent, 'Move(Sul)')
    
    # Verifica se a posição real no ambiente mudou para (0, 1)
    assert env.agents_data[agent]['pos'] == (0, 1)

def test_agent_deliberation(default_setup):
    """Verifica se o programa do agente gera um plano automaticamente ao receber percepção"""
    walls, box_pos, delivery_pos = default_setup
    agent = WarehouseAgent((0, 0), walls, box_pos, delivery_pos)
    
    # Simula percepção inicial: robô em (0,0) sem caixa
    percept = {'pos': (0, 0), 'has_box': False}
    
    action = agent.agent_program(percept)
    
    # O agente deve ter decidido uma ação (não pode ser NoOp se houver caminho)
    assert action != 'NoOp'
    assert len(agent.plan) > 0 # O plano deve ter sido populado pelo A*