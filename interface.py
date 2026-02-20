# ====================================================================================
# ALMOXARIFADO MANAGER 3D: SURVIVAL LOGISTICS
# Motor 3D Isométrico Responsivo (Ultrawide Ready), Radar, Leaderboard, e IA (A*).
# ====================================================================================

import tkinter as tk
from tkinter import simpledialog, messagebox
import sys, random, math, time, json, os

# Habilita suporte a cores ANSI no terminal Windows
if os.name == 'nt':
    os.system('')

# ─── IMPORTAÇÃO SEGURA DE MÍDIA E MATEMÁTICA ────────────────────────────────────────
try:
    import numpy as np
    import pygame
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False
    print("[SISTEMA] Aviso: Numpy ou Pygame não instalados. O jogo rodará sem áudio.")

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
    'giant':  ('Courier New', 36, 'bold'), 'title':  ('Courier New', 22, 'bold'),
    'score':  ('Courier New', 18, 'bold'), 'hud':    ('Courier New', 12, 'bold'),
    'med':    ('Courier New', 10, 'bold'), 'small':  ('Courier New', 8,  'bold'),
    'micro':  ('Courier New', 7,  'bold')
}

LEADERBOARD_FILE = 'leaderboard.json'

# ─── MOTOR DE ÁUDIO SINTÉTICO E BGM ─────────────────────────────────────────────────
class AudioEngine:
    def __init__(self):
        self.ok = False
        self.sons = {}
        self.volume_atual = 0.2
        if not AUDIO_OK: return
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self._gerar_biblioteca()
            self._carregar_bgm()
            self.ok = True
        except Exception as e:
            print(f"[SISTEMA] Erro no áudio: {e}")

    def _carregar_bgm(self):
        caminho_musica = os.path.join("musicas", "topguear.mp3")
        if os.path.exists(caminho_musica):
            pygame.mixer.music.load(caminho_musica)
            pygame.mixer.music.set_volume(self.volume_atual)
            pygame.mixer.music.play(-1)
        else:
            print(f"[SISTEMA] Música não encontrada em: {caminho_musica}.")

    def set_volume(self, volume):
        self.volume_atual = max(0.0, min(1.0, volume))
        if self.ok:
            pygame.mixer.music.set_volume(self.volume_atual)
            for som in self.sons.values():
                som.set_volume(self.volume_atual)

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
        som = pygame.sndarray.make_sound(np.column_stack((s, s)))
        som.set_volume(self.volume_atual)
        return som

    def _gerar_biblioteca(self):
        self.sons['menu_blip'] = self._criar_som([800], 0.05, 0.5)
        self.sons['start']     = self._criar_som([300], 0.8, 0.6, sweep_to=1200)
        self.sons['click']     = self._criar_som([1500, 2000], 0.1, 0.4)
        self.sons['delivery']  = self._criar_som([523, 659, 784, 1047], 0.3, 0.5)
        self.sons['angry']     = self._criar_som([150, 200], 0.4, 0.6, tipo='square')
        self.sons['step']      = self._criar_som([100], 0.05, 0.2, tipo='noise')
        self.sons['gameover']  = self._criar_som([400], 1.5, 0.7, sweep_to=50)

    def play(self, nome):
        if self.ok and nome in self.sons:
            self.sons[nome].play()

# ─── SISTEMA DE ARQUIVOS (LEADERBOARD) ──────────────────────────────────────────────
def carregar_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
        except: pass
    return [{"nome": "HERNANDI", "score": 15000, "entregas": 50}]

def salvar_leaderboard(dados):
    dados_sorted = sorted(dados, key=lambda x: x['score'], reverse=True)[:50]
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(dados_sorted, f)
    except: pass
    return dados_sorted

# ─── ENTIDADES E LÓGICA VISUAL ──────────────────────────────────────────────────────
class Funcionario:
    def __init__(self, pos_grid, dificuldade):
        self.pos_grid = pos_grid
        self.id = random.randint(100, 999)
        self.paciencia_max = max(120, 500 - dificuldade * 30) + random.randint(-40, 40)
        self.paciencia = float(self.paciencia_max)
        self.estado = 'esperando' 
        self.tremor = 0
        self.offset_y = 60 
        r = random.randint(1, 3)
        self.c_f = C[f'roupa_{r}_f']
        self.c_t = C[f'roupa_{r}_t']
        self.c_s = C[f'roupa_{r}_s']

    def atualizar(self):
        if self.offset_y > 0: self.offset_y = max(0, self.offset_y - 4)
        if self.estado == 'esperando':
            self.paciencia -= 1.0
            pct = self.paciencia / self.paciencia_max
            self.tremor = random.choice([-2, 0, 2]) if pct < 0.25 else 0

class Invasor:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Particula:
    def __init__(self, x, y, cor, vel_x, vel_y):
        self.x, self.y, self.cor = x, y, cor
        self.vx, self.vy = vel_x, vel_y
        self.vida = 1.0
        self.tamanho = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2 
        self.vida -= 0.04
        return self.vida > 0

class TextoFlutuante:
    def __init__(self, x, y, texto, cor):
        self.x, self.y, self.texto, self.cor, self.vida = x, y, texto, cor, 1.0

    def update(self):
        self.y -= 1.5
        self.vida -= 0.02
        return self.vida > 0

# ─── MOTOR PRINCIPAL (MÁQUINA DE ESTADOS E RENDER 3D RESPONSIVO) ────────────────────
class AlmoxarifadoManager3D:
    GRID_W, GRID_H = 14, 11

    def __init__(self, root):
        self.root = root
        self.root.title('ALMOXARIFADO MANAGER 3D: SURVIVAL LOGISTICS')
        self.root.configure(bg=C['bg_void'])
        
        # Geometria Inicial Dinâmica e Limites
        self.root.geometry("1100x750")
        self.root.minsize(800, 500)
        self.root.resizable(True, True)
        
        # Tenta maximizar a janela nativamente
        try: self.root.state('zoomed')
        except: pass
        
        self.SZ = 42       
        self.DEPTH = 12    
        self.offset_x = 0
        self.offset_y = 0

        self.audio = AudioEngine()
        self.leaderboard = carregar_leaderboard()
        self.pagina_leaderboard = 0 
        self.estado_jogo = 'MENU' 
        
        self.tick = 0
        self.particulas = []
        self.textos = []
        self.nome_jogador = "ANON"
        self.botoes_pause = {} 
        
        self._montar_janela()
        self._bind_teclas()
        self._loop_mestre()
        
        sys.stdout.write('\033[2J\033[H')
        print(f"\033[96m[SISTEMA] Motor 3D Iniciado (Modo Responsivo). Aguardando Jogador...\033[0m")

    def _montar_janela(self):
        h_hud = 60
        
        self.top_frame = tk.Frame(self.root, bg=C['bg_panel'], height=h_hud)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        
        self.hud = tk.Canvas(self.top_frame, height=h_hud, bg=C['bg_panel'], highlightthickness=0)
        self.hud.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.frame_vol = tk.Frame(self.top_frame, bg=C['bg_panel'])
        self.frame_vol.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(self.frame_vol, text="VOLUME", bg=C['bg_panel'], fg=C['cyan'], font=F['micro']).pack()
        self.vol_slider = tk.Scale(self.frame_vol, from_=0, to=100, orient=tk.HORIZONTAL, 
                                   bg=C['bg_panel'], fg=C['white'], highlightthickness=0,
                                   command=self._ajustar_volume, length=100, showvalue=0)
        self.vol_slider.set(20) 
        self.vol_slider.pack()

        self.frame_main = tk.Frame(self.root, bg=C['bg_void'])
        self.frame_main.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Panel assume tamanho fixo na largura e expande na altura
        self.painel = tk.Canvas(self.frame_main, width=300, bg=C['bg_panel'], highlightthickness=2, highlightbackground=C['border'])
        self.painel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas principal preenche todo o espaço restante
        self.canvas = tk.Canvas(self.frame_main, bg=C['bg'], highlightthickness=2, highlightbackground=C['border'])
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def _ajustar_volume(self, val):
        self.audio.set_volume(int(val) / 100.0)

    def _bind_teclas(self):
        self.root.bind('<space>', self._handle_space)
        self.root.bind('<Escape>', self._toggle_pause)
        self.root.bind('<p>', self._toggle_pause)
        self.root.bind('<P>', self._toggle_pause)
        self.root.bind('<Left>', self._handle_esq)
        self.root.bind('<Right>', self._handle_dir)
        self.canvas.bind('<Configure>', self._on_resize) # Evento Responsivo
        self.canvas.bind('<Button-1>', self._handle_click)

    # ── EVENTO RESPONSIVO: RECALCULA PROPORÇÕES AO REDIMENSIONAR TELA ───────────────
    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 100 or h < 100: return
        
        # Calcula qual é o maior tamanho de célula (SZ) que cabe na tela mantendo proporção
        sz_w = w / (self.GRID_W + 1)
        sz_h = h / (self.GRID_H + 1)
        self.SZ = max(20, int(min(sz_w, sz_h)))
        self.DEPTH = max(4, int(self.SZ * 0.28))
        
        # Calcula margens para centralizar o ambiente na tela
        self.offset_x = (w - (self.GRID_W * self.SZ)) // 2
        self.offset_y = (h - (self.GRID_H * self.SZ)) // 2

    # ── GERENCIADOR DE ESTADOS E EVENTOS DE TECLADO ───────────────────────────────────
    def _handle_esq(self, e):
        if self.estado_jogo == 'MENU' and self.pagina_leaderboard > 0:
            self.audio.play('menu_blip')
            self.pagina_leaderboard -= 1

    def _handle_dir(self, e):
        if self.estado_jogo == 'MENU':
            max_pag = max(0, (len(self.leaderboard) - 1) // 5)
            if self.pagina_leaderboard < max_pag:
                self.audio.play('menu_blip')
                self.pagina_leaderboard += 1

    def _handle_space(self, e):
        if self.estado_jogo in ['MENU', 'GAMEOVER']:
            self.audio.play('menu_blip')
            nome = simpledialog.askstring('NOVO JOGO', 'Código do Gestor (Máx 8):')
            if nome and nome.strip():
                self.nome_jogador = nome.strip()[:8].upper()
                self.pagina_leaderboard = 0 
                self._iniciar_partida()

    def _toggle_pause(self, e=None):
        if self.estado_jogo == 'JOGO':
            self.estado_jogo = 'PAUSE'
            self.audio.play('menu_blip')
            self._render_pause()
        elif self.estado_jogo == 'PAUSE':
            self.estado_jogo = 'JOGO'
            self.audio.play('menu_blip')

    def _iniciar_partida(self):
        self.audio.play('start')
        sys.stdout.write('\033[2J\033[H') 
        print(f"\033[96m[SISTEMA] --- INICIANDO PARTIDA: GESTOR {self.nome_jogador} ---\033[0m\n")
        
        self.score, self.entregas, self.reputacao = 0, 0, 100
        self.dificuldade = 0
        self.motivo_gameover = ""
        
        self.prateleiras = {}
        for x in [2, 3, 5, 6, 8, 9, 11]:
            for y in range(2, 7): self.prateleiras[(x, y)] = 5
                
        self.pos_robo_inicial = (7, 1) 
        self.pos_robo = self.pos_robo_inicial
        
        self.funcionarios_fila = []
        self.invasores = []
        self.funcionario_alvo = None
        
        self.ambiente = AmbienteAlmoxarifado(self.GRID_W, self.GRID_H, self.prateleiras.copy(), (0, 0))
        self.agente = AgenteAlmoxarifado(self.pos_robo, self.prateleiras.copy(), (0, 0), self.GRID_W, self.GRID_H)
        self.ambiente.add_thing(self.agente, location=self.pos_robo)
        
        self.particulas.clear()
        self.textos.clear()
        self.botoes_pause.clear()
        self.estado_jogo = 'JOGO'

    def _disparar_gameover(self, motivo):
        self.estado_jogo = 'GAMEOVER'
        self.motivo_gameover = motivo
        self.audio.play('gameover')
        
        self.leaderboard.append({'nome': self.nome_jogador, 'score': self.score, 'entregas': self.entregas})
        self.leaderboard = salvar_leaderboard(self.leaderboard)

    def _gerar_particulas(self, abs_x, abs_y, cor, qtd):
        for _ in range(qtd):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -1)
            self.particulas.append(Particula(abs_x, abs_y, cor, vx, vy))

    # ── LOOP MESTRE E LÓGICA DO JOGO ──────────────────────────────────────────────────
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

    def _update_logica(self):
        self.dificuldade = self.entregas // 4
        
        max_fila = min(4 + self.dificuldade, 10)
        taxa_spawn = 0.015 + (self.dificuldade * 0.005)
        
        if len(self.funcionarios_fila) < max_fila and random.random() < taxa_spawn:
            ocupados = {f.pos_grid[0] for f in self.funcionarios_fila}
            livres = [x for x in range(1, self.GRID_W - 1) if x not in ocupados]
            if livres:
                novo_f = Funcionario((random.choice(livres), self.GRID_H - 1), self.dificuldade)
                self.funcionarios_fila.append(novo_f)

        for f in self.funcionarios_fila[:]:
            f.atualizar()
            if f.paciencia <= 0:
                self.audio.play('angry')
                self.reputacao -= 12
                # Partículas em posições absolutas baseadas no Offset Responsivo
                px, py = self.offset_x + f.pos_grid[0]*self.SZ + self.SZ//2, self.offset_y + f.pos_grid[1]*self.SZ
                self._gerar_particulas(px, py, C['red'], 15)
                self.textos.append(TextoFlutuante(px - self.SZ//2, py - self.SZ, 'INVASÃO!!', C['red']))
                self.invasores.append(Invasor(f.pos_grid[0], f.pos_grid[1] - 1))
                
                self.funcionarios_fila.remove(f)
                if self.funcionario_alvo == f:
                    self.funcionario_alvo = None
                    self.agente.plano = [] 

        dados_robo = self.ambiente.dados_agentes[self.agente]
        rx, ry = dados_robo['posicao']

        if self.tick % max(3, 8 - self.dificuldade) == 0 and self.invasores:
            for inv in self.invasores:
                candidatos = []
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = inv.x + dx, inv.y + dy
                    if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H - 1:
                        if (nx, ny) not in self.prateleiras: candidatos.append((nx, ny))
                if candidatos:
                    candidatos.sort(key=lambda p: abs(p[0]-rx) + abs(p[1]-ry))
                    inv.x, inv.y = candidatos[0] if random.random() < 0.6 else random.choice(candidatos)

        if any(inv.x == rx and inv.y == ry for inv in self.invasores):
            px, py = self.offset_x + rx*self.SZ + self.SZ//2, self.offset_y + ry*self.SZ
            self._gerar_particulas(px, py, C['red'], 50)
            self._disparar_gameover("DESTRUÍDO PELOS INVASORES!")
            return

        caminhos = 0
        tem_inimigo = False
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = rx+dx, ry+dy
            if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                if any(inv.x == nx and inv.y == ny for inv in self.invasores): tem_inimigo = True
                elif (nx, ny) not in self.prateleiras: caminhos += 1
        
        if caminhos == 0 and tem_inimigo:
            self._disparar_gameover("ROBÔ ENCURRALADO!")
            return

        if self.reputacao <= 0:
            self._disparar_gameover("FALÊNCIA! A REPUTAÇÃO ZEROU.")
            return

        self.particulas = [p for p in self.particulas if p.update()]
        self.textos = [t for t in self.textos if t.update()]

        if self.tick % 2 == 0:
            memoria = self.ambiente.prateleiras.copy()
            for inv in self.invasores: memoria[(inv.x, inv.y)] = 0 
            self.agente.memoria_prateleiras = memoria

            antes = dados_robo['itens_entregues']
            moveu_agora = False
            
            if self.funcionario_alvo or dados_robo['tem_caixa']:
                pos_antes = dados_robo['posicao']
                self.ambiente.step() 
                pos_depois = self.ambiente.dados_agentes[self.agente]['posicao']
                if pos_antes != pos_depois:
                    moveu_agora = True
                    if random.random() < 0.3: self.audio.play('step')

            elif dados_robo['posicao'] != self.pos_robo_inicial:
                if not self.agente.plano:
                    obstaculos = set(self.ambiente.prateleiras.keys())
                    for inv in self.invasores: obstaculos.add((inv.x, inv.y))
                    
                    prob = ProblemaAlmoxarifado((dados_robo['posicao'][0], dados_robo['posicao'][1], 0),
                        obstaculos, self.pos_robo_inicial, self.pos_robo_inicial, self.GRID_W, self.GRID_H)
                    prob.goal_test = lambda state: state[0:2] == self.pos_robo_inicial
                    sol = astar_search(prob)
                    if sol: self.agente.plano = sol.solution()
                        
                if self.agente.plano:
                    pos_antes = dados_robo['posicao']
                    acao = self.agente.plano.pop(0)
                    self.ambiente.execute_action(self.agente, acao)
                    if pos_antes != self.ambiente.dados_agentes[self.agente]['posicao']:
                        moveu_agora = True
                        if random.random() < 0.3: self.audio.play('step')

            if moveu_agora or (self.tick % 20 == 0): self._imprimir_matriz_terminal()

            if self.ambiente.dados_agentes[self.agente]['itens_entregues'] > antes:
                self.audio.play('delivery')
                self.entregas += 1
                pts = 100 + self.dificuldade * 20
                self.score += pts
                self.reputacao = min(100, self.reputacao + 5)
                
                gx, gy = dados_robo['posicao']
                px, py = self.offset_x + gx*self.SZ + self.SZ//2, self.offset_y + gy*self.SZ
                self._gerar_particulas(px, py, C['green'], 20)
                self.textos.append(TextoFlutuante(px, py, f'+{pts} PTS', C['green']))
                
                if self.funcionario_alvo in self.funcionarios_fila: self.funcionarios_fila.remove(self.funcionario_alvo)
                self.funcionario_alvo = None

    def _imprimir_matriz_terminal(self):
        sys.stdout.write('\033[H') 
        C_CY = '\033[96m'; C_RE = '\033[91m'; C_GR = '\033[92m'; C_YE = '\033[93m'
        C_BL = '\033[94m'; C_WH = '\033[97m'; C_GY = '\033[90m'; C_RST = '\033[0m'
        
        rx, ry = self.ambiente.dados_agentes[self.agente]['posicao']
        dados = self.ambiente.dados_agentes[self.agente]
        
        print(f"{C_CY}=== MONITORAMENTO TÁTICO (TICK: {self.tick:05d}) ==={C_RST}")
        print(f"ROBÔ: ({rx:02d}, {ry:02d}) | BATERIA: {dados['bateria']}% | REP: {self.reputacao}%")
        print(f"SCORE: {self.score} | ENTREGAS: {self.entregas} | INVASORES: {len(self.invasores)}")
        print("-" * 50)
        
        for y in range(self.GRID_H):
            linha = []
            for x in range(self.GRID_W):
                char = f"{C_GY} . {C_RST}"
                if (x, y) in self.prateleiras: char = f"{C_YE}[P]{C_RST}"
                if (x, y) == self.pos_robo_inicial: char = f"{C_GR}[B]{C_RST}"
                if y == self.GRID_H - 1 and char == f"{C_GY} . {C_RST}": char = "___"
                    
                for inv in self.invasores:
                    if inv.x == x and inv.y == y: char = f"{C_RE}[I]{C_RST}"
                for f in self.funcionarios_fila:
                    if f.pos_grid == (x,y): char = f"{C_BL}[F]{C_RST}"
                if rx == x and ry == y: char = f"{C_CY}[R]{C_RST}"
                    
                linha.append(char)
            print(" ".join(linha))
        print("-" * 50 + " " * 10 + "\n")

    # ── TRATAMENTO DE CLIQUES COM COMPENSAÇÃO RESPONSIVA ─────────────────────────────
    def _handle_click(self, e):
        if self.estado_jogo == 'PAUSE':
            for acao, (x1, y1, x2, y2) in self.botoes_pause.items():
                if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                    self.audio.play('click')
                    if acao == 'CONTINUAR': self._toggle_pause()
                    elif acao == 'MENU':
                        sys.stdout.write('\033[2J\033[H')
                        self.pagina_leaderboard = 0
                        self.estado_jogo = 'MENU'
                    elif acao == 'SAIR':
                        self.root.quit()
            return

        if self.estado_jogo != 'JOGO': return
        
        # Converte clique absoluto para célula da Grid considerando os Offsets Adaptativos
        cx = int((e.x - self.offset_x - (self.GRID_H * self.SZ - (e.y - self.offset_y)) * 0.1) // self.SZ)
        cy = int((e.y - self.offset_y) // self.SZ)
        cx = max(0, min(self.GRID_W - 1, cx))
        cy = max(0, min(self.GRID_H - 1, cy))

        dados = self.ambiente.dados_agentes[self.agente]
        if dados['tem_caixa'] and self.funcionario_alvo: return 
        
        for f in self.funcionarios_fila:
            if f.pos_grid[0] == cx and abs(f.pos_grid[1] - cy) <= 1 and f.estado == 'esperando':
                self.audio.play('click')
                self.funcionario_alvo = f
                f.estado = 'sendo_atendido'
                
                self.ambiente.pos_entrega = f.pos_grid
                self.agente.pos_entrega = f.pos_grid
                self.agente.plano = [] 
                
                px, py = self.offset_x + f.pos_grid[0]*self.SZ, self.offset_y + f.pos_grid[1]*self.SZ - 20
                self.textos.append(TextoFlutuante(px, py, 'ALVO FIXADO!', C['cyan']))
                break

    # ── MOTOR DE RENDERIZAÇÃO 3D TOTALMENTE PROPORCIONAL E RELATIVO ────────────────
    def _draw_cube(self, c, x, y, w, h, d, c_f, c_t, c_s, outline='#000'):
        c.create_polygon(x, y-h, x+w, y-h, x+w+d, y-h-d, x+d, y-h-d, fill=c_t, outline=outline)
        c.create_polygon(x+w, y, x+w+d, y-d, x+w+d, y-h-d, x+w, y-h, fill=c_s, outline=outline)
        c.create_rectangle(x, y-h, x+w, y, fill=c_f, outline=outline)

    def _render_jogo(self):
        c = self.canvas
        c.delete('all')
        sz, d = self.SZ, self.DEPTH
        ox, oy = self.offset_x, self.offset_y

        for x in range(self.GRID_W):
            for y in range(self.GRID_H):
                col = C['floor_a'] if (x+y)%2==0 else C['floor_b']
                c.create_rectangle(ox + x*sz, oy + y*sz, ox + x*sz+sz, oy + y*sz+sz, fill=col, outline=C['grid'])

        yf = oy + (self.GRID_H - 1) * sz
        stripe_w = max(5, int(sz*0.4))
        for x in range(0, self.GRID_W * sz, stripe_w):
            cor = C['stripe_1'] if (x // stripe_w) % 2 == 0 else C['stripe_2']
            c.create_rectangle(ox + x, yf, ox + x+stripe_w, yf+max(2, int(sz*0.1)), fill=cor, outline='')

        base_x, base_y = self.pos_robo_inicial
        bx, by = ox + base_x * sz, oy + base_y * sz
        pad = max(1, int(sz*0.05))
        c.create_rectangle(bx+pad, by+pad, bx+sz-pad, by+sz-pad, fill='#022c22', outline=C['green'], width=2)

        render_list = []
        for (cx, cy), qtd in self.ambiente.prateleiras.items():
            render_list.append({'y': cy, 'draw': lambda cx=cx, cy=cy, q=qtd: self._draw_shelf(c, cx, cy, q, sz, d)})

        for cx in range(self.GRID_W):
            render_list.append({'y': self.GRID_H - 1.0, 'draw': lambda cx=cx: self._draw_desk(c, cx, self.GRID_H-1, sz, d)})

        for f in self.funcionarios_fila:
            render_list.append({'y': f.pos_grid[1] + 0.3, 'draw': lambda f=f: self._draw_worker(c, f, sz, d)})

        for inv in self.invasores:
            render_list.append({'y': inv.y + 0.1, 'draw': lambda inv=inv: self._draw_invader(c, inv, sz, d)})

        rx, ry = self.ambiente.dados_agentes[self.agente]['posicao']
        render_list.append({'y': ry + 0.2, 'draw': lambda: self._draw_robot(c, rx, ry, sz, d, self.ambiente.dados_agentes[self.agente]['tem_caixa'])})

        render_list.sort(key=lambda item: item['y'])
        for item in render_list: item['draw']()

        for p in self.particulas:
            ts = int(p.tamanho * p.vida)
            if ts > 0: c.create_rectangle(p.x, p.y, p.x+ts, p.y+ts, fill=p.cor, outline='')

        for t in self.textos:
            f_size = max(8, int(sz*0.25))
            c.create_text(int(t.x), int(t.y), text=t.texto, font=('Courier New', f_size, 'bold'), fill=t.cor)

    def _draw_shelf(self, c, cx, cy, qtd, sz, d):
        ox, oy = self.offset_x, self.offset_y
        p1, p2 = int(sz*0.1), int(sz*0.2)
        x, y = ox + cx * sz + p1, oy + cy * sz + sz - p1
        c.create_polygon(x, y, x+sz-p2, y, x+sz-p2+d, y-d, x+d, y-d, fill='#000', stipple='gray50')
        self._draw_cube(c, x, y, sz-p2, int(sz*0.9), d, C['shelf_f'], C['shelf_t'], C['shelf_s'])
        if qtd > 0:
            bx, by = x + p2, y - int(sz*0.9)
            self._draw_cube(c, bx, by, sz-int(sz*0.6), int(sz*0.3), d-p1, C['box_f'], C['box_t'], C['box_s'])

    def _draw_desk(self, c, cx, cy, sz, d):
        x, y = self.offset_x + cx * sz, self.offset_y + cy * sz + sz
        self._draw_cube(c, x, y, sz, int(sz*0.5), d, C['desk_f'], C['desk_t'], C['desk_s'])

    def _draw_robot(self, c, cx, cy, sz, d, tem_caixa):
        x, y = self.offset_x + cx * sz + int(sz*0.2), self.offset_y + cy * sz + sz - int(sz*0.1)
        bob = int(math.sin(self.tick * 0.4) * max(1, int(sz*0.07)))
        c.create_oval(x, y-5, x+sz-int(sz*0.4), y+5, fill='#000', outline='')
        self._draw_cube(c, x, y+bob, sz-int(sz*0.4), int(sz*0.5), d, C['robo_f'], C['robo_t'], C['robo_s'])
        
        olho_cor = C['cyan'] if not tem_caixa else C['yellow']
        c.create_rectangle(x+int(sz*0.1), y-int(sz*0.4)+bob, x+int(sz*0.25), y-int(sz*0.3)+bob, fill=olho_cor, outline='')
        c.create_rectangle(x+int(sz*0.35), y-int(sz*0.4)+bob, x+int(sz*0.5), y-int(sz*0.3)+bob, fill=olho_cor, outline='')
        if tem_caixa:
            self._draw_cube(c, x+int(sz*0.1), y-int(sz*0.6)+bob, sz-int(sz*0.6), int(sz*0.25), d-max(1, int(sz*0.1)), C['box_f'], C['box_t'], C['box_s'])

    def _draw_worker(self, c, f, sz, d):
        x = self.offset_x + f.pos_grid[0] * sz + int(sz*0.3) + f.tremor
        y = self.offset_y + f.pos_grid[1] * sz + sz - int(f.offset_y * (sz/60))
        self._draw_cube(c, x, y, sz-int(sz*0.6), int(sz*0.5), d-max(1, int(sz*0.1)), f.c_f, f.c_t, f.c_s)
        self._draw_cube(c, x+int(sz*0.1), y-int(sz*0.5), int(sz*0.3), int(sz*0.3), max(2, int(sz*0.15)), C['pele'], '#fde047', C['pele_esc'])
        
        if f == self.funcionario_alvo:
            c.create_polygon(x+int(sz*0.2), y-sz-int(sz*0.2), x+int(sz*0.05), y-sz-int(sz*0.6), x+int(sz*0.35), y-sz-int(sz*0.6), fill=C['yellow'], outline='#000')

        pct = f.paciencia / f.paciencia_max
        cor_bar = C['green'] if pct > 0.5 else (C['yellow'] if pct > 0.25 else C['red'])
        c.create_rectangle(x-int(sz*0.1), y+int(sz*0.15), x+sz-int(sz*0.4), y+int(sz*0.25), fill='#000', outline='')
        c.create_rectangle(x-int(sz*0.1), y+int(sz*0.15), x-int(sz*0.1) + int((sz-int(sz*0.3))*pct), y+int(sz*0.25), fill=cor_bar, outline='')

    def _draw_invader(self, c, inv, sz, d):
        x, y = self.offset_x + inv.x * sz + int(sz*0.25), self.offset_y + inv.y * sz + sz
        bob = abs(int(math.sin(self.tick * 0.5) * max(1, int(sz*0.15))))
        self._draw_cube(c, x, y-bob, sz-int(sz*0.5), int(sz*0.6), d, C['invader_f'], C['invader_t'], C['invader_s'])
        
        f_size = max(8, int(sz*0.3))
        c.create_text(x+int(sz*0.25), y-int(sz*0.8)-bob, text='!', font=('Courier New', f_size, 'bold'), fill=C['white'])

    # ── PAINEL LATERAL E RADAR ───────────────────────────────────────────────────────
    def _render_painel(self):
        c = self.painel
        c.delete('all')
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 10 or H < 10: return
        
        c.create_rectangle(0, 0, W, H, fill=C['bg_panel'], outline='')
        c.create_rectangle(0, 0, W, 40, fill=C['border'], outline='')
        c.create_text(W//2, 20, text='RADAR TÁTICO & STATUS', font=F['med'], fill=C['white'])
        
        map_sz = 14
        mx = (W - (self.GRID_W * map_sz)) // 2
        my = 50
        
        c.create_rectangle(mx-5, my-5, mx + self.GRID_W*map_sz + 5, my + self.GRID_H*map_sz + 5, fill='#000', outline=C['cyan'])
        
        for x in range(self.GRID_W):
            for y in range(self.GRID_H):
                rx, ry = mx + x*map_sz, my + y*map_sz
                if (x, y) in self.prateleiras: c.create_rectangle(rx+1, ry+1, rx+map_sz-1, ry+map_sz-1, fill=C['shelf_t'], outline='')
                if y == self.GRID_H - 1: c.create_rectangle(rx, ry, rx+map_sz, ry+map_sz, fill=C['gray_dark'], outline='')

        bx, by = self.pos_robo_inicial
        c.create_rectangle(mx+bx*map_sz+1, my+by*map_sz+1, mx+bx*map_sz+map_sz-1, my+by*map_sz+map_sz-1, fill='#022c22', outline='')

        rx, ry = self.ambiente.dados_agentes[self.agente]['posicao']
        c.create_oval(mx + rx*map_sz + 1, my + ry*map_sz + 1, mx + rx*map_sz + map_sz - 1, my + ry*map_sz + map_sz - 1, fill=C['cyan'], outline='')
        
        for f in self.funcionarios_fila:
            f_col = C['green'] if f.paciencia/f.paciencia_max > 0.5 else C['yellow']
            if f == self.funcionario_alvo: f_col = C['white']
            c.create_oval(mx + f.pos_grid[0]*map_sz + 2, my + f.pos_grid[1]*map_sz + 2, mx + f.pos_grid[0]*map_sz + map_sz - 2, my + f.pos_grid[1]*map_sz + map_sz - 2, fill=f_col, outline='')
        
        if self.tick % 10 < 5:
            for inv in self.invasores:
                c.create_rectangle(mx + inv.x*map_sz + 1, my + inv.y*map_sz + 1, mx + inv.x*map_sz + map_sz - 1, my + inv.y*map_sz + map_sz - 1, fill=C['red'], outline='')

        sy = my + self.GRID_H*map_sz + 20
        c.create_text(15, sy, anchor='w', text='INFO DA I.A. (A*)', font=F['med'], fill=C['cyan'])
        dados = self.ambiente.dados_agentes[self.agente]
        
        if dados['tem_caixa']: estado = "CARREGANDO CAIXA"
        elif self.funcionario_alvo: estado = "INDO BUSCAR CAIXA"
        elif dados['posicao'] != self.pos_robo_inicial: estado = "RETORNANDO À BASE"
        else: estado = "OCIOSO NA BASE"
        
        c.create_text(15, sy+25, anchor='w', text=f'ESTADO: {estado}', font=F['small'], fill=C['white'])
        c.create_text(15, sy+40, anchor='w', text=f'PASSOS RESTANTES: {len(self.agente.plano)}', font=F['small'], fill=C['gray'])
        
        c.create_text(W//2, sy+70, text="[ESC] ou [P] para Pausar", font=F['small'], fill=C['gray_dark'])
        
        if self.invasores:
            c.create_rectangle(10, sy+90, W-10, sy+130, fill=C['red_dim'], outline=C['red'], width=2)
            c.create_text(W//2, sy+110, text='⚠ INVASÃO ⚠', font=F['med'], fill=C['white'])

    def _render_hud(self):
        c = self.hud
        c.delete('all')
        W = c.winfo_width()
        if W < 50: return
        
        c.create_rectangle(0, 0, W, 60, fill=C['bg_panel'], outline='')
        c.create_text(15, 30, anchor='w', text='[ ALMOXARIFADO 3D ]', font=F['med'], fill=C['cyan'])
        c.create_text(220, 30, anchor='w', text=f'GESTOR: {self.nome_jogador}', font=F['small'], fill=C['white'])
        
        # Alinhamento dinâmico encostado à direita para ultrawides
        c.create_text(W - 350, 20, text='SCORE', font=F['micro'], fill=C['gray'])
        c.create_text(W - 350, 40, text=f'{self.score:06d}', font=F['score'], fill=C['yellow'])
        
        c.create_text(W - 200, 20, text='ENTREGAS/LVL', font=F['micro'], fill=C['gray'])
        c.create_text(W - 200, 40, text=f'{self.entregas:03d} / LVL {self.dificuldade+1}', font=F['med'], fill=C['white'])
        
        rep_col = C['green'] if self.reputacao > 50 else (C['yellow'] if self.reputacao > 25 else C['red'])
        rep_x = W - 70
        c.create_text(rep_x, 20, text='REPUTAÇÃO', font=F['micro'], fill=C['gray'])
        c.create_rectangle(rep_x - 50, 30, rep_x + 50, 45, fill='#000', outline=rep_col)
        c.create_rectangle(rep_x - 48, 32, rep_x - 48 + int(96 * (self.reputacao/100)), 43, fill=rep_col, outline='')

    # ── TELAS DE SISTEMA DINÂMICAS (MENU / PAUSE / GAMEOVER) ─────────────────────────
    def _render_menu(self):
        c = self.canvas
        c.delete('all')
        W, H = c.winfo_width(), c.winfo_height()
        if W < 10 or H < 10: return
        
        for i in range(0, max(W, H), 60):
            offset = (self.tick + i) % max(W, H)
            c.create_line(offset, 0, offset, H, fill=C['border'], width=1)
            c.create_line(0, offset, W, offset, fill=C['border'], width=1)
            
        cw = min(500, W - 40)
        cx = (W - cw) // 2
        cy_top = H // 2 - 150
        
        c.create_rectangle(cx, cy_top, cx+cw, cy_top + 100, fill=C['bg_panel'], outline=C['cyan'], width=2)
        c.create_text(W//2, cy_top + 35, text='ALMOXARIFADO 3D', font=F['giant'], fill=C['cyan'])
        c.create_text(W//2, cy_top + 70, text='SURVIVAL LOGISTICS', font=F['title'], fill=C['yellow'])
        
        if int(self.tick / 10) % 2 == 0:
            c.create_text(W//2, cy_top + 130, text='[ PRESSIONE ESPAÇO PARA INICIAR ]', font=F['med'], fill=C['white'])
            
        cy_board = cy_top + 160
        c.create_rectangle(cx, cy_board, cx+cw, cy_board + 230, fill=C['bg_panel'], outline=C['border_hl'], width=3)
        c.create_text(W//2, cy_board + 30, text='--- MELHORES GESTORES ---', font=F['med'], fill=C['cyan'])
        
        itens_por_pagina = 5
        max_pag = max(1, math.ceil(len(self.leaderboard) / itens_por_pagina))
        if self.pagina_leaderboard >= max_pag: self.pagina_leaderboard = max_pag - 1
            
        pag_atual = self.pagina_leaderboard + 1
        inicio = self.pagina_leaderboard * itens_por_pagina
        registros_pagina = self.leaderboard[inicio:inicio + itens_por_pagina]

        y = cy_board + 65
        for i, reg in enumerate(registros_pagina):
            pos_real = inicio + i + 1
            cor = C['yellow'] if pos_real == 1 else C['white']
            c.create_text(W//2 - 160, y, anchor='w', text=f"{pos_real:02d}. {reg['nome']}", font=F['med'], fill=cor)
            c.create_text(W//2 + 160, y, anchor='e', text=f"{reg['score']:06d} PTS", font=F['med'], fill=cor)
            y += 25
            
        c.create_text(W//2, cy_board + 205, text=f'[<-] Página {pag_atual}/{max_pag} [->]', font=F['small'], fill=C['gray'])
        self.painel.delete('all')
        self.hud.delete('all')

    def _render_pause(self):
        c = self.canvas
        W, H = c.winfo_width(), c.winfo_height()
        if W < 10 or H < 10: return
        
        c.create_rectangle(0, 0, W, H, fill='#000', stipple='gray50')
        pw, ph = 300, 250
        px, py = (W - pw)//2, (H - ph)//2
        c.create_rectangle(px, py, px+pw, py+ph, fill=C['bg_panel'], outline=C['cyan'], width=4)
        c.create_text(W//2, py + 40, text='PAUSADO', font=F['title'], fill=C['yellow'])
        
        self.botoes_pause = {
            'CONTINUAR': (W//2 - 100, py + 80, W//2 + 100, py + 120),
            'MENU':      (W//2 - 100, py + 140, W//2 + 100, py + 180),
            'SAIR':      (W//2 - 100, py + 200, W//2 + 100, py + 240)
        }
        for texto, (x1, y1, x2, y2) in self.botoes_pause.items():
            c.create_rectangle(x1, y1, x2, y2, fill=C['border'], outline=C['cyan'], width=2)
            c.create_text((x1+x2)//2, (y1+y2)//2, text=texto, font=F['med'], fill=C['white'])

    def _render_gameover(self):
        c = self.canvas
        W, H = c.winfo_width(), c.winfo_height()
        if W < 10 or H < 10: return
        
        c.create_rectangle(0, 0, W, H, fill='#000', stipple='gray50')
        pw, ph = 500, 250
        px, py = (W - pw)//2, (H - ph)//2
        c.create_rectangle(px, py, px+pw, py+ph, fill=C['bg_panel'], outline=C['red'], width=5)
        
        c.create_text(W//2, py + 40, text='GAME OVER', font=F['giant'], fill=C['red'])
        c.create_text(W//2, py + 100, text=self.motivo_gameover, font=F['med'], fill=C['yellow'])
        c.create_text(W//2, py + 150, text=f'PONTUAÇÃO: {self.score:06d}', font=F['title'], fill=C['white'])
        c.create_text(W//2, py + 180, text=f'NÍVEL: {self.dificuldade + 1}', font=F['med'], fill=C['gray'])
        
        if int(self.tick / 10) % 2 == 0:
            c.create_text(W//2, py + 220, text='[ PRESSIONE ESPAÇO PARA O MENU ]', font=F['small'], fill=C['cyan'])

if __name__ == '__main__':
    root = tk.Tk()
    app = AlmoxarifadoManager3D(root)
    root.mainloop()