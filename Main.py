"""
╔══════════════════════════════════════════════════════╗
║          FORJA ARCANA — Pygame Port                  ║
║    Criação & Conjuração de Magias Geométricas        ║
╚══════════════════════════════════════════════════════╝
"""

import pygame
import pygame.gfxdraw
import math
import random
import sys
import os
import json

# ──────────────────────────────────────────────────────────
# FIX DE DIRETÓRIO (Garante que o Pygame ache os arquivos)
# ──────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# ──────────────────────────────────────────────────────────
# CONSTANTES DE COR BASE E DICIONÁRIOS
# ──────────────────────────────────────────────────────────
INK           = (10,   6,  18)
GOLD          = (224, 169, 109)
GOLD_BRIGHT   = (245, 201, 122)
GOLD_DIM      = (138,  92,  42)
RUNE_GLOW     = (196, 122, 255)
WHITE         = (255, 255, 255)

ELEMENTOS = {
    "Neutro": {"nome": "Energia Arcana", "main": GOLD, "bright": GOLD_BRIGHT, "dim": GOLD_DIM, "bg": (8, 6, 18), "rune": "✦", "p_colors": [GOLD, GOLD_BRIGHT, RUNE_GLOW, WHITE]},
    "Fogo":   {"nome": "Fogo",   "main": (255, 80, 0),  "bright": (255, 180, 50), "dim": (150, 30, 0), "bg": (25, 5, 0), "rune": "ᚲ", "p_colors": [(255,80,0), (255,200,0), WHITE, (200,20,0)]},
    "Agua":   {"nome": "Água",   "main": (0, 150, 255), "bright": (100, 200, 255), "dim": (0, 50, 150), "bg": (0, 10, 25), "rune": "ᛚ", "p_colors": [(0,150,255), (100,200,255), WHITE]},
    "Terra":  {"nome": "Terra",  "main": (50, 200, 50), "bright": (150, 255, 150), "dim": (20, 100, 20), "bg": (5, 15, 5), "rune": "ᛒ", "p_colors": [(50,200,50), (100,255,100), (139,69,19), WHITE]},
    "Ar":     {"nome": "Ar",     "main": (200, 230, 255), "bright": (255, 255, 255), "dim": (100, 150, 200), "bg": (15, 20, 25), "rune": "ᚨ", "p_colors": [(200,230,255), WHITE, (150,200,255)]},
    "Raio":   {"nome": "Raio",   "main": (255, 255, 0), "bright": (255, 255, 200), "dim": (150, 150, 0), "bg": (20, 20, 0), "rune": "ᛋ", "p_colors": [(255,255,0), (255,255,200), (150,0,255), WHITE]},
}

CHALK_COLORS = {
    "Branco": (255, 255, 255), "Sangue": (220, 40, 40), "Ouro": (255, 215, 0),
    "Esmeralda": (50, 255, 100), "Cyan": (50, 220, 255), "Ametista": (180, 80, 255)
}

def clamp_color(val): return max(0, min(255, int(val)))
def apply_alpha(color, alpha): return (*color[:3], alpha) if len(color) == 3 else (*color[:3], alpha)

# ──────────────────────────────────────────────────────────
# PARTÍCULAS E POEIRA DE GIZ
# ──────────────────────────────────────────────────────────
class Star:
    COLORS = [(255, 255, 255), (224, 169, 109), (136, 136, 255), (204, 136, 255)]
    def __init__(self, w, h): self.w, self.h = w, h; self.reset()
    def reset(self):
        self.x, self.y = random.random() * self.w, random.random() * self.h
        self.r, self.alpha = random.uniform(0.4, 2.0), random.random()
        self.speed, self.dir = random.uniform(0.004, 0.012), 1 if random.random() > 0.5 else -1
        self.color = random.choice(Star.COLORS)
    def update(self):
        self.alpha += self.speed * self.dir * random.uniform(0.5, 1.5)
        if self.alpha > 1: self.alpha = 1; self.dir = -1
        elif self.alpha < 0.04: self.alpha = 0.04; self.dir = 1
    def draw(self, surf):
        pygame.gfxdraw.filled_circle(surf, int(self.x), int(self.y), max(1, int(self.r)), (*self.color, int(self.alpha * 255)))

class Particle:
    def __init__(self, cx, cy, colors):
        self.x, self.y = float(cx), float(cy)
        self.r = random.uniform(2, 6) / 2
        angle, speed = random.uniform(0, math.tau), random.uniform(20, 80)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.life, self.decay = 1.0, random.uniform(1.5, 2.5)
        self.color = random.choice(colors)
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt
        self.life -= self.decay * dt
        self.vx *= 0.92; self.vy *= 0.92
    @property
    def alive(self): return self.life > 0
    def draw(self, surf):
        a, r = max(0, min(255, int(self.life * 255))), max(1, int(self.r * self.life))
        pygame.gfxdraw.filled_circle(surf, int(self.x), int(self.y), r, (*self.color, a))

class FallingDust:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-15, 15), random.uniform(-10, 20)
        self.r, self.alpha = random.uniform(0.5, 1.5), random.uniform(180, 255)
        self.color = color
    def update(self, dt):
        self.vy += 200 * dt
        self.x += self.vx * dt; self.y += self.vy * dt
        self.alpha -= 120 * dt
    @property
    def alive(self): return self.alpha > 0
    def draw(self, surf):
        if self.alpha > 0: pygame.gfxdraw.filled_circle(surf, int(self.x), int(self.y), max(1, int(self.r)), apply_alpha(self.color, int(self.alpha)))

# ──────────────────────────────────────────────────────────
# LÓGICA DE CURVAS BÉZIER E MATEMÁTICA
# ──────────────────────────────────────────────────────────
def get_bezier_points(p0, p1, p2, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        pts.append((x, y))
    return pts

def point_to_line_dist(px, py, x1, y1, x2, y2):
    l2 = (x2 - x1)**2 + (y2 - y1)**2
    if l2 == 0: return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
    proj_x, proj_y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    return math.hypot(px - proj_x, py - proj_y)

def try_font(names, size, bold=False):
    for name in names:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except Exception: pass
    return pygame.font.Font(None, size)

def conjurar(pontos, linhas_dicts, el_nome, metamagic_count, has_unstable_curves):
    if len(pontos) < 2: return None, "⚠ Fricção insuficiente no Sigilo Maior!", None
    comportamento = "Alvo Único" if len(pontos) <= 3 else ("Área de Efeito" if len(pontos) == 4 else "Contenção")
    caos = "Estável"
    forma = "Projétil" if len(pontos) <= 3 else ("Expansivo" if len(pontos) == 4 else "Escudo")
    
    spell = f"{forma} de {el_nome} — {comportamento}"
    if metamagic_count > 0: spell += f" (+{metamagic_count} Modificadores)"
    if has_unstable_curves: caos = "INSTÁVEL (Alto Risco)"
    
    return spell, None, {"nós": len(pontos), "geometria": "Fechada" if len(pontos)>4 else "Agressiva", "caos": caos, "badge": "Anomalia Curva!" if has_unstable_curves else ""}

# ──────────────────────────────────────────────────────────
# DESENHO DOS DISCOS
# ──────────────────────────────────────────────────────────
RUNES = "ᚠ · ᚢ · ᚦ · ᚨ · ᚱ · ᚲ · ᚷ · ᚹ · ᚺ · ᚾ · ᛁ · ᛃ · ᛈ · ᛊ · ᛏ · ᛒ · ᛖ · ᛗ · ᛚ ·  · "

def draw_rune_ring(surf, cx, cy, radius, angle_offset, font, color, active_icon=None, active_rune=None):
    chars = list(RUNES); n = len(chars)
    icon_indices = [0, n // 4, n // 2, 3 * n // 4]
    dead_zone = set()
    for idx in icon_indices:
        dead_zone.add((idx - 1) % n); dead_zone.add((idx + 1) % n)

    for i, ch in enumerate(chars):
        angle = angle_offset + (i / n) * math.tau
        tx, ty = cx + math.cos(angle) * radius, cy + math.sin(angle) * radius
        if i in icon_indices:
            if active_icon: surf.blit(active_icon, active_icon.get_rect(center=(int(tx), int(ty))))
            elif active_rune:
                if active_rune == "✦": pygame.draw.circle(surf, color, (int(tx), int(ty)), 8, 2)
                else:
                    try:
                        glyph = font.render(active_rune, True, color); glyph.set_alpha(255)
                        surf.blit(glyph, glyph.get_rect(center=(int(tx), int(ty))))
                    except Exception: pass
        elif i not in dead_zone:
            try:
                glyph = font.render(ch, True, color)
                glyph.set_alpha(160) # Aumentado de 90 para 160
                surf.blit(glyph, glyph.get_rect(center=(int(tx), int(ty))))
            except Exception: pass

DISCO_SIZE, DISCO_CX, DISCO_CY, DISCO_R = 320, 160, 160, 145
SAT_SIZE, SAT_CX, SAT_CY, SAT_R = 150, 75, 75, 65

def render_sigilo(surf, cx, cy, r_max, num_nodes, pontos, linhas, anim_dust, el_data, font, draw_angles=True):
    surf.fill((0, 0, 0, 0))
    C_MAIN, C_BRIGHT, C_DIM, C_BG = el_data["main"], el_data["bright"], el_data["dim"], el_data["bg"]
    
    has_curve = any(l.get("is_curved", False) for l in linhas)

    pygame.gfxdraw.filled_circle(surf, cx, cy, r_max, (*C_BG, 255))
    pygame.draw.circle(surf, (*C_MAIN, 60), (cx, cy), r_max, 2)
    if draw_angles: pygame.draw.circle(surf, (*C_DIM, 100), (cx, cy), int(r_max * 0.6), 1)

    for i in range(num_nodes):
        angle = -math.pi/2 + i * (math.tau / num_nodes)
        nx, ny = int(cx + math.cos(angle) * r_max), int(cy + math.sin(angle) * r_max)
        destaque = (num_nodes == 24 and i % 6 == 0) or (num_nodes == 8 and i % 2 == 0)
        if destaque:
            pygame.draw.circle(surf, (*C_MAIN, 200), (nx, ny), 6 if draw_angles else 4, 1)
            pygame.gfxdraw.filled_circle(surf, nx, ny, 3 if draw_angles else 2, C_BRIGHT)
        else:
            pygame.draw.circle(surf, (*C_MAIN, 100), (nx, ny), 4 if draw_angles else 2, 1)
            pygame.gfxdraw.filled_circle(surf, nx, ny, 2 if draw_angles else 1, C_DIM)

    # Brilho de fundo das linhas e Giz
    for l in linhas:
        if not l["is_curved"]:
            pygame.draw.line(surf, (*C_MAIN, 30), (int(l["p1"][0]), int(l["p1"][1])), (int(l["p2"][0]), int(l["p2"][1])), 8)
            pygame.draw.line(surf, (*C_BRIGHT, 50), (int(l["p1"][0]), int(l["p1"][1])), (int(l["p2"][0]), int(l["p2"][1])), 2)
        else:
            pts = get_bezier_points(l["p1"], l["cp"], l["p2"])
            pygame.draw.aalines(surf, (*C_BRIGHT, 80), False, pts)
            
        for x, y, r, a, color in l["dust"]:
            pygame.gfxdraw.filled_circle(surf, int(x), int(y), int(r), apply_alpha(color, a))

    for x, y, r, a, color in anim_dust:
        pygame.gfxdraw.filled_circle(surf, int(x), int(y), int(r), apply_alpha(color, a))

    # ─── ÂNGULOS MULTI-DIRECIONAIS CORRIGIDOS ───
    if (draw_angles or not has_curve):
        node_connections = {}
        for l in linhas:
            if l.get("is_curved", False): continue
            
            p1, p2 = l["p1"], l["p2"]
            for p_curr, p_other in [(p1, p2), (p2, p1)]:
                found_node = None
                for knode in node_connections:
                    if math.hypot(knode[0] - p_curr[0], knode[1] - p_curr[1]) < 2:
                        found_node = knode; break
                if found_node is None:
                    found_node = p_curr
                    node_connections[found_node] = []
                node_connections[found_node].append(p_other)

        for n_center, connected in node_connections.items():
            if len(connected) < 2: continue
            
            angles_brutos = []
            for c_pt in connected:
                ang = math.atan2(c_pt[1] - n_center[1], c_pt[0] - n_center[0])
                if ang < 0: ang += math.tau
                angles_brutos.append((ang, c_pt))
            
            angles_brutos.sort(key=lambda x: x[0])
            
            num_con = len(angles_brutos)
            for i in range(num_con):
                ang1, pt1 = angles_brutos[i]
                ang2, pt2 = angles_brutos[(i + 1) % num_con]
                
                diff = (ang2 - ang1) % math.tau
                a_start = ang1
                
                graus = int(round(math.degrees(diff)))
                if 5 < graus < 175:
                    raio_arco = 20
                    pontos_arco = []
                    passos = max(5, graus // 6)
                    for step in range(passos + 1):
                        ang_step = a_start + (diff * step / passos)
                        pontos_arco.append((n_center[0] + math.cos(ang_step) * raio_arco, n_center[1] + math.sin(ang_step) * raio_arco))
                    if len(pontos_arco) > 1: pygame.draw.aalines(surf, C_DIM, False, pontos_arco)

                    bissetor = a_start + diff / 2
                    tx, ty = n_center[0] + math.cos(bissetor) * 34, n_center[1] + math.sin(bissetor) * 34
                    text_surf = font.render(f"{graus}°", True, C_BRIGHT)
                    text_surf.set_alpha(200)
                    surf.blit(text_surf, text_surf.get_rect(center=(int(tx), int(ty))))

    # TEXTO DA CURVA BÉZIER
    for l in linhas:
        if l.get("is_curved", False):
            mx, my = (l["p1"][0] + l["p2"][0])/2, (l["p1"][1] + l["p2"][1])/2
            vx_cp, vy_cp = l["cp"][0] - mx, l["cp"][1] - my
            
            dist_curva = math.hypot(vx_cp, vy_cp)
            if dist_curva > 8: 
                graus_curva = int(min(90, dist_curva * 1.5))
                lado = "IN" if vx_cp * (mx - cx) + vy_cp * (my - cy) < 0 else "OUT"
                
                txt_c = font.render(f"~{graus_curva}° {lado}", True, C_BRIGHT)
                txt_c.set_alpha(180)
                surf.blit(txt_c, txt_c.get_rect(center=(int(l["cp"][0]), int(l["cp"][1] - 14))))

    # Pontos finais do jogador
    for i, p in enumerate(pontos):
        pr, glow_r = (5, 9) if i == len(pontos) - 1 else (4, 8)
        pygame.gfxdraw.filled_circle(surf, int(p[0]), int(p[1]), glow_r, (*C_MAIN, 50))
        pygame.gfxdraw.filled_circle(surf, int(p[0]), int(p[1]), pr, C_BRIGHT)
        pygame.gfxdraw.aacircle(surf, int(p[0]), int(p[1]), pr, C_MAIN)

# ──────────────────────────────────────────────────────────
# CLASSE PRINCIPAL DA APLICAÇÃO (FORJA ARCANO)
# ──────────────────────────────────────────────────────────
class ForjaArcana:
    SIDEBAR_W, WIN_W, WIN_H, HEADER_H, FOOTER_H = 370, 1150, 820, 88, 28

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.WIN_W, self.WIN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Forja Arcana — Conjuração de Magias")
        self._load_fonts()
        self._load_icons()
        self._init_layout()
        self._init_state()

    def _load_fonts(self):
        try:
            self.fnt_title = pygame.font.Font("Alkhemikal.ttf", 42)
            self.fnt_h3    = pygame.font.Font("Alkhemikal.ttf", 17)
            self.fnt_body  = pygame.font.Font("Alkhemikal.ttf", 16)
            self.fnt_small = pygame.font.Font("Alkhemikal.ttf", 14)
            self.fnt_tiny  = pygame.font.Font("Alkhemikal.ttf", 12)
            self.fnt_spell = pygame.font.Font("Alkhemikal.ttf", 20)
            self.fnt_label = pygame.font.Font("Alkhemikal.ttf", 13)
            self.fnt_btn   = pygame.font.Font("Alkhemikal.ttf", 14)
        except Exception:
            self.fnt_title = try_font(["cinzel decorative", "cinzel", "georgia"], 42, bold=True)
            self.fnt_h3    = try_font(["cinzel decorative", "cinzel", "georgia"], 17, bold=True)
            self.fnt_body  = try_font(["crimson text", "georgia"], 16)
            self.fnt_small = try_font(["cinzel decorative", "cinzel", "georgia"], 14)
            self.fnt_tiny  = try_font(["cinzel decorative", "cinzel", "georgia"], 12)
            self.fnt_spell = try_font(["cinzel decorative", "cinzel", "georgia"], 20, bold=True)
            self.fnt_label = try_font(["cinzel decorative", "cinzel", "georgia"], 13)
            self.fnt_btn   = try_font(["cinzel decorative", "cinzel", "georgia"], 14, bold=True)

        try: self.fnt_rune = pygame.font.Font("NotoSansRunic-Regular.ttf", 16)
        except Exception: self.fnt_rune = try_font(["segoe ui historic", "segoe ui symbol"], 16)

    def _load_icons(self):
        self.icons = {}
        if os.path.exists("Flame_icon.png"):
            try:
                img = pygame.image.load("Flame_icon.png").convert_alpha()
                self.icons["Fogo"] = pygame.transform.smoothscale(img, (26, 26))
            except Exception: pass
            
        if os.path.exists("Options_btn.png"):
            try:
                img = pygame.image.load("Options_btn.png").convert_alpha()
                w, h = img.get_size()
                frame_w = w // 2
                img_normal = img.subsurface((0, 0, frame_w, h))
                img_hover = img.subsurface((frame_w, 0, frame_w, h))
                self.icons["Config_Normal"] = pygame.transform.smoothscale(img_normal, (45, 45))
                self.icons["Config_Hover"] = pygame.transform.smoothscale(img_hover, (45, 45))
            except Exception as e: print(f"Erro ao carregar Options_btn.png: {e}")
                
        if os.path.exists("Vertical_Menu_box.png"):
            try:
                img = pygame.image.load("Vertical_Menu_box.png").convert_alpha()
                self.icons["MenuBox"] = pygame.transform.smoothscale(img, (500, 800))
            except Exception: pass

        if os.path.exists("Input_large.png"):
            try:
                img = pygame.image.load("Input_large.png").convert_alpha()
                self.icons["ResolutionBox"] = pygame.transform.smoothscale(img, (420, 70))
            except Exception: pass
        
        for img_name, key, size in [
            ("Bar_empty.png", "BarEmpty", (400, 128)),
            ("Bar_full.png", "BarFull", (400, 128)),
            ("Point_btn.png", "SliderPoint", (110, 110))
        ]:
            if os.path.exists(img_name):
                try:
                    img = pygame.image.load(img_name).convert_alpha()
                    self.icons[key] = pygame.transform.smoothscale(img, size)
                except Exception: pass

    def _init_layout(self):
        W, H, S, HH, FH = self.WIN_W, self.WIN_H, self.SIDEBAR_W, self.HEADER_H, self.FOOTER_H
        self.rect_header  = pygame.Rect(0, 0, W, HH)
        self.rect_sidebar = pygame.Rect(0, HH, S, H - HH - FH)
        self.rect_forge   = pygame.Rect(S, HH, W-S, H - HH - FH)
        self.rect_footer  = pygame.Rect(0, H-FH, W, FH)

        self.rune_ring_r = DISCO_SIZE//2 + 36
        self.orbit_r = self.rune_ring_r + 85 
        
        fx, fy = S + (W-S)//2, HH + 20 + self.orbit_r + SAT_R
        self.disco_topleft = (fx - DISCO_SIZE//2, fy - DISCO_SIZE//2)
        self.disco_center  = (fx, fy)

        bw, bh, gap = 160, 38, 16
        bx, by = fx - (bw*2 + gap + 150)//2, fy + self.orbit_r + SAT_R + 25
        self.btn_conjure = pygame.Rect(bx, by, bw, bh)
        self.btn_clear   = pygame.Rect(bx+bw+gap, by, bw, bh)
        self.btn_orbit   = pygame.Rect(bx+2*(bw+gap), by, bw-20, bh)

        self.result_rect = pygame.Rect(fx - 240, by + bh + 12, 480, 115)
        self.btn_settings = pygame.Rect(self.WIN_W - 55, 15, 45, 45) 

        self.paleta_rects = {}
        py, px = HH + 50, S + 30
        for key in ["Fogo", "Agua", "Terra", "Ar", "Raio"]:
            self.paleta_rects[key] = pygame.Rect(px, py, 40, 40); py += 55
            
        self.chalk_rects = {}
        py_chalk, px_chalk = HH + 50, W - 70
        self.btn_tool_mode = pygame.Rect(px_chalk - 100, py_chalk - 35, 140, 26)
        
        for key in ["Branco", "Sangue", "Ouro", "Esmeralda", "Cyan", "Ametista"]:
            self.chalk_rects[key] = pygame.Rect(px_chalk, py_chalk, 40, 40); py_chalk += 55

    def _init_state(self):
        self.stars = [Star(self.WIN_W, self.WIN_H) for _ in range(220)]
        self.particles = []
        self.falling_dust = []
        
        self.main_disco = {"pontos": [], "linhas": []}
        self.satelites = [{"pontos": [], "linhas": [], "surf": pygame.Surface((SAT_SIZE, SAT_SIZE), pygame.SRCALPHA)} for _ in range(5)]
        
        self.orbiting = True
        self.orbit_angle = 0.0
        
        self.tool_mode = "Desenhar"
        self.dragged_line = None 
        self.drag_sat_idx = -1
        
        self.target_queue = []
        self.animating = False
        self.anim_target_idx = -1
        self.anim_start = None
        self.anim_target = None
        self.anim_progress = 0.0
        self.anim_dist = 0.0
        self.anim_dust = []
        self.draw_speed = 400.0
        
        self.active_element = "Neutro"
        self.active_chalk = "Branco"
        self.drag_element = None
        self.mouse_pos = (0, 0)
        
        self.hovered_main_node = None
        self.hovered_sat = None

        self.rune_angle = 0.0
        self.result_spell = self.result_error = self.result_stats = None
        self.result_flash = 0.0
        self.hover_btn_conjure = self.hover_btn_clear = self.hover_btn_orbit = self.hover_btn_tool = False
        
        # Audio / Settings
        self.hover_btn_settings = False 
        self.show_settings_menu = False
        self.dragging_slider = None
        self.music_vol = 0.3
        self.sfx_vol = 1.0
        self.available_resolutions = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080)]
        self.current_resolution_index = 3
        self.selected_resolution = self.available_resolutions[self.current_resolution_index]
        self.rect_music_slider = pygame.Rect(0, 0, 0, 0)
        self.rect_sfx_slider = pygame.Rect(0, 0, 0, 0)
        self.rect_res_left = pygame.Rect(0,0,0,0)
        self.rect_res_right = pygame.Rect(0,0,0,0)
        
        self.load_settings()
        
        self.disco_surf = pygame.Surface((DISCO_SIZE, DISCO_SIZE), pygame.SRCALPHA)
        self._redraw_all_discos()
        self.star_surf = pygame.Surface((self.WIN_W, self.WIN_H), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()

        # AUDIO INITIALIZATION
        self.chalk_sound = None
        if os.path.exists("Chalk.mp3"):
            try:
                self.chalk_sound = pygame.mixer.Sound("Chalk.mp3")
                self.chalk_sound.set_volume(self.sfx_vol)
            except Exception: pass
        self.chalk_sound_playing = False

        if os.path.exists("BG_music.mp3"):
            try:
                pygame.mixer.music.load("BG_music.mp3")
                pygame.mixer.music.play(-1) 
                pygame.mixer.music.set_volume(self.music_vol) 
            except Exception: pass
        
        self.select_sound = None
        if os.path.exists("Select.mp3"):
            try:
                self.select_sound = pygame.mixer.Sound("Select.mp3")
                self.select_sound.set_volume(self.sfx_vol)
            except Exception: pass
            
        self.last_sfx_time = 0

    def _update_slider_vol(self, mouse_x, slider_rect, vol_type):
        rel_x = max(0, min(mouse_x - slider_rect.x, slider_rect.width))
        vol = rel_x / slider_rect.width
        if vol_type == 'music':
            self.music_vol = vol; pygame.mixer.music.set_volume(vol)
        elif vol_type == 'sfx':
            self.sfx_vol = vol
            if getattr(self, 'select_sound', None): self.select_sound.set_volume(vol)
            if getattr(self, 'chalk_sound', None): self.chalk_sound.set_volume(vol)
        self.save_settings()

    def _redraw_all_discos(self):
        render_sigilo(self.disco_surf, DISCO_CX, DISCO_CY, DISCO_R, 24, self.main_disco["pontos"], self.main_disco["linhas"], self.anim_dust if self.anim_target_idx == -1 else [], ELEMENTOS[self.active_element], self.fnt_tiny, True)
        for i, sat in enumerate(self.satelites):
            render_sigilo(sat["surf"], SAT_CX, SAT_CY, SAT_R, 8, sat["pontos"], sat["linhas"], self.anim_dust if self.anim_target_idx == i else [], ELEMENTOS[self.active_element], self.fnt_tiny, False)
    
    def _add_node_point(self, target_idx, nx, ny): self.target_queue.append((target_idx, nx, ny))

    def _undo_point(self):
        self.target_queue.clear()
        if self.animating:
            self.animating = False; self.anim_dust.clear()
        else:
            if self.main_disco["pontos"]:
                self.main_disco["pontos"].pop()
                if self.main_disco["linhas"]: self.main_disco["linhas"].pop()
        self._redraw_all_discos()

    def _clear(self):
        self.target_queue.clear()
        self.animating = False; self.anim_dust.clear(); self.falling_dust.clear()
        if self.chalk_sound and self.chalk_sound_playing:
            self.chalk_sound.stop(); self.chalk_sound_playing = False
        self.main_disco = {"pontos": [], "linhas": []}
        for sat in self.satelites:
            sat["pontos"].clear(); sat["linhas"].clear()
        self.result_spell = self.result_error = self.result_stats = None
        self.result_flash = 0.0
        self._redraw_all_discos()

    def _conjurar(self):
        el_nome = ELEMENTOS[self.active_element]["nome"]
        has_unstable = any(any(l["is_curved"] for l in sat["linhas"]) for sat in self.satelites)
        metamagic_count = sum(1 for sat in self.satelites if len(sat["pontos"]) >= 2)
        
        spell, error, stats = conjurar(self.main_disco["pontos"], self.main_disco["linhas"], el_nome, metamagic_count, has_unstable)
        self.result_spell, self.result_error, self.result_stats = spell, error, stats
        if spell:
            self.result_flash = 1.0
            cx, cy = self.disco_center
            for _ in range(30): self.particles.append(Particle(cx + random.randint(-20, 20), cy + random.randint(-20, 20), ELEMENTOS[self.active_element]["p_colors"]))

    def handle_event(self, event):
        if event.type == pygame.QUIT: return False
        
        keys = pygame.key.get_pressed()
        mod_moldar = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_LCTRL] or self.tool_mode == "Moldar"
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if getattr(self, 'show_settings_menu', False):
                    self.show_settings_menu = False
                    if getattr(self, 'select_sound', None): self.select_sound.play()
                else: self._clear()
            elif not getattr(self, 'show_settings_menu', False):
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE): self._undo_point()
                elif event.key == pygame.K_RETURN: self._conjurar()

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            
            current_time = pygame.time.get_ticks()
            if getattr(self, 'show_settings_menu', False):
                if getattr(self, 'dragging_slider', None) == "music":
                    self._update_slider_vol(mx, self.rect_music_slider, "music")
                elif getattr(self, 'dragging_slider', None) == "sfx":
                    self._update_slider_vol(mx, self.rect_sfx_slider, "sfx")
                    if current_time - self.last_sfx_time > 100:
                        if getattr(self, 'select_sound', None): self.select_sound.play()
                        self.last_sfx_time = current_time
                return True

            self.mouse_pos = event.pos
            self.hover_btn_conjure = self.btn_conjure.collidepoint(event.pos)
            self.hover_btn_clear   = self.btn_clear.collidepoint(event.pos)
            self.hover_btn_orbit   = self.btn_orbit.collidepoint(event.pos)
            self.hover_btn_tool    = self.btn_tool_mode.collidepoint(event.pos)
            self.hover_btn_settings= self.btn_settings.collidepoint(event.pos)

            self.hovered_main_node = None
            self.hovered_sat = None
            
            if self.dragged_line is not None and self.drag_sat_idx != -1:
                sat_ang = self.orbit_angle + self.drag_sat_idx * (math.tau / 5) - math.pi/2
                sx, sy = self.disco_center[0] + math.cos(sat_ang) * self.orbit_r, self.disco_center[1] + math.sin(sat_ang) * self.orbit_r
                slx, sly = event.pos[0] - (sx - SAT_CX), event.pos[1] - (sy - SAT_CY)
                
                v_center_x, v_center_y = slx - SAT_CX, sly - SAT_CY
                dist_center = math.hypot(v_center_x, v_center_y)
                
                if dist_center > SAT_R:
                    slx = SAT_CX + (v_center_x / dist_center) * SAT_R
                    sly = SAT_CY + (v_center_y / dist_center) * SAT_R
                
                self.dragged_line["is_curved"] = True
                self.dragged_line["cp"] = (slx, sly)
                self.dragged_line["dust"] = []
                self._redraw_all_discos()
                return True

            lx, ly = event.pos[0] - self.disco_topleft[0], event.pos[1] - self.disco_topleft[1]
            for i in range(24):
                angle = -math.pi/2 + i * (math.tau / 24)
                nx, ny = DISCO_CX + math.cos(angle) * DISCO_R, DISCO_CY + math.sin(angle) * DISCO_R
                if (lx - nx)**2 + (ly - ny)**2 <= 225:
                    self.hovered_main_node = i
                    break
            
            if not self.orbiting and self.hovered_main_node is None:
                for i in range(5):
                    sat_ang = self.orbit_angle + i * (math.tau / 5) - math.pi/2
                    sx, sy = self.disco_center[0] + math.cos(sat_ang) * self.orbit_r, self.disco_center[1] + math.sin(sat_ang) * self.orbit_r
                    slx, sly = event.pos[0] - (sx - SAT_CX), event.pos[1] - (sy - SAT_CY)
                    for j in range(8):
                        nang = -math.pi/2 + j * (math.tau / 8)
                        nx, ny = SAT_CX + math.cos(nang) * SAT_R, SAT_CY + math.sin(nang) * SAT_R
                        if (slx - nx)**2 + (sly - ny)**2 <= 144:
                            self.hovered_sat = (i, j)
                            break
                    if self.hovered_sat: break

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = None
            if event.button == 1:
                if getattr(self, 'show_settings_menu', False): return True
                if self.drag_element:
                    lx, ly = event.pos[0] - self.disco_topleft[0], event.pos[1] - self.disco_topleft[1]
                    if (lx - DISCO_CX)**2 + (ly - DISCO_CY)**2 <= (DISCO_R + 20) ** 2:
                        self.active_element = self.drag_element
                        self._redraw_all_discos()
                    self.drag_element = None
                    
                elif self.dragged_line:
                    pts = get_bezier_points(self.dragged_line["p1"], self.dragged_line["cp"], self.dragged_line["p2"], 30)
                    new_dust = []
                    cor_giz = CHALK_COLORS[self.active_chalk]
                    for idx in range(len(pts)-1):
                        px, py = pts[idx]
                        new_dust.append((px + random.uniform(-0.5, 0.5), py + random.uniform(-0.5, 0.5), random.uniform(1.5, 2.5), 255, cor_giz))
                        if random.random() > 0.5:
                            new_dust.append((px + random.uniform(-2.5, 2.5), py + random.uniform(-2.5, 2.5), random.uniform(1.0, 3.0), random.randint(100, 200), cor_giz))
                    self.dragged_line["dust"] = new_dust
                    self.dragged_line = None
                    self.drag_sat_idx = -1
                    self._redraw_all_discos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 1:
                if getattr(self, 'show_settings_menu', False):
                    if self.rect_music_slider.collidepoint(mx, my):
                        self.dragging_slider = "music"; self._update_slider_vol(mx, self.rect_music_slider, "music"); return True
                    if self.rect_sfx_slider.collidepoint(mx, my):
                        self.dragging_slider = "sfx"; self._update_slider_vol(mx, self.rect_sfx_slider, "sfx"); return True
                    if self.rect_res_left.collidepoint(mx, my):
                        self.current_resolution_index = (self.current_resolution_index - 1) % len(self.available_resolutions)
                        self._apply_resolution(); 
                        if self.select_sound: self.select_sound.play()
                        return True
                    if self.rect_res_right.collidepoint(mx, my):
                        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.available_resolutions)
                        self._apply_resolution(); 
                        if self.select_sound: self.select_sound.play()
                        return True
                        
                    menu_img = self.icons.get("MenuBox")
                    menu_w, menu_h = menu_img.get_size() if menu_img else (300, 450)
                    menu_rect = pygame.Rect((self.WIN_W - menu_w)//2, (self.WIN_H - menu_h)//2, menu_w, menu_h)
                    if not menu_rect.collidepoint(mx, my):
                        self.show_settings_menu = False
                        if self.select_sound: self.select_sound.play()
                    return True

                if self.btn_settings.collidepoint(mx, my):
                    self.show_settings_menu = not self.show_settings_menu
                    if self.select_sound: self.select_sound.play()
                    return True

                if self.btn_tool_mode.collidepoint(mx, my):
                    self.tool_mode = "Moldar" if self.tool_mode == "Desenhar" else "Desenhar"
                    return True
                
                for key, rect in self.paleta_rects.items():
                    if rect.collidepoint(mx, my): self.drag_element = key; return True
                for key, rect in self.chalk_rects.items():
                    if rect.collidepoint(mx, my): self.active_chalk = key; return True

                if self.btn_conjure.collidepoint(mx, my): self._conjurar()
                elif self.btn_clear.collidepoint(mx, my): self._clear()
                elif self.btn_orbit.collidepoint(mx, my): self.orbiting = not self.orbiting
                
                if mod_moldar and not self.orbiting:
                    for i in range(5):
                        sat_ang = self.orbit_angle + i * (math.tau / 5) - math.pi/2
                        sx, sy = self.disco_center[0] + math.cos(sat_ang) * self.orbit_r, self.disco_center[1] + math.sin(sat_ang) * self.orbit_r
                        slx, sly = mx - (sx - SAT_CX), my - (sy - SAT_CY)
                        
                        best_dist = float('inf'); best_line = None
                        for linha in self.satelites[i]["linhas"]:
                            d = point_to_line_dist(slx, sly, linha["p1"][0], linha["p1"][1], linha["p2"][0], linha["p2"][1])
                            if d < best_dist: best_dist = d; best_line = linha
                        
                        if best_dist < 20: 
                            self.dragged_line = best_line
                            self.drag_sat_idx = i
                            return True
                
                if not mod_moldar:
                    if self.hovered_main_node is not None: 
                        angle = -math.pi/2 + self.hovered_main_node * (math.tau / 24)
                        self._add_node_point(-1, DISCO_CX + math.cos(angle) * DISCO_R, DISCO_CY + math.sin(angle) * DISCO_R)
                    elif self.hovered_sat is not None:
                        sat_idx, node_idx = self.hovered_sat
                        angle = -math.pi/2 + node_idx * (math.tau / 8)
                        self._add_node_point(sat_idx, SAT_CX + math.cos(angle) * SAT_R, SAT_CY + math.sin(angle) * SAT_R)
            
            elif event.button == 3: 
                if getattr(self, 'show_settings_menu', False): return True
                lx, ly = event.pos[0] - self.disco_topleft[0], event.pos[1] - self.disco_topleft[1]
                if (lx - DISCO_CX)**2 + (ly - DISCO_CY)**2 <= (DISCO_R + 20) ** 2: self._clear()

        return True

    def update(self, dt):
        for s in self.stars: s.update()
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles: p.update(dt)
        
        self.falling_dust = [fd for fd in self.falling_dust if fd.alive]
        for fd in self.falling_dust: fd.update(dt)
        
        if self.orbiting: self.orbit_angle += (math.tau / 2000) * dt * 60
        self.rune_angle += (math.tau / 1500) * dt * 60
        if self.result_flash > 0: self.result_flash = max(0.0, self.result_flash - dt * 1.2)

        if not self.animating and self.target_queue:
            t_idx, nx, ny = self.target_queue.pop(0)
            self.anim_target_idx = t_idx
            target_dict = self.main_disco if t_idx == -1 else self.satelites[t_idx]
            
            if not target_dict["pontos"]:
                target_dict["pontos"].append((nx, ny))
                self._redraw_all_discos()
            else:
                self.animating = True
                self.anim_start, self.anim_target = target_dict["pontos"][-1], (nx, ny)
                self.anim_progress, self.anim_dust = 0.0, []
                self.anim_dist = math.hypot(nx - self.anim_start[0], ny - self.anim_start[1])
                if self.chalk_sound and not self.chalk_sound_playing:
                    self.chalk_sound.play(-1)
                    self.chalk_sound_playing = True

        if self.animating:
            if self.anim_dist > 0: self.anim_progress += (self.draw_speed * dt) / self.anim_dist
            else: self.anim_progress = 1.0

            expected_particles = int(self.anim_dist * self.anim_progress * 3.0)
            cor_giz = CHALK_COLORS[self.active_chalk]
            
            while len(self.anim_dust) < expected_particles and self.anim_dist > 0:
                t = min(len(self.anim_dust) / (self.anim_dist * 3.0), 1.0)
                cx = self.anim_start[0] + (self.anim_target[0] - self.anim_start[0]) * t
                cy = self.anim_start[1] + (self.anim_target[1] - self.anim_start[1]) * t
                
                self.anim_dust.append((cx + random.uniform(-0.5, 0.5), cy + random.uniform(-0.5, 0.5), random.uniform(1.5, 2.5), 255, cor_giz))
                if random.random() > 0.5:
                    self.anim_dust.append((cx + random.uniform(-2.5, 2.5), cy + random.uniform(-2.5, 2.5), random.uniform(1.0, 3.0), random.randint(100, 200), cor_giz))
                
                if random.random() < 0.15:
                    if self.anim_target_idx == -1: screen_x, screen_y = self.disco_topleft[0] + cx, self.disco_topleft[1] + cy
                    else:
                        sat_ang = self.orbit_angle + self.anim_target_idx * (math.tau / 5) - math.pi/2
                        screen_x = self.disco_center[0] + math.cos(sat_ang) * self.orbit_r - SAT_CX + cx
                        screen_y = self.disco_center[1] + math.sin(sat_ang) * self.orbit_r - SAT_CY + cy
                    self.falling_dust.append(FallingDust(screen_x, screen_y, cor_giz))

            self._redraw_all_discos()

            if self.anim_progress >= 1.0:
                self.animating = False
                if self.chalk_sound and self.chalk_sound_playing:
                    self.chalk_sound.stop()
                    self.chalk_sound_playing = False
                target_dict = self.main_disco if self.anim_target_idx == -1 else self.satelites[self.anim_target_idx]
                target_dict["pontos"].append(self.anim_target)
                
                nova_linha = {"p1": self.anim_start, "p2": self.anim_target, "is_curved": False, "cp": ((self.anim_start[0]+self.anim_target[0])/2, (self.anim_start[1]+self.anim_target[1])/2), "dust": self.anim_dust.copy()}
                target_dict["linhas"].append(nova_linha)
                
                self.anim_dust.clear()
                self._redraw_all_discos()

    def draw(self):
        self.screen.fill(INK)
        self._draw_starfield()
        self._draw_header()
        
        pygame.draw.rect(self.screen, (14, 8, 32), self.rect_sidebar)
        pygame.draw.line(self.screen, GOLD_DIM, (self.rect_sidebar.right-1, self.rect_sidebar.y), (self.rect_sidebar.right-1, self.rect_sidebar.bottom))
        title = self.fnt_h3.render("📖  Grimório Arcano", True, GOLD)
        self.screen.blit(title, (16, self.rect_sidebar.y + 14))
        
        self._draw_forge()
        self._draw_footer()
        self._draw_particles()
        for fd in self.falling_dust: fd.draw(self.screen)
        
        if self.drag_element:
            el = ELEMENTOS[self.drag_element]
            mx, my = self.mouse_pos
            pygame.gfxdraw.filled_circle(self.screen, mx, my, 20, (*el["bg"], 200))
            pygame.draw.circle(self.screen, el["main"], (mx, my), 20, 2)
            if self.icons.get(self.drag_element): self.screen.blit(self.icons[self.drag_element], self.icons[self.drag_element].get_rect(center=(mx, my)))
            else:
                rs = self.fnt_rune.render(el["rune"], True, el["bright"])
                self.screen.blit(rs, rs.get_rect(center=(mx, my)))

        keys = pygame.key.get_pressed()
        if not getattr(self, 'show_settings_menu', False) and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_LCTRL] or self.tool_mode == "Moldar"):
            if not self.orbiting and self.drag_element is None:
                pygame.draw.circle(self.screen, WHITE, self.mouse_pos, 8, 1)

        self._draw_settings_menu() 
        pygame.display.flip()

    def _draw_settings_menu(self):
        if not getattr(self, 'show_settings_menu', False): return

        menu_img = self.icons.get("MenuBox")
        menu_w, menu_h = menu_img.get_size() if menu_img else (300, 450)
        menu_x = (self.WIN_W - menu_w) // 2
        menu_y = (self.WIN_H - menu_h) // 2
        menu_center_x = menu_x + menu_w // 2
        
        overlay = pygame.Surface((self.WIN_W, self.WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        if menu_img: 
            self.screen.blit(menu_img, (menu_x, menu_y))

        title_text = self.fnt_spell.render("Configurações", True, GOLD_BRIGHT)
        self.screen.blit(title_text, title_text.get_rect(center=(menu_x + menu_w // 2, menu_y + 80)))

        line_break = self.icons.get("LineBreak")
        if not line_break and os.path.exists("Line_break.png"):
            img = pygame.image.load("Line_break.png").convert_alpha()
            self.icons["LineBreak"] = pygame.transform.smoothscale(img, (int(menu_w * 0.8), 40))
            line_break = self.icons["LineBreak"]

        def draw_slider(lbl_text, y_pos, vol, hitbox_ref):
            lbl = self.fnt_body.render(lbl_text, True, GOLD_BRIGHT)
            self.screen.blit(lbl, lbl.get_rect(center=(menu_x + menu_w // 2, y_pos)))
            
            bar_img = self.icons.get("BarEmpty")
            if not bar_img: return hitbox_ref
            bar_w, bar_h = bar_img.get_size()
            
            slider_x = menu_x + (menu_w - bar_w) // 2
            slider_y = y_pos - 20
            
            hitbox_ref.update(slider_x, slider_y - 10, bar_w, bar_h + 20)
            
            fill_w = int(bar_w * vol)
            self.screen.blit(bar_img, (slider_x, slider_y))
            if fill_w > 0 and "BarFull" in self.icons:
                surf_full = self.icons["BarFull"].subsurface((0, 0, min(fill_w, bar_w), bar_h))
                self.screen.blit(surf_full, (slider_x, slider_y))
                
            pt_img = self.icons.get("SliderPoint")
            if pt_img:
                knob_margin = 28
                knob_x = slider_x + knob_margin + ((bar_w - knob_margin * 2) * vol)
                self.screen.blit(pt_img, pt_img.get_rect(center=(knob_x, slider_y + bar_h - 60)))
            
            return hitbox_ref

        y_cursor = menu_y + 100
        if line_break:
            self.screen.blit(line_break, (menu_x + (menu_w - line_break.get_width())//2, y_cursor))
        y_cursor += 60
        
        self.rect_music_slider = draw_slider("Volume da Música", y_cursor, self.music_vol, self.rect_music_slider)
        y_cursor += 100
        
        self.rect_sfx_slider = draw_slider("Volume dos Efeitos", y_cursor, self.sfx_vol, self.rect_sfx_slider)
        y_cursor += 120

        y_cursor += 110
        title = self.fnt_body.render("Resolução",True,GOLD_BRIGHT)
        self.screen.blit(title,title.get_rect(center=(menu_center_x, y_cursor)))

        box = self.icons.get("ResolutionBox")
        if box:
            box_x = menu_x + (menu_w - box.get_width()) // 2
            box_y = y_cursor
            self.screen.blit(box, (box_x, box_y))
            res = self.available_resolutions[self.current_resolution_index]
            res_text = f"<  {res[0]} x {res[1]}  >"
            txt = self.fnt_body.render(res_text,True,GOLD_BRIGHT)
            txt_rect = txt.get_rect(center=(box_x + box.get_width() // 2,box_y + box.get_height() // 2))
            self.screen.blit(txt, txt_rect)
            self.rect_res_left.update(txt_rect.left - 40,box_y,60,box.get_height())
            self.rect_res_right.update(txt_rect.right - 20,box_y,60,box.get_height())

    def save_settings(self):
        data = {"music_vol": self.music_vol, "sfx_vol": self.sfx_vol, "resolution": self.selected_resolution, "resolution_index": getattr(self, 'current_resolution_index', 3)}
        with open("settings.json", "w") as f: json.dump(data, f, indent=4)

    def _apply_resolution(self):
        self.selected_resolution = self.available_resolutions[self.current_resolution_index]
        self.WIN_W, self.WIN_H = self.selected_resolution
        self.screen = pygame.display.set_mode(self.selected_resolution, pygame.RESIZABLE)
        self._init_layout()
        self.save_settings()

    def load_settings(self):
        if not os.path.exists("settings.json"): return
        try:
            with open("settings.json", "r") as f: data = json.load(f)
            res = data.get("resolution", [1150, 820])
            self.selected_resolution = (res[0], res[1])
            self.WIN_W, self.WIN_H = self.selected_resolution
            self.screen = pygame.display.set_mode((self.WIN_W, self.WIN_H), pygame.RESIZABLE)
            self.current_resolution_index = data.get("resolution_index",3)
            self.music_vol, self.sfx_vol = data.get("music_vol", 0.3), data.get("sfx_vol", 1.0)
        except Exception as e: print("Erro carregando settings:", e)

    def _draw_starfield(self):
        self.star_surf.fill((0, 0, 0, 0))
        for s in self.stars: s.draw(self.star_surf)
        self.screen.blit(self.star_surf, (0, 0))

    def _draw_header(self):
        pygame.draw.rect(self.screen, (15, 6, 30), self.rect_header)
        pygame.draw.line(self.screen, GOLD_DIM, (0, self.rect_header.bottom-1), (self.rect_header.right, self.rect_header.bottom-1))
        title = self.fnt_title.render("Forja Arcana", True, GOLD_BRIGHT)
        self.screen.blit(title, (self.rect_header.centerx - title.get_width()//2, 14))
        
        btn_rect = self.btn_settings
        icon_key = "Config_Hover" if self.hover_btn_settings else "Config_Normal"
        icon = self.icons.get(icon_key)
        if icon:
            self.screen.blit(icon, icon.get_rect(center=btn_rect.center))

    def _draw_forge(self):
        el = ELEMENTOS[self.active_element]
        
        lbl = self.fnt_small.render("Sigilo Primordial & Modificadores", True, el["dim"])
        self.screen.blit(lbl, (self.disco_center[0] - lbl.get_width()//2, self.disco_center[1] - self.orbit_r - SAT_R - lbl.get_height() - 20))

        icone_ativo = self.icons.get(self.active_element)
        draw_rune_ring(self.screen, self.disco_center[0], self.disco_center[1], self.rune_ring_r, self.rune_angle, self.fnt_rune, el["dim"], icone_ativo, el["rune"])
        
        time_ms = pygame.time.get_ticks()
        for i, sat in enumerate(self.satelites):
            sat_ang = self.orbit_angle + i * (math.tau / 5) - math.pi/2
            sx, sy = self.disco_center[0] + math.cos(sat_ang) * self.orbit_r, self.disco_center[1] + math.sin(sat_ang) * self.orbit_r
            
            # ─── ATUALIZAÇÃO 3: Opacidade da linha de conexão do satélite (de 40 para 15) ───
            pygame.draw.line(self.screen, (*el["dim"], 15), self.disco_center, (sx, sy), 1)
            
            self.screen.blit(sat["surf"], (sx - SAT_CX, sy - SAT_CY))
            
            if self.hovered_sat and self.hovered_sat[0] == i:
                node_idx = self.hovered_sat[1]
                nang = -math.pi/2 + node_idx * (math.tau / 8)
                pygame.draw.circle(self.screen, WHITE, (int(sx + math.cos(nang) * SAT_R), int(sy + math.sin(nang) * SAT_R)), 8, 1)
                
            has_curve = any(l.get("is_curved", False) for l in sat["linhas"])
            
            # ─── ATUALIZAÇÃO 1: Brilho para todos os satélites que têm pontos ───
            if len(sat["pontos"]) > 0:
                if has_curve:
                    factor_r, factor_g, factor_b = el["main"][0] / 255.0, el["main"][1] / 255.0, el["main"][2] / 255.0
                    aur_r = int((math.sin(time_ms * 0.002 + i) + 1) * 127 * factor_r)
                    aur_g = int((math.sin(time_ms * 0.003 + i + 2) + 1) * 127 * factor_g)
                    aur_b = int((math.sin(time_ms * 0.004 + i + 4) + 1) * 127 * factor_b)
                    
                    if self.active_element == "Neutro":
                        aur_r, aur_g, aur_b = int(180 + math.sin(time_ms*0.003)*50), int(140 + math.cos(time_ms*0.002)*40), 70
                    
                    pygame.draw.circle(self.screen, (aur_r, aur_g, aur_b), (int(sx), int(sy)), SAT_R + 6, 2)
                    glow_surf = pygame.Surface((SAT_R*3, SAT_R*3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (aur_r, aur_g, aur_b, 60), (SAT_R*1.5, SAT_R*1.5), SAT_R + 12, 6)
                    self.screen.blit(glow_surf, (sx - SAT_R*1.5, sy - SAT_R*1.5))
                else:
                    pygame.draw.circle(self.screen, el["bright"], (int(sx), int(sy)), SAT_R + 6, 2)
                    glow_surf = pygame.Surface((SAT_R*3, SAT_R*3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*el["main"], 40), (SAT_R*1.5, SAT_R*1.5), SAT_R + 8, 4)
                    self.screen.blit(glow_surf, (sx - SAT_R*1.5, sy - SAT_R*1.5))

        self.screen.blit(self.disco_surf, self.disco_topleft)

        if self.hovered_main_node is not None:
            angle = -math.pi/2 + self.hovered_main_node * (math.tau / 24)
            nx, ny = self.disco_topleft[0] + DISCO_CX + math.cos(angle) * DISCO_R, self.disco_topleft[1] + DISCO_CY + math.sin(angle) * DISCO_R
            pygame.draw.circle(self.screen, el["bright"], (int(nx), int(ny)), 10, 2)
            pygame.draw.circle(self.screen, WHITE, (int(nx), int(ny)), 14, 1)
            deg_text = self.fnt_tiny.render(f"{self.hovered_main_node * 15}°", True, el["bright"])
            self.screen.blit(deg_text, deg_text.get_rect(center=(int(nx + math.cos(angle) * 28), int(ny + math.sin(angle) * 28))))

        # Paletas
        for key, rect in self.paleta_rects.items():
            pel = ELEMENTOS[key]
            hover = rect.collidepoint(self.mouse_pos) and not self.drag_element
            r_size = 22 if hover else 20
            pygame.gfxdraw.filled_circle(self.screen, rect.centerx, rect.centery, r_size, (*pel["bg"], 255))
            pygame.draw.circle(self.screen, pel["bright"] if hover else pel["main"], rect.center, r_size, 2)
            if self.icons.get(key): self.screen.blit(self.icons[key], self.icons[key].get_rect(center=rect.center))
            else:
                rs = self.fnt_rune.render(pel["rune"], True, pel["bright"] if hover else pel["main"])
                self.screen.blit(rs, rs.get_rect(center=rect.center))

        lbl_giz = self.fnt_tiny.render("Cor do Giz", True, GOLD_DIM)
        self.screen.blit(lbl_giz, (self.WIN_W - 95, self.HEADER_H + 25))
        
        texto_traco = f"Ferramenta: {self.tool_mode}"
        self._draw_button(self.btn_tool_mode, texto_traco, self.hover_btn_tool, False, (50, 40, 80))

        for key, rect in self.chalk_rects.items():
            color, hover, selected = CHALK_COLORS[key], rect.collidepoint(self.mouse_pos), (self.active_chalk == key)
            r_size = 20 if selected else (18 if hover else 15)
            pygame.gfxdraw.filled_circle(self.screen, rect.centerx, rect.centery, r_size, (*color, 255))
            pygame.draw.circle(self.screen, WHITE if selected else GOLD_DIM, rect.center, r_size, 2)

        hints = [("LMB", "Marcar"), ("SHIFT+LMB", "Curvar Modificador"), ("RMB", "Limpar Centro")]
        hx, hint_y, esp = self.disco_center[0] - 180, self.disco_center[1] + self.orbit_r + SAT_R + 10, 25
        for k, v in hints:
            ks, vs = self.fnt_tiny.render(f"[{k}]", True, GOLD), self.fnt_tiny.render(f" {v}", True, GOLD_DIM)
            self.screen.blit(ks, (hx, hint_y)); hx += ks.get_width()
            self.screen.blit(vs, (hx, hint_y)); hx += vs.get_width() + esp

        self._draw_button(self.btn_conjure, "Conjurar!", self.hover_btn_conjure, True)
        self._draw_button(self.btn_clear, "Limpar", self.hover_btn_clear, False)
        self._draw_button(self.btn_orbit, "Parar Órbita" if self.orbiting else "Girar Órbita", self.hover_btn_orbit, False, (100, 100, 150))
        self._draw_result()

    def _draw_button(self, rect, text, hover, primary, custom_color=None):
        if custom_color:
            c1 = custom_color
            c2 = (min(255, c1[0]+40), min(255, c1[1]+40), min(255, c1[2]+40)) if hover else c1
            text_color, border = WHITE, c1
        else:
            c1 = (138, 92, 42) if primary else (80, 15, 15)
            c2 = (180, 120, 30) if hover and primary else ((120, 25, 25) if hover else c1)
            text_color, border = ((10, 6, 18), GOLD_DIM) if primary else ((255, 136, 136), (139, 26, 26))
            
        pygame.draw.rect(self.screen, c2, rect, border_radius=3)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=3)
        ts = self.fnt_btn.render(text, True, text_color)
        self.screen.blit(ts, (rect.centerx - ts.get_width()//2, rect.centery - ts.get_height()//2))

    def _draw_result(self):
        r = self.result_rect
        pygame.draw.rect(self.screen, (0, 0, 0, 100), r, border_radius=5)
        pygame.draw.rect(self.screen, (*ELEMENTOS[self.active_element]["main"], 60), r, 1, border_radius=5)
        
        if self.result_error:
            et = self.fnt_body.render(self.result_error, True, (255, 96, 96))
            self.screen.blit(et, (r.centerx - et.get_width()//2, r.y + 14))
        elif self.result_spell:
            sp = self.fnt_spell.render(self.result_spell, True, ELEMENTOS[self.active_element]["bright"])
            self.screen.blit(sp, (r.centerx - sp.get_width()//2, r.y + 25))
            
            stats = self.result_stats
            lbls = [("Cruzamentos", str(stats["cruzamentos"])), ("Geometria", stats["geometria"]), ("Caos", stats["caos"])]
            for i, (lbl, val) in enumerate(lbls):
                cx2 = r.x + (r.width // 3) * i + (r.width // 6)
                self.screen.blit(self.fnt_tiny.render(lbl.upper(), True, GOLD_DIM), (cx2 - 30, r.y + 60))
                self.screen.blit(self.fnt_label.render(val, True, GOLD_BRIGHT), (cx2 - 20, r.y + 75))

    def _draw_footer(self):
        pygame.draw.line(self.screen, (*GOLD, 30), (0, self.rect_footer.y), (self.rect_footer.right, self.rect_footer.y))

    def _draw_particles(self):
        for p in self.particles: p.draw(self.screen)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if not self.handle_event(event): running = False
            self.update(dt)
            self.draw()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    app = ForjaArcana()
    app.run()