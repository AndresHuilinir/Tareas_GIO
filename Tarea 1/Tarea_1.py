import numpy as np
import pyomo.environ as pyo

modelo = pyo.ConcreteModel()

numero_de_grupo = 14
rng = np.random.default_rng(numero_de_grupo)

def init_C_m(m, k, t):
    if k == 1:
        return C_m11
    elif k == 2:
        return C_m21

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

#conjuntos
T= 24
modelo.T = pyo.RangeSet(1, T)
p = 3 
modelo.P = pyo.RangeSet(1, p)
k = 2
modelo.K = pyo.RangeSet(1, k)
M_0 = 8
modelo.M = pyo.RangeSet(1, M_0)

#parametros
Y_01 = 2 
Y_02 = 1
Y0 = [Y_01, Y_02]
modelo.Y0 = pyo.Param(modelo.K, initialize=lambda m, k: Y0[k-1])

H = 480
modelo.H = pyo.Param(initialize=H)

d_1 = generar_normal(2500,0.05*25000,1)
r_t = generar_uniforme(1.02, 1.04)
d_t = [d_1]

for t in range(2, T+1):
    d_siguiente = round(d_t[-1] * r_t)
    d_t.append(d_siguiente)
    r_t = generar_uniforme(1.02, 1.04)

modelo.d = pyo.Param(modelo.T, initialize=lambda m, t: d_t[t-1])

p_1 = generar_normal(6000,0.05*6000)
modelo.p_1 = pyo.Param(initialize=p_1)

p_2 = generar_normal(11500,0.05*11500)
modelo.p_2 = pyo.Param(initialize=p_2)

alfa = generar_normal(0.1,0.15*0.1,es_entero=False)
modelo.alfa = pyo.Param(initialize=alfa)

S_p = []
for p_ in range(p):
    S_p.append(generar_normal(100,0.05*100))

modelo.S_p = pyo.Param(modelo.P, initialize=lambda m, i: S_p[i-1])

u = 0.7
modelo.u = pyo.Param(initialize=u)

S_yk = []
for k_ in range(k):
    S_yk.append(generar_normal(15,0.05*15))

modelo.S_yk = pyo.Param(modelo.K, initialize=lambda m, i: S_yk[i-1])
print("\n")
S_m = []
for m_ in range(M_0):
    S_m.append(generar_normal(6,6*0.05))

modelo.S_m = pyo.Param(modelo.M, initialize=lambda m, i: S_m[i-1])

V_max = 0.1
modelo.V_max = pyo.Param(initialize=V_max)

O_max = 0.3
modelo.O_max = pyo.Param(initialize=O_max)

C_m11 = generar_normal(18000000,18000000*0.05) #tipo maquina/tiempo
C_m21 = generar_normal(32000000,32000000*0.05) #tipo maquina/tiempo
C_hire1 = generar_normal(500000,500000*0.05) #tiempo
C_fire1 = generar_normal(1800000,0.05*1800000) #tiempo
C_sal1 = generar_normal(7200000,0.03*7200000) #tiempo
C_r1 = generar_normal(15000000,0.05*15000000) #tiempo
C_I1 = generar_normal(45000000,0.05*45000000) #tiempo
C_p1 = generar_normal(2500,0.05*2500) #tiempo
C_lost1 = generar_normal(1200,0.05*1200) #tiempo


modelo.C_m = pyo.Param(modelo.K, modelo.T, initialize=init_C_m)
modelo.C_hire = pyo.Param(modelo.T, initialize=lambda m, t: C_hire1)
modelo.C_fire = pyo.Param(modelo.T, initialize=lambda m, t: C_fire1)
modelo.C_sal = pyo.Param(modelo.T, initialize=lambda m, t: C_sal1)
modelo.C_r = pyo.Param(modelo.T, initialize=lambda m, t: C_r1)
modelo.C_I = pyo.Param(modelo.T, initialize=lambda m, t: C_I1)
modelo.C_p = pyo.Param(modelo.T, initialize=lambda m, t: C_p1)
modelo.C_lost = pyo.Param(modelo.T, initialize=lambda m, t: C_lost1)

InfProm = generar_normal(0.04,0.002*0.002,0.03,False, 0.05)
R = generar_normal(0.10,0.005*0.005,0.09,False, 0.11)

pi_min = (1+InfProm)**0.25 -1
r = (1+R)**0.25 -1

def costo_en_el_tiempo(Variable_x):
    lista = [Variable_x]
    print(f"costo_1 = {lista[-1]}")
    for t in range(2,T+1):
        lista.append(Variable_x*(1+pi_min)**(t-1))
        print(f"costo_{t} = {lista[-1]}")
    return lista

def valor_presente(Variable_x):
    lista = [Variable_x]
    print(f"vp_1 = {lista[-1]}")
    for t in range(2,T+1):
        lista.append(Variable_x*((1+pi_min)/(1+r))**(t-1))
        print(f"vp_{t} = {lista[-1]}")
    return lista

modelo.pprint()