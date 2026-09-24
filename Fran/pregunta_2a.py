import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Cargar el log operacional desde la carpeta Bita
df_op = pd.read_csv('Bita/log_operacional_limpio.csv')

# 2. Filtrar los intentos de llegada 
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

# 3. Discretizar el tiempo en intervalos de 60 minutos
tamano_intervalo = 60
df_llegadas['intervalo'] = (df_llegadas['event_time'] // tamano_intervalo) * tamano_intervalo

# 4. Construir la grilla completa (incluyendo los intervalos donde llegaron 0 personas)
dias = df_llegadas['day_id'].unique()
intervalos_posibles = np.arange(0, 840, tamano_intervalo) 
grilla = pd.MultiIndex.from_product([dias, intervalos_posibles], names=['day_id', 'intervalo'])

# Conteo global y por perfil
conteos_global = df_llegadas.groupby(['day_id', 'intervalo']).size().reset_index(name='llegadas')
conteos_global = conteos_global.set_index(['day_id', 'intervalo']).reindex(grilla, fill_value=0).reset_index()

conteos_perfil = df_llegadas.groupby(['day_id', 'intervalo', 'profile']).size().reset_index(name='llegadas')

# 5. Generar los gráficos con horas reales
promedio_por_intervalo = conteos_global.groupby('intervalo')['llegadas'].mean()

# --- Creación de etiquetas de hora para el eje X ---
marcas_x = np.arange(0, 841, 120) 
etiquetas_x = [f"{(7 + t//60):02d}:00" for t in marcas_x]

# ==========================================
# Gráfico 1: Global
# ==========================================
plt.figure(figsize=(10, 5))
plt.plot(promedio_por_intervalo.index, promedio_por_intervalo.values, marker='o', color='black')
plt.title('Promedio de llegadas por intervalo (Global)')
plt.xlabel('Hora del día')
plt.ylabel('Promedio de llegadas')
plt.xticks(marcas_x, etiquetas_x) # <-- Aquí se aplican las horas
plt.grid(True, alpha=0.3)
plt.show()

# ==========================================
# Gráfico 2: Por Perfil
# ==========================================
plt.figure(figsize=(10, 5))
for p in df_llegadas['profile'].dropna().unique():
    data_p = conteos_perfil[conteos_perfil['profile'] == p]
    data_p = data_p.set_index(['day_id', 'intervalo'])['llegadas'].reindex(grilla, fill_value=0).reset_index()
    promedio_p = data_p.groupby('intervalo')['llegadas'].mean()
    plt.plot(promedio_p.index, promedio_p.values, marker='o', label=f'Perfil: {p}')

plt.title('Promedio de llegadas por intervalo según Perfil')
plt.xlabel('Hora del día')
plt.ylabel('Promedio de llegadas')
plt.xticks(marcas_x, etiquetas_x) # <-- Aquí se aplican las horas
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()