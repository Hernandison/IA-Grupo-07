# ====================================================================================
# ALMOXARIFADO MANAGER 3D: SURVIVAL LOGISTICS
# Motor 3D Isométrico, Sistema de Partículas, Radar Tático, Leaderboard e IA Invasora.
# ====================================================================================

import tkinter as tk
from tkinter import simpledialog, messagebox
import sys, random, math, time, json, os

# ─── IMPORTAÇÃO SEGURA DE MÍDIA E MATEMÁTICA ────────────────────────────────────────
try:
    import numpy as np
    import pygame
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False
    print("Aviso: Numpy ou Pygame não instalados. O jogo rodará sem áudio.")

import aima.utils
sys.modules['utils'] = aima.utils
from env.ambiente_almoxarifado import AmbienteAlmoxarifado
from agents.agente_almoxarifado import AgenteAlmoxarifado
from problems.problema_almoxarifado import ProblemaAlmoxarifado
from aima.search import astar_search

# ─── CONFIGURAÇÕES GLOBAIS E PALETAS DE CORES (INDUSTRIAL NEON / CYBERPUNK) ─────────
C = {
    'bg_void':   '#020205', 'bg':        '#050814', 'bg_panel':  '#0a0f1c',
    'grid':      '#1e293b', 'border':    '#1e3a8a', 'border_hl': '#3b82f6',
    
    'cyan':      '#00f0ff', 'cyan_dim':  '#0088aa', 'blue':      '#1d4ed8',
    'green':     '#10b981', 'green_dim': '#065f46', 'yellow':    '#facc15',
    'orange':    '#f97316', 'red':       '#ef4444', 'red_dim':   '#7f1d1d',
    'white':     '#f8fafc', 'gray':      '#64748b', 'gray_dark': '#334155',
    
    'floor_a':   '#0b1120', 'floor_b':   '#0f172a', 'stripe_1':  '#eab308', 'stripe_2': '#000000',
    
    # Cores 3D (Frente, Topo, Lado)
    'shelf_f':   '#1e3a8a', 'shelf_t':   '#3b82f6', 'shelf_s':   '#172554',
    'box_f':     '#d97706', 'box_t':     '#fbbf24', 'box_s':     '#92400e',
    'robo_f':    '#0ea5e9', 'robo_t':    '#22d3ee', 'robo_s':    '#0891b2',
    'desk_f':    '#1e293b', 'desk_t':    '#334155', 'desk_s':    '#0f172a',
    'invader_f': '#dc2626', 'invader_t': '#ef4444', 'invader_s': '#991b1b',
    
    # Skins Funcionários
    'roupa_1_f': '#4338ca', 'roupa_1_t': '#6d28d9', 'roupa_1_s': '#2e1065',
    'roupa_2_f': '#15803d', 'roupa_2_t': '#22c55e', 'roupa_2_s': '#14532d',
    'roupa_3_f': '#be185d', 'roupa_3_t': '#ec4899', 'roupa_3_s': '#831843',
    'pele':      '#fcd34d', 'pele_esc':  '#b45309'
}

F = {
    'giant':  ('Courier New', 48, 'bold'), 'title':  ('Courier New', 28, 'bold'),
    'score':  ('Courier New', 22, 'bold'), 'hud':    ('Courier New', 14, 'bold'),
    'med':    ('Courier New', 11, 'bold'), 'small':  ('Courier New', 9,  'bold'),
    'micro':  ('Courier New', 7,  'bold')
}

LEADERBOARD_FILE = 'leaderboard.json'

# ─── MOTOR DE ÁUDIO SINTÉTICO (ESTÉREO SEGURO) ──────────────────────────────────────
class AudioEngine:
    def __init__(self):
        self.ok = False
        self.sons = {}
        if not AUDIO_OK: return
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self._gerar_biblioteca()
            self.ok = True
        except Exception as e:
            print(f"Erro no áudio: {e}")

    def _criar_som(self, freqs, dur, vol, tipo='sine', sweep_to=None):
        sr = 44100
        n = int(sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        
        if sweep_to:
            f = np.linspace(freqs[0], sweep_to, n)
            wave = np.sin(2 * np.pi * np.cumsum(f) / sr)
        else:
            wave = sum(np.sin(2 * np.pi * freq * t) for freq in freqs) / len(freqs)
            
        if tipo == 'square': wave = np.sign(wave)
        elif tipo == 'noise': wave = np.random.uniform(-1, 1, n)

        fade = min(int(sr * 0.05), n)
        if fade > 0: 
            wave[:fade] *= np.linspace(0, 1, fade)
            wave[-fade:] *= np.linspace(1, 0, fade)
            
        s = (wave * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack((s, s)))

    def _gerar_biblioteca(self):
        self.sons['menu_blip'] = self._criar_som([800], 0.05, 0.1)
        self.sons['start']     = self._criar_som([300], 0.8, 0.2, sweep_to=1200)
        self.sons['click']     = self._criar_som([1500, 2000], 0.1, 0.1)
        self.sons['delivery']  = self._criar_som([523, 659, 784, 1047], 0.3, 0.15)
        self.sons['angry']     = self._criar_som([150, 200], 0.4, 0.2, tipo='square')
        self.sons['alarm']     = self._criar_som([880], 0.2, 0.1)
        self.sons['step']      = self._criar_som([100], 0.05, 0.05, tipo='noise')
        self.sons['gameover']  = self._criar_som([400], 1.5, 0.25, sweep_to=50)

    def play(self, nome):
        if self.ok and nome in self.sons:
            self.sons[nome].play()

# ─── SISTEMA DE ARQUIVOS (LEADERBOARD) ──────────────────────────────────────────────
def carregar_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
        except: pass
    return [
        {"nome": "HERNANDISON", "score": 15000, "entregas": 50},
        {"nome": "ALAN TURING", "score": 10000, "entregas": 35},
        {"nome": "ROBO_COP",    "score": 5000,  "entregas": 15}
    ]

def salvar_leaderboard(dados):
    dados_sorted = sorted(dados, key=lambda x: x['score'], reverse=True)[:8]
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(dados_sorted, f)
    except: pass
    return dados_sorted

# ─── ENTIDADES E LÓGICA VISUAL ──────────────────────────────────────────────────────
class Funcionario:
    def __init__(self, pos_grid, dificuldade):
        self.pos_grid = pos_grid
        self.id = random.randint(1000, 9999)
        self.paciencia_max = max(120, 500 - dificuldade * 30) + random.randint(-40, 40)
        self.paciencia = float(self.paciencia_max)
        self.estado = 'esperando' 
        self.tremor = 0
        self.offset_y = 60 # Animação caindo do teto
        
        r = random.randint(1, 3)
        self.c_f = C[f'roupa_{r}_f']
        self.c_t = C[f'roupa_{r}_t']
        self.c_s = C[f'roupa_{r}_s']

    def atualizar(self):
        if self.offset_y > 0:
            self.offset_y = max(0, self.offset_y - 4)
            
        if self.estado == 'esperando':
            self.paciencia -= 1.0
            pct = self.paciencia / self.paciencia_max
            if pct < 0.25: self.tremor = random.choice([-2, 0, 2])
            else: self.tremor = 0

class Invasor:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Particula:
    def __init__(self, x, y, cor, vel_x, vel_y):
        self.x, self.y = x, y
        self.vx, self.vy = vel_x, vel_y
        self.cor = cor
        self.vida = 1.0
        self.tamanho = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2 # gravidade
        self.vida -= 0.04
        return self.vida > 0

class TextoFlutuante:
    def __init__(self, x, y, texto, cor):
        self.x, self.y, self.texto, self.cor, self.vida = x, y, texto, cor, 1.0

    def update(self):
        self.y -= 1.5
        self.vida -= 0.02
        return self.vida > 0

# ─── MOTOR PRINCIPAL (MÁQUINA DE ESTADOS E RENDER 3D) ───────────────────────────────
class AlmoxarifadoManager3D:
    GRID_W, GRID_H = 14, 11
    SZ = 56       
    DEPTH = 16    

    def __init__(self, root):
        self.root = root
        self.root.title('ALMOXARIFADO MANAGER 3D: SURVIVAL LOGISTICS')
        self.root.configure(bg=C['bg_void'])
        self.root.resizable(False, False)
        
        self.audio = AudioEngine()
        self.leaderboard = carregar_leaderboard()
        self.estado_jogo = 'MENU'
        
        self.tick = 0
        self.particulas = []
        self.textos = []
        self.nome_jogador = "ANON"
        
        self._montar_janela()
        self._bind_teclas()
        self._loop_mestre()

    def _montar_janela(self):
        w_canvas = self.GRID_W * self.SZ + self.DEPTH
        h_canvas = self.GRID_H * self.SZ + self.DEPTH
        w_painel = 320
        h_hud = 60
        
        self.root.geometry(f"{w_canvas + w_painel + 30}x{h_canvas + h_hud + 30}")
        
        self.hud = tk.Canvas(self.root, height=h_hud, bg=C['bg_panel'], highlightthickness=0)
        self.hud.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        
        self.frame_main = tk.Frame(self.root, bg=C['bg_void'])
        self.frame_main.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.frame_main, width=w_canvas, height=h_canvas, bg=C['bg'], highlightthickness=2, highlightbackground=C['border'])
        self.canvas.pack(side=tk.LEFT)
        
        self.painel = tk.Canvas(self.frame_main, width=w_painel, height=h_canvas, bg=C['bg_panel'], highlightthickness=2, highlightbackground=C['border'])
        self.painel.pack(side=tk.RIGHT)

    def _bind_teclas(self):
        self.root.bind('<space>', self._handle_space)
        self.canvas.bind('<Button-1>', self._handle_click)

    # ── MÉTODOS AUXILIARES ──────────────────────────────────────────────────────────
    def _gerar_particulas(self, x, y, cor, qtd):
        """Método adicionado para corrigir o erro de atributo e gerar efeitos."""
        for _ in range(qtd):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -1)
            self.particulas.append(Particula(x + self.SZ//2, y + self.SZ//2, cor, vx, vy))

    # ── GERENCIADOR DE ESTADOS ───────────────────────────────────────────────────────
    def _handle_space(self, e):
        if self.estado_jogo in ['MENU', 'GAMEOVER']:
            self.audio.play('menu_blip')
            nome = simpledialog.askstring('NOVO JOGO', 'Código do Gestor (Máx 8):')
            if nome and nome.strip():
                self.nome_jogador = nome.strip()[:8].upper()
                self._iniciar_partida()

    def _iniciar_partida(self):
        self.audio.play('start')
        self.score, self.entregas, self.reputacao = 0, 0, 100
        self.dificuldade = 0
        self.motivo_gameover = ""
        
        self.prateleiras = {}
        for x in [2, 3, 5, 6, 8, 9, 11]:
            for y in range(2, 7): self.prateleiras[(x, y)] = 5
                
        self.pos_robo_inicial = (7, 1) # Ponto seguro de regresso (Base)
        self.pos_robo = self.pos_robo_inicial
        
        self.funcionarios_fila = []
        self.invasores = []
        self.funcionario_alvo = None
        
        self.ambiente = AmbienteAlmoxarifado(self.GRID_W, self.GRID_H, self.prateleiras.copy(), (0, 0))
        self.agente = AgenteAlmoxarifado(self.pos_robo, self.prateleiras.copy(), (0, 0), self.GRID_W, self.GRID_H)
        self.ambiente.add_thing(self.agente, location=self.pos_robo)
        
        self.particulas.clear()
        self.textos.clear()
        self.estado_jogo = 'JOGO'

    def _disparar_gameover(self, motivo):
        self.estado_jogo = 'GAMEOVER'
        self.motivo_gameover = motivo
        self.audio.play('gameover')
        self.leaderboard.append({'nome': self.nome_jogador, 'score': self.score, 'entregas': self.entregas})
        self.leaderboard = salvar_leaderboard(self.leaderboard)

    # ── LOOP MESTRE (60 Hz Aprox) ────────────────────────────────────────────────────
    def _loop_mestre(self):
        self.tick += 1
        
        if self.estado_jogo == 'MENU':
            self._render_menu()
        elif self.estado_jogo == 'JOGO':
            self._update_logica()
            self._render_jogo()
            self._render_painel()
            self._render_hud()
        elif self.estado_jogo == 'GAMEOVER':
            self._render_gameover()
            
        self.root.after(50, self._loop_mestre)

    # ── UPDATE LÓGICA DO JOGO (REGRESSO À BASE + INVASÕES) ───────────────────────────
    def _update_logica(self):
        self.dificuldade = self.entregas // 4
        
        # 1. Spawn de Funcionários no Balcão
        max_fila = min(4 + self.dificuldade, 10)
        taxa_spawn = 0.015 + (self.dificuldade * 0.005)
        
        if len(self.funcionarios_fila) < max_fila and random.random() < taxa_spawn:
            ocupados = {f.pos_grid[0] for f in self.funcionarios_fila}
            livres = [x for x in range(1, self.GRID_W - 1) if x not in ocupados]
            if livres:
                self.funcionarios_fila.append(Funcionario((random.choice(livres), self.GRID_H - 1), self.dificuldade))

        # 2. Paciência Esgotada -> O Funcionário vira Invasor
        for f in self.funcionarios_fila[:]:
            f.atualizar()
            if f.paciencia <= 0:
                self.audio.play('angry')
                self.reputacao -= 12
                self._gerar_particulas(f.pos_grid[0]*self.SZ, f.pos_grid[1]*self.SZ, C['red'], 15)
                self.textos.append(TextoFlutuante(f.pos_grid[0]*self.SZ, (f.pos_grid[1]-1)*self.SZ, 'INVASÃO!!', C['red']))
                
                # O funcionário pula o balcão
                self.invasores.append(Invasor(f.pos_grid[0], f.pos_grid[1] - 1))
                
                self.funcionarios_fila.remove(f)
                if self.funcionario_alvo == f:
                    self.funcionario_alvo = None
                    self.agente.plano = [] # Limpa a missão atual

        # 3. Mover Invasores (Eles caçam o robô)
        dados_robo = self.ambiente.dados_agentes[self.agente]
        rx, ry = dados_robo['posicao']

        if self.tick % max(3, 8 - self.dificuldade) == 0 and self.invasores:
            for inv in self.invasores:
                candidatos = []
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = inv.x + dx, inv.y + dy
                    # Limites do cenário. Não pode voltar ao balcão.
                    if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H - 1:
                        if (nx, ny) not in self.prateleiras:
                            candidatos.append((nx, ny))
                if candidatos:
                    candidatos.sort(key=lambda p: abs(p[0]-rx) + abs(p[1]-ry))
                    inv.x, inv.y = candidatos[0] if random.random() < 0.6 else random.choice(candidatos)

        # 4. Verifica Game Over por Colisão / Encurralamento
        if any(inv.x == rx and inv.y == ry for inv in self.invasores):
            self._gerar_particulas(rx*self.SZ, ry*self.SZ, C['red'], 50)
            self._disparar_gameover("DESTRUÍDO PELOS INVASORES!")
            return

        caminhos = 0
        tem_inimigo = False
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = rx+dx, ry+dy
            if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                if any(inv.x == nx and inv.y == ny for inv in self.invasores):
                    tem_inimigo = True
                elif (nx, ny) not in self.prateleiras:
                    caminhos += 1
        
        if caminhos == 0 and tem_inimigo:
            self._disparar_gameover("ROBÔ ENCURRALADO! SEM SAÍDA!")
            return

        if self.reputacao <= 0:
            self._disparar_gameover("FALÊNCIA! A REPUTAÇÃO CHEGOU A ZERO.")
            return

        self.particulas = [p for p in self.particulas if p.update()]
        self.textos = [t for t in self.textos if t.update()]

        # 5. Executa Inteligência Artificial (A*)
        if self.tick % 2 == 0:
            # Informa a IA de que os invasores são paredes sólidas para ela fugir
            memoria = self.ambiente.prateleiras.copy()
            for inv in self.invasores:
                memoria[(inv.x, inv.y)] = 0 
            self.agente.memoria_prateleiras = memoria

            antes = dados_robo['itens_entregues']
            
            # SE TIVER ALVO OU CAIXA: Faz o trabalho normal
            if self.funcionario_alvo or dados_robo['tem_caixa']:
                pos_antes = dados_robo['posicao']
                self.ambiente.step() 
                pos_depois = self.ambiente.dados_agentes[self.agente]['posicao']
                if pos_antes != pos_depois and random.random() < 0.3:
                    self.audio.play('step')

            # SE ESTIVER OCIOSO: Volta automaticamente para a base!
            elif dados_robo['posicao'] != self.pos_robo_inicial:
                if not self.agente.plano:
                    # Calcula rota segura para a doca de recarga (base)
                    obstaculos = set(self.ambiente.prateleiras.keys())
                    for inv in self.invasores: obstaculos.add((inv.x, inv.y))
                    
                    prob = ProblemaAlmoxarifado(
                        (dados_robo['posicao'][0], dados_robo['posicao'][1], 0),
                        obstaculos, self.pos_robo_inicial, self.pos_robo_inicial,
                        self.GRID_W, self.GRID_H
                    )
                    prob.goal_test = lambda state: state[0:2] == self.pos_robo_inicial
                    sol = astar_search(prob)
                    if sol:
                        self.agente.plano = sol.solution()
                        
                if self.agente.plano:
                    acao = self.agente.plano.pop(0)
                    self.ambiente.execute_action(self.agente, acao)
                    if random.random() < 0.3:
                        self.audio.play('step')

            # Verifica Sucesso de Entrega
            if self.ambiente.dados_agentes[self.agente]['itens_entregues'] > antes:
                self.audio.play('delivery')
                self.entregas += 1
                pts = 100 + self.dificuldade * 20
                self.score += pts
                self.reputacao = min(100, self.reputacao + 5)
                
                px, py = dados_robo['posicao']
                self._gerar_particulas(px*self.SZ, py*self.SZ, C['green'], 20)
                self.textos.append(TextoFlutuante(px*self.SZ, py*self.SZ, f'+{pts} PTS', C['green']))
                
                if self.funcionario_alvo in self.funcionarios_fila:
                    self.funcionarios_fila.remove(self.funcionario_alvo)
                self.funcionario_alvo = None

    def _handle_click(self, e):
        """Lida com cliques, permitindo INTERRUPÇÃO DINÂMICA de missões/voltas à base."""
        if self.estado_jogo != 'JOGO': return
        # Compensa a perspectiva 3D (Z-Depth) para encontrar a grade correta
        cx = int((e.x - (self.GRID_H * self.SZ - e.y) * 0.1) // self.SZ)
        cy = int(e.y // self.SZ)
        
        cx = max(0, min(self.GRID_W - 1, cx))
        cy = max(0, min(self.GRID_H - 1, cy))

        dados = self.ambiente.dados_agentes[self.agente]
        if dados['tem_caixa'] and self.funcionario_alvo: 
            return # Já está ocupado
        
        # Procura funcionário correspondente
        for f in self.funcionarios_fila:
            # Folga no eixo Y devido à isometria
            if f.pos_grid[0] == cx and abs(f.pos_grid[1] - cy) <= 1 and f.estado == 'esperando':
                self.audio.play('click')
                self.funcionario_alvo = f
                f.estado = 'sendo_atendido'
                
                self.ambiente.pos_entrega = f.pos_grid
                self.agente.pos_entrega = f.pos_grid
                
                # INTERRUPÇÃO: Limpa a mente (seja lá o que estava a fazer, vai buscar a caixa nova AGORA!)
                self.agente.plano = [] 
                
                self.textos.append(TextoFlutuante(f.pos_grid[0]*self.SZ, f.pos_grid[1]*self.SZ - 20, 'ALVO FIXADO!', C['cyan']))
                break

    # ── MOTOR DE RENDERIZAÇÃO 3D (Y-SORTING PERFEITO) ────────────────────────────────
    def _draw_cube(self, c, x, y, w, h, d, c_f, c_t, c_s, outline='#000'):
        # Topo
        c.create_polygon(x, y-h, x+w, y-h, x+w+d, y-h-d, x+d, y-h-d, fill=c_t, outline=outline)
        # Lado Direito
        c.create_polygon(x+w, y, x+w+d, y-d, x+w+d, y-h-d, x+w, y-h, fill=c_s, outline=outline)
        # Frente
        c.create_rectangle(x, y-h, x+w, y, fill=c_f, outline=outline)

    def _render_jogo(self):
        c = self.canvas
        c.delete('all')
        sz, d = self.SZ, self.DEPTH

        # 1. PINTA CHÃO LISO E DETALHES DE FUNDO
        for x in range(self.GRID_W):
            for y in range(self.GRID_H):
                col = C['floor_a'] if (x+y)%2==0 else C['floor_b']
                c.create_rectangle(x*sz, y*sz, x*sz+sz, y*sz+sz, fill=col, outline=C['grid'])

        # Fita amarela PINTADA NO CHÃO (Correção de sobreposição!)
        yf = (self.GRID_H - 1) * sz
        for x in range(0, self.GRID_W * sz, 20):
            cor = C['stripe_1'] if (x // 20) % 2 == 0 else C['stripe_2']
            c.create_rectangle(x, yf, x+20, yf+6, fill=cor, outline='')

        # Base de recarga iluminada (Onde o robô espera)
        base_x, base_y = self.pos_robo_inicial
        bx, by = base_x * sz, base_y * sz
        c.create_rectangle(bx+2, by+2, bx+sz-2, by+sz-2, fill='#022c22', outline=C['green'], width=2)
        c.create_text(bx+sz//2, by+sz//2, text="BASE", fill=C['green'], font=F['small'])

        # 2. LISTA DE OBJETOS COM PROFUNDIDADE (Z-BUFFER)
        # A ordem Y exata define quem fica na frente de quem.
        render_list = []

        # Prateleiras
        for (cx, cy), qtd in self.ambiente.prateleiras.items():
            render_list.append({'y': cy, 'draw': lambda cx=cx, cy=cy, q=qtd: self._draw_shelf(c, cx, cy, q, sz, d)})

        # Balcão (Atrás dos funcionários)
        for cx in range(self.GRID_W):
            render_list.append({'y': self.GRID_H - 1.0, 'draw': lambda cx=cx: self._draw_desk(c, cx, self.GRID_H-1, sz, d)})

        # Funcionários (Ligeiramente à frente do balcão)
        for f in self.funcionarios_fila:
            render_list.append({'y': f.pos_grid[1] + 0.3, 'draw': lambda f=f: self._draw_worker(c, f, sz, d)})

        # Invasores
        for inv in self.invasores:
            render_list.append({'y': inv.y + 0.1, 'draw': lambda inv=inv: self._draw_invader(c, inv, sz, d)})

        # Robô
        rx, ry = self.ambiente.dados_agentes[self.agente]['posicao']
        render_list.append({'y': ry + 0.2, 'draw': lambda: self._draw_robot(c, rx, ry, sz, d, self.ambiente.dados_agentes[self.agente]['tem_caixa'])})

        # Desenha pela ordem de profundidade
        render_list.sort(key=lambda item: item['y'])
        for item in render_list: item['draw']()

        # Partículas e Textos ficam SEMPRE por cima de tudo
        for p in self.particulas:
            ts = int(p.tamanho * p.vida)
            if ts > 0: c.create_rectangle(p.x, p.y, p.x+ts, p.y+ts, fill=p.cor, outline='')

        for t in self.textos:
            c.create_text(int(t.x), int(t.y), text=t.texto, font=F['med'], fill=t.cor)

    # ── MÉTODOS DE DESENHO DE ENTIDADES ──────────────────────────────────────────────
    def _draw_shelf(self, c, cx, cy, qtd, sz, d):
        x, y = cx * sz + 4, cy * sz + sz - 4
        c.create_polygon(x, y, x+sz-8, y, x+sz-8+d, y-d, x+d, y-d, fill='#000', stipple='gray50')
        self._draw_cube(c, x, y, sz-8, 50, d, C['shelf_f'], C['shelf_t'], C['shelf_s'])
        if qtd > 0:
            bx, by = x + 8, y - 50
            self._draw_cube(c, bx, by, sz-24, 16, d-4, C['box_f'], C['box_t'], C['box_s'])
            c.create_text(bx + (sz-24)//2, by - 8, text=f'x{qtd}', font=F['small'], fill=C['white'])

    def _draw_desk(self, c, cx, cy, sz, d):
        x, y = cx * sz, cy * sz + sz
        self._draw_cube(c, x, y, sz, 30, d, C['desk_f'], C['desk_t'], C['desk_s'])

    def _draw_robot(self, c, cx, cy, sz, d, tem_caixa):
        x, y = cx * sz + 10, cy * sz + sz - 5
        bob = int(math.sin(self.tick * 0.4) * 3)
        c.create_oval(x, y-5, x+sz-20, y+5, fill='#000', outline='')
        self._draw_cube(c, x, y+bob, sz-20, 26, d, C['robo_f'], C['robo_t'], C['robo_s'])
        c.create_rectangle(x+4, y-22+bob, x+sz-24, y-12+bob, fill='#000')
        olho_cor = C['cyan'] if not tem_caixa else C['yellow']
        c.create_rectangle(x+8, y-20+bob, x+14, y-14+bob, fill=olho_cor, outline='')
        c.create_rectangle(x+20, y-20+bob, x+26, y-14+bob, fill=olho_cor, outline='')
        if tem_caixa:
            self._draw_cube(c, x+4, y-30+bob, sz-28, 14, d-4, C['box_f'], C['box_t'], C['box_s'])

    def _draw_worker(self, c, f, sz, d):
        cx, cy = f.pos_grid
        x, y = cx * sz + 16 + f.tremor, cy * sz + sz - f.offset_y
        self._draw_cube(c, x, y, sz-32, 28, d-4, f.c_f, f.c_t, f.c_s)
        self._draw_cube(c, x+4, y-28, 16, 16, 8, C['pele'], '#fde047', C['pele_esc'])
        
        pct = f.paciencia / f.paciencia_max
        if pct < 0.3:
            c.create_rectangle(x+6, y-40, x+10, y-38, fill=C['red'], outline='')
            c.create_rectangle(x+14, y-40, x+18, y-38, fill=C['red'], outline='')
            if self.tick % 10 == 0: self.particulas.append(Particula(x+4, y-44, C['cyan'], random.uniform(-1,1), -2))

        if f == self.funcionario_alvo:
            c.create_polygon(x+12, y-60, x+4, y-75, x+20, y-75, fill=C['yellow'], outline='#000')

        cor_bar = C['green'] if pct > 0.5 else (C['yellow'] if pct > 0.25 else C['red'])
        c.create_rectangle(x-4, y+6, x+28, y+10, fill='#000', outline='')
        c.create_rectangle(x-4, y+6, x-4 + int(32*pct), y+10, fill=cor_bar, outline='')

    def _draw_invader(self, c, inv, sz, d):
        x, y = inv.x * sz + 14, inv.y * sz + sz
        bob = abs(int(math.sin(self.tick * 0.5) * 6))
        c.create_oval(x, y-5, x+sz-28, y+5, fill='#000', outline='')
        self._draw_cube(c, x, y-bob, sz-28, 32, d, C['invader_f'], C['invader_t'], C['invader_s'])
        c.create_text(x+13, y-45-bob, text='!', font=F['hud'], fill=C['white'])

    # ── PAINEL LATERAL E RADAR ───────────────────────────────────────────────────────
    def _render_painel(self):
        c = self.painel
        c.delete('all')
        W, H = int(c['width']), int(c['height'])
        
        c.create_rectangle(0, 0, W, H, fill=C['bg_panel'], outline='')
        c.create_rectangle(0, 0, W, 40, fill=C['border'], outline='')
        c.create_text(W//2, 20, text='RADAR TÁTICO & STATUS', font=F['med'], fill=C['white'])
        
        map_sz = 16
        mx = (W - (self.GRID_W * map_sz)) // 2
        my = 60
        
        c.create_rectangle(mx-5, my-5, mx + self.GRID_W*map_sz + 5, my + self.GRID_H*map_sz + 5, fill='#000', outline=C['cyan'])
        
        for x in range(self.GRID_W):
            for y in range(self.GRID_H):
                rx, ry = mx + x*map_sz, my + y*map_sz
                c.create_rectangle(rx, ry, rx+map_sz, ry+map_sz, outline='#111')
                if (x, y) in self.prateleiras:
                    c.create_rectangle(rx+2, ry+2, rx+map_sz-2, ry+map_sz-2, fill=C['shelf_t'], outline='')
                if y == self.GRID_H - 1:
                    c.create_rectangle(rx, ry, rx+map_sz, ry+map_sz, fill=C['gray_dark'], outline='')

        # Base 
        bx, by = self.pos_robo_inicial
        c.create_rectangle(mx+bx*map_sz+2, my+by*map_sz+2, mx+bx*map_sz+map_sz-2, my+by*map_sz+map_sz-2, fill='#022c22', outline='')

        # Robô no Radar
        rx, ry = self.ambiente.dados_agentes[self.agente]['posicao']
        c.create_oval(mx + rx*map_sz + 2, my + ry*map_sz + 2, mx + rx*map_sz + map_sz - 2, my + ry*map_sz + map_sz - 2, fill=C['cyan'], outline='')
        
        # Funcionários
        for f in self.funcionarios_fila:
            f_col = C['green'] if f.paciencia/f.paciencia_max > 0.5 else C['yellow']
            if f == self.funcionario_alvo: f_col = C['white']
            c.create_oval(mx + f.pos_grid[0]*map_sz + 4, my + f.pos_grid[1]*map_sz + 4, mx + f.pos_grid[0]*map_sz + map_sz - 4, my + f.pos_grid[1]*map_sz + map_sz - 4, fill=f_col, outline='')
        
        # Invasores (Blink)
        if self.tick % 10 < 5:
            for inv in self.invasores:
                c.create_rectangle(mx + inv.x*map_sz + 2, my + inv.y*map_sz + 2, mx + inv.x*map_sz + map_sz - 2, my + inv.y*map_sz + map_sz - 2, fill=C['red'], outline='')

        sy = my + self.GRID_H*map_sz + 30
        c.create_text(20, sy, anchor='w', text='INFO DA I.A. (A*)', font=F['med'], fill=C['cyan'])
        dados = self.ambiente.dados_agentes[self.agente]
        
        if dados['tem_caixa']: estado = "CARREGANDO CAIXA"
        elif self.funcionario_alvo: estado = "INDO BUSCAR CAIXA"
        elif dados['posicao'] != self.pos_robo_inicial: estado = "RETORNANDO À BASE"
        else: estado = "OCIOSO NA BASE"
        
        c.create_text(20, sy+30, anchor='w', text=f'ESTADO: {estado}', font=F['small'], fill=C['white'])
        c.create_text(20, sy+50, anchor='w', text=f'PASSOS RESTANTES: {len(self.agente.plano)}', font=F['small'], fill=C['gray'])
        
        if self.invasores:
            c.create_rectangle(10, sy+90, W-10, sy+140, fill=C['red_dim'], outline=C['red'], width=2)
            c.create_text(W//2, sy+115, text='⚠ ALERTA DE INVASÃO ⚠', font=F['med'], fill=C['white'])

    def _render_hud(self):
        c = self.hud
        c.delete('all')
        W = int(c['width'])
        
        c.create_rectangle(0, 0, W, 60, fill=C['bg_panel'], outline=C['border'], width=2)
        c.create_text(20, 30, anchor='w', text='[ ALMOXARIFADO 3D ]', font=F['hud'], fill=C['cyan'])
        c.create_text(300, 30, anchor='w', text=f'GESTOR: {self.nome_jogador}', font=F['med'], fill=C['white'])
        
        c.create_text(600, 20, text='SCORE', font=F['small'], fill=C['gray'])
        c.create_text(600, 40, text=f'{self.score:06d}', font=F['score'], fill=C['yellow'])
        
        c.create_text(750, 20, text='ENTREGAS / NÍVEL', font=F['small'], fill=C['gray'])
        c.create_text(750, 40, text=f'{self.entregas:03d} / LVL {self.dificuldade+1}', font=F['hud'], fill=C['white'])
        
        rep_col = C['green'] if self.reputacao > 50 else (C['yellow'] if self.reputacao > 25 else C['red'])
        c.create_text(1000, 20, text='REPUTAÇÃO', font=F['small'], fill=C['gray'])
        c.create_rectangle(900, 30, 1100, 45, fill='#000', outline=rep_col)
        c.create_rectangle(902, 32, 902 + int(196 * (self.reputacao/100)), 43, fill=rep_col, outline='')

    # ── TELAS DE SISTEMA (MENU / GAMEOVER) ───────────────────────────────────────────
    def _render_menu(self):
        c = self.canvas
        c.delete('all')
        W, H = int(c['width']), int(c['height'])
        
        for i in range(0, W, 40):
            offset = (self.tick + i) % W
            c.create_line(offset, 0, offset, H, fill=C['border'], width=1)
            
        c.create_text(W//2, 120, text='ALMOXARIFADO 3D', font=F['giant'], fill=C['cyan'])
        c.create_text(W//2, 180, text='SURVIVAL LOGISTICS', font=F['title'], fill=C['yellow'])
        
        if int(self.tick / 10) % 2 == 0:
            c.create_text(W//2, 280, text='[ PRESSIONE ESPAÇO PARA INICIAR ]', font=F['score'], fill=C['white'])
            
        c.create_rectangle(W//2 - 250, 350, W//2 + 250, 650, fill=C['bg_panel'], outline=C['border_hl'], width=3)
        c.create_text(W//2, 380, text='--- MELHORES GESTORES ---', font=F['med'], fill=C['cyan'])
        
        y = 430
        for i, reg in enumerate(self.leaderboard[:6]):
            cor = C['yellow'] if i == 0 else C['white']
            c.create_text(W//2 - 200, y, anchor='w', text=f"{i+1}. {reg['nome']}", font=F['hud'], fill=cor)
            c.create_text(W//2 + 200, y, anchor='e', text=f"{reg['score']:06d} PTS", font=F['hud'], fill=cor)
            y += 35
            
        self.painel.delete('all')
        self.hud.delete('all')

    def _render_gameover(self):
        c = self.canvas
        W, H = int(c['width']), int(c['height'])
        
        c.create_rectangle(0, 0, W, H, fill='#000', stipple='gray50')
        pw, ph = 600, 300
        px, py = (W - pw)//2, (H - ph)//2
        c.create_rectangle(px, py, px+pw, py+ph, fill=C['bg_panel'], outline=C['red'], width=5)
        
        c.create_text(W//2, py + 50, text='GAME OVER', font=F['giant'], fill=C['red'])
        c.create_text(W//2, py + 120, text=self.motivo_gameover, font=F['hud'], fill=C['yellow'])
        
        c.create_text(W//2, py + 180, text=f'PONTUAÇÃO FINAL: {self.score:06d}', font=F['title'], fill=C['white'])
        c.create_text(W//2, py + 220, text=f'NÍVEL ALCANÇADO: {self.dificuldade + 1}', font=F['med'], fill=C['gray'])
        
        if int(self.tick / 10) % 2 == 0:
            c.create_text(W//2, py + 270, text='[ PRESSIONE ESPAÇO PARA VOLTAR AO MENU ]', font=F['small'], fill=C['cyan'])

if __name__ == '__main__':
    root = tk.Tk()
    app = AlmoxarifadoManager3D(root)
    root.mainloop()