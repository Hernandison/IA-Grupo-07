import sys
import os

# Adiciona a pasta 'aima' ao path de forma absoluta para garantir que a biblioteca
# consiga carregar seus próprios arquivos internos sem erros de "ModuleNotFoundError".
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'aima')))

try:
    # Importações atualizadas refletindo a nova estrutura de diretórios e classes em português
    from env.ambiente_almoxarifado import AmbienteAlmoxarifado
    from agents.agente_almoxarifado import AgenteAlmoxarifado
except ImportError as e:
    print("ERRO DE IMPORTAÇÃO:")
    print("Certifique-se de que as pastas '/env' e '/agents' existem e contêm os arquivos corretos.")
    print(f"Detalhe do erro: {e}")
    sys.exit(1)

def main():
    print("\n===========================================================")
    print("   PROJETO GRUPO 07: AGENTE INTELIGENTE DE ALMOXARIFADO")
    print("===========================================================\n")

    # ---------------------------------------------------------
    # 1. DEFINIÇÃO DO CENÁRIO (LAYOUT DO DEPÓSITO)
    # ---------------------------------------------------------
    largura = 10
    altura = 10
    
    # Posições Chave
    pos_inicial = (0, 0)       # Início (Entrada do Depósito)
    pos_entrega = (0, 9)       # Onde deve ser entregue (Canto inferior esquerdo - Balcão)

    # Definindo as Prateleiras e Obstáculos
    # O dicionário mapeia {(x, y): quantidade_de_itens_disponiveis}
    # Prateleiras com 0 itens funcionam estritamente como obstáculos físicos (paredes)
    prateleiras = {
        # Prateleira Esquerda Superior
        (2, 0): 0, (2, 1): 0, (2, 2): 0,
        # Prateleira Esquerda Inferior
        (2, 4): 0, (2, 5): 0, (2, 6): 0,
        # Prateleira Central
        (5, 5): 0, (5, 6): 0, (5, 7): 0, (5, 8): 0,
        # Prateleira Direita
        (7, 1): 0, (7, 2): 0, (7, 3): 0,
        # Obstáculo solto
        (8, 5): 0,
        
        # Onde está o item a ser buscado (Canto superior direito)
        (9, 0): 1  
    }

    print(f"-> Mapa: {largura}x{altura}")
    print(f"-> Agente Inicia em: {pos_inicial}")
    print(f"-> Zona de Entrega:  {pos_entrega}")
    print(f"-> Prateleiras/Obstáculos: {len(prateleiras)} blocos registrados")
    print("-" * 60)

    # ---------------------------------------------------------
    # 2. INICIALIZAÇÃO DA ARQUITETURA (AMBIENTE E AGENTE)
    # ---------------------------------------------------------
    
    # Cria o Ambiente Físico (Simulação)
    # Passamos uma cópia do dicionário para que o ambiente gerencie o estado real
    ambiente = AmbienteAlmoxarifado(largura, altura, prateleiras.copy(), pos_entrega)

    # Cria o Agente Inteligente
    # Passamos uma cópia para que o agente tenha a sua própria "memória" do mapa
    agente = AgenteAlmoxarifado(pos_inicial, prateleiras.copy(), pos_entrega, largura, altura)

    # Adiciona o Agente ao Ambiente na posição inicial
    ambiente.add_thing(agente, location=pos_inicial)

    # ---------------------------------------------------------
    # 3. EXECUÇÃO DA SIMULAÇÃO
    # ---------------------------------------------------------
    print("Iniciando simulação do agente...\n")
    
    # Rodamos por um número máximo de passos para evitar loops infinitos caso algo dê errado
    # A cada passo, o ambiente chamará o método render() que acabamos de adicionar
    ambiente.run(steps=60)

    print("\n===========================================================")
    print("                  FIM DA SIMULAÇÃO")
    print("===========================================================")

if __name__ == "__main__":
    main()