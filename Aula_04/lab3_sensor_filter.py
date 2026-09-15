"""
Exercício 3 — Varredura Sensorial com Filtro de Alcance e Desvio de Ruído
7 feixes de distância cobrindo 180° (-π/2 a +π/2).
Ruído gaussiano: d_ruido = d_real + N(0, 5.0)
Filtro de Limiar:
  < 10 px  → descartado (erro de leitura) → exibido como 0
  > 200 px → cravado em 200 px
"""

import pygame
import math
import sys
import numpy as np

# ──────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 650
FPS  = 30
NUM_FEIXES  = 7
FOV_START   = -math.pi / 2
FOV_END     =  math.pi / 2
D_MIN       = 10.0    # px — abaixo disso = erro
D_MAX       = 200.0   # px — acima disso = clampado
NOISE_STD   = 5.0     # desvio padrão do ruído gaussiano

# Cores
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (200, 200, 200)
DARK_GRAY  = (100, 100, 100)
BLUE       = (50,  120, 230)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
ORANGE     = (255, 160, 0)
YELLOW     = (240, 220, 0)
BG         = (30,  30,  40)
PANEL_BG   = (45,  45,  60)


def filtro_limiar(d):
    """Aplica filtro de limiar sobre a leitura com ruído."""
    if d < D_MIN:
        return None          # descartado
    if d > D_MAX:
        return D_MAX         # cravado
    return d


def cast_ray(rx, ry, angle, obstacles, max_dist=D_MAX):
    """
    Lança um raio a partir de (rx, ry) na direção 'angle' e retorna
    a distância até o obstáculo mais próximo (ou max_dist se livre).
    """
    step = 1.0
    for dist in np.arange(0, max_dist, step):
        px = rx + dist * math.cos(angle)
        py = ry + dist * math.sin(angle)
        for obs in obstacles:
            ox, oy, ow, oh = obs
            if ox <= px <= ox + ow and oy <= py <= oy + oh:
                return dist
    return max_dist


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab 3 — Filtro Sensorial")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("consolas", 14)
    font_b= pygame.font.SysFont("consolas", 16, bold=True)

    # Robô
    rx, ry    = WIDTH // 3, HEIGHT // 2
    r_theta   = 0.0   # orientação (rad)
    speed     = 2.0
    rot_speed = 0.03

    # Obstáculos (rect: x, y, w, h)
    obstacles = [
        (350, 200, 80, 200),
        (500, 150, 60, 160),
        (200, 380, 120, 50),
        (600, 320, 100, 80),
        (150, 150, 50, 120),
    ]

    # Bordas como obstáculos implícitos — tratadas no cast_ray via clamp
    border_rects = [
        (0, 0, WIDTH, 10),
        (0, HEIGHT - 10, WIDTH, 10),
        (0, 0, 10, HEIGHT),
        (WIDTH - 10, 0, 10, HEIGHT),
    ]
    all_obs = obstacles + border_rects

    # Ângulos dos feixes
    angles_rel = np.linspace(FOV_START, FOV_END, NUM_FEIXES)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            rx += speed * math.cos(r_theta)
            ry += speed * math.sin(r_theta)
        if keys[pygame.K_DOWN]:
            rx -= speed * math.cos(r_theta)
            ry -= speed * math.sin(r_theta)
        if keys[pygame.K_LEFT]:
            r_theta -= rot_speed
        if keys[pygame.K_RIGHT]:
            r_theta += rot_speed

        rx = max(20, min(WIDTH  - 20, rx))
        ry = max(20, min(HEIGHT - 20, ry))

        # ── Leituras sensoriais ──────────────────
        d_real   = []
        d_ruido  = []
        d_filtro = []

        for ang_rel in angles_rel:
            ang_abs = r_theta + ang_rel
            dist_real = cast_ray(rx, ry, ang_abs, all_obs, D_MAX)
            d_real.append(dist_real)

            noise = np.random.normal(0, NOISE_STD)
            dist_ruid = dist_real + noise
            d_ruido.append(dist_ruid)

            dist_filt = filtro_limiar(dist_ruid)
            d_filtro.append(dist_filt)

        # ── Renderização ─────────────────────────
        screen.fill(BG)

        # Bordas
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, 10))
        pygame.draw.rect(screen, DARK_GRAY, (0, HEIGHT - 10, WIDTH, 10))
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, 10, HEIGHT))
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH - 10, 0, 10, HEIGHT))

        # Obstáculos
        for ox, oy, ow, oh in obstacles:
            pygame.draw.rect(screen, (80, 80, 120), (ox, oy, ow, oh))
            pygame.draw.rect(screen, GRAY,           (ox, oy, ow, oh), 1)

        # Feixes
        for i, ang_rel in enumerate(angles_rel):
            ang_abs = r_theta + ang_rel

            # Feixe real (verde escuro, fino)
            ex_r = rx + d_real[i] * math.cos(ang_abs)
            ey_r = ry + d_real[i] * math.sin(ang_abs)
            pygame.draw.line(screen, (0, 120, 0), (int(rx), int(ry)), (int(ex_r), int(ey_r)), 1)

            # Feixe com ruído (amarelo)
            d_r = max(0, d_ruido[i])
            ex_n = rx + d_r * math.cos(ang_abs)
            ey_n = ry + d_r * math.sin(ang_abs)
            pygame.draw.line(screen, YELLOW, (int(rx), int(ry)), (int(ex_n), int(ey_n)), 1)

            # Feixe filtrado (verde brilhante) — só se não foi descartado
            if d_filtro[i] is not None:
                ex_f = rx + d_filtro[i] * math.cos(ang_abs)
                ey_f = ry + d_filtro[i] * math.sin(ang_abs)
                pygame.draw.line(screen, GREEN, (int(rx), int(ry)), (int(ex_f), int(ey_f)), 2)
                pygame.draw.circle(screen, GREEN, (int(ex_f), int(ey_f)), 4)
            else:
                # Ponto vermelho = leitura descartada
                pygame.draw.circle(screen, RED, (int(rx), int(ry)), 5)

        # Robô
        pygame.draw.circle(screen, BLUE, (int(rx), int(ry)), 12)
        ex = int(rx + 15 * math.cos(r_theta))
        ey = int(ry + 15 * math.sin(r_theta))
        pygame.draw.line(screen, WHITE, (int(rx), int(ry)), (ex, ey), 3)

        # ── Painel lateral ───────────────────────
        panel_x = WIDTH - 320
        pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, 320, HEIGHT))
        pygame.draw.line(screen, GRAY, (panel_x, 0), (panel_x, HEIGHT), 1)

        screen.blit(font_b.render("LEITURAS SENSORIAIS", True, WHITE), (panel_x + 10, 10))
        screen.blit(font.render(f"{'Feixe':>6} {'Real':>7} {'Ruído':>8} {'Filtro':>8}", True, GRAY),
                    (panel_x + 10, 34))
        pygame.draw.line(screen, GRAY, (panel_x + 10, 52), (panel_x + 300, 52), 1)

        for i in range(NUM_FEIXES):
            ang_deg = math.degrees(angles_rel[i])
            filt_str = f"{d_filtro[i]:>7.1f}" if d_filtro[i] is not None else "  ERRO "
            filt_col = GREEN if d_filtro[i] is not None else RED
            if d_filtro[i] == D_MAX:
                filt_col = ORANGE
                filt_str = f"{D_MAX:>7.1f}*"

            row = 58 + i * 38
            label = font_b.render(f"#{i+1} ({ang_deg:+.0f}°)", True, CYAN if False else WHITE)
            screen.blit(label, (panel_x + 10, row))

            vals = font.render(
                f"Real:{d_real[i]:>6.1f}  Ruído:{d_ruido[i]:>6.1f}",
                True, YELLOW
            )
            screen.blit(vals, (panel_x + 10, row + 18))

            filt_lbl = font.render(f"Filtro: {filt_str}", True, filt_col)
            screen.blit(filt_lbl, (panel_x + 160, row + 18))

        # Legenda
        ly = HEIGHT - 130
        pygame.draw.line(screen, GREEN,  (panel_x + 10, ly),      (panel_x + 40, ly),      2)
        screen.blit(font.render("Feixe filtrado",          True, GREEN),  (panel_x + 45, ly - 5))
        pygame.draw.line(screen, YELLOW, (panel_x + 10, ly + 20), (panel_x + 40, ly + 20), 1)
        screen.blit(font.render("Feixe com ruído",         True, YELLOW), (panel_x + 45, ly + 15))
        pygame.draw.line(screen, (0,120,0),(panel_x+10,ly+40),(panel_x+40,ly+40), 1)
        screen.blit(font.render("Feixe real",              True, (0,200,0)),(panel_x+45,ly+35))
        screen.blit(font.render("* = cravado em 200 px",   True, ORANGE),   (panel_x + 10, ly + 60))
        screen.blit(font.render("ERRO = descartado (<10)", True, RED),      (panel_x + 10, ly + 80))
        screen.blit(font.render("↑↓←→ mover robô",        True, GRAY),      (panel_x + 10, ly + 100))

        title = font_b.render("Lab 3 — Filtro Sensorial com Ruído Gaussiano", True, WHITE)
        screen.blit(title, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
