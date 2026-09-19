import pandas as pd
import numpy as np
import scipy.stats as stats

# 1. Cargar datos y preparar conteos
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