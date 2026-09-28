def controle_reativo(distancias):

    frente = distancias['frente']
    esquerda = distancias['esquerda']
    direita = distancias['direita']

    distancia_critica = 0.4


    if frente < distancia_critica:
        v = 0.0

        if esquerda > direita:
            omega = 1.0
        else:
            omega = -1.0

    else:

        v = 0.5


        ganho = 1.0
        omega = ganho * (esquerda - direita)

    return v, omega
print("\n===== EXERCÍCIO 3 =====")

distancias = {
    'frente': 0.3,
    'esquerda': 2.0,
    'direita': 1.0
}

print(controle_reativo(distancias))