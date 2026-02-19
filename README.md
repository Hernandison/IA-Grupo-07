# 🤖 Agente Inteligente de Almoxarifado (Warehouse Robot)

**Disciplina:** Inteligência Artificial  
**Grupo:** 07  
**Integrantes:** Niceu Santos Biriba, Hernandison da Silva Bispo, Letícia Oliveira, João Marcos  

---

## 1) Descrição do Projeto

Este projeto implementa um **Agente Racional Baseado em Objetivos** aplicado à logística de um almoxarifado automatizado.

O problema foi modelado como um **ambiente de grade (Grid World)**, no qual o agente deve planejar rotas inteligentes para:

- Navegar através de obstáculos (prateleiras/paredes);
- Localizar e coletar itens distribuídos no armazém;
- Transportar os itens até a zona de entrega (Balcão).

A solução utiliza a arquitetura **Ambiente – Agente – Programa de Agente** e aplica o algoritmo de busca **A\*** (A-Star), inspirado na abordagem de Russell & Norvig (AIMA), para encontrar o caminho mais curto até os objetivos.

---

## ✨ Principais Funcionalidades

- 🎮 **Interface Gráfica Interativa** com estética "Retro/16-bit".
- 🛠 **Editor de Cenário** para criação de layouts e obstáculos personalizados.
- 🧠 **Pathfinding com A\*** utilizando a heurística de Distância de Manhattan.
- 📦 **Múltiplas Entregas** com coleta sequencial de itens.
- 🔄 **Replanejamento automático** (Heurística Gulosa de alto nível para decidir a prateleira mais próxima).

---

## 🧠 Arquitetura e Algoritmos do AIMA

Para cumprir os requisitos da disciplina, o projeto foi construído herdando as classes base do repositório `aima-python`.

### ✅ Classes e Algoritmos Utilizados
* **`Environment`** (de `aima.agents`): Utilizado como base para a classe `AmbienteAlmoxarifado`. Mantém o estado do mundo, as posições das prateleiras, do balcão e gerencia a física do robô.
* **`Agent`** (de `aima.agents`): Base para a classe `AgenteAlmoxarifado`. Mantém o ciclo de receber percepções e retornar ações através do método genérico `agent_program`.
* **`Problem`** (de `aima.search`): Base para a classe `ProblemaAlmoxarifado`. Formaliza a representação dos estados, modelo de transição, conjunto de ações e teste de objetivo.
* **`astar_search`** (Busca A*): O algoritmo principal utilizado no programa do agente. Foi escolhido pois o problema de navegação em grade exige uma solução **ótima e completa**. Como conhecemos as coordenadas do agente e do alvo, a heurística de Manhattan garante que o A* expanda o menor número possível de nós para encontrar o caminho mais curto, contornando prateleiras de forma inteligente.

### ❌ Algoritmos Não Utilizados (e porquê)
* **Buscas Cegas (BFS, DFS, Custo Uniforme):** Foram descartadas porque não utilizam informação do estado objetivo (heurística). Num ambiente de grade (*Grid World*), a BFS expandiria nós radialmente em todas as direções, sendo muito ineficiente. A DFS não garante o caminho mais curto (não é ótima).
* **Greedy Best-First Search (Busca Gulosa):** Embora rápida, não foi utilizada no pathfinding porque não é ótima e não é completa (pode ficar presa em obstáculos em formato de "U", comuns em layouts de prateleiras).
* **Buscas Locais (Hill Climbing, Simulated Annealing):** Descartadas por não serem adequadas para problemas clássicos de navegação labiríntica, visto que o agente ficaria facilmente preso em máximos locais (encurralado atrás de uma prateleira).

---

## 2) Especificação Formal do Problema (AIMA) + Mapeamento no Código

O problema é resolvido como uma sequência de **subproblemas de navegação em grade** (ir até uma prateleira com item; depois ir até o balcão). Cada subproblema é modelado como uma instância de `ProblemaAlmoxarifado`.

### Representação dos estados
- **Estado**: tupla `(x, y, status)`
	- `x, y`: coordenadas do robô no grid
	- `status`: 0 (sem caixa), 1 (com caixa), 2 (entregou)
- Implementação: `problems/problema_almoxarifado.py` (`ProblemaAlmoxarifado`).

### Estado inicial
- Definido pelo programa do agente a partir da percepção do ambiente:
	- Ex.: `(pos_atual[0], pos_atual[1], 0)` para buscar item
	- Ex.: `(pos_atual[0], pos_atual[1], 1)` para entregar no balcão
- Implementação: `agents/agente_almoxarifado.py` (`programa_agente`).

### Conjunto de ações
- Movimentos discretos: `N`, `S`, `O`, `L`.
- Ações de interação: `Pegar`, `Entregar` (disponíveis apenas quando o robô está no alvo do subproblema).
- Implementação: `problems/problema_almoxarifado.py` (`actions`).

### Modelo de transição `result(s, a)`
- Movimentos atualizam `(x, y)`.
- `Pegar` muda o `status` para 1.
- `Entregar` muda o `status` para 2.
- Implementação: `problems/problema_almoxarifado.py` (`result`).

### Teste de objetivo `goal_test(s)`
- Para cada subproblema, o objetivo é **chegar na coordenada alvo** (prateleira ou balcão).
- Implementação: `problems/problema_almoxarifado.py` (`goal_test`).

### Custo de caminho `path_cost`
- Cada movimento custa 1 (custo uniforme), herdado da classe `Problem` do AIMA.
- Observação: a ação de interação (`Pegar`/`Entregar`) não é parte do caminho de navegação retornado pelo A* neste projeto; ela é executada ao final do plano.

### Heurística `h(n)`
- Heurística: Distância de Manhattan até o alvo.
- Implementação: `problems/problema_almoxarifado.py` (`h`).

---

## 3) Classificação do Ambiente (AIMA)

Classificação do ambiente do Almoxarifado, conforme Russell & Norvig:

- **Determinístico**: dada uma ação, o próximo estado é definido (não há aleatoriedade).
- **Totalmente observável**: a percepção do agente contém a posição atual e a visão do mapa de prateleiras (cópia do dicionário do ambiente).
- **Estático (durante o raciocínio)**: o mundo não muda “sozinho”; só muda por ações do agente (pegar/entregar altera quantidades).
- **Discreto**: estados (células) e ações (passos) são discretos.
- **Agente único**: a simulação e a política são modeladas para um robô (embora a classe `Environment` suporte adicionar mais agentes).

---

## 4) Arquitetura: Ambiente – Agente – Programa de Agente

A implementação respeita explicitamente a separação arquitetural exigida pelo AIMA, com cada componente em um módulo distinto e com responsabilidades bem definidas.

### Ambiente (`AmbienteAlmoxarifado` — `env/ambiente_almoxarifado.py`)

O Ambiente é responsável por:
- **Manter o estado do mundo**: dicionário de prateleiras, posição de cada agente, quantidade de itens entregues.
- **Fornecer percepções**: método `percept(agent)` retorna a percepção atual do agente.
- **Executar ações**: método `execute_action(agent, action)` aplica a ação física no mundo (movimento, coleta, entrega).
- **Render**: método `render()` imprime o estado visual do mundo a cada passo.

**Exemplo de ciclo no Ambiente:**
```python
# A classe Environment do AIMA chama este ciclo:
def step(self):
    super().step()  # Chama agent_program para cada agente
    self.render()   # Mostra novo estado
```

### Agente (`AgenteAlmoxarifado` — `agents/agente_almoxarifado.py`)

O Agente é a entidade **inserida no ambiente**:
- Mantém memória do mapa de prateleiras (`memoria_prateleiras`).
- Possui um **programa de agente** (função `programa_agente`) que é chamado a cada passo.
- Acumula um **plano** (sequência de ações gerada pelo A*) na variável `self.plano`.

**Ciclo de vida:**
```python
class AgenteAlmoxarifado(Agent):
    def __init__(self, pos_inicial, dados_prateleiras, ...):
        super().__init__(self.programa_agente)  # Registra o programa
        self.memoria_prateleiras = dados_prateleiras
        self.plano = []  # Plano de ações gerado pela busca
    
    def programa_agente(self, percepcao):
        # Função que decide ações a partir de percepções
        # (detalhado em 4.3)
```

### Programa de Agente (dentro de `programa_agente` — `agents/agente_almoxarifado.py`)

Este é o **núcleo do projeto**, onde a separação conceitual é mais crítica.

O programa de agente é uma **função que:**

#### 1️⃣ Recebe Percepções do Ambiente
```python
def programa_agente(self, percepcao):
    pos_atual = percepcao['posicao']
    tem_caixa = percepcao['tem_caixa']
    # A percepção fornece o que o agente "vê" no mundo
```

#### 2️⃣ Decide Quando Formular um Problema
```python
# Se tem um plano na memória, executa o próximo passo
if self.plano:
    return self.plano.pop(0)

# Se não tem plano, cria um novo subproblema
if tem_caixa:
    alvo = self.pos_entrega  # Sub-objetivo: balcão
else:
    # Escolhe a prateleira com item mais próxima
    prateleiras_disponiveis = [...]
    alvo = prateleiras_disponiveis[0]
```

#### 3️⃣ Executa Algoritmo de Busca para Gerar Plano
```python
# Formula o subproblema (instância de ProblemaAlmoxarifado)
obstaculos = set(self.memoria_prateleiras.keys()) - {alvo}
prob = ProblemaAlmoxarifado(
    (pos_atual[0], pos_atual[1], status_caixa),
    obstaculos,
    alvo,
    self.pos_entrega,
    self.largura_grid,
    self.altura_grid
)

# ⚠️ AQUI: Chama A* para gerar o plano (sequência de ações)
no_solucao = astar_search(prob)

if no_solucao:
    self.plano = no_solucao.solution()  # Lista de ações
    self.plano.append('Pegar')  # Ou 'Entregar' conforme o contexto
```

#### 4️⃣ Retorna Uma Ação por Passo
```python
# A cada chamada do programa, retorna apenas UMA ação
return self.plano.pop(0) if self.plano else 'NoOp'
```

### Relação com `SimpleProblemSolvingAgentProgram` (AIMA)

O `programa_agente` implementa o **conceito central** de `SimpleProblemSolvingAgentProgram`:

| Etapa AIMA | Implementação no Projeto |
|-----------|-------------------------|
| Formulate Goal | Dinâmico: `alvo = self.pos_entrega` ou `alvo = prateleira_mais_prox` |
| Formulate Problem | `ProblemaAlmoxarifado(estado_inicial, obstáculos, alvo, ...)` |
| Search | `astar_search(prob)` retorna nó-solução com caminho |
| Extract Plan | `no_solucao.solution()` extrai sequência de ações |
| Execute One Step | `return self.plano.pop(0)` retorna 1 ação; Ambiente executa |

### Fluxo Completo de Uma Interação

```
[ AMBIENTE ]
    ↓ (percept)
[ PROGRAMA DE AGENTE ]
    ↓ (se sem plano, cria subproblema)
[ A* SEARCH ]
    ↓ (retorna solução: nó com .solution())
[ PROGRAMA DE AGENTE ]
    ↓ (extrai plano e retorna 1 ação)
[ AMBIENTE ]
    ↓ (execute_action aplica ação física no mundo)
[ render() mostra o novo estado ]
```

Este ciclo se repete até o ambiente estar completo (`is_done()`).

---

##  Estrutura do Projeto

O código foi rigorosamente organizado para respeitar a arquitetura exigida:

```text
/IA-Grupo-07
├── /env                    # Contém a física e as regras do mundo
│   └── ambiente_almoxarifado.py
├── /agents                 # Contém a inteligência e tomada de decisão
│   └── agente_almoxarifado.py
├── /problems               # Contém a formulação matemática da busca
│   └── problema_almoxarifado.py
├── /tests                  # Contém os testes automatizados da modelagem
│   └── teste_almoxarifado.py
├── /aima                   # Biblioteca base Russell & Norvig (aima-python)
├── main.py                 # Script de execução em modo Terminal/Texto
├── interface.py            # Script de execução em modo Interface Gráfica
└── README.md
```

---

## Como Usar / Getting Started

### 1. Clonar e Preparar o Ambiente

```bash
git clone [https://github.com/Hernandison/IA-Grupo-07.git](https://github.com/Hernandison/IA-Grupo-07.git)
cd IA-Grupo-07

# No Windows:
python -m venv venv
venv\Scripts\activate

# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Executar o Agente

#### 🖥️ Modo Terminal (Texto)
Vê o agente em ação com render `render()` imprimindo a grade a cada passo. Útil para **debug** e **avaliação** do algoritmo.

```bash
python main.py
```

Você verá algo como:
```
===========================================================
   PROJETO GRUPO 07: AGENTE INTELIGENTE DE ALMOXARIFADO
===========================================================

-> Mapa: 10x10
-> Agente Inicia em: (0, 0)
-> Zona de Entrega:  (0, 9)
-> Prateleiras/Obstáculos: 14 blocos registrados
------------------------------------------------------------
Iniciando simulação do agente...

===================================
 ESTADO ATUAL DO ALMOXARIFADO
===================================
 🤖  .    .    .    .     .      .      .      . [1].    
 ...
```

#### 🎮 Modo Interface Gráfica (Retro/16-bit)
Editor visual para criar cenários personalizados e visualizar o agente navegando em tempo real.

```bash
python interface.py
```

### 3. Rodar Testes Automatizados

Valida a **modelagem formal** do problema (estados, ações, transições, heurística):

```bash
pytest tests/teste_almoxarifado.py -v
```

Resultados esperados:
```
tests/teste_almoxarifado.py::test_restricoes_movimento PASSED
tests/teste_almoxarifado.py::test_logica_pegar PASSED
tests/teste_almoxarifado.py::test_admissibilidade_heuristica PASSED
tests/teste_almoxarifado.py::test_solucao_missao_completa PASSED
tests/teste_almoxarifado.py::test_execucao_ambiente PASSED
tests/teste_almoxarifado.py::test_deliberacao_agente PASSED

====== 6 passed in 0.76s ======
```
