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

A solução utiliza a arquitetura **Ambiente – Agente – Programa de Agente** e aplica o algoritmo de busca **A\*** (A-Star), inspirado na abordagem de Russell & Norvig, para encontrar o caminho mais curto até os objetivos.

---

## ✨ Principais Funcionalidades

- 🎮 Interface Gráfica Interativa com estética "Retro/16-bit"
- 🛠 Editor de Cenário para criação de layouts personalizados
- 🧠 Pathfinding com A\* (heurística Manhattan)
- 📦 Múltiplas Entregas com coleta sequencial de itens
- 🔄 Replanejamento automático para o item mais próximo

---

## 📂 Estrutura do Projeto


### 📄 Descrição dos Arquivos

- **interface.py**  
  Responsável pela interface gráfica e controle da simulação.

- **warehouse.py**  
  Implementa o ambiente, o agente racional e o algoritmo A\*.

- **aima/** (opcional)  
  Contém arquivos auxiliares baseados na biblioteca AIMA (caso não estejam instalados via `pip`).

---

## 🚀 Instalação e Execução

### 📌 Pré-requisitos

- Python 3.8 ou superior
- Tkinter (normalmente já incluso na instalação padrão do Python)

---

### 🔧 Passo a Passo

1. Clone este repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_PROJETO>


python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate



pip install -r requirements.txt


python interface.py
