import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

# Fijar semilla para reproducibilidad
np.random.seed(42)

# Extracción de parámetros históricos
df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

# Proporciones de perfiles
proporciones = df_llegadas['profile'].value_counts(normalize=True)
perfiles = proporciones.index.values
prob_perfiles = proporciones.values

# Tasas lambda por BLOQUE (estimadas en 2c), expresadas por hora
bloques = {
    '07:00-10:00': (0, 180),
    '10:00-13:00': (180, 360),
    '13:00-16:00': (360, 540),
    '16:00-19:00': (540, 720),
    '19:00-21:00': (720, 840),
}
dias_totales = df_llegadas['day_id'].nunique()
intervalos = np.arange(0, 840, 60)
tasa_lambda = np.zeros(len(intervalos))
for nombre, (a, b) in bloques.items():
    N_b = ((df_llegadas['event_time'] >= a) & (df_llegadas['event_time'] < b)).sum()
    lam_b = N_b / (dias_totales * (b - a) / 60)          # llegadas/hora del bloque
    tasa_lambda[(intervalos >= a) & (intervalos < b)] = lam_b   # misma tasa para cada hora del bloque

# ALGORITMO DE THINNING (Parte 3a)
def simular_dia_llegadas(lambda_rates, perfiles, prob_perfiles):
    lambda_max = np.max(lambda_rates)
    t = 0
    T_max = 840  
    llegadas = []
    
    while t < T_max:

        t += np.random.exponential(60 / lambda_max)
        
        if t >= T_max:
            break
            
        hora_idx = int(t // 60)
        if hora_idx > 13: 
            hora_idx = 13
            
        prob_aceptar = lambda_rates[hora_idx] / lambda_max
        
        if np.random.rand() < prob_aceptar:
            perfil_asignado = np.random.choice(perfiles, p=prob_perfiles)
            llegadas.append({'tiempo_llegada': t, 'perfil': perfil_asignado})
            
    return pd.DataFrame(llegadas)

# SIMULAR 200 DÍAS (Parte 3b)
N_simulaciones = 200
todas_llegadas_sim = []

for dia in range(N_simulaciones):
    df_dia = simular_dia_llegadas(tasa_lambda, perfiles, prob_perfiles)
    if not df_dia.empty:
        df_dia['dia_sim'] = dia
        todas_llegadas_sim.append(df_dia)

df_simulacion = pd.concat(todas_llegadas_sim)


# ============================================================
# VALIDACIÓN (Parte 3b): histórico vs simulado
def matriz_conteos(df, col_dia, n_dias_idx, perfil=None):
    if perfil is not None:
        df = df[df['perfil'] == perfil]
    return (df.groupby([col_dia, 'intervalo']).size().unstack(fill_value=0)
              .reindex(index=n_dias_idx, columns=intervalos, fill_value=0))

df_llegadas['perfil'] = df_llegadas['profile']
df_llegadas['intervalo'] = (df_llegadas['event_time'] // 60) * 60
df_simulacion['intervalo'] = (df_simulacion['tiempo_llegada'] // 60) * 60
dias_hist = sorted(df_llegadas['day_id'].unique())
C_hist = matriz_conteos(df_llegadas, 'day_id', dias_hist)
C_sim = matriz_conteos(df_simulacion, 'dia_sim', range(N_simulaciones))

# 1) Media y varianza por hora + test de Mann-Whitney (hist vs sim)
print("=" * 75)
print("1) LLEGADAS POR HORA: HISTÓRICO VS SIMULADO")
print("-" * 75)
print(f"{'Hora':<7}{'Media hist':>11}{'Media sim':>11}{'Var hist':>10}{'Var sim':>10}{'p MW':>8}")
for t in intervalos:
    p_mw = stats.mannwhitneyu(C_hist[t], C_sim[t]).pvalue
    print(f"{7 + t//60:02d}:00  {C_hist[t].mean():>10.2f}{C_sim[t].mean():>11.2f}"
          f"{C_hist[t].var(ddof=1):>10.2f}{C_sim[t].var(ddof=1):>10.2f}{p_mw:>8.3f}")
error_rel = (np.abs(C_sim.mean() - C_hist.mean()) / C_hist.mean()) * 100
print(f"Error relativo medio: {error_rel.mean():.2f}%  (máximo: {error_rel.max():.2f}%)")

# 2) Total de llegadas por jornada
tot_hist, tot_sim = C_hist.sum(axis=1), C_sim.sum(axis=1)
mw_tot = stats.mannwhitneyu(tot_hist, tot_sim)
print("\n" + "=" * 75)
print("2) TOTAL DE LLEGADAS POR JORNADA")
print("-" * 75)
print(f"Histórico: media={tot_hist.mean():.2f}, var={tot_hist.var(ddof=1):.2f}")
print(f"Simulado : media={tot_sim.mean():.2f}, var={tot_sim.var(ddof=1):.2f}")
print(f"Mann-Whitney: U={mw_tot.statistic:.1f}, p-value={mw_tot.pvalue:.4f}")
# 3) Proporción de perfiles
tabla_perf = pd.DataFrame({'hist': df_llegadas['perfil'].value_counts(),
                           'sim': df_simulacion['perfil'].value_counts()})
chi2_p, p_p, gl_p, _ = stats.chi2_contingency(tabla_perf.values)
print("\n" + "=" * 75)
print("3) PROPORCIÓN DE PERFILES")
print("-" * 75)
print((tabla_perf / tabla_perf.sum()).round(4).to_string())
print(f"Chi-cuadrado de homogeneidad: chi2={chi2_p:.4f}, gl={gl_p}, p-value={p_p:.4f}")

# ------------------ GRÁFICOS ------------------
x = intervalos + 30                              
marcas_x = np.arange(0, 841, 120)
etiquetas_x = [f"{7 + t//60:02d}:00" for t in marcas_x]

# Figura A: global 
plt.figure(figsize=(10, 5))
plt.step(np.r_[intervalos, 840], np.r_[tasa_lambda, tasa_lambda[-1]], where='post',
         color='grey', label='λ(t) estimada')
plt.errorbar(x - 5, C_hist.mean(), 1.96 * C_hist.std(ddof=1) / np.sqrt(len(dias_hist)),
             fmt='o', capsize=3, label='Histórico (40 jornadas), IC 95%')
plt.errorbar(x + 5, C_sim.mean(), 1.96 * C_sim.std(ddof=1) / np.sqrt(N_simulaciones),
             fmt='x', capsize=3, label='Simulado (200 jornadas), IC 95%')
plt.title('Validación del generador: llegadas por hora')
plt.xlabel('Hora del día'); plt.ylabel('Llegadas promedio por hora')
plt.xticks(marcas_x, etiquetas_x); plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()

# Figura B: por perfil
plt.figure(figsize=(10, 5))
for i, p in enumerate(tabla_perf.index):
    plt.plot(x, matriz_conteos(df_llegadas, 'day_id', dias_hist, p).mean(), 'o-', color=f'C{i}',
             label=f'{p} histórico')
    plt.plot(x, matriz_conteos(df_simulacion, 'dia_sim', range(N_simulaciones), p).mean(), 'x--',
             color=f'C{i}', label=f'{p} simulado')
plt.title('Validación del generador: llegadas por hora según perfil')
plt.xlabel('Hora del día'); plt.ylabel('Llegadas promedio por hora')
plt.xticks(marcas_x, etiquetas_x); plt.legend(ncol=2, fontsize=8); plt.grid(True, alpha=0.3)
plt.tight_layout()

# Figura C: total por jornada e índice de dispersión
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
bins = np.arange(300, 461, 10)
ax[0].hist(tot_hist, bins=bins, density=True, alpha=0.5, label='Histórico')
ax[0].hist(tot_sim, bins=bins, density=True, alpha=0.5, label='Simulado')
ax[0].set(title='Llegadas totales por jornada', xlabel='Llegadas', ylabel='Densidad'); ax[0].legend()
ax[1].bar(x - 8, C_hist.var(ddof=1) / C_hist.mean(), width=16, label='Histórico')
ax[1].bar(x + 8, C_sim.var(ddof=1) / C_sim.mean(), width=16, label='Simulado')
ax[1].axhline(1, color='black', linestyle='--', linewidth=1)
ax[1].set(title='Índice de dispersión (varianza/media) por hora', xlabel='Hora del día')
ax[1].set_xticks(marcas_x, etiquetas_x); ax[1].legend()
plt.tight_layout()
plt.show()