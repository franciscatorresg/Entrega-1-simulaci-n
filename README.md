# Entrega 1 — Análisis del Input y Proceso de Llegada

**ICS2133 Fundamentos de Simulación de Sistemas Estocásticos — PUC**
Paula Castro · Bárbara Dablé Said · Francisca Torres Giglio

Este repositorio contiene el código y los resultados que respaldan el informe de la Entrega 1. Cada sección del informe indica el script que la genera; este archivo explica dónde está cada cosa y cómo ejecutarla.

---

## Estructura de la carpeta

```
Entrega 1 simulación/
├── README.md
├── ENUNCIADOS/
│   ├── Proyecto - Enunciado.pdf          # Enunciado del proyecto
│   └── Proyecto - Entrega 1.pdf          # Enunciado de la Entrega 1
│
├── Bita/                                 # Limpieza de datos + Parte 1 (S^C_i y S^rep_f)
│   ├── diccionario_logs.xlsx             # Diccionario de variables de los logs
│   ├── log_operacional_historico.csv     # Datos originales
│   ├── log_reparaciones_historico.csv    # Datos originales
│   ├── limpieza_operacional.py           # -> log_operacional_limpio.csv
│   ├── limpieza_reparaciones.py          # -> log_reparaciones_limpio.csv
│   ├── log_operacional_limpio.csv
│   ├── log_reparaciones_limpio.csv
│   ├── filtros.py                        # -> rutina.csv, fuerza.csv, cardio.csv
│   ├── rutina.csv / fuerza.csv / cardio.csv
│   ├── ajustes.py                        # Funciones de ajuste y bondad de ajuste (módulo)
│   ├── sci.py                            # Parte 1: duración de cardio S^C_i
│   └── srep.py                           # Parte 1: tiempo de reparación S^rep_f
│
├── Pauli/                                # Parte 1 (R_i y S^F_ij)
│   ├── analisis_rutina.py                # Parte 1: tipo de rutina R_i
│   ├── analisis_fuerza.py                # Parte 1: duración de ejercicios de fuerza S^F_ij
│   └── *.csv                             # Tablas de resultados (ver detalle abajo)
│
├── Fran/                                 # Partes 2 y 3 (proceso de llegada)
│   ├── pregunta_2a.py                    # Parte 2a: análisis exploratorio
│   ├── pregunta_2b.py                    # Parte 2b: tests de hipótesis
│   ├── pregunta_2c.py                    # Parte 2c: estimación de parámetros
│   └── pregunta_3.py                     # Parte 3: simulación (thinning) y validación
│
└── Figuras ajustes/                      # Figuras de la Parte 1 (histogramas, boxplots, QQ-plots)
```

---

## Requisitos

- Python 3.10 o superior
- Librerías: `pandas`, `numpy`, `scipy`, `matplotlib`

```bash
pip install pandas numpy scipy matplotlib
```

---

## Orden de ejecución

Los scripts deben ejecutarse en este orden, ya que cada etapa usa los archivos generados por la anterior.

### 1. Limpieza de datos (carpeta `Bita/`)

Estos scripts usan rutas relativas a su propia carpeta, por lo que se ejecutan **desde dentro de `Bita/`**:

```bash
cd Bita
python limpieza_operacional.py      # log_operacional_historico.csv  -> log_operacional_limpio.csv
python limpieza_reparaciones.py     # log_reparaciones_historico.csv -> log_reparaciones_limpio.csv
python filtros.py                   # genera rutina.csv, fuerza.csv y cardio.csv
cd ..
```

### 2. Parte 1 — Análisis y ajuste de distribuciones

| Variable | Script | Ejecutar desde | Resultados |
|---|---|---|---|
| Tipo de rutina $R_i$ | `Pauli/analisis_rutina.py` | carpeta raíz | `Pauli/resultados_rutina.csv`, `Pauli/rutina_por_perfil.csv`, `Pauli/proporcion_rutina_por_perfil.csv`, figuras `distribucion_rutinas.png` y `rutina_por_perfil.png` |
| Duración de fuerza $S^F_{ij}$ | `Pauli/analisis_fuerza.py` | carpeta raíz | `Pauli/resultados_ajuste_fuerza.csv`, `Pauli/seleccion_distribuciones_fuerza.csv`, `Pauli/modelo_fuerza_final.csv`, `Pauli/tabla_maestra_fuerza.csv`, figuras por máquina |
| Duración de cardio $S^C_i$ | `Bita/sci.py` | `Bita/` | Figuras por perfil (histogramas, boxplots, QQ-plots) y resultados en consola |
| Tiempo de reparación $S^{rep}_f$ | `Bita/srep.py` | `Bita/` | Figuras por categoría funcional y resultados en consola |

```bash
python Pauli/analisis_rutina.py
python Pauli/analisis_fuerza.py
cd Bita
python sci.py
python srep.py
cd ..
```

`Bita/ajustes.py` no se ejecuta directamente: es el módulo con la función `ajustar_distribucion`, que ajusta las distribuciones candidatas por máxima verosimilitud, genera histogramas y QQ-plots y aplica el test de Kolmogorov-Smirnov (con bootstrap paramétrico cuando el p-value cae en la zona ambigua). Lo usan `sci.py`, `srep.py` y `analisis_fuerza.py`.

Todas las figuras de la Parte 1 se guardan en `Figuras ajustes/`.

### 3. Parte 2 — Análisis del proceso de llegada

Se ejecutan **desde la carpeta raíz** (leen `Bita/log_operacional_limpio.csv`):

| Sección | Script | Contenido |
|---|---|---|
| 2a | `Fran/pregunta_2a.py` | Llegadas promedio por hora, global y por perfil |
| 2b | `Fran/pregunta_2b.py` | Tests: (1) Chi-cuadrado de llegadas diarias Poisson, (2) Kruskal-Wallis entre jornadas, (3) KS de homogeneidad del proceso, (4) Chi-cuadrado de tasa constante por bloque, (5) KS de uniformidad por bloque, (6) Chi-cuadrado de independencia perfil–hora |
| 2c | `Fran/pregunta_2c.py` | Probabilidades de perfil y tasas $\lambda_b$ del proceso de Poisson no homogéneo por bloque horario, con intervalos de confianza |

```bash
python Fran/pregunta_2a.py
python Fran/pregunta_2b.py
python Fran/pregunta_2c.py
```

### 4. Parte 3 — Simulación del proceso de llegada

| Sección | Script | Contenido |
|---|---|---|
| 3a y 3b | `Fran/pregunta_3.py` | Generación de llegadas con el algoritmo de Thinning, simulación de 200 jornadas y comparación con los datos históricos (por hora, por perfil y total diario) |

```bash
python Fran/pregunta_3.py
```

El código que genera las llegadas es la función `simular_dia_llegadas` de `Fran/pregunta_3.py`. La simulación usa una semilla fija (`np.random.seed(42)`), por lo que los resultados del informe son reproducibles.

---

## Datos

- Los archivos `*_historico.csv` son los datos originales entregados en `DatosInput.zip` y no se modifican.
- Los archivos `*_limpio.csv` son el resultado de la depuración descrita en la Parte 1a del informe.
- Tal como indica el enunciado, `log_operacional` y `log_reparaciones` son historiales independientes: `day_id` e `historical_day` no se utilizan para vincularlos.
