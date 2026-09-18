import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from ajustes import ajustar_distribucion, CARPETA_FIGURAS

#Paso 1: cargar cardio.csv y verificar que se ve como se espera
df_cardio = pd.read_csv('cardio.csv')

print(df_cardio.shape)
print(df_cardio.columns.tolist())
print(df_cardio.isnull().sum())

#Paso 2: boxplot comparativo y test de Kruskal-Wallis por profile
orden = df_cardio.groupby('profile')['duration_min'].median().sort_values().index

plt.figure(figsize=(8, 6))
datos_por_grupo = [df_cardio[df_cardio['profile'] == p]['duration_min'].values for p in orden]
plt.boxplot(datos_por_grupo, tick_labels=orden)
plt.ylabel('duration_min')
plt.title('duration_min por profile')
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_FIGURAS, 'boxplot_cardio_por_profile.png'))
plt.close()

h, p = stats.kruskal(*datos_por_grupo)
print(f'H = {h:.4f}')
print(f'p-value = {p:.6f}')

#Paso 3: candidatas de contexto (variable continua, positiva, sin cota superior)
candidatas = ['expon', 'gamma', 'lognorm', 'weibull_min']

#Paso 4: ajuste y test de bondad de ajuste por profile
tablas_resultado = []
for perfil in df_cardio['profile'].unique():
    datos_perfil = df_cardio[df_cardio['profile'] == perfil]['duration_min'].values
    tabla_perfil = ajustar_distribucion(datos_perfil, f'cardio_{perfil}', candidatas)
    tablas_resultado.append(tabla_perfil)

tabla_sci = pd.concat(tablas_resultado, ignore_index=True)
print(tabla_sci[['grupo', 'distribucion', 'estadistico', 'p_value', 'p_value_simulado', 'conclusion']])

#Paso 5: revisar la acumulacion en el maximo para el perfil standard
datos_standard = df_cardio[df_cardio['profile'] == 'standard']['duration_min']
tope = datos_standard[datos_standard == datos_standard.max()]

print(f'{len(tope)} de {len(datos_standard)} observaciones ({100*len(tope)/len(datos_standard):.2f}%) en el maximo ({datos_standard.max()} min)')

tope_dias_usuarios = df_cardio[(df_cardio['profile'] == 'standard') & (df_cardio['duration_min'] == datos_standard.max())]
print(tope_dias_usuarios['day_id'].nunique(), 'dias distintos de', df_cardio[df_cardio['profile']=='standard']['day_id'].nunique())
print(tope_dias_usuarios['user_id'].nunique(), 'usuarios distintos')
print((tope_dias_usuarios['user_id'].value_counts() > 1).sum(), 'usuarios con mas de una sesion en el tope')

#Paso 6: verificar si routine aporta diferencia adicional dentro de cada profile
orden_rutina = df_cardio.groupby('routine')['duration_min'].median().sort_values().index
datos_por_rutina = [df_cardio[df_cardio['routine'] == r]['duration_min'].values for r in orden_rutina]
h_rutina, p_rutina = stats.kruskal(*datos_por_rutina)
print(f'Todos los perfiles juntos, por routine: H = {h_rutina:.4f}, p-value = {p_rutina:.6f}')

for perfil in df_cardio['profile'].unique():
    sub = df_cardio[df_cardio['profile'] == perfil]
    datos_rutina_perfil = [sub[sub['routine'] == r]['duration_min'].values for r in sub['routine'].unique()]
    h_int, p_int = stats.kruskal(*datos_rutina_perfil)
    print(f'{perfil}: H = {h_int:.4f}, p-value = {p_int:.6f}')