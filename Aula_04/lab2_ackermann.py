"""
Exercício 2 — Calculadora de Giro Ackermann vs. Diferencial
Compara visualmente e matematicamente o raio de curvatura de uma tração
Ackermann em relação ao modelo Diferencial.

Controles:
  SETA CIMA / SETA BAIXO   →  aumenta / diminui velocidade linear v
  SETA DIREITA / ESQUERDA  →  aumenta / diminui ângulo de esterço φ
  ESPAÇO                   →  pausa / retoma simulação
  R                        →  reinicia posição do robô
"""

import pygame
import math
import sys

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 700
FPS  = 60
DT   = 1.0 / FPS

# Modelo Ackermann
L    = 2.0          # entre-eixos (m)
PHI_MAX = math.radians(30)   # ±30°

# Escala visual
SCALE = 40          # px/m

# Origem
OX, OY = WIDTH // 2, HEIGHT // 2

# Cores
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (210, 210, 210)
DARK_GRAY  = (130, 130, 130)
BLUE       = (30,  100, 220)
RED        = (210, 50,  50)
GREEN      = (50,  180, 50)
ORANGE     = (255, 160, 0)
CYAN       = (0,   200, 200)
TRAIL_ACK  = (255, 130, 30)
TRAIL_DIF  = (50,  120, 255)
BG_PANEL   = (245, 245, 245)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def w2s(x, y):
    """Mundo (m) → tela (px)."""
    return int(OX + x * SCALE), int(OY - y * SCALE)

def desenha_grade(surf):
    for gx in range(OX % SCALE, WIDTH, SCALE):
        pygame.draw.line(surf, GRAY, (gx, 0), (gx, HEIGHT))
    for gy in range(OY % SCALE, HEIGHT, SCALE):
        pygame.draw.line(surf, GRAY, (0, gy), (WIDTH, gy))
    pygame.draw.line(surf, DARK_GRAY, (0, OY), (WIDTH, OY), 2)
    pygame.draw.line(surf, DARK_GRAY, (OX, 0), (OX, HEIGHT), 2)

def desenha_robo(surf, x, y, theta, color, size=12):
    cx, cy = w2s(x, y)
    pygame.draw.circle(surf, color, (cx, cy), size)
    ex = cx + int(size * math.cos(theta))
    ey = cy - int(size * math.sin(theta))
    pygame.draw.line(surf, WHITE, (cx, cy), (ex, ey), 3)

def desenha_circulo_curvatura(surf, x, y, theta, R, color):
    """Desenha o círculo de curvatura (se R finito)."""
    if abs(R) > 500 or abs(R) < 0.01:
        return
    # Centro da curvatura: perpendicular à frente do robô
    cx_w = x - R * math.sin(theta)
    cy_w = y + R * math.cos(theta)
    csx, csy = w2s(cx_w, cy_w)
    r_px = int(abs(R) * SCALE)
    if r_px > 3000:
        return
    pygame.draw.circle(surf, color, (csx, csy), r_px, 1)

def omega_ackermann(v, phi):
    """ω = (v / L) · tan(φ)"""
    return (v / L) * math.tan(phi) if L != 0 else 0.0

def raio_ackermann(phi):
    """R = L / tan(φ)  (infinito quando φ→0)"""
    if abs(math.tan(phi)) < 1e-9:
        return float('inf')
    return L / math.tan(phi)

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab 2 — Ackermann vs. Diferencial")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("consolas", 15)
    font_b= pygame.font.SysFont("consolas", 17, bold=True)

    # Estado do robô Ackermann
    ax, ay, atheta = 0.0, 0.0, 0.0
    trail_ack = [(ax, ay)]

    # Estado do robô Diferencial (controlado pelos mesmos v, ω)
    dx, dy, dtheta = 0.0, -1.5, 0.0   # levemente deslocado para comparação
    trail_dif = [(dx, dy)]

    # Parâmetros de controle
    v   =  1.0          # m/s
    phi =  0.0          # rad (ângulo de esterço)
    v_step   = 0.1
    phi_step = math.radians(2)

    pausado = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    v = min(v + v_step, 5.0)
                if event.key == pygame.K_DOWN:
                    v = max(v - v_step, -5.0)
                if event.key == pygame.K_RIGHT:
                    phi = max(phi - phi_step, -PHI_MAX)
                if event.key == pygame.K_LEFT:
                    phi = min(phi + phi_step,  PHI_MAX)
                if event.key == pygame.K_SPACE:
                    pausado = not pausado
                if event.key == pygame.K_r:
                    ax, ay, atheta = 0.0, 0.0, 0.0
                    dx, dy, dtheta = 0.0, -1.5, 0.0
                    trail_ack = [(ax, ay)]
                    trail_dif = [(dx, dy)]

        # ── Física ──────────────────────────────
        if not pausado:
            w = omega_ackermann(v, phi)

            # Ackermann
            ax     += v * DT * math.cos(atheta)
            ay     += v * DT * math.sin(atheta)
            atheta += w * DT
            trail_ack.append((ax, ay))
            if len(trail_ack) > 4000:
                trail_ack.pop(0)

            # Diferencial (usa os mesmos v e ω — comportamento de referência)
            dx     += v * DT * math.cos(dtheta)
            dy     += v * DT * math.sin(dtheta)
            dtheta += w * DT
            trail_dif.append((dx, dy))
            if len(trail_dif) > 4000:
                trail_dif.pop(0)

        # ── Cálculos para exibição ────────────────
        w       = omega_ackermann(v, phi)
        R_ack   = raio_ackermann(phi)
        phi_deg = math.degrees(phi)

        # ── Renderização ─────────────────────────
        screen.fill(WHITE)
        desenha_grade(screen)

        # Círculos de curvatura
        desenha_circulo_curvatura(screen, ax, ay, atheta, R_ack, ORANGE)
        desenha_circulo_curvatura(screen, dx, dy, dtheta, R_ack, CYAN)

        # Trilhas
        if len(trail_ack) > 1:
            pts = [w2s(px, py) for px, py in trail_ack]
            pygame.draw.lines(screen, TRAIL_ACK, False, pts, 2)
        if len(trail_dif) > 1:
            pts = [w2s(px, py) for px, py in trail_dif]
            pygame.draw.lines(screen, TRAIL_DIF, False, pts, 2)

        # Robôs
        desenha_robo(screen, ax, ay, atheta, ORANGE)
        desenha_robo(screen, dx, dy, dtheta, BLUE)

        # ── Painel de informações ──────────────────
        panel_x = 10
        pygame.draw.rect(screen, BG_PANEL, (panel_x, 10, 310, 310))
        pygame.draw.rect(screen, BLACK,    (panel_x, 10, 310, 310), 1)

        r_str = f"{R_ack:.2f} m" if R_ack != float('inf') else "∞  (reta)"
        status = "PAUSADO" if pausado else "RODANDO"
        phi_max_deg = math.degrees(PHI_MAX)

        linhas = [
            ("── ACKERMANN ──────────────────", ORANGE),
            (f"  φ (esterço) = {phi_deg:+.1f}°  (máx ±{phi_max_deg:.0f}°)", BLACK),
            (f"  v           = {v:+.2f} m/s", BLACK),
            (f"  ω           = {w:+.4f} rad/s", BLACK),
            (f"  R curvatura = {r_str}", RED),
            ("", None),
            ("── DIFERENCIAL (ref.) ─────────", CYAN),
            (f"  Mesmo v e ω que Ackermann", BLACK),
            (f"  Pode fazer R → 0 (giro no eixo)", BLACK),
            ("", None),
            ("── DIFERENÇA ──────────────────", BLACK),
            ("  Ackermann: R mínimo = L/tan(φ_max)", BLACK),
            (f"  R_min = {L/math.tan(PHI_MAX):.3f} m  ≠  0", RED),
            ("", None),
            (f"  [{status}]", GREEN if not pausado else RED),
            ("  ↑↓ velocidade  ←→ esterço", DARK_GRAY),
            ("  ESPAÇO pausa  R reinicia", DARK_GRAY),
        ]
        for i, (txt, col) in enumerate(linhas):
            c = col if col else BLACK
            screen.blit(font.render(txt, True, c), (panel_x + 5, 18 + i * 17))

        # Legenda de cores
        pygame.draw.circle(screen, ORANGE, (panel_x + 15, 320), 8)
        screen.blit(font.render("Ackermann", True, BLACK), (panel_x + 28, 313))
        pygame.draw.circle(screen, BLUE, (panel_x + 130, 320), 8)
        screen.blit(font.render("Diferencial", True, BLACK), (panel_x + 143, 313))

        title = font_b.render("Lab 2 — Ackermann vs. Diferencial", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 8))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
