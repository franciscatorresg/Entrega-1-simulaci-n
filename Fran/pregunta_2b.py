import pandas as pd
import numpy as np
import scipy.stats as stats

df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

tamano_intervalo = 60
df_llegadas['intervalo'] = (df_llegadas['event_time'] // tamano_intervalo) * tamano_intervalo

dias = df_llegadas['day_id'].unique()
intervalos_posibles = np.arange(0, 840, tamano_intervalo) 
grilla = pd.MultiIndex.from_product([dias, intervalos_posibles], names=['day_id', 'intervalo'])

conteos_global = df_llegadas.groupby(['day_id', 'intervalo']).size().reset_index(name='llegadas')
conteos_global = conteos_global.set_index(['day_id', 'intervalo']).reindex(grilla, fill_value=0).reset_index()

print("="*60)
print("TEST 1: ESTACIONARIEDAD (Kruskal-Wallis)")
print("H0: La distribución de las llegadas es igual en todos los intervalos (Tasa constante).")
print("H1: Al menos un intervalo tiene una distribución distinta (Tasa variable).")
print("-" * 60)

grupos_intervalos = [group['llegadas'].values for name, group in conteos_global.groupby('intervalo')]
stat_kw, pval_kw = stats.kruskal(*grupos_intervalos)

print(f"Estadístico de prueba: {stat_kw:.4f}")
print(f"P-value: {pval_kw:.4e}")
if pval_kw < 0.05:
    print("Conclusión: Se rechaza H0. La tasa de llegadas cambia sistemáticamente (Proceso No Estacionario).")
else:
    print("Conclusión: No se rechaza H0. La tasa es constante (Estacionaria).")

print("\n" + "="*60)
print("TEST 2: HOMOGENEIDAD DE PERFILES (Chi-cuadrado de Independencia)")
print("H0: La proporción de perfiles es independiente del intervalo de tiempo.")
print("H1: La proporción de perfiles cambia según el intervalo de tiempo.")
print("-" * 60)

tabla_contingencia = pd.crosstab(df_llegadas['intervalo'], df_llegadas['profile'])
chi2_stat, p_val_chi2, dof, expected = stats.chi2_contingency(tabla_contingencia)

print(f"Estadístico de prueba: {chi2_stat:.4f}")
print(f"P-value: {p_val_chi2:.4f}")
if p_val_chi2 < 0.05:
    print("Conclusión: Se rechaza H0. Existen diferencias sistemáticas entre grupos a lo largo del día.")
else:
    print("Conclusión: No se rechaza H0. La estructura de perfiles es consistente durante la jornada.")

print("\n" + "="*60)
print("TEST 3: PROPIEDAD DE POISSON (Test de Dispersión / Método de Fisher)")
print("H0: Los conteos siguen una distribución de Poisson (Varianza = Media) en cada intervalo.")
print("H1: Los conteos no siguen una distribución de Poisson.")
print("-" * 60)

p_values_dispersion = []
for name, group in conteos_global.groupby('intervalo'):
    conteos = group['llegadas'].values
    n = len(conteos)
    media = np.mean(conteos)
    varianza = np.var(conteos, ddof=1)
    
    if media > 0:
        # Estadístico: (n-1)*S^2 / media
        disp_stat = (n - 1) * varianza / media
        # P-value a dos colas para detectar sobre o sub-dispersión
        p_val = 2 * min(stats.chi2.cdf(disp_stat, df=n-1), 1 - stats.chi2.cdf(disp_stat, df=n-1))
        p_values_dispersion.append(p_val)

# Combinar los p-values de todos los intervalos para dar una conclusión global
stat_fisher, pval_fisher = stats.combine_pvalues(p_values_dispersion)

print(f"Estadístico de prueba (Fisher combinado): {stat_fisher:.4f}")
print(f"P-value global: {pval_fisher:.4f}")
if pval_fisher < 0.05:
    print("Conclusión: Se rechaza H0. Los conteos exhiben una dispersión estadísticamente distinta a Poisson.")
else:
    print("Conclusión: No se rechaza H0. El proceso es compatible con las propiedades de Poisson.")
print("="*60)


# ============================================================
# BLOQUES HORARIOS (minutos desde las 07:00) observados en 2a
# ============================================================
bloques = {
    '07:00-10:00': (0, 180),
    '10:00-13:00': (180, 360),
    '13:00-16:00': (360, 540),
    '16:00-19:00': (540, 720),
    '19:00-21:00': (720, 840),
}
# Total de llegadas por intervalo (sumando las 40 jornadas)
total_por_intervalo = conteos_global.groupby('intervalo')['llegadas'].sum()

print("\n" + "="*60)
print("TEST 4: TASA CONSTANTE DENTRO DE CADA BLOQUE (Chi-cuadrado de homogeneidad)")
print("H0: Todas las horas del bloque tienen la misma tasa.")
print("H1: Al menos una hora del bloque tiene una tasa distinta.")
print("-" * 60)
for nombre, (a, b) in bloques.items():
    conteos_bloque = total_por_intervalo.loc[a:b - 1]
    chi2_b, p_b = stats.chisquare(conteos_bloque)
    print(f"{nombre}: conteos={conteos_bloque.tolist()}, chi2={chi2_b:.4f}, gl={len(conteos_bloque)-1}, p-value={p_b:.4f}")


print("\n" + "="*60)
print("TEST 5: UNIFORMIDAD CONDICIONAL DENTRO DE CADA BLOQUE (Kolmogorov-Smirnov)")
print("H0: Dentro del bloque, los instantes de llegada son Uniformes(a, b).")
print("H1: Los instantes de llegada no son uniformes dentro del bloque.")
print("-" * 60)
for nombre, (a, b) in bloques.items():
    tiempos = df_llegadas.loc[(df_llegadas['event_time'] >= a) & (df_llegadas['event_time'] < b), 'event_time']
    ks_u = stats.kstest((tiempos - a) / (b - a), 'uniform')
    print(f"{nombre}: n={len(tiempos)}, D={ks_u.statistic:.4f}, p-value={ks_u.pvalue:.4f}")


print("\n" + "="*60)
print("TEST 6: TIEMPOS ENTRE LLEGADAS EXPONENCIALES POR BLOQUE (Kolmogorov-Smirnov)")
print("H0: Los tiempos entre llegadas del bloque siguen una Exponencial.")
print("H1: Los tiempos entre llegadas no siguen una Exponencial.")
print("-" * 60)
for nombre, (a, b) in bloques.items():
    sub = df_llegadas[(df_llegadas['event_time'] >= a) & (df_llegadas['event_time'] < b)]
    entre_llegadas = []
    for dia, grupo in sub.groupby('day_id'):          # solo diferencias dentro de un mismo día
        entre_llegadas.extend(np.diff(np.sort(grupo['event_time'].values)))
    entre_llegadas = np.array(entre_llegadas)
    media_ia = entre_llegadas.mean()
    ks_e = stats.kstest(entre_llegadas, 'expon', args=(0, media_ia))
    print(f"{nombre}: n={len(entre_llegadas)}, media={media_ia:.3f} min, "
          f"CV={entre_llegadas.std()/media_ia:.3f}, D={ks_e.statistic:.4f}, p-value={ks_e.pvalue:.4f}")
    

print("\n" + "="*60)
print("TEST 7: INCREMENTOS INDEPENDIENTES (Correlación entre horas consecutivas / Fisher)")
print("H0: Los conteos de horas consecutivas no están correlacionados.")
print("H1: Existe correlación entre conteos de horas consecutivas.")
print("-" * 60)
matriz = conteos_global.pivot(index='day_id', columns='intervalo', values='llegadas')
p_values_corr, correlaciones = [], []
for t in intervalos_posibles[:-1]:
    r, p_r = stats.pearsonr(matriz[t], matriz[t + tamano_intervalo])
    correlaciones.append(r)
    p_values_corr.append(p_r)
stat_corr, pval_corr = stats.combine_pvalues(p_values_corr)
print(f"Correlación promedio: {np.mean(correlaciones):.4f}")
print(f"Estadístico de prueba (Fisher combinado): {stat_corr:.4f}")
print(f"P-value global: {pval_corr:.4f}")


print("\n" + "="*60)
print("TEST 8: ESTABILIDAD ENTRE JORNADAS")
print("-" * 60)
totales_diarios = matriz.sort_index().sum(axis=1).values
n_dias = len(totales_diarios)
disp_dias = (n_dias - 1) * np.var(totales_diarios, ddof=1) / np.mean(totales_diarios)
p_disp_dias = stats.chi2.sf(disp_dias, df=n_dias - 1)
print("8a) H0: Todas las jornadas tienen la misma intensidad (totales diarios Poisson).")
print(f"    Estadístico: {disp_dias:.4f} (gl={n_dias-1}), p-value: {p_disp_dias:.4f}")
rho, p_tend = stats.spearmanr(np.arange(n_dias), totales_diarios)
print("8b) H0: No existe tendencia en el total diario de llegadas (Spearman).")
print(f"    Estadístico: rho={rho:.4f}, p-value: {p_tend:.4f}")
print("="*60)