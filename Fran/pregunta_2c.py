import pandas as pd
import numpy as np

df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

print("=== PARÁMETROS DE PERFIL DE USUARIO ===")
print("Distribución Categórica (Proporciones):")
proporciones = df_llegadas['profile'].value_counts(normalize=True)
for perfil, prob in proporciones.items():
    print(f"P({perfil}) = {prob:.4f}")

print("\n=== TASAS DEL PROCESO DE POISSON NO ESTACIONARIO (Lambda) ===")
print("Tasa promedio de llegadas por intervalo de 60 minutos:")
tamano_intervalo = 60
df_llegadas['intervalo'] = (df_llegadas['event_time'] // tamano_intervalo) * tamano_intervalo

dias_totales = df_llegadas['day_id'].nunique()
llegadas_por_intervalo = df_llegadas.groupby('intervalo').size()
tasa_lambda = llegadas_por_intervalo / dias_totales

intervalos_posibles = np.arange(0, 840, tamano_intervalo)
tasa_lambda = tasa_lambda.reindex(intervalos_posibles, fill_value=0)

for intervalo, tasa in tasa_lambda.items():
    hora = int(7 + intervalo // 60)
    print(f"[{hora:02d}:00 - {hora+1:02d}:00] : lambda = {tasa:.4f} llegadas/hora")