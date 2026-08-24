Aula 02 — O que a gente entendeu

Estado do Robô e POSE 2D

A POSE 2D é basicamente para saber onde o robô está.
Tem o 
𝑥
, que é um lado, o 
𝑦
, que é o outro lado, e o 
𝜃
, que é para onde o robô está olhando.
Então é tipo:
“O robô está aqui e está virado para lá.”
É isso que a gente entendeu.


Cinemática Diferencial

A cinemática diferencial é sobre as rodas do robô.
O robô tem uma roda de cada lado. Quando as duas rodas andam na mesma velocidade, ele anda reto. Quando uma roda anda mais rápido que a outra, ele vira.

Por exemplo:

roda direita e esquerda iguais = anda reto;
uma roda mais rápida = faz curva;
uma roda para trás e outra para frente = gira praticamente no lugar.
Então é basicamente entender como as rodas fazem o robô andar.


Odometria Discreta

A odometria serve para o robô tentar saber quanto ele andou e onde ele está agora.
Ele olha o quanto as rodas giraram e tenta calcular a nova posição.
Por exemplo, se ele estava em um lugar e andou para frente, ele calcula que agora está mais para frente.
Só que não é perfeito. Se a roda escorregar ou o sensor errar, o robô pode achar que está em um lugar, mas na verdade está em outro.
Então a gente entendeu que odometria é tipo o robô tentando acompanhar seus próprios passos.


Navegação GO-TO-GOAL

GO-TO-GOAL é basicamente mandar o robô ir até um lugar.
O robô vê onde ele está e onde precisa chegar. Depois ele calcula para qual lado precisa virar e começa a andar.
Se estiver indo para o lado errado, ele vira. Se estiver indo certo, continua andando.
É tipo falar:
“Robô, você está aqui. O lugar que você precisa ir é ali. Então vai para ali.”
Quando chega perto o suficiente do lugar, ele para.

E o GO-TO-GOAL faz ele tentar chegar em um lugar específico.

Resumindo bem simples: saber onde está → mexer as rodas → descobrir onde foi parar → tentar chegar no lugar certo.
