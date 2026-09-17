import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt


def p_value_simulado(datos, nombre_dist, parametros_originales, estadistico_observado, m=1000):
    """
    Calcula un p-value simulado via bootstrap parametrico, para cuando el p-value
    del test KS con parametros estimados cae en la zona ambigua (0.05 a 0.2).
    """
    distribucion = getattr(stats, nombre_dist)
    n = len(datos)
    contador = 0

    for _ in range(m):
        muestra_y = distribucion.rvs(*parametros_originales, size=n)
        parametros_y = distribucion.fit(muestra_y)
        estadistico_y, _ = stats.kstest(muestra_y, nombre_dist, args=parametros_y)

        if estadistico_y >= estadistico_observado:
            contador += 1

    return contador / m


def ajustar_distribucion(datos, nombre_grupo, candidatas):
    """
    Ajusta y testea distribuciones candidatas sobre un vector de datos.

    Parametros
    ----------
    datos : array-like
        Vector de valores numericos (ej. duraciones de un grupo).
    nombre_grupo : str
        Etiqueta del grupo, para identificarlo en la tabla de resultados.
    candidatas : list[str]
        Nombres de distribuciones de scipy.stats a probar (ej. ['gamma', 'lognorm']).

    Retorna
    -------
    pd.DataFrame con columnas: grupo, distribucion, parametros, estadistico, p_value,
    p_value_simulado, conclusion
    """
    #Paso A: estadisticas descriptivas (incluyendo forma, colas y atipicos)
    descriptivas = pd.Series(datos).describe()
    asimetria = stats.skew(datos)
    curtosis = stats.kurtosis(datos)

    q1 = np.percentile(datos, 25)
    q3 = np.percentile(datos, 75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    atipicos = datos[(datos < limite_inferior) | (datos > limite_superior)]

    print(f"--- Descriptivas: {nombre_grupo} ---")
    print(descriptivas)
    print(f"Asimetria (skewness): {asimetria:.4f}")
    print(f"Curtosis: {curtosis:.4f}")
    print(f"Atipicos (regla IQR): {len(atipicos)} de {len(datos)} ({100*len(atipicos)/len(datos):.2f}%)")

    plt.figure()
    plt.boxplot(datos, orientation='horizontal')
    plt.title(f'Boxplot - {nombre_grupo}')
    plt.xlabel('Valor')
    plt.tight_layout()
    plt.savefig(f'Figuras ajustes/boxplot_{nombre_grupo}.png')
    plt.close()

    #Paso B: estimar parametros, testear bondad de ajuste (KS), simular p-value si es ambiguo, y generar QQ-plot
    resultados_ajuste = []
    alpha = 0.05
    for nombre_dist in candidatas:
        distribucion = getattr(stats, nombre_dist)
        parametros = distribucion.fit(datos)

        estadistico, p_value = stats.kstest(datos, nombre_dist, args=parametros)

        #Si el p-value cae en la zona ambigua (0.05 a 0.2), simular el p-value real
        p_value_sim = None
        if 0.05 <= p_value < 0.2:
            print(f"{nombre_dist}: p-value {p_value:.4f} en zona ambigua, simulando (esto puede tardar)...")
            p_value_sim = p_value_simulado(datos, nombre_dist, parametros, estadistico, m=1000)

        #La conclusion final usa el p-value simulado si existe, si no, el del kstest normal
        p_value_final = p_value_sim if p_value_sim is not None else p_value
        conclusion = 'se rechaza H0' if p_value_final < alpha else 'no se rechaza H0'

        resultados_ajuste.append({
            'grupo': nombre_grupo,
            'distribucion': nombre_dist,
            'parametros': parametros,
            'estadistico': estadistico,
            'p_value': p_value,
            'p_value_simulado': p_value_sim,
            'conclusion': conclusion
        })

        plt.figure()
        stats.probplot(datos, dist=nombre_dist, sparams=parametros, plot=plt)
        plt.title(f'QQ-plot - {nombre_grupo} - {nombre_dist}')
        plt.savefig(f'qqplot_{nombre_grupo}_{nombre_dist}.png')
        plt.close()

    #Paso C: histograma con las densidades ajustadas de las candidatas superpuestas
    plt.figure()
    plt.hist(datos, bins=30, density=True, alpha=0.6, color='steelblue', edgecolor='black', label='Datos')

    x = np.linspace(min(datos), max(datos), 500)
    for resultado in resultados_ajuste:
        distribucion = getattr(stats, resultado['distribucion'])
        plt.plot(x, distribucion.pdf(x, *resultado['parametros']), label=resultado['distribucion'])

    plt.title(f'Histograma con densidades ajustadas - {nombre_grupo}')
    plt.xlabel('Valor')
    plt.ylabel('Densidad')
    plt.legend()
    plt.savefig(f'Figuras ajustes/histograma_{nombre_grupo}.png')
    plt.close()

    tabla_resultados = pd.DataFrame(resultados_ajuste)
    return tabla_resultados

#EJEMPLO DE USO
#Paso 1: cargar el vector de prueba (reparacion) y confirmar que se ve bien
#df_rep = pd.read_csv('log_reparaciones_limpio.csv')
#datos_prueba = df_rep['repair_duration_min']
#print(datos_prueba.shape)
#print(datos_prueba.describe())

#Paso 2: probar la funcion completa e integrada
#tabla = ajustar_distribucion(datos_prueba, 'reparacion_todas', ['gamma', 'lognorm', 'weibull_min'])
#print(tabla)