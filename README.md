
🤖 Agente Inteligente de Almoxarifado (Warehouse Robot)

Disciplina: Inteligência Artificial
Grupo: 07
Integrantes: Niceu Santos Biriba, Hernandison da Silva Bispo, Letícia, João Marcos

📖 Descrição do Projeto

Este projeto implementa um Agente Racional Baseado em Objetivos para atuar na logística de um almoxarifado automatizado. O problema foi modelado como um ambiente de grade (Grid World) onde o agente deve planejar rotas inteligentes para:

Navegar através de obstáculos dinâmicos (prateleiras).

Localizar e Coletar itens distribuídos no armazém.

Transportar os itens até a zona de entrega (Balcão).

A solução utiliza a arquitetura Ambiente - Agente - Programa de Agente e aplica algoritmos de busca competitiva (Busca A*) da biblioteca baseada em Russell & Norvig para encontrar o caminho mais curto.

✨ Principais Funcionalidades

Interface Gráfica Interativa: Visualização em tempo real com estética "Retro/16-bit".

Editor de Cenário: Permite criar layouts personalizados de prateleiras e obstáculos.

Pathfinding A:* O robô recalcula rotas automaticamente para buscar o item mais próximo.

Múltiplas Entregas: Suporte para coleta sequencial de vários itens antes de finalizar a missão.

📂 Estrutura do Projeto

interface.py: Arquivo principal. Contém a interface gráfica (GUI) em Tkinter e o loop de animação.

warehouse.py: Contém a lógica da Inteligência Artificial (Ambiente, Agente e Algoritmo A*).

aima/: (Opcional) Diretório contendo as bibliotecas auxiliares de IA (search.py, agents.py), caso não estejam instaladas via pip.

🚀 Instalação e Execução
Pré-requisitos

Python 3.8 ou superior.

Biblioteca tkinter (geralmente já vem instalada com o Python).

Passo a Passo

Clone ou baixe este repositório para sua máquina local.

(Opcional) Crie e ative um ambiente virtual.

Instale as dependências necessárias (caso utilize bibliotecas externas):

code
Bash
download
content_copy
expand_less
pip install -r requirements.txt

Execute o Simulador:
Para abrir a interface gráfica e testar o agente, execute o comando abaixo no terminal:

code
Bash
download
content_copy
expand_less
python interface.py
🎮 Guia de Uso do Simulador

Ao executar o comando acima, uma janela gráfica será aberta. Siga os passos abaixo para configurar e rodar a simulação:

1. Criando o Cenário (Painel Lateral)

Use as ferramentas no menu "INVENTORY SELECT" à esquerda:

📦 PRATELEIRA:

Clique Esquerdo (Mouse): Adiciona uma prateleira ou aumenta a quantidade de itens nela.

Clique Direito (Mouse): Diminui a quantidade de itens (se chegar a 0, a prateleira some).

🏁 BALCÃO:

Clique Esquerdo: Define o ponto de entrega (Goal). É obrigatório ter um balcão.

🤖 PLAYER 1 (Agente):

Clique Esquerdo: Define a posição inicial do robô.

🧹 BORRACHA:

Clique Esquerdo: Remove qualquer elemento da célula clicada.

2. Executando a Missão

Após configurar o cenário (garanta que há pelo menos 1 Prateleira com itens e 1 Balcão):

Clique no botão "START MISSION".

O robô irá planejar a rota, navegar até as prateleiras, coletar os itens (mudando de cor) e levá-los ao balcão.

Acompanhe o progresso no placar SCORE e ITEMS.

3. Reiniciando

Para limpar o cenário ou tentar uma nova configuração, clique em "RESET STAGE".

🛠 Tecnologias Utilizadas

Linguagem: Python 3

Interface Gráfica: Tkinter

IA/Algoritmos: A* Search (Heurística Manhattan), Agentes Racionais.