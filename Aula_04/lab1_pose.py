"""
Exercício 1 — Validador de Pose em Malha Aberta (Cinemática Diferencial)
Calcula e simula a nova Pose (x, y, θ) de um robô diferencial após uma
sequência de comandos de velocidade temporizados.
"""

import pygame
import math
import sys

# ──────────────────────────────────────────────
# 1. CÁLCULO TEÓRICO DA POSE FINAL
# ──────────────────────────────────────────────

def calcular_pose_teorica():
    """
    Integra analiticamente cada trecho e retorna a pose final (x, y, theta).
    Para ω = 0  →  movimento retilíneo:  x += v·t·cos(θ), y += v·t·sin(θ)
    Para v = 0  →  rotação pura:         θ += ω·t
    """
    x, y, theta = 0.0, 0.0, 0.0

    # Trecho 1: v=0.5 m/s, ω=0.0, t=4.0 s
    v1, w1, t1 = 0.5, 0.0, 4.0
    x += v1 * t1 * math.cos(theta)
    y += v1 * t1 * math.sin(theta)
    theta += w1 * t1

    # Trecho 2: v=0.0 m/s, ω=π/4 rad/s, t=2.0 s
    v2, w2, t2 = 0.0, math.pi / 4, 2.0
    x += v2 * t2 * math.cos(theta)
    y += v2 * t2 * math.sin(theta)
    theta += w2 * t2

    # Trecho 3: v=0.4 m/s, ω=0.0, t=3.0 s
    v3, w3, t3 = 0.4, 0.0, 3.0
    x += v3 * t3 * math.cos(theta)
    y += v3 * t3 * math.sin(theta)
    theta += w3 * t3

    return x, y, theta

pose_teorica = calcular_pose_teorica()
print("=" * 50)
print("  POSE TEÓRICA CALCULADA (Cinemática Diferencial)")
print("=" * 50)
print(f"  x     = {pose_teorica[0]:.4f} m")
print(f"  y     = {pose_teorica[1]:.4f} m")
print(f"  theta = {math.degrees(pose_teorica[2]):.4f}° ({pose_teorica[2]:.4f} rad)")
print("=" * 50)

# ──────────────────────────────────────────────
# 2. SIMULAÇÃO EM PYGAME
# ──────────────────────────────────────────────

# Escala: 1 metro = SCALE pixels
SCALE = 80          # px/m
WIDTH, HEIGHT = 900, 700
FPS = 60
DT = 1.0 / FPS      # passo de simulação (s)

# Origem na tela (centro-esquerdo)
ORIGIN_X = 100
ORIGIN_Y = HEIGHT // 2

# Cores
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (200, 200, 200)
BLUE       = (30,  100, 220)
RED        = (220, 50,  50)
GREEN      = (50,  180, 50)
ORANGE     = (255, 160, 0)
TRAIL_COL  = (100, 160, 255)

# Sequência de trechos: (v m/s, ω rad/s, duração s)
TRECHOS = [
    (0.5, 0.0,            4.0),
    (0.0, math.pi / 4,    2.0),
    (0.4, 0.0,            3.0),
]

def world_to_screen(x, y):
    """Converte coordenadas do mundo (m) para pixels na tela."""
    sx = int(ORIGIN_X + x * SCALE)
    sy = int(ORIGIN_Y - y * SCALE)   # eixo y invertido
    return sx, sy

def desenha_robo(surface, x, y, theta, color=BLUE):
    cx, cy = world_to_screen(x, y)
    r = 14
    pygame.draw.circle(surface, color, (cx, cy), r)
    ex = cx + int(r * math.cos(theta))
    ey = cy - int(r * math.sin(theta))
    pygame.draw.line(surface, WHITE, (cx, cy), (ex, ey), 3)

def desenha_grade(surface):
    for gx in range(0, WIDTH, SCALE):
        pygame.draw.line(surface, GRAY, (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, SCALE):
        pygame.draw.line(surface, GRAY, (0, gy), (WIDTH, gy), 1)
    # Eixos
    pygame.draw.line(surface, (180, 180, 180), (0, ORIGIN_Y), (WIDTH, ORIGIN_Y), 2)
    pygame.draw.line(surface, (180, 180, 180), (ORIGIN_X, 0), (ORIGIN_X, HEIGHT), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab 1 — Pose em Malha Aberta")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("consolas", 16)
    font_big = pygame.font.SysFont("consolas", 18, bold=True)

    # Estado do robô
    x, y, theta = 0.0, 0.0, 0.0
    trail = [(x, y)]

    trecho_idx   = 0
    tempo_trecho = 0.0
    simulando    = True
    finalizado   = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reiniciar
                x, y, theta = 0.0, 0.0, 0.0
                trail = [(x, y)]
                trecho_idx   = 0
                tempo_trecho = 0.0
                simulando    = True
                finalizado   = False

        # ── Atualização física ──
        if simulando and trecho_idx < len(TRECHOS):
            v, w, dur = TRECHOS[trecho_idx]

            # Integração por Euler
            x     += v * DT * math.cos(theta)
            y     += v * DT * math.sin(theta)
            theta += w * DT
            tempo_trecho += DT
            trail.append((x, y))

            if tempo_trecho >= dur:
                trecho_idx  += 1
                tempo_trecho = 0.0

        elif simulando and trecho_idx >= len(TRECHOS):
            simulando  = False
            finalizado = True
            print("\n" + "=" * 50)
            print("  POSE SIMULADA (Euler, dt = {:.4f} s)".format(DT))
            print("=" * 50)
            print(f"  x     = {x:.4f} m")
            print(f"  y     = {y:.4f} m")
            print(f"  theta = {math.degrees(theta):.4f}° ({theta:.4f} rad)")
            print("=" * 50)

        # ── Renderização ──
        screen.fill(WHITE)
        desenha_grade(screen)

        # Trilha
        if len(trail) > 1:
            pts = [world_to_screen(px, py) for px, py in trail]
            pygame.draw.lines(screen, TRAIL_COL, False, pts, 2)

        # Robô
        cor = GREEN if finalizado else BLUE
        desenha_robo(screen, x, y, theta, cor)

        # Origem
        ox, oy = world_to_screen(0, 0)
        pygame.draw.circle(screen, RED, (ox, oy), 6)

        # Pose teórica (alvo)
        tx, ty, tt = pose_teorica
        tsx, tsy = world_to_screen(tx, ty)
        pygame.draw.circle(screen, ORANGE, (tsx, tsy), 8, 2)
        screen.blit(font.render("Alvo teórico", True, ORANGE), (tsx + 10, tsy - 8))

        # HUD
        trecho_label = f"Trecho: {trecho_idx + 1}/{len(TRECHOS)}" if not finalizado else "Concluído!"
        v_cur = TRECHOS[min(trecho_idx, len(TRECHOS)-1)][0]
        w_cur = TRECHOS[min(trecho_idx, len(TRECHOS)-1)][1]

        hud = [
            ("POSE SIMULADA",           None),
            (f"  x     = {x:.3f} m",    BLUE),
            (f"  y     = {y:.3f} m",    BLUE),
            (f"  θ     = {math.degrees(theta):.1f}°", BLUE),
            ("",                         None),
            ("POSE TEÓRICA",             None),
            (f"  x     = {pose_teorica[0]:.3f} m",  ORANGE),
            (f"  y     = {pose_teorica[1]:.3f} m",  ORANGE),
            (f"  θ     = {math.degrees(pose_teorica[2]):.1f}°", ORANGE),
            ("",                         None),
            (trecho_label,               GREEN if finalizado else RED),
            (f"  v = {v_cur:.2f} m/s",  BLACK),
            (f"  ω = {w_cur:.4f} rad/s", BLACK),
            ("",                         None),
            ("[R] Reiniciar",            (120, 120, 120)),
        ]

        pygame.draw.rect(screen, (240, 240, 240), (WIDTH - 220, 10, 210, 270))
        pygame.draw.rect(screen, BLACK,            (WIDTH - 220, 10, 210, 270), 1)
        for i, (txt, col) in enumerate(hud):
            c = col if col else BLACK
            screen.blit(font.render(txt, True, c), (WIDTH - 215, 18 + i * 17))

        title = font_big.render("Lab 1 — Validador de Pose (Malha Aberta)", True, BLACK)
        screen.blit(title, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
