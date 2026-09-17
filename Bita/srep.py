import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from ajustes import ajustar_distribucion

#Paso 1: cargar log_reparaciones_limpio.csv y verificar que se ve como se espera
df_rep = pd.read_csv('log_reparaciones_limpio.csv')

print(df_rep.shape)
print(df_rep.columns.tolist())
print(df_rep.isnull().sum())

#Paso 2: boxplot comparativo y test de Kruskal-Wallis por machine_type
orden = df_rep.groupby('machine_type')['repair_duration_min'].median().sort_values().index

plt.figure(figsize=(10, 6))
datos_por_grupo = [df_rep[df_rep['machine_type'] == m]['repair_duration_min'].values for m in orden]
plt.boxplot(datos_por_grupo, tick_labels=orden)
plt.ylabel('repair_duration_min')
plt.title('repair_duration_min por machine_type')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('boxplot_reparacion_por_machine_type.png')
plt.close()

h, p = stats.kruskal(*datos_por_grupo)
print(f'H = {h:.4f}')
print(f'p-value = {p:.6f}')

#Paso 3: mapear machine_type a categoria (segun diccionario_logs.xlsx, hoja Recursos) y test de Kruskal-Wallis por categoria
categoria_por_maquina = {
    'treadmill': 'Cardio',
    'chest_press': 'Empuje',
    'shoulder_press': 'Empuje',
    'chest_fly': 'Empuje',
    'lat_pulldown': 'Jalón',
    'seated_row': 'Jalón',
    'biceps_curl': 'Jalón',
    'leg_press': 'Piernas',
    'leg_curl': 'Piernas',
    'leg_extension': 'Piernas',
    'cable': 'Multifuncional'
}

df_rep['categoria'] = df_rep['machine_type'].map(categoria_por_maquina)

print(df_rep['categoria'].value_counts())
print(df_rep['categoria'].isnull().sum())

orden_cat = df_rep.groupby('categoria')['repair_duration_min'].median().sort_values().index

plt.figure(figsize=(8, 6))
datos_por_categoria = [df_rep[df_rep['categoria'] == c]['repair_duration_min'].values for c in orden_cat]
plt.boxplot(datos_por_categoria, tick_labels=orden_cat)
plt.ylabel('repair_duration_min')
plt.title('repair_duration_min por categoria')
plt.tight_layout()
plt.savefig('boxplot_reparacion_por_categoria.png')
plt.close()

h_cat, p_cat = stats.kruskal(*datos_por_categoria)
print(f'H = {h_cat:.4f}')
print(f'p-value = {p_cat:.6f}')

#Paso 4: verificar homogeneidad interna de cada categoria (Kruskal-Wallis dentro de Empuje, Jalon y Piernas)
categorias_multi = ['Empuje', 'Jalón', 'Piernas']

for cat in categorias_multi:
    maquinas_en_categoria = df_rep[df_rep['categoria'] == cat]['machine_type'].unique()
    datos_internos = [df_rep[df_rep['machine_type'] == m]['repair_duration_min'].values for m in maquinas_en_categoria]
    h_int, p_int = stats.kruskal(*datos_internos)
    print(f'{cat} ({list(maquinas_en_categoria)}): H = {h_int:.4f}, p-value = {p_int:.6f}')

#Paso 5: ajuste y test de bondad de ajuste por categoria, con las 4 candidatas de contexto
candidatas = ['expon', 'gamma', 'lognorm', 'weibull_min']

tablas_resultado = []
for cat in df_rep['categoria'].unique():
    datos_cat = df_rep[df_rep['categoria'] == cat]['repair_duration_min'].values
    tabla_cat = ajustar_distribucion(datos_cat, f'reparacion_{cat}', candidatas)
    tablas_resultado.append(tabla_cat)

tabla_srep = pd.concat(tablas_resultado, ignore_index=True)
print(tabla_srep[['grupo', 'distribucion', 'estadistico', 'p_value', 'p_value_simulado', 'conclusion']])

#Paso 6: revisar si hay una acumulacion de valores en o cerca del maximo para Cardio
datos_cardio = df_rep[df_rep['categoria'] == 'Cardio']['repair_duration_min']
print(datos_cardio.sort_values(ascending=False).head(10))
print()
print((datos_cardio == 50).sum(), 'observaciones exactamente en 50')
print((datos_cardio >= 48).sum(), 'observaciones en 48 o mas')

