import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Bita.ajustes import ajustar_distribucion

# Primero cargamos los datos
df = pd.read_csv("Bita/fuerza.csv")

# Variable de interés
duracion = df["duration_min"]

# Imprimimos las estadisticas descriptivas

print("========== ESTADÍSTICAS DE S^F_ij ==========")

print("\nCantidad de observaciones:")
print(len(duracion))

print("\nEstadísticas descriptivas:")
print(duracion.describe())

print("\nMedia:")
print(duracion.mean())

print("\nMediana:")
print(duracion.median())

print("\nDesviación estándar:")
print(duracion.std())

print("\nVarianza:")
print(duracion.var())

print("\nAsimetría (skewness):")
print(duracion.skew())

print("\nCurtosis:")
print(duracion.kurtosis())


# Estudiamos los percentiles

print("\nPercentiles:")

for p in [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]:
    print(f"{p*100:.0f}%: {duracion.quantile(p):.4f}")


# Vemos outliers segun regla del iqr

Q1 = duracion.quantile(0.25)
Q3 = duracion.quantile(0.75)

IQR = Q3 - Q1

limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR

outliers = duracion[
    (duracion < limite_inferior) |
    (duracion > limite_superior)
]

print("\n========== OUTLIERS ==========")

print(f"Q1: {Q1:.4f}")
print(f"Q3: {Q3:.4f}")
print(f"IQR: {IQR:.4f}")

print(f"Límite inferior: {limite_inferior:.4f}")
print(f"Límite superior: {limite_superior:.4f}")

print(f"\nCantidad de posibles outliers: {len(outliers)}")
print(f"Porcentaje de posibles outliers: {len(outliers)/len(duracion)*100:.2f}%")


# Histograma

plt.figure(figsize=(10, 6))

plt.hist(duracion, bins=40)

plt.xlabel("Duración del ejercicio (minutos)")
plt.ylabel("Frecuencia")
plt.title("Distribución de la duración de ejercicios de fuerza")

plt.tight_layout()

plt.savefig("Pauli/histograma_fuerza.png", dpi=300)

#plt.show()


# Boxplot

plt.figure(figsize=(10, 4))

plt.boxplot(duracion, vert=False)

plt.xlabel("Duración del ejercicio (minutos)")
plt.title("Boxplot de la duración de ejercicios de fuerza")

plt.tight_layout()

plt.savefig("Pauli/boxplot_fuerza.png", dpi=300)

#plt.show()


print("\n========== FIN DEL ANÁLISIS ==========")

# ============================================================
# CLASIFICACIÓN DE MÁQUINAS POR CATEGORÍA
# ============================================================

categorias = {
    "chest_press": "empuje",
    "shoulder_press": "empuje",
    "chest_fly": "empuje",
    "lat_pulldown": "jalón",
    "seated_row": "jalón",
    "biceps_curl": "jalón",
    "leg_press": "piernas",
    "leg_extension": "piernas",
    "leg_curl": "piernas",
    "cable": "multifuncional"
}

df["category"] = df["resource"].map(categorias)


# ============================================================
# ESTADÍSTICAS POR CATEGORÍA
# ============================================================

print("\n========== DURACIÓN POR CATEGORÍA ==========")

estadisticas_categoria = df.groupby("category")["duration_min"].agg(
    ["count", "mean", "median", "std", "min", "max"]
)

print(estadisticas_categoria)


# ============================================================
# BOXPLOT POR CATEGORÍA
# ============================================================

categorias_orden = [
    "empuje",
    "jalón",
    "piernas",
    "multifuncional"
]

datos_categoria = [
    df[df["category"] == categoria]["duration_min"]
    for categoria in categorias_orden
]

plt.figure(figsize=(10, 6))

plt.boxplot(
    datos_categoria,
    tick_labels=categorias_orden
)

plt.xlabel("Categoría de máquina")
plt.ylabel("Duración (minutos)")
plt.title("Duración de ejercicios de fuerza por categoría")

plt.tight_layout()

plt.savefig("Pauli/boxplot_por_categoria.png", dpi=300)

#plt.show()


# ============================================================
# BOXPLOT POR MÁQUINA
# ============================================================

maquinas_orden = sorted(df["resource"].unique())

datos_maquina = [
    df[df["resource"] == maquina]["duration_min"]
    for maquina in maquinas_orden
]

plt.figure(figsize=(12, 6))

plt.boxplot(
    datos_maquina,
    tick_labels=maquinas_orden
)

plt.xlabel("Máquina")
plt.ylabel("Duración (minutos)")
plt.title("Duración de ejercicios de fuerza por máquina")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig("Pauli/boxplot_por_maquina.png", dpi=300)

#plt.show()

# ============================================================
# PRUEBA DE KRUSKAL-WALLIS POR CATEGORÍA
# ============================================================

from scipy.stats import kruskal

print("\n========== KRUSKAL-WALLIS POR CATEGORÍA ==========")

grupos_categoria = [
    df[df["category"] == categoria]["duration_min"]
    for categoria in categorias_orden
]

H_categoria, p_categoria = kruskal(*grupos_categoria)

print(f"Estadístico H: {H_categoria:.4f}")
print(f"p-value: {p_categoria:.10f}")

alpha = 0.05

if p_categoria < alpha:
    print("Resultado: se rechaza H0.")
    print("Existe evidencia de diferencias entre las categorías.")
else:
    print("Resultado: no se rechaza H0.")
    print("No existe evidencia suficiente de diferencias entre las categorías.")


# ============================================================
# PRUEBA DE KRUSKAL-WALLIS POR MÁQUINA
# ============================================================

print("\n========== KRUSKAL-WALLIS POR MÁQUINA ==========")

grupos_maquina = [
    df[df["resource"] == maquina]["duration_min"]
    for maquina in maquinas_orden
]

H_maquina, p_maquina = kruskal(*grupos_maquina)

print(f"Estadístico H: {H_maquina:.4f}")
print(f"p-value: {p_maquina:.10f}")

if p_maquina < alpha:
    print("Resultado: se rechaza H0.")
    print("Existe evidencia de diferencias entre las máquinas.")
else:
    print("Resultado: no se rechaza H0.")
    print("No existe evidencia suficiente de diferencias entre las máquinas.")



# ============================================================
# KRUSKAL-WALLIS DE MÁQUINAS DENTRO DE CADA CATEGORÍA
# ============================================================

print("\n========== MÁQUINAS DENTRO DE CADA CATEGORÍA ==========")

for categoria in categorias_orden:

    maquinas_categoria = df[
        df["category"] == categoria
    ]["resource"].unique()

    # Si hay más de una máquina, podemos comparar
    if len(maquinas_categoria) > 1:

        grupos = [
            df[df["resource"] == maquina]["duration_min"]
            for maquina in maquinas_categoria
        ]

        H, p = kruskal(*grupos)

        print(f"\nCategoría: {categoria}")
        print(f"Máquinas: {list(maquinas_categoria)}")
        print(f"Estadístico H: {H:.4f}")
        print(f"p-value: {p:.10f}")

        if p < alpha:
            print("Resultado: se rechaza H0.")
            print("Existe evidencia de diferencias entre las máquinas de esta categoría.")
        else:
            print("Resultado: no se rechaza H0.")
            print("No existe evidencia suficiente de diferencias entre las máquinas de esta categoría.")

    else:
        print(f"\nCategoría: {categoria}")
        print(f"Solo existe una máquina: {list(maquinas_categoria)}")
        print("No corresponde realizar Kruskal-Wallis.")


# ============================================================
# ESTADÍSTICAS POR MÁQUINA
# ============================================================

print("\n========== ESTADÍSTICAS POR MÁQUINA ==========")

estadisticas_maquina = df.groupby("resource")["duration_min"].agg(
    ["count", "mean", "median", "std", "min", "max"]
)

print(estadisticas_maquina)


# ============================================================
# AJUSTE DE DISTRIBUCIONES PARA LEG PRESS
# ============================================================


datos_leg_press = df[
    df["resource"] == "leg_press"
]["duration_min"].values

print("\n========== AJUSTE: LEG PRESS ==========")

tabla_leg_press = ajustar_distribucion(
    datos_leg_press,
    "leg_press",
    ["gamma", "lognorm", "weibull_min"]
)

print("\nResultados:")
print(tabla_leg_press)

print("\n========== FIN AJUSTE LEG PRESS ==========")


# ============================================================
# AJUSTE DE DISTRIBUCIONES PARA TODAS LAS MÁQUINAS
# ============================================================

maquinas = sorted(df["resource"].unique())

resultados_todos = []

for maquina in maquinas:

    datos_maquina = df[
        df["resource"] == maquina
    ]["duration_min"].values

    print(f"\n========== AJUSTE: {maquina} ==========")

    resultado = ajustar_distribucion(
        datos_maquina,
        maquina,
        ["gamma", "lognorm", "weibull_min"]
    )

    resultados_todos.append(resultado)

# Unir todos los resultados
tabla_ajustes = pd.concat(resultados_todos, ignore_index=True)

print("\n\n========== RESUMEN DE AJUSTES ==========")
print(tabla_ajustes)

# Guardar resultados
tabla_ajustes.to_csv(
    "Pauli/resultados_ajuste_fuerza.csv",
    index=False
)

print("\nResultados guardados en:")
print("Pauli/resultados_ajuste_fuerza.csv")

# ============================================================
# SELECCIÓN DE DISTRIBUCIÓN POR MÁQUINA
# ============================================================

def seleccionar_distribucion(grupo):

    # Primero consideramos las distribuciones que NO rechazan H0
    aceptadas = grupo[
        grupo["conclusion"] == "no se rechaza H0"
    ]

    if len(aceptadas) > 0:
        # Si hay alguna compatible con los datos,
        # elegimos la de menor estadístico KS
        seleccionada = aceptadas.loc[
            aceptadas["estadistico"].idxmin()
        ]
        criterio = "No rechazo H0; menor KS entre las candidatas"
    else:
        # Si todas son rechazadas, elegimos la de menor KS
        seleccionada = grupo.loc[
            grupo["estadistico"].idxmin()
        ]
        criterio = "Todas rechazadas; menor KS relativo"

    return pd.Series({
        "distribucion_seleccionada": seleccionada["distribucion"],
        "estadistico_KS": seleccionada["estadistico"],
        "p_value": seleccionada["p_value"],
        "p_value_simulado": seleccionada["p_value_simulado"],
        "conclusion": seleccionada["conclusion"],
        "criterio": criterio,
        "parametros": seleccionada["parametros"]
    })


tabla_seleccion = (
    tabla_ajustes
    .groupby("grupo")
    .apply(seleccionar_distribucion)
    .reset_index()
)


# ============================================================
# P-VALUE FINAL UTILIZADO PARA LA DECISIÓN
# ============================================================

tabla_seleccion["p_value_final"] = np.where(
    tabla_seleccion["p_value_simulado"].notna(),
    tabla_seleccion["p_value_simulado"],
    tabla_seleccion["p_value"]
)

print("\n\n========== TABLA FINAL PARA INFORME ==========")

columnas_informe = [
    "grupo",
    "distribucion_seleccionada",
    "parametros",
    "estadistico_KS",
    "p_value_final",
    "conclusion",
    "criterio"
]

print(
    tabla_seleccion[columnas_informe]
    .to_string(index=False)
)

tabla_seleccion[columnas_informe].to_csv(
    "Pauli/modelo_fuerza_final.csv",
    index=False
)

print("\n\n========== DISTRIBUCIÓN SELECCIONADA POR MÁQUINA ==========")
print(tabla_seleccion.to_string(index=False))

# Guardar tabla final
tabla_seleccion.to_csv(
    "Pauli/seleccion_distribuciones_fuerza.csv",
    index=False
)

print("\nTabla de selección guardada en:")
print("Pauli/seleccion_distribuciones_fuerza.csv")


# ============================================================
# PARÁMETROS FINALES DEL MODELO DE FUERZA
# ============================================================

print("\n\n========== PARÁMETROS FINALES ==========")

for _, fila in tabla_seleccion.iterrows():

    print(f"\nMáquina: {fila['grupo']}")
    print(f"Distribución: {fila['distribucion_seleccionada']}")
    print(f"Parámetros: {fila['parametros']}")
    print(f"KS: {fila['estadistico_KS']:.6f}")
    print(f"p-value: {fila['p_value']:.6f}")

    if pd.notna(fila["p_value_simulado"]):
        print(f"p-value simulado: {fila['p_value_simulado']:.6f}")

    print(f"Criterio: {fila['criterio']}")


    # ============================================================
# TABLA MAESTRA: ANÁLISIS DE DURACIÓN DE FUERZA
# ============================================================

resumen_descriptivo = []

for maquina in maquinas:

    datos = df[
        df["resource"] == maquina
    ]["duration_min"]

    resumen_descriptivo.append({
        "grupo": maquina,
        "n": len(datos),
        "media": datos.mean(),
        "mediana": datos.median(),
        "desv_std": datos.std(),
        "min": datos.min(),
        "max": datos.max(),
        "asimetria": datos.skew()
    })

tabla_descriptiva = pd.DataFrame(resumen_descriptivo)

# Unir descriptivas con la selección de distribución
tabla_final_fuerza = tabla_descriptiva.merge(
    tabla_seleccion[
        [
            "grupo",
            "distribucion_seleccionada",
            "parametros",
            "estadistico_KS",
            "p_value_final",
            "conclusion",
            "criterio"
        ]
    ],
    on="grupo",
    how="left"
)

# Ordenar por máquina
tabla_final_fuerza = tabla_final_fuerza.sort_values("grupo")

print("\n\n============================================================")
print("           TABLA MAESTRA - MODELO DE FUERZA")
print("============================================================")

print(
    tabla_final_fuerza.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# Guardar
tabla_final_fuerza.to_csv(
    "Pauli/tabla_maestra_fuerza.csv",
    index=False
)

print("\nTabla maestra guardada en:")
print("Pauli/tabla_maestra_fuerza.csv")