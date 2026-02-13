# Arquivo: tests/teste_almoxarifado.py

import pytest
import sys
import os

# Adiciona a raiz do projeto ao path para que o pytest encontre as pastas env, agents, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Resolve dependências internas do AIMA para os testes
import aima.utils
sys.modules['utils'] = aima.utils

from problems.problema_almoxarifado import ProblemaAlmoxarifado
from env.ambiente_almoxarifado import AmbienteAlmoxarifado
from agents.agente_almoxarifado import AgenteAlmoxarifado
from aima.search import astar_search, Node

# =============================================================================
# FIXTURES (Cenários Automáticos de Teste)
# =============================================================================

@pytest.fixture
def setup_padrao():
    """Configuração padrão: Mapa 10x10, Parede em (1,0) a (1,2), Caixa em (2,2), Destino em (4,4)"""
    prateleiras = {
        (1, 0): 0, (1, 1): 0, (1, 2): 0, # Barreira vertical (0 itens = obstáculo)
        (2, 2): 1                        # Onde está o item a ser buscado
    }
    pos_inicial = (0, 0)
    pos_entrega = (4, 4)
    return prateleiras, pos_inicial, pos_entrega

# =============================================================================
# TESTES DE MODELAGEM (ProblemaAlmoxarifado)
# =============================================================================

def test_restricoes_movimento(setup_padrao):
    """Garante que o robô não atravesse prateleiras vazias (paredes)"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    alvo = (2, 2)
    obstaculos = set(prateleiras.keys()) - {alvo} 
    
    # Inicia em (0,1). Com prateleira em (1,1), a ação 'L' (Leste) deve ser proibida.
    estado_inicial = (0, 1, 0)
    problema = ProblemaAlmoxarifado(estado_inicial, obstaculos, alvo, pos_entrega)
    
    acoes = problema.actions(estado_inicial)
    assert 'L' not in acoes  # Bloqueado pela prateleira
    assert 'N' in acoes      # Caminho livre para o Norte

def test_logica_pegar(setup_padrao):
    """Verifica se a ação 'Pegar' só aparece no local exato do alvo"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    alvo = (2, 2)
    obstaculos = set(prateleiras.keys()) - {alvo}
    
    # Caso 1: Fora do local da caixa
    estado_longe = (0, 0, 0)
    prob1 = ProblemaAlmoxarifado(estado_longe, obstaculos, alvo, pos_entrega)
    assert 'Pegar' not in prob1.actions(estado_longe)
    
    # Caso 2: No local exato da caixa
    estado_no_alvo = (2, 2, 0)
    prob2 = ProblemaAlmoxarifado(estado_no_alvo, obstaculos, alvo, pos_entrega)
    assert 'Pegar' in prob2.actions(estado_no_alvo)

def test_admissibilidade_heuristica(setup_padrao):
    """Verifica se a Heurística de Manhattan nunca é negativa e diminui ao se aproximar"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    alvo = (2, 2)
    obstaculos = set(prateleiras.keys()) - {alvo}
    
    problema = ProblemaAlmoxarifado((0,0,0), obstaculos, alvo, pos_entrega)
    
    no_longe = Node((0, 0, 0))
    no_perto = Node((1, 1, 0))
    
    h_longe = problema.h(no_longe)
    h_perto = problema.h(no_perto)
    
    assert h_longe > h_perto
    assert h_perto >= 0

# =============================================================================
# TESTES DE INTEGRAÇÃO (Agente + Ambiente + Busca)
# =============================================================================

def test_solucao_missao_completa(setup_padrao):
    """Teste de fôlego: Verifica se o A* encontra uma rota válida contornando a parede"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    alvo = (2, 2)
    obstaculos = set(prateleiras.keys()) - {alvo}
    
    # Estado: (0,0) sem caixa. Alvo: (2,2)
    estado_inicial = (0, 0, 0)
    problema = ProblemaAlmoxarifado(estado_inicial, obstaculos, alvo, pos_entrega)
    # Injeta a condição de paragem igual à feita pelo agente
    problema.goal_test = lambda state: state[0:2] == alvo
    
    solucao = astar_search(problema)
    
    assert solucao is not None
    assert len(solucao.solution()) > 0 # Garante que gerou passos de movimento

def test_execucao_ambiente(setup_padrao):
    """Verifica se o Ambiente processa ações e atualiza a posição física do agente"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    
    ambiente = AmbienteAlmoxarifado(10, 10, prateleiras.copy(), pos_entrega)
    agente = AgenteAlmoxarifado(pos_inicial, prateleiras.copy(), pos_entrega, 10, 10)
    ambiente.add_thing(agente, location=pos_inicial) # Agente em (0,0)
    
    # Força uma ação manual de movimento
    ambiente.execute_action(agente, 'S') # Move para o Sul
    
    # Verifica se a posição real no ambiente mudou para (0, 1)
    assert ambiente.dados_agentes[agente]['posicao'] == (0, 1)

def test_deliberacao_agente(setup_padrao):
    """Verifica se o programa do agente gera um plano automaticamente ao receber percepção"""
    prateleiras, pos_inicial, pos_entrega = setup_padrao
    agente = AgenteAlmoxarifado(pos_inicial, prateleiras.copy(), pos_entrega, 10, 10)
    
    # Simula percepção inicial: robô em (0,0) sem caixa, vendo as prateleiras
    percepcao = {'posicao': (0, 0), 'tem_caixa': False}
    
    acao = agente.programa_agente(percepcao)
    
    # O agente deve ter decidido uma ação (pois há uma caixa em 2,2)
    assert acao != 'NoOp'
    assert len(agente.plano) > 0 # O plano deve ter sido populado pelo A*