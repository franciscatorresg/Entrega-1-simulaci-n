import pandas as pd
import numpy as np
import scipy.stats as stats

df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

T = 840                                   # minutos de admisión (07:00 a 21:00)
dias = sorted(df_llegadas['day_id'].unique())
r = len(dias)                             # número de jornadas

bloques = {
    '07:00-10:00': (0, 180),
    '10:00-13:00': (180, 360),
    '13:00-16:00': (360, 540),
    '16:00-19:00': (540, 720),
    '19:00-21:00': (720, 840),
}

print("="*60)
print("TEST 1 (Paso 1): LLEGADAS DIARIAS POISSON (Chi-cuadrado de bondad de ajuste)")
print("H0: La cantidad de llegadas por jornada distribuye Poisson(alpha).")
print("H1: La cantidad de llegadas por jornada no distribuye Poisson.")
print("-" * 60)
n_dia = df_llegadas.groupby('day_id').size().values
alpha_hat = n_dia.mean()                  # EMV de alpha
# Intervalos [a_{j-1}, a_j) elegidos para que cada uno tenga frecuencia esperada >= 5
limites = [0, 370, 380, 390, 400, np.inf]
observados = np.histogram(n_dia, bins=limites)[0]
cdf = [stats.poisson.cdf(l - 1, alpha_hat) if np.isfinite(l) else 1.0 for l in limites]
p_j = np.diff(cdf)
esperados = r * p_j
T_chi = np.sum((observados - esperados)**2 / esperados)
gl = len(observados) - 1 - 1              # k - 1 - (parámetros estimados)
p_chi = stats.chi2.sf(T_chi, gl)
print(f"alpha estimado: {alpha_hat:.2f} llegadas por jornada")
print(f"Observados: {observados.tolist()}")
print(f"Esperados : {np.round(esperados, 2).tolist()}")
print(f"Estadístico de prueba: {T_chi:.4f} (gl = {gl})")
print(f"P-value: {p_chi:.4f}")

print("\n" + "="*60)
print("TEST 2 (Paso 2): MISMO COMPORTAMIENTO EN TODAS LAS JORNADAS (Kruskal-Wallis)")
print("H0: Los tiempos de llegada de todas las jornadas provienen de la misma distribución.")
print("H1: Al menos una jornada tiene una distribución distinta.")
print("-" * 60)
tiempos_por_dia = [g['event_time'].values for _, g in df_llegadas.groupby('day_id')]
stat_kw, pval_kw = stats.kruskal(*tiempos_por_dia)
print(f"Estadístico de prueba: {stat_kw:.4f}")
print(f"P-value: {pval_kw:.4f}")

print("\n" + "="*60)
print("TEST 3 (Paso 3.1): ¿PROCESO POISSON HOMOGÉNEO? (Kolmogorov-Smirnov)")
print("H0: Los tiempos de llegada distribuyen Uniforme(0, T) (tasa constante).")
print("H1: Los tiempos de llegada no son uniformes (tasa variable).")
print("-" * 60)
ks_global = stats.kstest(df_llegadas['event_time'] / T, 'uniform')
print(f"Estadístico de prueba: D = {ks_global.statistic:.4f}")
print(f"P-value: {ks_global.pvalue:.4e}")

print("\n" + "="*60)
print("TEST 4: TASA CONSTANTE DENTRO DE CADA BLOQUE (Chi-cuadrado)")
print("H0: Todas las horas del bloque tienen la misma tasa.")
print("H1: Al menos una hora del bloque tiene una tasa distinta.")
print("-" * 60)
df_llegadas['intervalo'] = (df_llegadas['event_time'] // 60) * 60
total_por_intervalo = df_llegadas.groupby('intervalo').size()
for nombre, (a, b) in bloques.items():
    conteos_bloque = total_por_intervalo.loc[a:b - 1]
    chi2_b, p_b = stats.chisquare(conteos_bloque)
    print(f"{nombre}: conteos={conteos_bloque.tolist()}, chi2={chi2_b:.4f}, gl={len(conteos_bloque)-1}, p-value={p_b:.4f}")

print("\n" + "="*60)
print("TEST 5: POISSON HOMOGÉNEO DENTRO DE CADA BLOQUE (Kolmogorov-Smirnov)")
print("H0: Dentro del bloque, los tiempos de llegada son Uniformes(a, b).")
print("H1: Los tiempos de llegada no son uniformes dentro del bloque.")
print("-" * 60)
for nombre, (a, b) in bloques.items():
    tiempos = df_llegadas.loc[(df_llegadas['event_time'] >= a) & (df_llegadas['event_time'] < b), 'event_time']
    ks_u = stats.kstest((tiempos - a) / (b - a), 'uniform')
    print(f"{nombre}: n={len(tiempos)}, D={ks_u.statistic:.4f}, p-value={ks_u.pvalue:.4f}")

print("\n" + "="*60)
print("TEST 6: HOMOGENEIDAD DE PERFILES (Chi-cuadrado de independencia)")
print("H0: La proporción de perfiles es independiente del intervalo de tiempo.")
print("H1: La proporción de perfiles cambia según el intervalo de tiempo.")
print("-" * 60)
tabla_contingencia = pd.crosstab(df_llegadas['intervalo'], df_llegadas['profile'])
chi2_stat, p_val_chi2, dof, expected = stats.chi2_contingency(tabla_contingencia)
print(f"Estadístico de prueba: {chi2_stat:.4f} (gl = {dof})")
print(f"P-value: {p_val_chi2:.4f}")
