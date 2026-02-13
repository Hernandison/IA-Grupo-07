import tkinter as tk
from tkinter import messagebox
import math
import time
from warehouse import WarehouseEnvironment, WarehouseAgent

# =============================================================================
# CONFIGURAÇÃO VISUAL (PALETA DE CORES 16-BIT)
# =============================================================================
COR_FUNDO = "#2f3542"        # Cinza Chumbo (Fundo Geral)
COR_GRID = "#57606f"         # Linhas da Grade
COR_PAINEL = "#1e272e"       # Painel Lateral Escuro
COR_TEXTO = "#ffffff"        # Texto Branco

# Elementos do Jogo
COR_PRATELEIRA_TOPO = "#e67e22"  # Laranja Tijolo
COR_PRATELEIRA_LATERAL = "#d35400" # Sombra Tijolo
COR_ITEM = "#f1c40f"         # Amarelo Moeda
COR_BALCAO_FUNDO = "#27ae60" # Verde Fundo
COR_BALCAO_BORDA = "#2ecc71" # Verde Claro Borda

# Robô
COR_ROBO_CORPO = "#0984e3"   # Azul Mega Man
COR_ROBO_DETALHE = "#74b9ff" # Azul Claro
COR_ROBO_CARREGANDO = "#8e44ad" # Roxo (Quando tem item)

# Fontes
FONTE_TITULO = ("Courier New", 16, "bold")
FONTE_UI = ("Courier New", 10, "bold")
FONTE_NUMERO = ("Courier New", 14, "bold")

class SuperWarehouseGame:
    def __init__(self, root):
        self.root = root
        self.root.title("WAREHOUSE QUEST - GRUPO 07")
        self.root.configure(bg=COR_FUNDO)
        
        # Configurações do Grid
        self.grid_w, self.grid_h = 10, 10
        self.cell_size = 60
        
        # Estados do Jogo
        self.prateleiras = {} # Dict {(x,y): quantidade}
        self.pos_entrega = None
        self.pos_inicio_agente = (0, 0)
        self.em_execucao = False
        self.modo_edicao = tk.StringVar(value="prateleira")
        
        # Variáveis de Animação
        self.pos_visual_agente = [0, 0] # Float [x, y]
        self.agente_tem_caixa = False
        
        self.configurar_interface()
        self.desenhar_grid_estatico()

    def configurar_interface(self):
        # --- PAINEL LATERAL (HUD) ---
        painel = tk.Frame(self.root, width=280, bg=COR_PAINEL, padx=15, pady=15, relief=tk.RAISED, bd=3)
        painel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Título
        tk.Label(painel, text=">> LOGÍSTICA <<\nSIMULATOR", font=FONTE_TITULO, bg=COR_PAINEL, fg="#f1c40f").pack(pady=(0, 20))
        
        # Placar (Scoreboard)
        frame_placar = tk.Frame(painel, bg="black", bd=2, relief=tk.SUNKEN, padx=10, pady=10)
        frame_placar.pack(fill=tk.X, pady=10)
        
        tk.Label(frame_placar, text="ITENS PENDENTES", font=("Courier New", 8), bg="black", fg="#bdc3c7").pack(anchor="w")
        self.lbl_itens = tk.Label(frame_placar, text="00", font=("Courier New", 28, "bold"), bg="black", fg=COR_ITEM)
        self.lbl_itens.pack()
        
        tk.Label(frame_placar, text="ITENS ENTREGUES", font=("Courier New", 8), bg="black", fg="#bdc3c7").pack(anchor="w", pady=(5,0))
        self.lbl_entregues = tk.Label(frame_placar, text="000", font=("Courier New", 18, "bold"), bg="black", fg=COR_BALCAO_BORDA)
        self.lbl_entregues.pack()

        # Menu de Ferramentas
        tk.Label(painel, text="[ FERRAMENTAS ]", font=FONTE_UI, bg=COR_PAINEL, fg="white").pack(anchor="w", pady=(20,5))
        
        opcoes = [
            ("📦 Prateleira (+Item)", "prateleira"),
            ("🏁 Ponto de Entrega", "entrega"),
            ("🤖 Pos. Inicial Robô", "agente"),
            ("❌ Borracha / Limpar", "borracha")
        ]
        
        for texto, modo in opcoes:
            rb = tk.Radiobutton(painel, text=texto, variable=self.modo_edicao, value=modo, 
                                indicatoron=0, height=2, bg="#34495e", fg="white", selectcolor=COR_PRATELEIRA_TOPO, 
                                font=("Segoe UI", 9, "bold"), borderwidth=2, relief=tk.RAISED, activebackground=COR_PRATELEIRA_TOPO)
            rb.pack(fill=tk.X, pady=3)

        # Instruções Rápidas
        lbl_instrucao = tk.Label(painel, text="* Clique ESQ: Adicionar\n* Clique DIR: Remover", 
                                 font=("Courier New", 8), bg=COR_PAINEL, fg="#95a5a6", justify=tk.LEFT)
        lbl_instrucao.pack(pady=10)

        # Botões de Ação
        frame_botoes = tk.Frame(painel, bg=COR_PAINEL)
        frame_botoes.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        self.btn_iniciar = tk.Button(frame_botoes, text="INICIAR MISSÃO", command=self.iniciar_simulacao, 
                  bg="#27ae60", fg="white", font=FONTE_TITULO, relief=tk.RAISED, bd=4, activebackground="#2ecc71")
        self.btn_iniciar.pack(fill=tk.X, pady=5)
        
        tk.Button(frame_botoes, text="REINICIAR FASE", command=self.reiniciar, 
                  bg="#c0392b", fg="white", font=FONTE_UI, relief=tk.RAISED, bd=2).pack(fill=tk.X)

        # --- ÁREA DO JOGO (CANVAS) ---
        container_canvas = tk.Frame(self.root, bg=COR_FUNDO, bd=10, relief=tk.FLAT)
        container_canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        self.canvas = tk.Canvas(container_canvas, width=self.grid_w*self.cell_size, height=self.grid_h*self.cell_size, 
                                bg="#2f3640", highlightthickness=2, highlightbackground="#7f8c8d")
        self.canvas.pack(expand=True)
        self.canvas.bind("<Button-1>", lambda e: self.ao_clicar(e, 1))  # Botão Esquerdo
        self.canvas.bind("<Button-3>", lambda e: self.ao_clicar(e, -1)) # Botão Direito

    def desenhar_grid_estatico(self):
        """Desenha o chão quadriculado"""
        self.canvas.delete("grid")
        w, h = self.grid_w, self.grid_h
        sz = self.cell_size
        
        for y in range(h):
            for x in range(w):
                # Padrão xadrez sutil
                cor = "#353b48" if (x + y) % 2 == 0 else "#3d4655"
                self.canvas.create_rectangle(x*sz, y*sz, (x+1)*sz, (y+1)*sz, fill=cor, outline="", tags="grid")
                # Pontinhos nos cantos para dar ar técnico
                self.canvas.create_oval(x*sz-1, y*sz-1, x*sz+1, y*sz+1, fill=COR_GRID, tags="grid")

        self.desenhar_elementos()

    def desenhar_elementos(self):
        """Renderiza prateleiras, balcão e itens"""
        self.canvas.delete("elementos")
        sz = self.cell_size
        
        # 1. Ponto de Entrega (Base)
        if self.pos_entrega:
            dx, dy = self.pos_entrega
            cx, cy = dx * sz, dy * sz
            pad = 4
            # Borda tracejada
            self.canvas.create_rectangle(cx+pad, cy+pad, cx+sz-pad, cy+sz-pad, 
                                       outline="white", width=2, dash=(4, 4), tags="elementos")
            # Fundo colorido
            self.canvas.create_rectangle(cx+10, cy+10, cx+sz-10, cy+sz-10,
                                       fill=COR_BALCAO_FUNDO, outline=COR_BALCAO_BORDA, width=2, tags="elementos")
            self.canvas.create_text(cx + sz/2, cy + sz/2,
                                  text="FIM", fill="white", font=("Courier New", 10, "bold"), tags="elementos")

        # 2. Prateleiras (Blocos 3D)
        for (x, y), qtd in self.prateleiras.items():
            cx, cy = x * sz, y * sz
            pad = 3
            
            # Sombra (Lateral) para efeito 3D
            self.canvas.create_rectangle(cx+pad+4, cy+pad+4, cx+sz-pad, cy+sz-pad,
                                       fill="#1e272e", outline="", tags="elementos")
            # Face Frontal
            self.canvas.create_rectangle(cx+pad, cy+pad, cx+sz-pad-4, cy+sz-pad-4, 
                                       fill=COR_PRATELEIRA_TOPO, outline="black", width=1, tags="elementos")
            # Detalhe Lateral
            self.canvas.create_line(cx+sz-pad-4, cy+pad, cx+sz-pad-4, cy+sz-pad-4, fill=COR_PRATELEIRA_LATERAL, width=2, tags="elementos")
            self.canvas.create_line(cx+pad, cy+sz-pad-4, cx+sz-pad-4, cy+sz-pad-4, fill=COR_PRATELEIRA_LATERAL, width=2, tags="elementos")

            # Contador de Itens
            if qtd > 0:
                # Círculo preto de fundo
                self.canvas.create_oval(cx+32, cy+32, cx+52, cy+52, fill="black", outline="white", width=1, tags="elementos")
                self.canvas.create_text(cx+42, cy+42, text=f"{qtd}", fill=COR_ITEM, font=FONTE_NUMERO, tags="elementos")
                # Ícone de caixinha pequena decorativa
                self.canvas.create_rectangle(cx+8, cy+8, cx+20, cy+20, fill=COR_ITEM, outline="black", tags="elementos")

        self.atualizar_textos()
        if not self.em_execucao:
            self.desenhar_agente_estatico()

    def desenhar_agente_estatico(self):
        self.canvas.delete("agente")
        
        # Define posição (inicial ou animada)
        ax, ay = self.pos_inicio_agente if not self.em_execucao else self.pos_visual_agente
        sz = self.cell_size
        cx, cy = ax * sz, ay * sz
        
        cor_corpo = COR_ROBO_CARREGANDO if self.agente_tem_caixa else COR_ROBO_CORPO
        
        # --- DESENHO DO ROBÔ ---
        # Sombra no chão
        self.canvas.create_oval(cx+10, cy+48, cx+50, cy+56, fill="#1e272e", outline="", tags="agente")
        
        # Esteiras (Rodas)
        self.canvas.create_rectangle(cx+5, cy+40, cx+15, cy+52, fill="#7f8c8d", outline="black", tags="agente")
        self.canvas.create_rectangle(cx+45, cy+40, cx+55, cy+52, fill="#7f8c8d", outline="black", tags="agente")
        
        # Corpo Principal
        self.canvas.create_rectangle(cx+10, cy+15, cx+50, cy+48, fill=cor_corpo, outline="black", width=2, tags="agente")
        self.canvas.create_rectangle(cx+15, cy+20, cx+45, cy+35, fill="black", tags="agente") # Visor
        
        # Olhos (LEDs)
        cor_olho = "#e74c3c" if not self.agente_tem_caixa else "#2ecc71"
        self.canvas.create_rectangle(cx+18, cy+22, cx+28, cy+32, fill=cor_olho, tags="agente")
        self.canvas.create_rectangle(cx+32, cy+22, cx+42, cy+32, fill=cor_olho, tags="agente")

        # Item sobre a cabeça (se estiver carregando)
        if self.agente_tem_caixa:
             # Caixa flutuando
             self.canvas.create_rectangle(cx+18, cy-8, cx+42, cy+12, fill=COR_ITEM, outline="white", width=2, tags="agente")
             self.canvas.create_text(cx+30, cy+2, text="$", fill="black", font=("Courier", 10, "bold"), tags="agente")

    def atualizar_textos(self):
        total_itens = sum(self.prateleiras.values())
        self.lbl_itens.config(text=f"{total_itens:02d}")
        
        if hasattr(self, 'env') and self.agente in self.env.agents_data:
            entregues = self.env.agents_data[self.agente]['items_delivered']
            self.lbl_entregues.config(text=f"{entregues:03d}")

    def ao_clicar(self, evento, mudanca_valor):
        if self.em_execucao: return
        gx, gy = evento.x // self.cell_size, evento.y // self.cell_size
        
        # Verifica se clicou dentro do grid
        if not (0 <= gx < self.grid_w and 0 <= gy < self.grid_h): return

        modo = self.modo_edicao.get()
        
        if modo == "prateleira":
            # Remove ponto de entrega se clicar em cima dele
            if (gx, gy) == self.pos_entrega: self.pos_entrega = None
            
            qtd_atual = self.prateleiras.get((gx, gy), 0)
            
            # Se for clique direito em vazio, ignora
            if (gx, gy) not in self.prateleiras and mudanca_valor < 0: return
            
            nova_qtd = max(1, qtd_atual + mudanca_valor) if (gx, gy) in self.prateleiras else 1
            
            # Se diminuir de 1, remove
            if mudanca_valor < 0 and qtd_atual <= 1:
                if (gx, gy) in self.prateleiras: del self.prateleiras[(gx, gy)]
            else:
                self.prateleiras[(gx, gy)] = nova_qtd
                
        elif modo == "entrega":
            # Remove prateleira se houver
            if (gx, gy) in self.prateleiras: del self.prateleiras[(gx, gy)]
            self.pos_entrega = (gx, gy)
            
        elif modo == "agente":
            self.pos_inicio_agente = (gx, gy)
            
        elif modo == "borracha":
            if (gx, gy) in self.prateleiras: del self.prateleiras[(gx, gy)]
            if (gx, gy) == self.pos_entrega: self.pos_entrega = None

        self.desenhar_elementos()

    def reiniciar(self):
        self.em_execucao = False
        self.prateleiras = {}
        self.pos_entrega = None
        self.pos_inicio_agente = (0, 0)
        self.agente_tem_caixa = False
        self.lbl_entregues.config(text="000")
        self.btn_iniciar.config(state=tk.NORMAL, bg="#27ae60", text="INICIAR MISSÃO")
        self.desenhar_grid_estatico()

    def iniciar_simulacao(self):
        if not self.prateleiras or not self.pos_entrega:
            messagebox.showwarning("Atenção", "Configure o cenário:\n- Pelo menos 1 Prateleira com itens\n- 1 Ponto de Entrega")
            return

        self.em_execucao = True
        self.btn_iniciar.config(state=tk.DISABLED, bg="#7f8c8d", text="EM ANDAMENTO...")
        
        # Inicializa Lógica (WarehouseEnvironment)
        self.env = WarehouseEnvironment(self.grid_w, self.grid_h, self.prateleiras.copy(), self.pos_entrega)
        self.agente = WarehouseAgent(self.pos_inicio_agente, self.prateleiras.copy(), self.pos_entrega, self.grid_w, self.grid_h)
        self.env.add_thing(self.agente, location=self.pos_inicio_agente)
        
        self.pos_visual_agente = list(self.pos_inicio_agente)
        self.passo_logico()

    def passo_logico(self):
        if not self.em_execucao: return
        
        if self.env.is_done():
            self.em_execucao = False
            self.btn_iniciar.config(state=tk.NORMAL, bg="#27ae60", text="INICIAR MISSÃO")
            messagebox.showinfo("Sucesso", "Missão Cumprida!\nTodas as entregas realizadas.")
            return

        # Executa 1 passo na lógica
        self.env.step()
        
        # Sincroniza dados para visualização
        dados_agente = self.env.agents_data[self.agente]
        pos_destino = dados_agente['pos']
        self.agente_tem_caixa = dados_agente['has_box']
        self.prateleiras = self.env.shelves.copy() 
        
        self.desenhar_elementos()
        self.animar_movimento(pos_destino)

    def animar_movimento(self, pos_destino):
        inicio_x, inicio_y = self.pos_visual_agente
        fim_x, fim_y = pos_destino
        
        # Se não saiu do lugar (ex: pegando caixa), espera e vai pro próximo passo
        if inicio_x == fim_x and inicio_y == fim_y:
            self.desenhar_agente_estatico()
            self.root.after(150, self.passo_logico)
            return

        passos = 8 # Frames da animação
        dx = (fim_x - inicio_x) / passos
        dy = (fim_y - inicio_y) / passos

        def frame(contador):
            if contador < passos:
                self.pos_visual_agente[0] += dx
                self.pos_visual_agente[1] += dy
                self.desenhar_agente_estatico()
                self.root.after(20, lambda: frame(contador + 1))
            else:
                # Garante posição final exata
                self.pos_visual_agente = [fim_x, fim_y]
                self.desenhar_agente_estatico()
                self.root.after(20, self.passo_logico)

        frame(0)

if __name__ == "__main__":
    root = tk.Tk()
    # Centraliza a janela na tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    x = (largura_tela/2) - (950/2)
    y = (altura_tela/2) - (700/2)
    root.geometry(f"950x700+{int(x)}+{int(y)}")
    
    app = SuperWarehouseGame(root)
    root.mainloop()