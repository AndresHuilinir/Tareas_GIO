import numpy as np

numero_de_grupo = 14
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

def init_C_m(model, k, t, C1, C2):
    if k == 1:
        return C1
    elif k == 2:
        return C2

def calcular_costo_en_el_tiempo(Variable_x, T, pi_min):
    lista = [Variable_x]
    for t in range(2, T + 1):
        lista.append(Variable_x*(1 + pi_min)**(t-1))
    return lista

def calcular_valor_presente(Variable_x, T, pi_min, r):
    lista = [Variable_x]
    for t in range(2, T + 1):
        lista.append(Variable_x*((1 + pi_min)/(1 + r))**(t-1))
    return lista