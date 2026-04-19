import pyomo.environ as pyo

model = pyo.ConcreteModel()

# Conjuntos
model.I = pyo.Set()   # por ejemplo productos
model.T = pyo.Set()   # por ejemplo tiempo

# Parámetros
model.c = pyo.Param(model.I, model.T)   # coeficiente de la función objetivo
model.tope = pyo.Param(model.I, model.T)
model.inv0 = pyo.Param(model.I)         # inventario inicial, si aplica

# Variables de decisión
model.x = pyo.Var(model.I, model.T, domain=pyo.NonNegativeReals)
model.inv = pyo.Var(model.I, model.T, domain=pyo.NonNegativeReals)
model.y = pyo.Var(model.I, model.T, domain=pyo.NonNegativeReals)

# Función objetivo: min sum(variable * parametro)
def obj_rule(m):
    return sum(m.c[i, t] * m.x[i, t] for i in m.I for t in m.T)

model.OBJ = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

# Restricción tipo variable <= tope
def tope_rule(m, i, t):
    return m.x[i, t] <= m.tope[i, t]

model.TopeCon = pyo.Constraint(model.I, model.T, rule=tope_rule)

# Restricción de balance
# inventario actual = inventario anterior + entra - sale
def balance_rule(m, i, t):
    # ejemplo simple: t tiene que estar ordenado si vas a usar el "anterior"
    t_list = list(m.T)
    pos = t_list.index(t)

    if pos == 0:
        return m.inv[i, t] == m.inv0[i] + m.y[i, t] - m.x[i, t]
    else:
        t_prev = t_list[pos - 1]
        return m.inv[i, t] == m.inv[i, t_prev] + m.y[i, t] - m.x[i, t]

model.Balance = pyo.Constraint(model.I, model.T, rule=balance_rule)