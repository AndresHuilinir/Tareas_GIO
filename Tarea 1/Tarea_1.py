import numpy as np
import pyomo.environ as pyo
import shutil

modelo = pyo.ConcreteModel()

numero_de_grupo = 14
rng = np.random.default_rng(numero_de_grupo)

# Funciones auxiliares

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


InfProm = generar_normal(0.04, 0.002, 0.03, False, 0.05)
R = generar_normal(0.10, 0.005, 0.09, False, 0.11)
pi_min = (1+InfProm)**0.25-1
r = (1+R)**0.25-1

def valor_presente(Variable_contexto):
    lista = [Variable_contexto]
    for t in range(2, T + 1):
        lista.append(Variable_contexto * ((1 + pi_min) / (1 + r)) ** (t - 1))
    return lista

# Conjuntos
T = 24
modelo.T = pyo.RangeSet(1, T)
modelo.K = pyo.RangeSet(1, 2)

# Parámetros operativos
M_0  = 8
Y_01 = 2  # Máquinas tipo 1 iniciales
Y_02 = 1  # Máquinas tipo 2 iniciales
Y0   = [Y_01, Y_02]
P_0  = 1  # Plantas iniciales (escalar)

modelo.Y0 = pyo.Param(modelo.K, initialize=lambda m, k: Y0[k - 1])
modelo.H  = pyo.Param(initialize=480)

d_1 = generar_normal(25000, 0.05 * 25000, 1)
r_t = generar_uniforme(1.02, 1.04)
d_t = [d_1]

for t in range(2, T + 1):
    d_siguiente = round(d_t[-1] * r_t)
    d_t.append(d_siguiente)
    r_t = generar_uniforme(1.02, 1.04)

modelo.d = pyo.Param(modelo.T, initialize=lambda m, t: d_t[t - 1])

rho_1 = generar_normal(6000,0.05*6000)
rho_2 = generar_normal(11500,0.05*11500)
Capacidad = [rho_1, rho_2]
modelo.Capacidad_k = pyo.Param(modelo.K, initialize=lambda m, i: Capacidad[i-1])

alfa = generar_normal(0.1,0.15*0.1,es_entero=False)
modelo.alfa = pyo.Param(initialize=alfa)

# FIX: S_p como escalar (no lista/Param indexado por planta)
S_p = generar_normal(100, 0.05 * 100, es_entero=False)
modelo.S_p = pyo.Param(initialize=S_p)

modelo.u = pyo.Param(initialize=0.7)

S_yk = [generar_normal(15, 0.05 * 15, es_entero=False) for _ in range(2)]
modelo.S_yk = pyo.Param(modelo.K, initialize=lambda m, i: S_yk[i-1])

S_m = generar_normal(6, 6 * 0.05, es_entero=False)
modelo.S_m = pyo.Param(initialize=S_m)

modelo.V_max = pyo.Param(initialize=0.1)
modelo.O_max = pyo.Param(initialize=0.3)

# Parámetros de costo (generados en t=1)
C_m11 = generar_normal(18000000,18000000*0.05)
C_m21 = generar_normal(32000000,32000000*0.05)
C_hire1 = generar_normal(500000,500000*0.05)
C_fire1 = generar_normal(1800000,1800000*0.05)
C_sal1 = generar_normal(7200000,7200000*0.03)
C_r1 = generar_normal(15000000,15000000*0.05)
C_I1 = generar_normal(45000000,45000000*0.05)
C_p1 = generar_normal(2500,2500*0.05)

C_lost1 = generar_normal(12000,12000*0.05)

# Indexación a valor presente
C_m1_vp = valor_presente(C_m11)
C_m2_vp = valor_presente(C_m21)
C_hire_vp = valor_presente(C_hire1)
C_fire_vp = valor_presente(C_fire1)
C_sal_vp = valor_presente(C_sal1)
C_r_vp = valor_presente(C_r1)
C_I_vp = valor_presente(C_I1)
C_p_vp = valor_presente(C_p1)
C_lost_vp = valor_presente(C_lost1)

modelo.C_m = pyo.Param(modelo.K, modelo.T,initialize=lambda m, k, t: C_m1_vp[t-1] if k == 1 else C_m2_vp[t-1])
modelo.C_hire = pyo.Param(modelo.T, initialize=lambda m, t: C_hire_vp[t-1])
modelo.C_fire = pyo.Param(modelo.T, initialize=lambda m, t: C_fire_vp[t-1])
modelo.C_sal = pyo.Param(modelo.T, initialize=lambda m, t: C_sal_vp[t-1])
modelo.C_r = pyo.Param(modelo.T, initialize=lambda m, t: C_r_vp[t-1])
modelo.C_I = pyo.Param(modelo.T, initialize=lambda m, t: C_I_vp[t-1])
modelo.C_p = pyo.Param(modelo.T, initialize=lambda m, t: C_p_vp[t-1])
modelo.C_lost = pyo.Param(modelo.T, initialize=lambda m, t: C_lost_vp[t-1])

# Variables de decisión
modelo.x   = pyo.Var(modelo.T,           domain=pyo.NonNegativeReals)
modelo.l   = pyo.Var(modelo.T,           domain=pyo.NonNegativeReals)
modelo.m   = pyo.Var(modelo.K, modelo.T, domain=pyo.NonNegativeIntegers)
modelo.Y   = pyo.Var(modelo.K, modelo.T, domain=pyo.NonNegativeIntegers)
modelo.h   = pyo.Var(modelo.T,           domain=pyo.NonNegativeIntegers)
modelo.f   = pyo.Var(modelo.T,           domain=pyo.NonNegativeIntegers)
modelo.W   = pyo.Var(modelo.T,           domain=pyo.PositiveIntegers)
modelo.n   = pyo.Var(modelo.T,           domain=pyo.NonNegativeIntegers)
modelo.P_a = pyo.Var(modelo.T,           domain=pyo.PositiveIntegers)

def demanda(m, t):
    return m.x[t] + m.l[t] == m.d[t]

modelo.demanda = pyo.Constraint(modelo.T, rule=demanda)

def capacidad_maquinas(m,t):
    return m.x[t] <= sum(m.Y[k,t]*m.Capacidad_k[k] for k in m.K)

modelo.capacidad_maquinas = pyo.Constraint(modelo.T, rule=capacidad_maquinas)

def capacidad_mano_de_obra(m,t):
    return m.alfa * m.x[t] <= m.H * m.W[t]

modelo.capacidad_mano_de_obra = pyo.Constraint(modelo.T, rule=capacidad_mano_de_obra)

def acumulacion_maquinas(mod,k,t):
    if (t==1):
        return mod.Y[k,t] == mod.Y0[k]+mod.m[k,t]
    return mod.Y[k,t] == mod.Y[k,t-1]+mod.m[k,t]

modelo.acumulacion_maquinas = pyo.Constraint(modelo.K, modelo.T, rule=acumulacion_maquinas)

def balance_operarios(m,t):
    if (t==1):
        return m.W[t]==M_0 + m.h[t]-m.f[t]
    return m.W[t]==m.W[t-1] + m.h[t]-m.f[t]

modelo.balance_operarios = pyo.Constraint(modelo.T, rule=balance_operarios)

def plantas_activas(m,t):
    if (t==1):
        return m.P_a[t] == P_0 + m.n[t]
    return m.P_a[t] == m.P_a[t-1] + m.n[t]

modelo.plantas_activas = pyo.Constraint(modelo.T, rule=plantas_activas)

def restriccion_espacio(m, t):
    return (sum(m.S_yk[k]*m.Y[k,t] for k in m.K) + m.S_m*m.W[t] <= m.u*m.S_p*m.P_a[t])

modelo.restriccion_espacio = pyo.Constraint(modelo.T, rule=restriccion_espacio)

def nivel_servicio(m, t):
    return m.l[t] <= m.V_max*m.d[t]

modelo.nivel_servicio = pyo.Constraint(modelo.T, rule=nivel_servicio)

def sobrecapacidad_prod_maquinas(m, t):
    return sum(m.Capacidad_k[k]*m.Y[k, t] for k in m.K)<=(1+m.O_max)*m.d[t]

modelo.sobrecapacidad_prod_maquinas = pyo.Constraint(modelo.T, rule=sobrecapacidad_prod_maquinas)

def sobrecapacidad_prod_mano_obra(m, t):
    return m.H*m.W[t]/m.alfa <= (1+m.O_max)*m.d[t]

modelo.sobrecapacidad_prod_mano_obra = pyo.Constraint(modelo.T, rule=sobrecapacidad_prod_mano_obra)

def funcion_objetivo(m):
    return sum(
        sum(m.C_m[k,t]*m.m[k,t] for k in m.K) + m.C_I[t]* m.n[t]+ m.C_hire[t]*m.h[t]+ m.C_fire[t]*m.f[t]
        +m.C_sal[t]*m.W[t]+ m.C_r[t]*m.P_a[t]+ m.C_p[t]*m.x[t]+ m.C_lost[t]*m.l[t]for t in m.T)

modelo.objetivo = pyo.Objective(rule=funcion_objetivo, sense=pyo.minimize)
cbc_path = shutil.which("cbc")
if cbc_path is None:
    raise RuntimeError("CBC no está instalado o no está en el PATH")

solver = pyo.SolverFactory('cbc', executable=cbc_path)
resultado = solver.solve(modelo, tee=True)
if str(resultado.solver.termination_condition)!="optimal":
    print("Modelo inviable")
    exit()

print(f"Costo total VP: {pyo.value(modelo.objetivo):,.0f} CLP\n")

print(f"{'t':>3} {'d_t':>8} {'x_t':>8} {'l_t':>6} {'W_t':>5}"
      f"{'h_t':>5} {'f_t':>5} {'P_a':>4} {'n_t':>4}"
      f"{'m1_t':>5} {'m2_t':>5} {'Y1_t':>5} {'Y2_t':>5}")
print("-" * 80)
for t in modelo.T:
    print(f"{t:>3} {pyo.value(modelo.d[t]):>8.0f}{pyo.value(modelo.x[t]):>8.0f}"
          f"{pyo.value(modelo.l[t]):>6.0f}{pyo.value(modelo.W[t]):>5.0f}"
          f"{pyo.value(modelo.h[t]):>5.0f}{pyo.value(modelo.f[t]):>5.0f}"
          f"{pyo.value(modelo.P_a[t]):>4.0f}{pyo.value(modelo.n[t]):>4.0f}"
          f"{pyo.value(modelo.m[1, t]):>5.0f}{pyo.value(modelo.m[2,t]):>5.0f}"
          f"{pyo.value(modelo.Y[1, t]):>5.0f}{pyo.value(modelo.Y[2,t]):>5.0f}")
