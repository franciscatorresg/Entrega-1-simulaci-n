import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Fijar semilla para reproducibilidad (requisito de la simulación)
np.random.seed(42)

# 1. EXTRAER PARÁMETROS DEL HISTÓRICO
df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

# Proporciones de perfiles
proporciones = df_llegadas['profile'].value_counts(normalize=True)
perfiles = proporciones.index.values
prob_perfiles = proporciones.values

# Tasas lambda por bloque de 60 minutos
df_llegadas['intervalo'] = (df_llegadas['event_time'] // 60) * 60
dias_totales = df_llegadas['day_id'].nunique()
tasa_lambda = (df_llegadas.groupby('intervalo').size() / dias_totales).reindex(np.arange(0, 840, 60), fill_value=0).values

# 2. GENERADOR: ALGORITMO DE THINNING (Parte 3a)
def simular_dia_llegadas(lambda_rates, perfiles, prob_perfiles):
    lambda_max = np.max(lambda_rates)
    t = 0
    T_max = 840  # 14 horas de operación (de 07:00 a 21:00)
    llegadas = []
    
    while t < T_max:
        # Generar tiempo hasta la próxima llegada (usando tasa máxima por minuto)
        # En numpy, exponential recibe scale = 1/rate
        t += np.random.exponential(60 / lambda_max)
        
        if t >= T_max:
            break
            
        # Determinar en qué bloque de 60 minutos cayó la llegada
        hora_idx = int(t // 60)
        if hora_idx > 13: 
            hora_idx = 13
            
        # Probabilidad de aceptar la llegada
        prob_aceptar = lambda_rates[hora_idx] / lambda_max
        
        # Lanzar moneda para aceptar/rechazar (Adelgazamiento)
        if np.random.rand() < prob_aceptar:
            perfil_asignado = np.random.choice(perfiles, p=prob_perfiles)
            llegadas.append({'tiempo_llegada': t, 'perfil': perfil_asignado})
            
    return pd.DataFrame(llegadas)

# 3. VALIDACIÓN: SIMULAR 100 DÍAS (Parte 3b)
N_simulaciones = 100
todas_llegadas_sim = []

for dia in range(N_simulaciones):
    df_dia = simular_dia_llegadas(tasa_lambda, perfiles, prob_perfiles)
    if not df_dia.empty:
        df_dia['dia_sim'] = dia
        todas_llegadas_sim.append(df_dia)

df_simulacion = pd.concat(todas_llegadas_sim)

# 4. GRAFICAR RESULTADOS PARA EL INFORME
df_simulacion['intervalo'] = (df_simulacion['tiempo_llegada'] // 60) * 60
sim_por_hora = df_simulacion.groupby('intervalo').size() / N_simulaciones
sim_por_hora = sim_por_hora.reindex(np.arange(0, 840, 60), fill_value=0)

plt.figure(figsize=(10, 5))
plt.plot(np.arange(0, 840, 60), tasa_lambda, label='Histórico (Teórico)', marker='o', linewidth=2)
plt.plot(np.arange(0, 840, 60), sim_por_hora.values, label='Simulado (Promedio 100 días)', marker='x', linestyle='--', linewidth=2)
plt.title('Validación del Generador de Llegadas: Histórico vs Simulado')
plt.xlabel('Minuto de operación (0 = 07:00)')
plt.ylabel('Llegadas promedio por hora')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()