# Entrega 1 — Análisis del Input y Proceso de Llegada

**ICS2133 Fundamentos de Simulación de Sistemas Estocásticos — PUC**
Paula Castro · Bárbara Dablé Said · Francisca Torres Giglio

Este repositorio contiene el código y los resultados que respaldan el informe de la Entrega 1. Cada sección del informe indica el script que la genera; este archivo explica dónde está cada cosa y cómo ejecutarla.

---

## Estructura de la carpeta

```
Entrega 1 simulación/
├── README.md
├── Enunciados y Plan de Trabajo/
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

## Cómo ejecutar

Abrir una terminal en la carpeta principal (`Entrega 1 simulación/`) y copiar estos comandos **en este orden**:

```bash
cd Bita

# Paso 1 — Limpieza de datos
python limpieza_operacional.py
python limpieza_reparaciones.py
python filtros.py

# Paso 2 — Parte 1: cardio y reparaciones
python sci.py
python srep.py
cd ..

# Paso 3 — Parte 1: rutina y fuerza (se corre desde la carpeta principal)
python Pauli/analisis_rutina.py
python Pauli/analisis_fuerza.py

# Paso 4 — Partes 2 y 3: proceso de llegada (se corre desde la carpeta principal)
python Fran/pregunta_2a.py
python Fran/pregunta_2b.py
python Fran/pregunta_2c.py
python Fran/pregunta_3.py
```

> **Importante:** los scripts de `Bita/` se ejecutan **dentro** de `Bita/`; los de `Pauli/` y `Fran/` se ejecutan desde la **carpeta principal**.
>
> El Paso 1 solo es necesario para regenerar los datos limpios. Los archivos resultantes ya están incluidos en `Bita/`, por lo que esos tres comandos se pueden omitir (manteniendo el `cd Bita`).

---

## ¿Dónde está cada pregunta del informe?

| Pregunta | Script | Qué hace |
|---|---|---|
| 1 — Tipo de rutina $R_i$ | `Pauli/analisis_rutina.py` | Frecuencias, test $\chi^2$ perfil–rutina y probabilidades por perfil |
| 1 — Fuerza $S^F_{ij}$ | `Pauli/analisis_fuerza.py` | Análisis por máquina, ajuste y selección de distribuciones |
| 1 — Cardio $S^C_i$ | `Bita/sci.py` | Análisis por perfil, ajuste y selección de distribuciones |
| 1 — Reparaciones $S^{rep}_f$ | `Bita/srep.py` | Análisis por categoría, ajuste y selección de distribuciones |
| 2a | `Fran/pregunta_2a.py` | Gráficos de llegadas promedio por hora (global y por perfil) |
| 2b | `Fran/pregunta_2b.py` | Tests de hipótesis del proceso de llegada |
| 2c | `Fran/pregunta_2c.py` | Estimación de tasas por bloque y probabilidades de perfil |
| 3a y 3b | `Fran/pregunta_3.py` | Simulación de llegadas (Thinning) y comparación con los datos históricos |

**Notas:**
- `Bita/ajustes.py` no se ejecuta: contiene la función `ajustar_distribucion`, que usan los scripts de la Parte 1.
- Las figuras de la Parte 1 se guardan en `Figuras ajustes/`; las tablas de resultados de fuerza y rutina, en `Pauli/`.
- El código que genera las llegadas es la función `simular_dia_llegadas` de `Fran/pregunta_3.py`. Usa la semilla `42`, por lo que los resultados son reproducibles.

---

## Datos

- Los archivos `*_historico.csv` son los datos originales entregados en `DatosInput.zip` y no se modifican.
- Los archivos `*_limpio.csv` son el resultado de la depuración descrita en la Parte 1a del informe.
- Tal como indica el enunciado, `log_operacional` y `log_reparaciones` son historiales independientes: `day_id` e `historical_day` no se utilizan para vincularlos.
