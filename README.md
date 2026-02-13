# 🤖 Agente Inteligente de Almoxarifado (Warehouse Robot)

**Disciplina:** Inteligência Artificial  
**Grupo:** 07  
**Integrantes:** Niceu Santos Biriba, Hernandison da Silva Bispo, Letícia, João Marcos  

---

## 📖 Descrição do Projeto

Este projeto implementa um **Agente Racional Baseado em Objetivos** aplicado à logística de um almoxarifado automatizado.

O problema foi modelado como um **ambiente de grade (Grid World)**, no qual o agente deve planejar rotas inteligentes para:

- Navegar através de obstáculos dinâmicos (prateleiras);
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


MODO TERMINAL:

python main.py


MODO INTERFACE:

python interface.py


TESTES PYTESTS:

pytest tests/teste_almoxarifado.py -v
