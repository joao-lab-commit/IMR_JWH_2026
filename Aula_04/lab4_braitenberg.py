"""
Exercício 4 — Braitenberg com Conexões Diretas (Atração / Agressão)
Conexão DIRETA (não cruzada):
  vL = v0 + α · (1 - d_esq / d_max)
  vR = v0 + α · (1 - d_dir / d_max)

Comportamento esperado: ao detectar obstáculo à direita, vR aumenta →
robô vira EM DIREÇÃO ao obstáculo (agressão/atração).
"""

import pygame
import math
import sys

# ──────────────────────────────────────────────
WIDTH, HEIGHT = 900, 700
FPS   = 60
DT    = 1.0 / FPS

# Parâmetros Braitenberg
V0    = 60.0    # velocidade base (px/s)
ALPHA = 80.0    # ganho de atração
D_MAX = 200.0   # alcance do sensor (px)

# Geometria do robô diferencial
WHEEL_BASE = 30.0   # distância entre rodas (px)
ROBOT_R    = 14     # raio visual (px)

# Cores
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
GRAY      = (180, 180, 180)
DARK      = (60,  60,  60)
BLUE      = (50,  100, 220)
RED       = (220, 50,  50)
GREEN     = (50,  200, 80)
ORANGE    = (255, 160, 0)
YELLOW    = (240, 220, 0)
WALL_COL  = (100, 100, 140)
OBS_COL   = (200, 80,  80)
TRAIL_COL = (100, 150, 255)
BG        = (30,  32,  40)


def cast_sensor(rx, ry, angle, obstacles, walls, max_d=D_MAX):
    step = 2.0
    d = 0.0
    while d < max_d:
        px = rx + d * math.cos(angle)
        py = ry + d * math.sin(angle)
        for obj in obstacles + walls:
            ox, oy, ow, oh = obj
            if ox <= px <= ox + ow and oy <= py <= oy + oh:
                return d
        d += step
    return max_d


def braitenberg_direto(d_esq, d_dir, v0=V0, alpha=ALPHA, d_max=D_MAX):
    """
    Conexão direta: sensor esquerdo → roda esquerda, sensor direito → roda direita.
    Obstáculo perto → roda desse lado acelera → robô gira em direção ao obstáculo.
    """
    vL = v0 + alpha * (1.0 - d_esq / d_max)
    vR = v0 + alpha * (1.0 - d_dir / d_max)
    return vL, vR


def update_pose(x, y, theta, vL, vR, wb=WHEEL_BASE, dt=DT):
    v = (vL + vR) / 2.0
    w = (vR - vL) / wb
    x     += v * dt * math.cos(theta)
    y     += v * dt * math.sin(theta)
    theta += w * dt
    return x, y, theta


def draw_robot(surf, x, y, theta, color=BLUE):
    cx, cy = int(x), int(y)
    pygame.draw.circle(surf, color, (cx, cy), ROBOT_R)
    ex = cx + int(ROBOT_R * math.cos(theta))
    ey = cy + int(ROBOT_R * math.sin(theta))
    pygame.draw.line(surf, WHITE, (cx, cy), (ex, ey), 3)

    # Rodas
    lx = cx + int(ROBOT_R * math.cos(theta + math.pi / 2))
    ly = cy + int(ROBOT_R * math.sin(theta + math.pi / 2))
    rx = cx + int(ROBOT_R * math.cos(theta - math.pi / 2))
    ry = cy + int(ROBOT_R * math.sin(theta - math.pi / 2))
    pygame.draw.circle(surf, ORANGE, (lx, ly), 5)
    pygame.draw.circle(surf, GREEN,  (rx, ry), 5)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab 4 — Braitenberg Direto (Atração)")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("consolas", 14)
    font_b= pygame.font.SysFont("consolas", 16, bold=True)

    # Paredes (bordas)
    walls = [
        (0, 0, WIDTH, 10),
        (0, HEIGHT - 10, WIDTH, 10),
        (0, 0, 10, HEIGHT),
        (WIDTH - 10, 0, 10, HEIGHT),
    ]

    # Obstáculos móveis / fixos
    obstacles = [
        (480, 280, 60, 80),
        (250, 400, 70, 60),
        (600, 150, 50, 100),
        (150, 200, 80, 50),
    ]

    # Robô
    rx, ry    = 100.0, HEIGHT / 2
    r_theta   = 0.0
    trail     = []
    auto_mode = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rx, ry, r_theta = 100.0, HEIGHT / 2, 0.0
                    trail = []
                if event.key == pygame.K_m:
                    auto_mode = not auto_mode

        # ── Sensores (ângulos relativos ao robô) ──
        # Esquerda: +90°, Direita: -90°
        ang_esq = r_theta + math.pi / 2
        ang_dir = r_theta - math.pi / 2

        d_esq = cast_sensor(rx, ry, ang_esq, obstacles, walls)
        d_dir = cast_sensor(rx, ry, ang_dir, obstacles, walls)

        # Sensor frontal adicional (45° esq e dir)
        d_f_esq = cast_sensor(rx, ry, r_theta + math.pi / 4, obstacles, walls)
        d_f_dir = cast_sensor(rx, ry, r_theta - math.pi / 4, obstacles, walls)

        # Braitenberg direto
        vL, vR = braitenberg_direto(d_esq, d_dir)

        # Atualiza pose
        rx, ry, r_theta = update_pose(rx, ry, r_theta, vL, vR)

        # Clamp nas bordas
        rx = max(20, min(WIDTH  - 20, rx))
        ry = max(20, min(HEIGHT - 20, ry))

        trail.append((int(rx), int(ry)))
        if len(trail) > 3000:
            trail.pop(0)

        # ── Renderização ─────────────────────────
        screen.fill(BG)

        # Paredes
        for wx, wy, ww, wh in walls:
            pygame.draw.rect(screen, DARK, (wx, wy, ww, wh))

        # Obstáculos
        for ox, oy, ow, oh in obstacles:
            pygame.draw.rect(screen, OBS_COL, (ox, oy, ow, oh))
            pygame.draw.rect(screen, RED,     (ox, oy, ow, oh), 2)

        # Trilha
        if len(trail) > 1:
            pygame.draw.lines(screen, TRAIL_COL, False, trail, 2)

        # Feixes sensoriais
        for ang, col, dist in [
            (ang_esq, ORANGE, d_esq),
            (ang_dir, GREEN,  d_dir),
            (r_theta + math.pi / 4, YELLOW, d_f_esq),
            (r_theta - math.pi / 4, YELLOW, d_f_dir),
        ]:
            ex = int(rx + dist * math.cos(ang))
            ey = int(ry + dist * math.sin(ang))
            pygame.draw.line(screen, col, (int(rx), int(ry)), (ex, ey), 1)
            pygame.draw.circle(screen, col, (ex, ey), 4)

        # Robô
        draw_robot(screen, rx, ry, r_theta)

        # ── HUD ──────────────────────────────────
        panel_x = WIDTH - 260
        pygame.draw.rect(screen, (45, 45, 60), (panel_x, 0, 260, HEIGHT))
        pygame.draw.line(screen, GRAY, (panel_x, 0), (panel_x, HEIGHT))

        hud = [
            ("BRAITENBERG DIRETO", WHITE),
            ("(Atração / Agressão)", ORANGE),
            ("", None),
            ("── Sensores ──────────────", GRAY),
            (f"  d_esq = {d_esq:>6.1f} px", ORANGE),
            (f"  d_dir = {d_dir:>6.1f} px", GREEN),
            ("", None),
            ("── Rodas ─────────────────", GRAY),
            (f"  vL = {vL:>6.1f} px/s", ORANGE),
            (f"  vR = {vR:>6.1f} px/s", GREEN),
            ("", None),
            ("── Comportamento ─────────", GRAY),
            ("  Obs à direita →", WHITE),
            ("  vR↑ → gira p/ obstáculo", RED),
            ("  (oposto ao medo/aversão)", GRAY),
            ("", None),
            ("── Legenda ───────────────", GRAY),
            ("  ● laranja = roda esq",    ORANGE),
            ("  ● verde   = roda dir",    GREEN),
            ("", None),
            ("  [R] reiniciar",           GRAY),
        ]
        for i, (txt, col) in enumerate(hud):
            c = col if col else WHITE
            screen.blit(font.render(txt, True, c), (panel_x + 8, 12 + i * 17))

        title = font_b.render("Lab 4 — Braitenberg Direto", True, WHITE)
        screen.blit(title, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
