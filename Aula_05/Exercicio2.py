def processar_scan(leituras_lidar):
    if len(leituras_lidar) != 360:
        raise ValueError("O LiDAR deve possuir exatamente 360 leituras.")

    def validas(valores):
        return [x for x in valores if 0.1 <= x <= 5.0]

    frente = validas(
        list(leituras_lidar[345:360]) +
        list(leituras_lidar[0:16])
    )

    esquerda = validas(leituras_lidar[45:136])

    direita = validas(leituras_lidar[225:316])


    min_frente = min(frente) if frente else None
    min_esq = min(esquerda) if esquerda else None
    min_dir = min(direita) if direita else None

    return {
        'frente': min_frente,
        'esquerda': min_esq,
        'direita': min_dir
    }
print("\n===== EXERCÍCIO 2 =====")

leituras = [2.0] * 360

leituras[5] = 1.2
leituras[100] = 0.8
leituras[280] = 1.5

resultado_scan = processar_scan(leituras)

print(resultado_scan)