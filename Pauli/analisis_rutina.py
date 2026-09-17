import pandas as pd
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

# R_i — Analisis de rutinas
# Cargar datos
df = pd.read_csv("Bita/rutina.csv")

print("DIMENSIONES")
print(df.shape)

print("\nCOLUMNAS")
print(df.columns.tolist())

print("\nVALORES NULOS")
print(df.isnull().sum())

# Distribucion de rutinas

print("\n DISTRIBUCIÓN DE RUTINAS")
conteo_rutinas = df["routine"].value_counts()
proporcion_rutinas = df["routine"].value_counts(normalize=True)
tabla_rutinas = pd.DataFrame({
    "frecuencia": conteo_rutinas,
    "proporcion": proporcion_rutinas})
print(tabla_rutinas)

# Distribución por perfil

print("\nDISTRIBUCIÓN DE RUTINAS POR PERFIL")
tabla_perfil = pd.crosstab(df["profile"], df["routine"])
print(tabla_perfil)
print("\nPROPORCIONES POR PERFIL")

tabla_perfil_prop = pd.crosstab(
    df["profile"],
    df["routine"],
    normalize="index")
print(tabla_perfil_prop)

# Chi cuadrado, perfil vs rutina

print("\nCHI CUADRADO PERFIL - RUTINA")

chi2, p_value, grados_libertad, esperados = chi2_contingency(tabla_perfil)
print(f"Chi-cuadrado: {chi2:.4f}")
print(f"p-value: {p_value:.10f}")
print(f"Grados de libertad: {grados_libertad}")
alpha = 0.05

if p_value < alpha:
    print("\nResultado: se rechaza H0.")
    print("Existe evidencia de asociación entre el perfil y la rutina.")
else:
    print("\nResultado: no se rechaza H0.")
    print("No existe evidencia suficiente de asociación entre el perfil y la rutina.")

# Guardamos los resultados

tabla_rutinas.to_csv("Pauli/resultados_rutina.csv")
tabla_perfil.to_csv("Pauli/rutina_por_perfil.csv")
tabla_perfil_prop.to_csv("Pauli/proporcion_rutina_por_perfil.csv")

print("\nArchivos guardados")

# grafico, distribucion global de las rutinas

orden_rutinas = ["push", "pull", "legs", "upper", "full_body"]
conteo_rutinas = df["routine"].value_counts().reindex(orden_rutinas)

plt.figure(figsize=(8, 5))
conteo_rutinas.plot(kind="bar")

plt.title("Distribución de rutinas")
plt.xlabel("Rutina")
plt.ylabel("Frecuencia")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig("Pauli/distribucion_rutinas.png", dpi=300)
plt.show()


# grafico, rutina segun perfil
tabla_perfil_prop = tabla_perfil_prop.reindex(columns=orden_rutinas)

tabla_perfil_prop.plot(
    kind="bar",
    figsize=(9, 5))

plt.title("Distribución de rutinas según perfil")
plt.xlabel("Perfil")
plt.ylabel("Proporción")
plt.xticks(rotation=0)
plt.legend(title="Rutina")
plt.tight_layout()

plt.savefig("Pauli/rutina_por_perfil.png", dpi=300)
plt.show()
