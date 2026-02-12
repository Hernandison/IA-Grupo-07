# 🤖 Agente Inteligente de Almoxarifado (Warehouse Robot)

**Disciplina:** Inteligência Artificial  
**Grupo:** 07  
**Integrantes:** Niceu Santos Biriba, Hernandison da Silva Bispo, Letícia, João Marcos  

---

## 📖 Descrição do Projeto

Este projeto implementa um agente racional baseado em objetivos para atuar na logística de um almoxarifado automatizado. O problema foi modelado como um ambiente de grade (Grid World) onde o agente deve planejar uma rota para:
1. Navegar através de obstáculos (prateleiras).
2. Localizar e coletar um item (Caixa).
3. Transportar o item até a zona de entrega.

A solução utiliza a arquitetura **Ambiente - Agente - Programa de Agente** e algoritmos de busca competitiva (A*) da biblioteca `aima-python` (Russell & Norvig).

---

## 🚀 Como Executar

### Pré-requisitos
* Python 3.8 ou superior.
* As bibliotecas listadas em `requirements.txt`.

### Instalação
1. Clone ou baixe este repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt