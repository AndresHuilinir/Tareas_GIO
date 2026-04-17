import numpy as np

#La funcion por defecto revisa que se trunque para >0 y si no
#es un valor de conteo (num enteros) hay que avisarle con 0

numero_de_grupo = 3

rng = np.random.default_rng(numero_de_grupo)

def generar_normal(mu, sigma, limite_inferior=0, es_entero=True):
    valor = rng.normal(mu, sigma)
    if es_entero:
        valor = round(valor)
    return max(limite_inferior, valor)

def generar_uniforme(a, b, es_entero=False):
    valor = rng.uniform(a, b)
    if es_entero:
        valor = max(0, round(valor))
    return valor


T= 24
p = 3 # cantidad de plantas
k = 2 # tipo de maquina
M_0 = 5 # Cantidad de operarios inicial
# Definir Y_0k, que es la cantidad inicial de maquinas
# instaladas de cada tipo
H = 480
d_1 = generar_normal(2500,0.05*25000,1)
r_t = generar_uniforme(1.02,1.04)
#Acá debo crear una lista para crear el resto de d_t
#Va del 2 al 24
d_t = [d_1]

print(f"d_1 = {d_1}")
print(f"r_1 = {r_t}\n")

for t in range(2, T+1):
    d_siguiente = round(d_t[-1] * r_t)
    d_t.append(d_siguiente)
    print(f"d_{t} = {d_t[-1]}")
    
    r_t = generar_uniforme(1.02, 1.04)
    print(f"r_{t} = {r_t}\n")

p_1 = generar_normal(6000,0.05*6000)
p_2 = generar_normal(11500,0.05*11500)
alfa = generar_normal(0.1,0.15*0.1)
S_p = []
for p_ in range(p):
    S_p[p_] = generar_normal(100,0.05*100)

u = 0.7
S_yk = []
for k_ in range(k):
    S_yk[k_] = generar_normal(15,0.05*15)

print(f"p_1 = {p_1}")
print(f"p_2 = {p_2}")