import numpy as np

#La funcion por defecto revisa que se trunque para >0 y si no
#es un valor de conteo (num enteros) hay que avisarle con 0

numero_de_grupo = 1

def generar_normal(mu, sigma, limite_inferior=0, es_entero=True):
    rng = np.random.default_rng(numero_de_grupo)
    valor = rng.normal(mu, sigma)
    if es_entero:
        valor = round(valor)
    return max(limite_inferior, valor)

def generar_uniforme(a, b, es_entero=False):
    rng = np.random.default_rng(numero_de_grupo)
    valor = rng.uniform(a, b)
    if es_entero:
        valor = max(0, round(valor))
    return valor



H = 480
d_1 = generar_normal(2500,0.05*25000,1)
r_t = generar_uniforme(1.02,1.04)
p_1 = generar_normal(6000,0.05*6000)
p_2 = generar_normal(11500,0.05*11500)