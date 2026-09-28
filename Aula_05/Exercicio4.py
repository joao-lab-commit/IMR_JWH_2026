import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):

    theta_alvo = math.atan2(
        y_alvo - y,
        x_alvo - x
    )


    e_theta = theta_alvo - theta


    while e_theta > math.pi:
        e_theta -= 2 * math.pi

    while e_theta < -math.pi:
        e_theta += 2 * math.pi


    omega = Kp * e_theta

    return omega
print("\n===== EXERCÍCIO 4 =====")

omega = calcular_orientacao_alvo(
    0, 0, 0,
    1, 1
)

print("Omega:", omega)