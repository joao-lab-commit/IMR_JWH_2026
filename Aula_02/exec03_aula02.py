import pygame
import math
import numpy as np


# ==========================================
# CONSTANTES
# ==========================================

LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 60

COR_FUNDO = (30, 30, 30)
COR_ROBO = (0, 180, 255)
COR_DIRECAO = (255, 50, 50)
COR_TRAJETORIA = (100, 200, 100)

COR_ALVO = (255, 200, 0)
COR_TOLERANCIA = (255, 200, 0)


# ==========================================
# PARÂMETROS DO CONTROLADOR
# ==========================================

# Velocidade linear máxima
VELOCIDADE_LINEAR = 80.0

# Ganho proporcional angular
KP = 2.0

# Velocidade angular máxima
OMEGA_MAX = 4.0

# Tolerância solicitada no exercício
TOLERANCIA = 10.0


# ==========================================
# ROBÔ DIFERENCIAL
# ==========================================

class DiffDriveRobot:

    def __init__(
        self,
        x,
        y,
        theta=0.0,
        wheelbase=30.0,
        radius=15.0
    ):

        # --------------------------------------
        # Estado
        # --------------------------------------

        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

        # --------------------------------------
        # Parâmetros físicos
        # --------------------------------------

        self.L = float(wheelbase)
        self.radius = float(radius)

        # --------------------------------------
        # Velocidades
        # --------------------------------------

        self.v = 0.0
        self.omega = 0.0

        # --------------------------------------
        # Histórico
        # --------------------------------------

        self.history = []


    # ==========================================
    # COMANDO DE VELOCIDADE
    # ==========================================

    def set_direct_velocity(self, v, omega):

        self.v = v
        self.omega = omega


    # ==========================================
    # ATUALIZAÇÃO
    # ==========================================

    def update(self, dt):

        # Atualiza orientação
        self.theta += self.omega * dt

        # Normaliza theta entre -pi e pi
        self.theta = (
            self.theta + math.pi
        ) % (2 * math.pi) - math.pi

        # Atualiza posição
        self.x += (
            self.v
            * math.cos(self.theta)
            * dt
        )

        self.y += (
            self.v
            * math.sin(self.theta)
            * dt
        )

        # Guarda trajetória
        if (
            len(self.history) == 0
            or np.hypot(
                self.x - self.history[-1][0],
                self.y - self.history[-1][1]
            ) > 5
        ):

            self.history.append(
                (self.x, self.y)
            )

            if len(self.history) > 1000:
                self.history.pop(0)


    # ==========================================
    # DESENHO
    # ==========================================

    def draw(self, surface):

        # --------------------------------------
        # Rastro
        # --------------------------------------

        if len(self.history) > 1:

            pygame.draw.lines(
                surface,
                COR_TRAJETORIA,
                False,
                self.history,
                2
            )

        # --------------------------------------
        # Corpo
        # --------------------------------------

        pos = (
            int(self.x),
            int(self.y)
        )

        pygame.draw.circle(
            surface,
            COR_ROBO,
            pos,
            int(self.radius)
        )

        # --------------------------------------
        # Direção
        # --------------------------------------

        frente_x = (
            self.x
            + (self.radius + 10)
            * math.cos(self.theta)
        )

        frente_y = (
            self.y
            + (self.radius + 10)
            * math.sin(self.theta)
        )

        pygame.draw.line(
            surface,
            COR_DIRECAO,
            pos,
            (
                int(frente_x),
                int(frente_y)
            ),
            3
        )


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    pygame.init()

    # --------------------------------------
    # Janela
    # --------------------------------------

    screen = pygame.display.set_mode(
        (
            LARGURA_TELA,
            ALTURA_TELA
        )
    )

    pygame.display.set_caption(
        "Exercicio 3 - Controle Proporcional"
    )

    clock = pygame.time.Clock()

    # --------------------------------------
    # Fonte
    # --------------------------------------

    font = pygame.font.SysFont(
        "monospace",
        14
    )


    # ======================================
    # CRIAÇÃO DO ROBÔ
    # ======================================

    robot = DiffDriveRobot(
        x=LARGURA_TELA // 2,
        y=ALTURA_TELA // 2,
        theta=0.0
    )


    # ======================================
    # VARIÁVEIS DO ALVO
    # ======================================

    alvo = None

    chegou = False

    distancia = 0.0

    erro_theta = 0.0


    # ======================================
    # LOOP PRINCIPAL
    # ======================================

    running = True

    while running:

        # --------------------------------------
        # Delta time
        # --------------------------------------

        dt = clock.tick(FPS) / 1000.0


        # ======================================
        # EVENTOS
        # ======================================

        for event in pygame.event.get():

            # ----------------------------------
            # Fechar janela
            # ----------------------------------

            if event.type == pygame.QUIT:

                running = False


            # ----------------------------------
            # Clique do mouse
            # ----------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    # Define novo alvo
                    alvo = event.pos

                    # O robô ainda não chegou
                    chegou = False

                    # Reinicia trajetória
                    robot.history = [
                        (robot.x, robot.y)
                    ]


        # ======================================
        # CONTROLE PROPORCIONAL
        # ======================================

        if alvo is not None and not chegou:

            alvo_x = alvo[0]
            alvo_y = alvo[1]


            # ==================================
            # DISTÂNCIA ATÉ O ALVO
            # ==================================

            dx = alvo_x - robot.x
            dy = alvo_y - robot.y

            distancia = math.hypot(
                dx,
                dy
            )


            # ==================================
            # VERIFICA SE CHEGOU
            # ==================================

            if distancia < TOLERANCIA:

                # --------------------------------
                # PARAR
                # --------------------------------

                robot.set_direct_velocity(
                    0.0,
                    0.0
                )

                chegou = True


            else:

                # ==================================
                # ÂNGULO DO ALVO
                # ==================================

                theta_alvo = math.atan2(
                    dy,
                    dx
                )


                # ==================================
                # ERRO ANGULAR
                # ==================================

                erro_theta = (
                    theta_alvo
                    - robot.theta
                )


                # Normaliza entre -pi e pi
                erro_theta = (
                    erro_theta + math.pi
                ) % (2 * math.pi) - math.pi


                # ==================================
                # CONTROLADOR PROPORCIONAL
                # ==================================

                omega = (
                    KP
                    * erro_theta
                )


                # ==================================
                # LIMITA VELOCIDADE ANGULAR
                # ==================================

                omega = max(
                    -OMEGA_MAX,
                    min(
                        omega,
                        OMEGA_MAX
                    )
                )


                # ==================================
                # VELOCIDADE LINEAR
                # ==================================

                v = VELOCIDADE_LINEAR


                # ==================================
                # SE ESTIVER PERTO DO ALVO
                # ==================================

                if distancia < 50:

                    v = 30.0


                # ==================================
                # SE ESTIVER MUITO DESALINHADO
                # ==================================

                if abs(erro_theta) > math.radians(60):

                    # Primeiro gira
                    v = 0.0


                # ==================================
                # ENVIA COMANDO
                # ==================================

                robot.set_direct_velocity(
                    v,
                    omega
                )


        else:

            # ==================================
            # SEM ALVO OU JÁ CHEGOU
            # ==================================

            robot.set_direct_velocity(
                0.0,
                0.0
            )


        # ======================================
        # ATUALIZA ROBÔ
        # ======================================

        robot.update(dt)


        # ======================================
        # RENDERIZAÇÃO
        # ======================================

        screen.fill(COR_FUNDO)


        # ======================================
        # DESENHA ALVO
        # ======================================

        if alvo is not None:

            # ----------------------------------
            # Círculo de tolerância
            # ----------------------------------

            pygame.draw.circle(
                screen,
                COR_TOLERANCIA,
                alvo,
                int(TOLERANCIA),
                1
            )

            # ----------------------------------
            # Ponto central
            # ----------------------------------

            pygame.draw.circle(
                screen,
                COR_ALVO,
                alvo,
                6
            )

            # ----------------------------------
            # Linha até o alvo
            # ----------------------------------

            pygame.draw.line(
                screen,
                COR_ALVO,
                (
                    int(robot.x),
                    int(robot.y)
                ),
                alvo,
                1
            )


        # ======================================
        # DESENHA ROBÔ
        # ======================================

        robot.draw(screen)


        # ======================================
        # STATUS
        # ======================================

        if alvo is None:

            status = "Aguardando alvo"

        elif chegou:

            status = "ALVO ALCANCADO"

        else:

            status = "Indo para o alvo"


        # ======================================
        # TELEMETRIA
        # ======================================

        info_txt = [

            f"Status: {status}",

            f"X: {robot.x:.1f} px",

            f"Y: {robot.y:.1f} px",

            f"Theta: "
            f"{math.degrees(robot.theta):.1f} graus",

            f"v = "
            f"{robot.v:.1f} px/s",

            f"omega = "
            f"{robot.omega:.2f} rad/s",

            f"Distancia ao alvo = "
            f"{distancia:.2f} px",

            f"Erro angular = "
            f"{math.degrees(erro_theta):.2f} graus",

            "",

            f"KP = {KP:.2f}",

            f"Tolerancia = "
            f"{TOLERANCIA:.1f} px",

            "",

            "Clique esquerdo = novo alvo"

        ]


        # ======================================
        # MOSTRA TELEMETRIA
        # ======================================

        for i, txt in enumerate(info_txt):

            rendered = font.render(
                txt,
                True,
                (220, 220, 220)
            )

            screen.blit(
                rendered,
                (
                    15,
                    15 + i * 19
                )
            )


        # ======================================
        # ATUALIZA TELA
        # ======================================

        pygame.display.flip()


    # ======================================
    # FINALIZA
    # ======================================

    pygame.quit()


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    main()
