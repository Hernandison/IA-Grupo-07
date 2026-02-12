import pytest
from warehouse import WarehouseProblem

def test_goal_state():
    """Teste para verificar se o objetivo é reconhecido corretamente."""
    # Cenário: Robô na posição de entrega (0,0) COM a caixa entregue (status 2)
    mapa_vazio = []
    problem = WarehouseProblem((0, 0, 0), mapa_vazio, (5,5), (0,0))
    
    estado_final = (0, 0, 2) # Status 2 = Entregue
    assert problem.goal_test(estado_final) == True

def test_heuristic_consistency():
    """Teste se a heurística é consistente (não negativa)."""
    mapa_vazio = []
    # Robô em (0,0), Caixa em (2,2), Entrega em (4,4)
    problem = WarehouseProblem((0, 0, 0), mapa_vazio, (2,2), (4,4))
    
    # Cria um nó dummy para testar h(n)
    from aima.search import Node
    node = Node((0, 0, 0))
    
    h_val = problem.h(node)
    # A distância deve ser > 0
    assert h_val > 0