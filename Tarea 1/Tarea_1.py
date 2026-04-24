import numpy as np
import pyomo.environ as pyo
import shutil

numero_de_grupo = 14
rng = np.random.default_rng(numero_de_grupo)

T = 24
M_0 = 8
Y0 = [2,1]
P_0 = 1

def generar_normal(mu,sigma,limite_inferior=0, es_entero=True, limite_superior=None):
    valor = rng.normal(mu,sigma)
    if es_entero:
        valor = round(valor)
    valor = max(limite_inferior, valor)
    if limite_superior is not None:
        valor = min(limite_superior, valor)
    return valor

def generar_uniforme(a,b,es_entero=False):
    valor = rng.uniform(a,b)
    if es_entero:
        valor = max(0, round(valor))
    return valor

def valor_presente(Variable_contexto):
    lista = [Variable_contexto]
    for t in range(2,T+1):
        lista.append(Variable_contexto*((1+pi_min)/(1+r))**(t-1))
    return lista

InfProm = generar_normal(0.04,0.002,0.03,False,0.05)
R = generar_normal(0.10,0.005,0.09,False,0.11)
pi_min = (1+InfProm)**0.25-1
r = (1+R)**0.25-1
d_1 = generar_normal(25000,0.05*25000,1)
r_t = generar_uniforme(1.02,1.04)
d_t = [d_1]
for t in range(2,T+1):
    d_t.append(round(d_t[-1]*r_t))
    r_t = generar_uniforme(1.02,1.04)

rho_1 = generar_normal(6000,0.05*6000)
rho_2 = generar_normal(11500,0.05*11500)
Capacidad = [rho_1,rho_2]
alfa = generar_normal(0.1,0.15*0.1,es_entero=False)
S_p = generar_normal(100,0.05*100,es_entero=False)
S_yk = [generar_normal(15,0.05 * 15,es_entero=False) for _ in range(2)]
S_m = generar_normal(6,6*0.05, es_entero=False)

C_m11 = generar_normal(18_000_000,18_000_000*0.05)
C_m21 = generar_normal(32_000_000,32_000_000*0.05)
C_hire1 = generar_normal(500_000,500_000*0.05)
C_fire1 = generar_normal(1_800_000,1_800_000*0.05)
C_sal1 = generar_normal(7_200_000,7_200_000*0.03)
C_r1 = generar_normal(15_000_000,15_000_000*0.05)
C_I1 = generar_normal(45_000_000,45_000_000*0.05)
C_p1 = generar_normal(2_500,2_500*0.05)
C_lost1 = generar_normal(12_000,12_000*0.05)

C_m1_vp = valor_presente(C_m11)
C_m2_vp = valor_presente(C_m21)
C_hire_vp = valor_presente(C_hire1)
C_fire_vp = valor_presente(C_fire1)
C_sal_vp = valor_presente(C_sal1)
C_r_vp = valor_presente(C_r1)
C_I_vp = valor_presente(C_I1)
C_p_vp = valor_presente(C_p1)
C_lost_vp = valor_presente(C_lost1)

def demanda(m,t):
    return m.x[t]+m.l[t] == m.d[t]

def capacidad_maquinas(m,t):
    return m.x[t] <= sum(m.Y[k, t]*m.Capacidad_k[k] for k in m.K)

def capacidad_mano_de_obra(m,t):
    return m.alfa*m.x[t] <= m.H*m.W[t]

def acumulacion_maquinas(mod,k,t):
    if t==1:
        return mod.Y[k,t] == mod.Y0[k]+mod.m[k,t]
    return mod.Y[k,t] == mod.Y[k,t-1]+mod.m[k,t]

def balance_operarios(mod, t):
    if t == 1:
        return mod.W[t] == M_0+mod.h[t]-mod.f[t]
    return mod.W[t] == mod.W[t-1]+mod.h[t]-mod.f[t]

def plantas_activas(mod,t):
    if t == 1:
        return mod.P_t[t] == P_0 + mod.n[t]
    return mod.P_t[t] == mod.P_t[t - 1] + mod.n[t]

def restriccion_espacio(mod,t):
    return (sum(mod.S_yk[k]*mod.Y[k, t] for k in mod.K) + mod.S_m*mod.W[t]<= mod.u*mod.S_p*mod.P_t[t])

def nivel_servicio(m, t):
    return m.l[t] <= m.V_max*m.d[t]

def sobrecapacidad_prod_maquinas(m,t):
    return sum(m.Capacidad_k[k]*m.Y[k, t] for k in m.K) <= (1 + m.O_max)*m.d[t]

def sobrecapacidad_prod_mano_obra(m,t):
    return m.H*m.W[t]/m.alfa <= (1+m.O_max)*m.d[t]

def funcion_objetivo_base(m):
    return sum(sum(m.C_m[k, t] * m.m[k, t] for k in m.K)+ m.C_I[t]*m.n[t]+ m.C_hire[t]*m.h[t]+ m.C_fire[t]*m.f[t]
    + m.C_sal[t]*m.W[t]+ m.C_r[t]*m.P_t[t]+ m.C_p[t]*m.x[t]+ m.C_lost[t]*m.l[t] for t in m.T)

def construir_modelo(
    restricciones_extra=None, #[nombre,indices,rule]
    variables_extra=None, #[nombre,indices,dominio]
    funcion_objetivo=None, # por defecto usa la de antes de las variables
    params_extra=None, # dict{nombre:valor}
):
    m = pyo.ConcreteModel()
    m.T = pyo.RangeSet(1,T)
    m.K = pyo.RangeSet(1,2)
    m.Y0 = pyo.Param(m.K,initialize=lambda mo,k:Y0[k-1])
    m.H = pyo.Param(initialize=480)
    m.d = pyo.Param(m.T,initialize=lambda mo, t: d_t[t-1])
    m.Capacidad_k = pyo.Param(m.K,     initialize=lambda mo, i: Capacidad[i - 1])
    m.alfa        = pyo.Param(initialize=alfa)
    m.S_p         = pyo.Param(initialize=S_p)
    m.u           = pyo.Param(initialize=0.7)
    m.S_yk        = pyo.Param(m.K,     initialize=lambda mo, i: S_yk[i - 1])
    m.S_m         = pyo.Param(initialize=S_m)
    m.V_max       = pyo.Param(initialize=0.1)
    m.O_max       = pyo.Param(initialize=0.3)
    m.C_m         = pyo.Param(m.K, m.T, initialize=lambda mo, k, t: C_m1_vp[t-1] if k == 1 else C_m2_vp[t-1])
    m.C_hire      = pyo.Param(m.T,     initialize=lambda mo, t: C_hire_vp[t - 1])
    m.C_fire      = pyo.Param(m.T,     initialize=lambda mo, t: C_fire_vp[t - 1])
    m.C_sal       = pyo.Param(m.T,     initialize=lambda mo, t: C_sal_vp[t - 1])
    m.C_r         = pyo.Param(m.T,     initialize=lambda mo, t: C_r_vp[t - 1])
    m.C_I         = pyo.Param(m.T,     initialize=lambda mo, t: C_I_vp[t - 1])
    m.C_p         = pyo.Param(m.T,     initialize=lambda mo, t: C_p_vp[t - 1])
    m.C_lost      = pyo.Param(m.T,     initialize=lambda mo, t: C_lost_vp[t - 1])

    if params_extra:
        for nombre, valor in params_extra.items():
            m.add_component(nombre, pyo.Param(initialize=valor))

    # Variables base
    m.x   = pyo.Var(m.T,        domain=pyo.NonNegativeReals)
    m.l   = pyo.Var(m.T,        domain=pyo.NonNegativeReals)
    m.m   = pyo.Var(m.K, m.T,   domain=pyo.NonNegativeIntegers)
    m.Y   = pyo.Var(m.K, m.T,   domain=pyo.NonNegativeIntegers)
    m.h   = pyo.Var(m.T,        domain=pyo.NonNegativeIntegers)
    m.f   = pyo.Var(m.T,        domain=pyo.NonNegativeIntegers)
    m.W   = pyo.Var(m.T,        domain=pyo.PositiveIntegers)
    m.n   = pyo.Var(m.T,        domain=pyo.NonNegativeIntegers)
    m.P_t = pyo.Var(m.T,        domain=pyo.PositiveIntegers)

    if variables_extra:
        for nombre, indices, domain in variables_extra:
            if indices is None:
                m.add_component(nombre, pyo.Var(domain=domain))
            elif isinstance(indices, tuple):
                m.add_component(nombre, pyo.Var(*indices, domain=domain))
            else:
                m.add_component(nombre, pyo.Var(indices, domain=domain))

    # Restricciones base
    m.demanda                    = pyo.Constraint(m.T,       rule=demanda)
    m.capacidad_maquinas         = pyo.Constraint(m.T,       rule=capacidad_maquinas)
    m.capacidad_mano_de_obra     = pyo.Constraint(m.T,       rule=capacidad_mano_de_obra)
    m.acumulacion_maquinas       = pyo.Constraint(m.K, m.T,  rule=acumulacion_maquinas)
    m.balance_operarios          = pyo.Constraint(m.T,       rule=balance_operarios)
    m.plantas_activas            = pyo.Constraint(m.T,       rule=plantas_activas)
    m.restriccion_espacio        = pyo.Constraint(m.T,       rule=restriccion_espacio)
    m.nivel_servicio             = pyo.Constraint(m.T,       rule=nivel_servicio)
    m.sobrecapacidad_prod_maquinas   = pyo.Constraint(m.T,   rule=sobrecapacidad_prod_maquinas)
    m.sobrecapacidad_prod_mano_obra  = pyo.Constraint(m.T,   rule=sobrecapacidad_prod_mano_obra)

    if restricciones_extra:
        for nombre, indices, rule in restricciones_extra:
            if indices is None:
                m.add_component(nombre, pyo.Constraint(rule=rule))
            elif isinstance(indices, tuple):
                m.add_component(nombre, pyo.Constraint(*indices, rule=rule))
            else:
                m.add_component(nombre, pyo.Constraint(indices, rule=rule))

    obj_rule = funcion_objetivo if funcion_objetivo is not None else funcion_objetivo_base
    m.objetivo = pyo.Objective(rule=obj_rule, sense=pyo.minimize)
    return m

# ══════════════════════════════════════════════════════════════════════
#  RESOLVER Y MOSTRAR RESULTADOS
# ══════════════════════════════════════════════════════════════════════
cbc_path = shutil.which("cbc")
if cbc_path is None:
    raise RuntimeError("CBC no está instalado o no está en el PATH")
solver = pyo.SolverFactory('cbc', executable=cbc_path)

def resolver(modelo_v, nombre=""):
    resultado = solver.solve(modelo_v)
    if str(resultado.solver.termination_condition) != "optimal":
        print(f"[{nombre}] Modelo inviable")
        return False
    print(f"\n{'─'*60}")
    print(f"  {nombre}")
    print(f"  Costo total VP: {pyo.value(modelo_v.objetivo):,.0f} CLP")
    print(f"{'─'*60}")
    header = (f"{'t':>3}  {'d_t':>8} {'x_t':>8} {'l_t':>8} {'W_t':>5} "
              f"{'h_t':>5} {'f_t':>5} {'P_t':>5} {'n_t':>5} "
              f"{'m1_t':>6} {'m2_t':>6} {'Y1_t':>6} {'Y2_t':>6}")
    print(header)
    print("-" * len(header))
    for t in modelo_v.T:
        print(f"{t:>3}  {pyo.value(modelo_v.d[t]):>8.0f} {pyo.value(modelo_v.x[t]):>8.0f} "
              f"{pyo.value(modelo_v.l[t]):>8.0f} {pyo.value(modelo_v.W[t]):>5.0f} "
              f"{pyo.value(modelo_v.h[t]):>5.0f} {pyo.value(modelo_v.f[t]):>5.0f} "
              f"{pyo.value(modelo_v.P_t[t]):>5.0f} {pyo.value(modelo_v.n[t]):>5.0f} "
              f"{pyo.value(modelo_v.m[1, t]):>6.0f} {pyo.value(modelo_v.m[2, t]):>6.0f} "
              f"{pyo.value(modelo_v.Y[1, t]):>6.0f} {pyo.value(modelo_v.Y[2, t]):>6.0f}")
    return True

# ══════════════════════════════════════════════════════════════════════
#  EJECUCIÓN — MODELO BASE
# ══════════════════════════════════════════════════════════════════════
modelo_base = construir_modelo()
resolver(modelo_base, nombre="Modelo Base")