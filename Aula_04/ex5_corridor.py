"""
Exercício 5 — Centralização Autônoma em Corredor (Controle Proporcional)
Dois feixes laterais a -90° e +90° medem d_esq e d_dir.
Erro:   e = d_esq - d_dir
Controle: ω = Kp · e
Velocidade linear constante: v = 40.0 px/s
"""

import pygame
import math
import sys

# ──────────────────────────────────────────────
WIDTH, HEIGHT   = 900, 700
FPS             = 60
DT              = 1.0 / FPS

# Controle proporcional
V_LINEAR = 40.0   # px/s  (velocidade constante)
KP       = 0.01   # ganho proporcional

# Corredor
CORRIDOR_TOP    = 150
CORRIDOR_BOTTOM = HEIGHT - 150
WALL_THICK      = 20

# Robô
WHEEL_BASE = 30.0
ROBOT_R    = 14

# Sensor
D_MAX = 300.0

# Cores
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
GRAY      = (180, 180, 180)
DARK      = (50,  50,  60)
BLUE      = (50,  100, 220)
RED       = (220, 50,  50)
GREEN     = (50,  200, 80)
ORANGE    = (255, 160, 0)
YELLOW    = (240, 220, 0)
WALL_COL  = (80,  90,  130)
TRAIL_COL = (80,  160, 255)
BG        = (35,  35,  45)
PANEL_BG  = (45,  45,  58)
CENTER_L  = (60,  60,  80)


def cast_lateral(rx, ry, angle, walls, max_d=D_MAX):
    step = 2.0
    d = 0.0
    while d < max_d:
        px = rx + d * math.cos(angle)
        py = ry + d * math.sin(angle)
        for wx, wy, ww, wh in walls:
            if wx <= px <= wx + ww and wy <= py <= wy + wh:
                return d
        d += step
    return max_d


def update_pose_diff(x, y, theta, v, omega, dt=DT):
    x     += v * dt * math.cos(theta)
    y     += v * dt * math.sin(theta)
    theta += omega * dt
    return x, y, theta


def draw_robot(surf, x, y, theta):
    cx, cy = int(x), int(y)
    pygame.draw.circle(surf, BLUE, (cx, cy), ROBOT_R)
    ex = cx + int(ROBOT_R * math.cos(theta))
    ey = cy + int(ROBOT_R * math.sin(theta))
    pygame.draw.line(surf, WHITE, (cx, cy), (ex, ey), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ex 5 — Corredor: Controle Proporcional")
    clock = pygame.time.Clock()
    font   = pygame.font.SysFont("consolas", 14)
    font_b = pygame.font.SysFont("consolas", 16, bold=True)
    font_s = pygame.font.SysFont("consolas", 12)

    # Paredes do corredor (horizontal)
    walls = [
        (0, CORRIDOR_TOP - WALL_THICK,    WIDTH, WALL_THICK),   # parede superior
        (0, CORRIDOR_BOTTOM,              WIDTH, WALL_THICK),   # parede inferior
    ]

    # Centro do corredor
    corridor_center_y = (CORRIDOR_TOP + CORRIDOR_BOTTOM) / 2

    # Robô — começa levemente desalinhado para mostrar a correção
    rx      = 80.0
    ry      = CORRIDOR_TOP + 60.0    # desalinhado: perto da parede de cima
    r_theta = math.radians(5)        # leve desvio angular
    trail   = []

    # Histórico de erro para gráfico
    error_hist = []
    MAX_HIST   = 400

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                rx      = 80.0
                ry      = CORRIDOR_TOP + 60.0
                r_theta = math.radians(5)
                trail   = []
                error_hist = []

        # ── Sensores laterais ────────────────────
        ang_esq = r_theta + math.pi / 2    # +90° relativo ao robô
        ang_dir = r_theta - math.pi / 2    # -90°

        d_esq = cast_lateral(rx, ry, ang_esq, walls)
        d_dir = cast_lateral(rx, ry, ang_dir, walls)

        # ── Controle proporcional ────────────────
        erro  = d_esq - d_dir
        omega = KP * erro

        error_hist.append(erro)
        if len(error_hist) > MAX_HIST:
            error_hist.pop(0)

        # ── Atualiza pose ────────────────────────
        rx, ry, r_theta = update_pose_diff(rx, ry, r_theta, V_LINEAR, omega)

        # Wrap horizontal (robô sai pela direita → volta pela esquerda)
        if rx > WIDTH + 20:
            rx = -20.0

        # Clamp vertical (segurança)
        ry = max(float(CORRIDOR_TOP + ROBOT_R + 2),
                 min(float(CORRIDOR_BOTTOM - ROBOT_R - 2), ry))

        trail.append((int(rx), int(ry)))
        if len(trail) > 5000:
            trail.pop(0)

        # ── Renderização ─────────────────────────
        screen.fill(BG)

        # Linha central do corredor (referência)
        pygame.draw.line(screen, CENTER_L,
                         (0, int(corridor_center_y)),
                         (WIDTH, int(corridor_center_y)), 1)

        # Paredes
        for wx, wy, ww, wh in walls:
            pygame.draw.rect(screen, WALL_COL, (wx, wy, ww, wh))
            pygame.draw.rect(screen, GRAY,     (wx, wy, ww, wh), 1)

        # Rótulos das paredes
        screen.blit(font_s.render("PAREDE SUPERIOR", True, GRAY),
                    (10, CORRIDOR_TOP - WALL_THICK + 3))
        screen.blit(font_s.render("PAREDE INFERIOR", True, GRAY),
                    (10, CORRIDOR_BOTTOM + 4))

        # Trilha
        if len(trail) > 1:
            pygame.draw.lines(screen, TRAIL_COL, False, trail, 2)

        # Feixes sensoriais
        for ang, col, dist in [
            (ang_esq, ORANGE, d_esq),
            (ang_dir, GREEN,  d_dir),
        ]:
            ex = int(rx + dist * math.cos(ang))
            ey = int(ry + dist * math.sin(ang))
            pygame.draw.line(screen, col, (int(rx), int(ry)), (ex, ey), 2)
            pygame.draw.circle(screen, col, (ex, ey), 5)

        # Robô
        draw_robot(screen, rx, ry)

        # ── Gráfico de erro ──────────────────────
        graph_x, graph_y = 10, HEIGHT - 120
        graph_w, graph_h = 380, 100
        pygame.draw.rect(screen, DARK, (graph_x, graph_y, graph_w, graph_h))
        pygame.draw.rect(screen, GRAY, (graph_x, graph_y, graph_w, graph_h), 1)
        # Linha zero
        mid_y = graph_y + graph_h // 2
        pygame.draw.line(screen, (80, 80, 100),
                         (graph_x, mid_y), (graph_x + graph_w, mid_y))
        screen.blit(font_s.render("Erro e = d_esq - d_dir", True, GRAY),
                    (graph_x + 5, graph_y + 3))

        if len(error_hist) > 1:
            scale_e = graph_h / 2 / max(1, max(abs(e) for e in error_hist))
            pts = []
            for j, e in enumerate(error_hist):
                ex_g = graph_x + int(j * graph_w / MAX_HIST)
                ey_g = mid_y   - int(e * scale_e)
                pts.append((ex_g, ey_g))
            if len(pts) > 1:
                pygame.draw.lines(screen, YELLOW, False, pts, 1)

        # ── Painel de info ───────────────────────
        panel_x = WIDTH - 250
        pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, 250, HEIGHT))
        pygame.draw.line(screen, GRAY, (panel_x, 0), (panel_x, HEIGHT))

        hud = [
            ("CORREDOR — CTRL P", WHITE),
            ("", None),
            ("── Sensores ──────────────", GRAY),
            (f"  d_esq = {d_esq:>6.1f} px", ORANGE),
            (f"  d_dir = {d_dir:>6.1f} px", GREEN),
            ("", None),
            ("── Controle ──────────────", GRAY),
            (f"  erro e = {erro:>+7.1f} px", YELLOW),
            (f"  ω = Kp · e", WHITE),
            (f"  Kp      = {KP}", WHITE),
            (f"  ω       = {KP*erro:>+6.3f} rad/s", RED if abs(erro) > 20 else GREEN),
            (f"  v       = {V_LINEAR:.1f} px/s", BLUE),
            ("", None),
            ("── Pose ──────────────────", GRAY),
            (f"  x     = {rx:>6.1f} px", WHITE),
            (f"  y     = {ry:>6.1f} px", WHITE),
            (f"  θ     = {math.degrees(r_theta):>+6.1f}°", WHITE),
            ("", None),
            ("── Centro do corredor ────", GRAY),
            (f"  y_c   = {corridor_center_y:.1f} px", GRAY),
            (f"  Δy    = {ry - corridor_center_y:>+6.1f} px",
             RED if abs(ry - corridor_center_y) > 20 else GREEN),
            ("", None),
            ("  [R] reiniciar",           GRAY),
        ]
        for i, (txt, col) in enumerate(hud):
            c = col if col else WHITE
            screen.blit(font.render(txt, True, c), (panel_x + 8, 12 + i * 17))

        title = font_b.render("Ex 5 — Centralização no Corredor", True, WHITE)
        screen.blit(title, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
