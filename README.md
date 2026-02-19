# 🤖 Agente Inteligente de Almoxarifado (Warehouse Robot)

**Disciplina:** Inteligência Artificial  
**Grupo:** 07  
**Integrantes:** Niceu Santos Biriba, Hernandison da Silva Bispo, Letícia Oliveira, João Marcos  

---

## 1) 📖 Descrição do Projeto

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

## 2) ✅ Especificação Formal do Problema (AIMA) + Mapeamento no Código

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

## 3) ✅ Classificação do Ambiente (AIMA)

Classificação do ambiente do Almoxarifado, conforme Russell & Norvig:

- **Determinístico**: dada uma ação, o próximo estado é definido (não há aleatoriedade).
- **Totalmente observável**: a percepção do agente contém a posição atual e a visão do mapa de prateleiras (cópia do dicionário do ambiente).
- **Estático (durante o raciocínio)**: o mundo não muda “sozinho”; só muda por ações do agente (pegar/entregar altera quantidades).
- **Discreto**: estados (células) e ações (passos) são discretos.
- **Agente único**: a simulação e a política são modeladas para um robô (embora a classe `Environment` suporte adicionar mais agentes).

---

## 4) Programa de Agente (onde a busca acontece)

O algoritmo de busca **não é chamado isoladamente**: ele faz parte do ciclo deliberativo do agente.

- **Ambiente Simulado (Environment):** O projeto utiliza a arquitetura base do AIMA para gerir o ciclo de perceção e ação. A classe `AmbienteAlmoxarifado` gere as regras físicas do mapa (limites e prateleiras). Isso foi escolhido porque separa a "física" do mundo do "cérebro" do robô, cumprindo o requisito estrutural da disciplina.
- **Agente Baseado em Modelos (Model-Based Agent):** O agente mantém um estado interno do mundo que não consegue ver num único relance. O `AgenteAlmoxarifado` guarda o mapa das prateleiras na variável `memoria_prateleiras`. Isso é essencial porque, num almoxarifado, o robô precisa de lembrar onde estão as caixas sem ter de explorar o mapa às cegas a cada turno.
- **Agente Baseado em Objetivos (Goal-Based Agent):** O robô não reage apenas a estímulos imediatos; ele projeta o futuro para atingir um alvo (sub-objetivo). O programa decide dinamicamente o seu objetivo: se está vazio, o objetivo é uma prateleira; se tem uma caixa, o objetivo é o balcão.

---

## 📂 Estrutura do Projeto

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

git clone [https://github.com/Hernandison/IA-Grupo-07.git](https://github.com/Hernandison/IA-Grupo-07.git)
cd IA-Grupo-07

# No Windows:
python -m venv venv
venv\Scripts\activate

# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt


#MODO TERMINAL:

python main.py


#MODO INTERFACE:

python interface.py


#TESTES PYTESTS:

pytest -v

# (alternativa equivalente)
# pytest tests/teste_almoxarifado.py -v
