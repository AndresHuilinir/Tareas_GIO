import numpy as np

numero_de_grupo = 3

rng = np.random.default_rng(numero_de_grupo)

def generar_normal(mu, sigma, limite_inferior=0, es_entero=True, limite_superior=None):
    valor = rng.normal(mu, sigma)
    if es_entero:
        valor = round(valor)
    valor = max(limite_inferior, valor)
    if limite_superior is not None:
        valor = min(limite_superior, valor)
    return valor

def generar_uniforme(a, b, es_entero=False):
    valor = rng.uniform(a, b)
    if es_entero:
        valor = max(0, round(valor))
    return valor

T= 24
p = 3 
k = 2 
M_0 = 8 
Y_01 = 2 
Y_02 = 1

H = 480
d_1 = generar_normal(2500, 0.05*25000, 1)
r_t = generar_uniforme(1.02, 1.04)
d_t = [d_1]

print(f"d_1 = {d_1}")
print(f"r_1 = {r_t}\n")

for t in range(2, T+1):
    d_siguiente = round(d_t[-1] * r_t)
    d_t.append(d_siguiente)
    print(f"d_{t} = {d_t[-1]}")
    r_t = generar_uniforme(1.02, 1.04)
    print(f"r_{t} = {r_t}\n")

p_1 = generar_normal(6000, 0.05*6000)
p_2 = generar_normal(11500, 0.05*11500)
alfa = generar_normal(0.1, 0.15*0.1, es_entero=False)

S_p = []
for p_ in range(p):
    S_p.append(generar_normal(100,0.05*100))

u = 0.7
S_yk = []
for k_ in range(k):
    S_yk.append(generar_normal(15,0.05*15))

S_m = []
for m_ in range(M_0):
    S_m.append(generar_normal(6,6*0.05))

V_max = 0.1
O_max = 0.3

C_m11 = generar_normal(18000000,18000000*0.05)
C_m21 = generar_normal(32000000,32000000*0.05)
C_hire1 = generar_normal(500000,500000*0.05)
C_fire1 = generar_normal(1800000,0.05*1800000)
C_sal1 = generar_normal(7200000,0.03*7200000)
C_r1 = generar_normal(15000000,0.05*15000000)
C_I1 = generar_normal(45000000,0.05*45000000)
C_p1 = generar_normal(2500,0.05*2500)
C_lost1 = generar_normal(1200,0.05*1200)

InfProm = generar_normal(0.04,0.002*0.002,0.03,False, 0.05)

print(f"p_1 = {p_1}")
print(f"p_2 = {p_2}")
print(f"alfa = {alfa}")