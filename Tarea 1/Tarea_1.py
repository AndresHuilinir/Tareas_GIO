import numpy as np
import pyomo.environ as pyo

modelo = pyo.ConcreteModel()

numero_de_grupo = 14
rng = np.random.default_rng(numero_de_grupo)

#funciones para evitar aglomerar todo desordenado abajo

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

InfProm = generar_normal(0.04,0.002*0.002,0.03,False, 0.05)
R = generar_normal(0.10,0.005*0.005,0.09,False, 0.11)
pi_min = (1+InfProm)**0.25 -1
r = (1+R)**0.25 -1

def C_mt(m, k, t):
    if k == 1:
        return C_m11
    elif k == 2:
        return C_m21

def valor_presente(Variable_contexto):
    lista = [Variable_contexto]
    for t in range(2,T+1):
        lista.append(Variable_contexto*((1+pi_min)/(1+r))**(t-1))
    return lista

#conjuntos
T= 24
modelo.T = pyo.RangeSet(1, T)
p = 1
modelo.P = pyo.RangeSet(1, p)
k = 2
modelo.K = pyo.RangeSet(1, k)

#parametros
M_0 = 8
Y_01 = 2 #Maquina tipo 1 inicial
Y_02 = 1 #Maquina tipo 2 inicial
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

Capacidad = [p_1,p_2]
modelo.Capacidad_k = pyo.Param(modelo.K, initialize=lambda m, i: Capacidad[i-1])

alfa = generar_normal(0.1,0.15*0.1,es_entero=False)
modelo.alfa = pyo.Param(initialize=alfa)

S_p = [] #superficie total por planta
for p_ in range(p):
    S_p.append(generar_normal(100,0.05*100,es_entero=False))

modelo.S_p = pyo.Param(modelo.P, initialize=lambda m, i: S_p[i-1])

u = 0.7
modelo.u = pyo.Param(initialize=u)

S_yk = [] #superficie por maquina tipo k
for k_ in range(k):
    S_yk.append(generar_normal(15,0.05*15,es_entero=False))

modelo.S_yk = pyo.Param(modelo.K, initialize=lambda m, i: S_yk[i-1])

S_m = generar_normal(6,6*0.05,es_entero=False)
modelo.S_m = pyo.Param(initialize=S_m)

V_max = 0.1
modelo.V_max = pyo.Param(initialize=V_max)

Oc_max = 0.3
modelo.O_max = pyo.Param(initialize=Oc_max)

C_m11 = generar_normal(18000000,18000000*0.05) #tipo maquina/tiempo
C_m21 = generar_normal(32000000,32000000*0.05) #tipo maquina/tiempo
C_hire1 = generar_normal(500000,500000*0.05) #tiempo # 
C_fire1 = generar_normal(1800000,0.05*1800000) #tiempo
C_sal1 = generar_normal(7200000,0.03*7200000) #tiempo
C_r1 = generar_normal(15000000,0.05*15000000) #tiempo
C_I1 = generar_normal(45000000,0.05*45000000) #tiempo
C_p1 = generar_normal(2500,0.05*2500) #tiempo
C_lost1 = generar_normal(1200,0.05*1200) #tiempo

C_m1_vp = valor_presente(C_m11)  #
C_m2_vp = valor_presente(C_m21)  #
C_hire_vp = valor_presente(C_hire1) #
C_fire_vp = valor_presente(C_fire1) #
C_sal_vp = valor_presente(C_sal1) #
C_r_vp = valor_presente(C_r1) #
C_I_vp = valor_presente(C_I1) #
C_p_vp = valor_presente(C_p1) #
C_lost_vp = valor_presente(C_lost1) #

modelo.C_m = pyo.Param(modelo.K, modelo.T,initialize=lambda m, k, t: C_m1_vp[t-1] if k == 1 else C_m2_vp[t-1]) #
modelo.C_hire = pyo.Param(modelo.T,initialize=lambda m, t: C_hire_vp[t-1]) #
modelo.C_fire = pyo.Param(modelo.T,initialize=lambda m, t: C_fire_vp[t-1]) #
modelo.C_sal = pyo.Param(modelo.T,initialize=lambda m, t: C_sal_vp[t-1]) #
modelo.C_r = pyo.Param(modelo.T, initialize=lambda m, t: C_r_vp[t-1]) #
modelo.C_I = pyo.Param(modelo.T, initialize=lambda m, t: C_I_vp[t-1]) #
modelo.C_p = pyo.Param(modelo.T, initialize=lambda m, t: C_p_vp[t-1]) #
modelo.C_lost = pyo.Param(modelo.T, initialize=lambda m, t: C_lost_vp[t-1])


#Variables

modelo.x = pyo.Var(modelo.T, domain=pyo.NonNegativeIntegers)
modelo.l = pyo.Var(modelo.T, domain=pyo.NonNegativeIntegers)
modelo.m = pyo.Var(modelo.K,modelo.T, domain=pyo.NonNegativeIntegers)
modelo.Y = pyo.Var(modelo.P, modelo.K, modelo.T, domain=pyo.NonNegativeIntegers)
modelo.h = pyo.Var(modelo.T, domain=pyo.NonNegativeIntegers)
modelo.f = pyo.Var(modelo.T, domain=pyo.NonNegativeIntegers)
modelo.W = pyo.Var(modelo.T, domain=pyo.PositiveIntegers)
modelo.n = pyo.Var(modelo.T, domain=pyo.NonNegativeIntegers)
modelo.P_a = pyo.Var(modelo.T, domain=pyo.PositiveIntegers)

modelo.W[1].fix(M_0)
modelo.P_a[1].fix(p)
for k in modelo.K:
    modelo.Y[k,1].fix(modelo.Y0[k])


#A partir de aca abajo hago modelos, arriba pura variable e.e

#como que tengo que definirlo asi
def demanda(m, t): #solo deja 
    return m.x[t] + m.l[t] == m.d[t]

modelo.demanda = pyo.Constraint(modelo.T, rule=demanda)

def capacidad_maquinas(m, t):
    return m.x[t] <= sum(m.Y[k,t]*m.Capacidad_k[k] for k in m.K)

modelo.capacidad_maquinas = pyo.Constraint(modelo.T, rule=capacidad_maquinas)

def capacidad_mano_de_obra(m,t):
    return m.alfa*m.x[t] <= m.H*m.W[t]

modelo.capacidad_mano_de_obra = pyo.Constraint(modelo.T,rule=capacidad_mano_de_obra)

def acumulacion_maquinas(mod, t, k):
    if t == 1:
        return pyo.Constraint.Skip
    return mod.Y[k,t] == mod.Y[k,t-1] + mod.m[k,t-1]

modelo.acumulacion_maquinas = pyo.Constraint(modelo.T, modelo.K, rule=acumulacion_maquinas)

def balance_operarios(m, t):
    if t == 1:
        return pyo.Constraint.Skip
    return m.W[t] == m.W[t-1] + m.h[t] - m.f[t]

modelo.balance_operarios = pyo.Constraint(modelo.T, rule=balance_operarios)

def plantas_activas(m,t):
    if t == 1:
        return pyo.Constraint.Skip
    return m.P_a[t] == m.P_a[t-1] + m.n[t]

modelo.plantas_activas = pyo.Constraint(modelo.T, rule=plantas_activas)

def restriccion_espacio(m, t):
    return sum(m.S_yk[k]*m.Y[k,t] for k in m.K) + m.S_m*m.W[t] <= m.u*sum(m.S_p[p] for p in m.P)*m.P_a[t]

modelo.restriccion_espacio = pyo.Constraint(modelo.T, rule=restriccion_espacio)

def nivel_servicio(m,t):
    return m.l[t] <= m.V_max*m.d[t]

modelo.nivel_servicio = pyo.Constraint(modelo.T, rule=nivel_servicio)

def sobrecapacidad_prod_maquinas(m,t):
    return sum(m.Capacidad_k[k]*m.Y[k,t] for k in m.K) <= (1+m.Oc_max)*m.d[t]

modelo.sobrecapacidad_prod_maquinas = pyo.Constraint(modelo.T, rule=sobrecapacidad_prod_maquinas)

def sobrecapacidad_prod_mano_obra(m,t):
    return m.H*m.W[t]/m.alfa <= (1+m.Oc_max)*m.d[t]

modelo.sobrecapacidad_prod_mano_obra = pyo.Constraint(modelo.T, rule=sobrecapacidad_prod_mano_obra)

modelo.pprint()