def converter_cmd_vel(v, omega, L=0.3, max_wheel_speed=1.5):
    v_e = v - (omega * L / 2)
    v_d = v + (omega * L / 2)

    maior_velocidade = max(abs(v_e), abs(v_d))

    if maior_velocidade > max_wheel_speed:
        fator = max_wheel_speed / maior_velocidade

        v_e = v_e * fator
        v_d = v_d * fator

    return v_e, v_d


print("===== EXERCÍCIO 1 =====")
print(converter_cmd_vel(1.2, 3.0))