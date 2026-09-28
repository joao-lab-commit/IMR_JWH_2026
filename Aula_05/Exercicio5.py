import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):
    theta_alvo = math.atan2(y_alvo - y, x_alvo - x)

    e_theta = theta_alvo - theta

    while e_theta > math.pi:
        e_theta -= 2 * math.pi

    while e_theta < -math.pi:
        e_theta += 2 * math.pi

    omega = Kp * e_theta

    return omega


def controle_reativo(distancias):
    frente = distancias['frente']
    esquerda = distancias['esquerda']
    direita = distancias['direita']

    if frente < 0.4:
        v = 0.0

        if esquerda > direita:
            omega = 1.0
        else:
            omega = -1.0
    else:
        v = 0.5
        omega = esquerda - direita

    return v, omega


def maquina_de_estados(
    x, y, theta,
    x_alvo, y_alvo,
    dist_frente, dist_esq, dist_dir
):

    distancia_alvo = math.sqrt(
        (x_alvo - x) ** 2 +
        (y_alvo - y) ** 2
    )


    if distancia_alvo < 0.2:
        estado_atual = 'OBJETIVO_ALCANÇADO'
        v_cmd = 0.0
        omega_cmd = 0.0


    elif dist_frente < 0.5:
        estado_atual = 'DESVIAR_OBSTACULO'

        distancias = {
            'frente': dist_frente,
            'esquerda': dist_esq,
            'direita': dist_dir
        }

        v_cmd, omega_cmd = controle_reativo(distancias)


    else:
        estado_atual = 'IR_PARA_ALVO'

        v_cmd = 0.5
        omega_cmd = calcular_orientacao_alvo(
            x, y, theta,
            x_alvo, y_alvo
        )

    return estado_atual, v_cmd, omega_cmd


# Teste
estado, v, omega = maquina_de_estados(
    0, 0, 0,
    2, 2,
    1.0, 2.0, 2.0
)
print("\n===== EXERCÍCIO 5 =====")
print("Estado:", estado)
print("Velocidade linear:", v)
print("Velocidade angular:", omega)
