import pandas as pd
import numpy as np
import scipy.stats as stats

df_op = pd.read_csv('Bita/log_operacional_limpio.csv')
df_llegadas = df_op[df_op['event_type'] == 'visit'].copy()

print("=== PARÁMETROS DE PERFIL DE USUARIO ===")
n_total = len(df_llegadas)
proporciones = df_llegadas['profile'].value_counts(normalize=True)
for perfil, prob in proporciones.items():
    ic = 1.96 * np.sqrt(prob * (1 - prob) / n_total)
    print(f"P({perfil}) = {prob:.4f}   IC95%: [{prob - ic:.4f}, {prob + ic:.4f}]")

print("\n=== TASAS DEL PROCESO DE POISSON NO ESTACIONARIO (Lambda por bloque) ===")
dias_totales = df_llegadas['day_id'].nunique()
bloques = {
    '07:00-10:00': (0, 180),
    '10:00-13:00': (180, 360),
    '13:00-16:00': (360, 540),
    '16:00-19:00': (540, 720),
    '19:00-21:00': (720, 840),
}
tasas_bloque = {}
for nombre, (a, b) in bloques.items():
    horas = (b - a) / 60
    N_b = ((df_llegadas['event_time'] >= a) & (df_llegadas['event_time'] < b)).sum()
    exposicion = dias_totales * horas                 # horas-jornada observadas en el bloque
    lam = N_b / exposicion                            # estimador de máxima verosimilitud
    
    tasas_bloque[nombre] = lam
    print(f"[{nombre}] : N = {N_b}, lambda = {lam:.4f} llegadas/hora "
          f"({lam/60:.4f} por min)   IC95%: [{ic_inf:.4f}, {ic_sup:.4f}]")

print("\n=== TASAS POR PERFIL: lambda_k(t) = P(k) * lambda(t) ===")
for nombre, lam in tasas_bloque.items():
    texto = ", ".join(f"{p}={prob*lam:.3f}" for p, prob in proporciones.items())
    print(f"[{nombre}] : {texto}")

esperadas = sum(tasas_bloque[n] * (b - a) / 60 for n, (a, b) in bloques.items())
print(f"\nLlegadas esperadas por jornada: {esperadas:.2f} "
      f"(promedio histórico: {n_total / dias_totales:.2f})")