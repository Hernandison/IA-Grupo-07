import sys
import time

# Adiciona a pasta 'aima' ao caminho do sistema para garantir que as importações funcionem
# (Caso o warehouse.py ainda não tenha feito isso ou para garantir redundância)
sys.path.append('./aima')

try:
    from warehouse import WarehouseEnvironment, WarehouseAgent
except ImportError as e:
    print("ERRO DE IMPORTAÇÃO:")
    print("Certifique-se de que o arquivo 'warehouse.py' está na mesma pasta que o 'main.py'.")
    print(f"Detalhe do erro: {e}")
    sys.exit(1)

def main():
    print("\n===========================================================")
    print("   PROJETO GRUPO 07: AGENTE INTELIGENTE DE ALMOXARIFADO")
    print("===========================================================\n")

    # ---------------------------------------------------------
    # 1. DEFINIÇÃO DO CENÁRIO (LAYOUT DO DEPÓSITO)
    # ---------------------------------------------------------
    width = 10
    height = 10
    
    # Definindo as Paredes (Simulando prateleiras do almoxarifado)
    # O agente terá que contornar isso usando o algoritmo A*
    walls = [
        (2, 0), (2, 1), (2, 2),          # Prateleira Esquerda Superior
        (2, 4), (2, 5), (2, 6),          # Prateleira Esquerda Inferior
        (5, 5), (5, 6), (5, 7), (5, 8),  # Prateleira Central
        (7, 1), (7, 2), (7, 3),          # Prateleira Direita
        (8, 5)                           # Obstáculo solto
    ]
    
    # Posições Chave
    start_pos = (0, 0)         # Início (Entrada do Depósito)
    box_location = (9, 0)      # Onde está o item a ser buscado (Canto superior direito)
    delivery_location = (0, 9) # Onde deve ser entregue (Canto inferior esquerdo)

    print(f"-> Mapa: {width}x{height}")
    print(f"-> Agente Inicia em: {start_pos}")
    print(f"-> Caixa (Alvo) em:  {box_location}")
    print(f"-> Zona de Entrega:  {delivery_location}")
    print(f"-> Obstáculos:       {len(walls)} blocos de parede")
    print("-" * 60)

    # ---------------------------------------------------------
    # 2. INICIALIZAÇÃO DA ARQUITETURA (AMBIENTE E AGENTE)
    # ---------------------------------------------------------
    
    # Cria o Ambiente Físico (Simulação)
    env = WarehouseEnvironment(width, height, walls, box_location, delivery_location)

    # Cria o Agente Inteligente
    # Note que passamos 'walls' para o agente. Isso representa que ele tem o "mapa da planta"
    # do prédio na memória dele, permitindo planejar a rota antes de andar.
    robot = WarehouseAgent(start_pos, walls, box_location, delivery_location)

    # Adiciona o Agente ao Ambiente na posição inicial
    env.add_thing(robot, location=start_pos)

    # ---------------------------------------------------------
    # 3. EXECUÇÃO DA SIMULAÇÃO
    # ---------------------------------------------------------
    print("Iniciando simulação do agente...\n")
    
    # Rodamos por um número máximo de passos para evitar loops infinitos caso algo dê errado
    # O agente deve imprimir seus planos (A*) e o ambiente deve imprimir os movimentos.
    env.run(steps=60)

    print("\n===========================================================")
    print("                  FIM DA SIMULAÇÃO")
    print("===========================================================")

if __name__ == "__main__":
    main()