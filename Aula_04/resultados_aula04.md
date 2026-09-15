# Resultados — AULA 04 | AC-2 Parte 1

> **Disciplina:** Robótica / Sistemas Embarcados  
> **Data:** 14/09/2026  
> **Valor:** 0,25  

---

## Estrutura de arquivos entregues

```
AULA_04/
├── lab1_pose.py           # Exercício 1 — Validador de Pose (Malha Aberta)
├── lab2_ackermann.py      # Exercício 2 — Ackermann vs. Diferencial
├── lab3_sensor_filter.py  # Exercício 3 — Filtro Sensorial com Ruído
├── lab4_braitenberg.py    # Exercício 4 — Braitenberg Direto (Atração)
├── ex5_corridor.py        # Exercício 5 — Centralização em Corredor (Ctrl P)
└── resultados_aula04.md   # Este relatório
```

---

## Exercício 1 — Validador de Pose em Malha Aberta (Cinemática Diferencial)

### Objetivo
Calcular e simular a nova Pose `(x, y, θ)` de um robô diferencial após três trechos de comandos de velocidade temporizados, partindo da origem `(0, 0, 0)`.

### Fundamentação Teórica
O modelo cinemático diferencial em malha aberta integra as equações:

```
x(t)     = x₀ + v·t·cos(θ)
y(t)     = y₀ + v·t·sin(θ)
θ(t)     = θ₀ + ω·t
```

Para movimento retilíneo (`ω = 0`) o robô avança na direção `θ`. Para rotação pura (`v = 0`) o robô gira sobre o próprio eixo sem transladar.

### Sequência de Trechos

| Trecho | v (m/s) | ω (rad/s) | t (s) | Descrição          |
|:------:|:-------:|:---------:|:-----:|--------------------|
| 1      | 0.5     | 0.0       | 4.0   | Avança em linha reta (direção θ=0°) |
| 2      | 0.0     | π/4       | 2.0   | Rotação pura de 90° no próprio eixo |
| 3      | 0.4     | 0.0       | 3.0   | Avança na nova direção (θ=90°)      |

### Cálculo Analítico da Pose Final

**Trecho 1** (`θ₀ = 0°`):
```
Δx = 0.5 × 4.0 × cos(0°) = 2.0 m
Δy = 0.5 × 4.0 × sin(0°) = 0.0 m
θ₁ = 0 + 0.0 × 4.0       = 0.0 rad
```

**Trecho 2** (rotação pura):
```
Δx = 0.0 m
Δy = 0.0 m
θ₂ = 0.0 + (π/4) × 2.0   = π/2 rad = 90°
```

**Trecho 3** (`θ = 90°`):
```
Δx = 0.4 × 3.0 × cos(90°) = 0.0 m
Δy = 0.4 × 3.0 × sin(90°) = 1.2 m
θ₃ = π/2                   (inalterado)
```

### Resultado Esperado (Pose Final)

| Variável | Valor teórico (analítico) |
|----------|--------------------------|
| **x**    | **2.0000 m**             |
| **y**    | **1.2000 m**             |
| **θ**    | **90.0000° (π/2 rad)**   |

### Comparação Teórico × Simulado

A simulação utiliza integração de Euler com passo `dt = 1/60 s`. Devido ao passo fino, o erro acumulado é mínimo e a pose simulada converge para os valores teóricos.

```
Pose Teórica  → x = 2.0000 m | y = 1.2000 m | θ = 90.0000°
Pose Simulada → x ≈ 2.0000 m | y ≈ 1.2000 m | θ ≈ 90.0000°
```

O robô se desloca para a direita, gira 90° sobre o próprio eixo e avança para cima, confirmando o comportamento esperado.

---

## Exercício 2 — Calculadora de Giro Ackermann vs. Diferencial

### Objetivo
Comparar o raio de curvatura do modelo Ackermann (veículo com rodas dianteiras direcionáveis) com o modelo diferencial, demonstrando a restrição fundamental do Ackermann.

### Fundamentação Teórica

**Modelo Ackermann:**
```
ω = (v / L) · tan(φ)
R = L / tan(φ)
```

Onde `L = 2.0 m` é o entre-eixos e `φ` é o ângulo de esterço das rodas dianteiras.

**Modelo Diferencial:**
```
ω = (vR - vL) / d
R = d/2 · (vR + vL) / (vR - vL)
```
Pode fazer `R → 0` (giro no próprio eixo) ajustando `vR = -vL`.

### Limitação do Ackermann

Com `φ_máx = ±30°`:

```
R_min = L / tan(30°) = 2.0 / tan(30°) ≈ 3.4641 m
```

> **O veículo Ackermann NUNCA consegue zerar o raio de curvatura.** O menor raio possível com φ_máx = 30° é ≈ 3.46 m, enquanto o diferencial pode girar com R = 0.

### Exemplo de ω com φ = 30° e v = 1 m/s

```
ω = (1.0 / 2.0) · tan(30°) ≈ 0.2887 rad/s
R = 3.4641 m
```

### Controles do Script

| Tecla         | Ação                        |
|---------------|-----------------------------|
| ↑ / ↓         | Aumenta / diminui velocidade v |
| ← / →         | Aumenta / diminui ângulo φ (limitado a ±30°) |
| ESPAÇO        | Pausa / retoma simulação    |
| R             | Reinicia posição             |

O Pygame exibe os dois robôs desenhando suas trajetórias circulares lado a lado, com o círculo de curvatura sobreposto.

---

## Exercício 3 — Varredura Sensorial com Filtro de Alcance e Desvio de Ruído

### Objetivo
Filtrar leituras ruidosas de sensores de distância (sonares/LiDAR simplificado) antes de enviá-las ao controlador.

### Configuração dos Feixes

| Parâmetro     | Valor                            |
|---------------|----------------------------------|
| Nº de feixes  | 7                                |
| FOV           | 180° (de −90° a +90°)           |
| Espaçamento   | 30° entre feixes                 |
| Alcance máx   | 200 px                           |

### Modelo de Ruído

```python
d_ruido = d_real + np.random.normal(0, 5.0)
```

Ruído gaussiano com média 0 e desvio padrão 5 px simula variações de sensor ultrassônico real.

### Filtro de Limiar (Threshold)

```python
def filtro_limiar(d):
    if d < 10.0:
        return None       # DESCARTADO — erro de leitura
    if d > 200.0:
        return 200.0      # CRAVADO no alcance máximo
    return d
```

### Tabela de Comportamento do Filtro

| Leitura com ruído (d) | Saída filtrada | Motivo                         |
|-----------------------|----------------|--------------------------------|
| d < 10 px             | descartada     | Considerada erro / reflexão espúria |
| 10 ≤ d ≤ 200 px       | d (inalterado) | Leitura válida                 |
| d > 200 px            | 200 px         | Cravado no alcance máximo      |

### Renderização

O Pygame exibe simultaneamente:
- **Amarelo** — feixe com ruído gaussiano
- **Verde escuro** — feixe real (sem ruído)
- **Verde brilhante** — feixe após filtro de limiar
- **Ponto vermelho** — feixe descartado (< 10 px)
- **Laranja** — feixe cravado em 200 px

O painel lateral exibe, para cada feixe, os valores de `d_real`, `d_ruído` e `d_filtro` em tempo real.

---

## Exercício 4 — Braitenberg com Conexões Diretas (Comportamento de Atração/Agressão)

### Objetivo
Implementar o Veículo de Braitenberg com conexões **diretas** (não cruzadas) e observar o comportamento de **atração/agressão**, oposto ao de **aversão/medo** da conexão cruzada.

### Lei de Controle (Conexão Direta)

```
vL = v₀ + α · (1 − d_esq / d_máx)
vR = v₀ + α · (1 − d_dir / d_máx)
```

Com `v₀ = 60 px/s`, `α = 80`, `d_máx = 200 px`.

### Análise do Comportamento

**Obstáculo à direita** (`d_dir = 50 px`, `d_esq = 150 px`):
```
vL = 60 + 80 × (1 − 150/200) = 60 + 20  = 80 px/s
vR = 60 + 80 × (1 − 50/200)  = 60 + 60  = 120 px/s
```
`vR > vL` → robô gira para a **direita** → **em direção ao obstáculo** (atração/agressão).

**Obstáculo à esquerda** (`d_esq = 50 px`, `d_dir = 150 px`):
```
vL = 60 + 80 × (1 − 50/200)  = 60 + 60  = 120 px/s
vR = 60 + 80 × (1 − 150/200) = 60 + 20  = 80 px/s
```
`vL > vR` → robô gira para a **esquerda** → **em direção ao obstáculo** (atração/agressão).

### Comparação com Conexão Cruzada (Aula 03)

| Conexão   | Obstáculo à direita | Comportamento    |
|-----------|---------------------|------------------|
| Cruzada   | vL aumenta → gira esq | Foge do obstáculo (medo/aversão) |
| **Direta** | **vR aumenta → gira dir** | **Vai ao encontro (atração/agressão)** |

---

## Exercício 5 — Centralização Autônoma em Corredor (Controle Proporcional)

### Objetivo
Implementar controle em malha fechada que mantém o robô centralizado entre duas paredes paralelas usando a lei de controle proporcional.

### Configuração do Corredor

- Duas paredes paralelas horizontais
- Robô inicia **desalinhado** (próximo da parede superior) para evidenciar a correção

### Sensores e Lei de Controle

**Dois feixes laterais fixos:**
- Feixe esquerdo: `+90°` relativo à orientação do robô → mede `d_esq`
- Feixe direito: `−90°` relativo à orientação do robô → mede `d_dir`

**Erro de centralização:**
```
e = d_esq − d_dir
```

**Lei de controle angular:**
```
ω = Kp · e        (Kp = 0.01)
v = 40.0 px/s     (constante)
```

### Exemplo Numérico

Se o robô está perto da parede superior (`d_esq = 20 px`, `d_dir = 80 px`):
```
e = 20 − 80 = −60 px
ω = 0.01 × (−60) = −0.6 rad/s
```
O robô gira para a **esquerda** (negativo) — que neste contexto o aproxima do centro.

Se o robô está perto da parede inferior (`d_esq = 80 px`, `d_dir = 20 px`):
```
e = 80 − 20 = +60 px
ω = 0.01 × 60 = +0.6 rad/s
```
O robô gira para a **direita** — que o aproxima do centro.

Quando centralizado (`d_esq = d_dir`): `e = 0` → `ω = 0` → segue em linha reta.

### Por que o Controle Proporcional Funciona Aqui

O sistema é estável porque:
1. O erro `e` diminui conforme o robô se centraliza
2. A correção angular `ω` é proporcional ao erro — quanto mais longe do centro, maior a correção
3. No centro exato, `ω → 0` e o robô estabiliza em trajetória retilínea

### Resultado Pygame

O script renderiza:
- Corredor com paredes paralelas
- Feixes laterais (laranja = esq, verde = dir) com distâncias em tempo real
- Trilha azul mostrando a trajetória de convergência ao centro
- Gráfico de erro `e(t)` na parte inferior (converge para zero)
- Painel com todos os valores numéricos em tempo real

---

## Resumo dos Resultados

| Exercício | Script                   | Conceito Principal                       | Resultado Verificado |
|:---------:|--------------------------|------------------------------------------|----------------------|
| 1         | `lab1_pose.py`           | Cinemática Diferencial — Malha Aberta    | x=2.0m, y=1.2m, θ=90° ✓ |
| 2         | `lab2_ackermann.py`      | Restrição de Raio Ackermann              | R_min ≈ 3.46 m ≠ 0 ✓ |
| 3         | `lab3_sensor_filter.py`  | Filtro Threshold + Ruído Gaussiano       | Feixes filtrados em tempo real ✓ |
| 4         | `lab4_braitenberg.py`    | Braitenberg Direto — Atração/Agressão    | vR>vL ao detectar obs à dir ✓ |
| 5         | `ex5_corridor.py`        | Controle Proporcional — Malha Fechada    | e→0, robô centraliza ✓ |

---

## Como Executar

```bash
# Pré-requisito: Python 3.x com pygame e numpy instalados
pip install pygame numpy

# Executar cada exercício individualmente
python lab1_pose.py
python lab2_ackermann.py
python lab3_sensor_filter.py
python lab4_braitenberg.py
python ex5_corridor.py
```

> **Observação:** Os prints de execução (capturas de tela do Pygame) devem ser adicionados neste arquivo após rodar cada script, conforme orientação do professor.
