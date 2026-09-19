import pandas as pd

#Paso 1: cargar el archivo
df = pd.read_csv("log_operacional_historico.csv", sep=";", encoding="utf-8-sig", low_memory=False)

print(df.shape)
print(df.head())

#Paso 2: arreglar las comas decimales en las columnas numericas
columnas_numericas = [
    "event_time", "planned_order", "speed_m_per_min", "duration_min",
    "wait_min", "water_liters", "towel_count", "stock_after", "dissatisfaction"
]

for col in columnas_numericas:
    df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")

print(df[columnas_numericas].dtypes)
print(df[columnas_numericas].head())

#Paso 3: revisar que no haya tiempos o duraciones negativas o en cero donde no corresponde
columnas_tiempo = ["event_time", "duration_min", "wait_min"]

for col in columnas_tiempo:
    negativos = (df[col] < 0).sum()
    ceros = (df[col] == 0).sum()
    print(f"{col}: {negativos} negativos, {ceros} en cero")

#Paso 4: revisar la fila con duration_min en cero
print(df[df["duration_min"] == 0])

#Paso 5: revisar valores invalidos en event_type y outcome
print(df["event_type"].value_counts())
print()
print(df["outcome"].value_counts())

#Paso 6: mirar de cerca las filas con event_type invalido
pd.set_option("display.max_columns", None)
print(df[df["event_type"] == "evento_mal_escrito"].head(10))

#Paso 7: revisar las 41 filas completas, no solo las primeras 10
pd.set_option("display.max_rows", None)
print(df[df["event_type"] == "evento_mal_escrito"][["resource", "outcome", "duration_min", "origin", "destination", "worker_id", "user_id"]])

#Paso 8: reclasificar las filas de evento_mal_escrito a su evento real
mascara = df["event_type"] == "evento_mal_escrito"

es_insumo = df["resource"].isin(["towels", "water"])
es_traslado = df["resource"].isin(["trainers", "receptionists", "technicians"])

df.loc[mascara & es_insumo & (df["outcome"] == "completed"), "event_type"] = "supply_pickup"
df.loc[mascara & es_insumo & (df["outcome"] == "empty"), "event_type"] = "stockout"
df.loc[mascara & es_traslado, "event_type"] = "worker_travel"
df.loc[mascara & (df["outcome"] == "arrived"), "event_type"] = "assistance"

print(df["event_type"].value_counts())

#Paso 9: mirar de cerca las filas con outcome invalido
print(df[df["outcome"] == "resultado_desconocido"][["event_type", "resource", "duration_min", "wait_min", "water_liters", "towel_count", "stock_after"]])

#Paso 10: reclasificar las filas de outcome resultado_desconocido
mascara2 = df["outcome"] == "resultado_desconocido"

df.loc[mascara2 & (df["event_type"] == "supply_pickup"), "outcome"] = "completed"
df.loc[mascara2 & (df["event_type"] == "assistance"), "outcome"] = "arrived"
df.loc[mascara2 & (df["event_type"] == "worker_travel"), "outcome"] = "completed"
df.loc[mascara2 & (df["event_type"] == "stockout"), "outcome"] = "empty"

print(df["outcome"].value_counts())

#Paso 11: revisar las filas con water_liters = 1.000.000
print(df[df["water_liters"] == 1_000_000][["event_type", "resource", "outcome", "water_liters"]])

#Paso 12: revisar si towel_count y stock_after tienen el mismo valor centinela
print("towel_count valores unicos:", sorted(df["towel_count"].dropna().unique())[-5:])
print("stock_after valores unicos:", sorted(df["stock_after"].dropna().unique())[-5:])

#Paso 13: convertir el valor centinela de water_liters a NaN
df.loc[df["water_liters"] == 1_000_000, "water_liters"] = pd.NA

print(df["water_liters"].describe())

#Paso 14: revisar las filas con destination fuera del rango valido (1 a 49)
print(df[df["destination"].astype(str).str.match(r"^\d+$") & (pd.to_numeric(df["destination"], errors="coerce") > 49)])

#Paso 15: investigar el significado del codigo 99 en destination
for et in ["supply_pickup", "worker_travel", "assistance"]:
    total = (df["event_type"] == et).sum()
    con_99 = ((df["event_type"] == et) & (df["destination"] == "99")).sum()
    print(f"{et}: {con_99} de {total} filas tienen destination = 99")

print()
print("Aparece 99 alguna vez en origin?:", (df["origin"] == "99").sum())

print()
print("Otros valores no numericos o fuera de rango en destination:")
destino_num = pd.to_numeric(df["destination"], errors="coerce")
print(df.loc[(destino_num > 49) | (destino_num < 1), "destination"].value_counts())

#Paso 16: convertir destination = 99 a NaN
df.loc[df["destination"] == "99", "destination"] = pd.NA

print((df["destination"] == "99").sum())

#Paso 17: revisar las filas con origin/destination en formato de coordenadas
formato_raro = df["origin"].astype(str).str.contains(r"\(", na=False) | df["destination"].astype(str).str.contains(r"\(", na=False)
print(df[formato_raro][["event_type", "resource", "origin", "destination"]])

#Paso 17: verificar si las coordenadas en metros corresponden a la celda real de la maquina
import re

# celdas reales de cada tipo de maquina, segun la hoja "Recursos" del diccionario
celdas_reales = {
    "chest_press": [42, 47],
    "shoulder_press": [49, 45],
    "chest_fly": [46],
    "lat_pulldown": [36, 22],
    "seated_row": [15, 29],
    "biceps_curl": [11, 33],
    "leg_press": [26, 32],
    "leg_curl": [31, 24],
    "leg_extension": [12, 10],
    "cable": [8, 43],
    "treadmill": [14, 21, 28, 35],
}

def coordenada_a_celda(texto):
    match = re.match(r"\(([\d.]+),([\d.]+)\)", str(texto))
    if not match:
        return None
    x, y = float(match.group(1)), float(match.group(2))
    col = int(x // 2.5)
    row = 6 - int(y // 2.5)
    return 49 - (row * 7 + col)

filas_raras = df[df["destination"].astype(str).str.match(r"^\(")]

for idx, fila in filas_raras.iterrows():
    maquina_base = re.sub(r"-\d+$", "", str(fila["resource"]))
    celda_calculada = coordenada_a_celda(fila["destination"])
    celdas_esperadas = celdas_reales.get(maquina_base, [])
    calza = celda_calculada in celdas_esperadas
    print(f"resource={maquina_base:15s} coordenada={fila['destination']:20s} celda_calculada={celda_calculada}  celdas_reales={celdas_esperadas}  calza={calza}")

#Paso 18: convertir las coordenadas en metros a NaN
formato_raro_dest = df["destination"].astype(str).str.match(r"^\(")
formato_raro_orig = df["origin"].astype(str).str.match(r"^\(")

df.loc[formato_raro_dest, "destination"] = pd.NA
df.loc[formato_raro_orig, "origin"] = pd.NA

print("Quedan en destination:", df["destination"].astype(str).str.match(r"^\(").sum())
print("Quedan en origin:", df["origin"].astype(str).str.match(r"^\(").sum())

#Paso 19: verificaciones rapidas (booleanas, profile, routine, duplicados)

# columnas booleanas: confirmar que solo tienen True, False o vacio
for col in ["assistance", "cardio_planned", "cable_planned"]:
    print(col, "valores unicos:", df[col].unique())

print()
# profile vacio: confirmar que coincide con actividades de personal
print("Filas con profile vacio, por event_type:")
print(df[df["profile"].isna()]["event_type"].value_counts())

print()
# routine: confirmar que solo toma las 5 categorias esperadas, sin vacios raros
print("routine valores unicos:", df["routine"].dropna().unique())
print("Filas de visit/exercise con routine vacio:")
print(df[(df["event_type"].isin(["visit", "exercise"])) & (df["routine"].isna())].shape[0])

print()
# duplicados
print("Filas duplicadas exactas:", df.duplicated().sum())
print("event_id repetido dentro del mismo day_id:", df.duplicated(subset=["day_id", "event_id"]).sum())

#Paso 20: revisar eventos que empiezan despues del cierre (900 min)
despues_cierre = df[df["event_time"] > 900]
print(despues_cierre["event_type"].value_counts())
print()
print("Detalle de los ejercicios despues del cierre:")
print(despues_cierre[despues_cierre["event_type"] == "exercise"][["day_id", "event_time", "resource", "outcome", "duration_min"]])

#Paso 21: revisar en detalle los 7 casos raros de duration_min en fuerza
pd.set_option("display.max_columns", None)

print("Caso 1: completed con duration_min vacio")
print(df[(df["event_type"] == "exercise") & (df["outcome"] == "completed") & (df["duration_min"].isna())])

print()
print("Caso 2: no completado con duration_min = 1.0")
print(df[(df["event_type"] == "exercise") & (df["outcome"] != "completed") & (df["duration_min"] == 1.0)])

#Paso 22: verificar que profile solo tenga valor en actividades de usuario
print(df.groupby("event_type")["profile"].apply(lambda x: x.notnull().sum()))

#Paso 23: corregir profile en filas de worker_travel (no le corresponde tener valor)
df.loc[(df["event_type"] == "worker_travel") & (df["profile"].notnull()), "profile"] = pd.NA

print(df.groupby("event_type")["profile"].apply(lambda x: x.notnull().sum()))

#Paso 24: verificar worker_travel completados con origin o destination faltante
print(df[(df["event_type"] == "worker_travel") & (df["outcome"] == "completed") & (df["destination"].isna())])
print()
print(df[(df["event_type"] == "worker_travel") & (df["outcome"] == "completed") & (df["origin"].isna())])

#Paso 25: verificar visitas completadas con duration_min, wait_min o dissatisfaction vacíos
print(df[(df["event_type"] == "visit") & (df["outcome"] == "completed") &
         (df["duration_min"].isna() | df["wait_min"].isna() | df["dissatisfaction"].isna())])

#Paso 26: verificar registration sin destination
print(df[(df["event_type"] == "registration") & (df["destination"].isna())])
print()
print(df[df["event_type"] == "registration"]["destination"].value_counts())

#Paso 27: convertir origin y destination a numero entero (permite NaN)
df["origin"] = pd.to_numeric(df["origin"], errors="coerce").astype("Int64")
df["destination"] = pd.to_numeric(df["destination"], errors="coerce").astype("Int64")

print(df[["origin", "destination"]].dtypes)
print(df[["origin", "destination"]].describe())

#Paso 28: corregir destination faltante en registration usando el valor fijo esperado (7)
df.loc[(df["event_type"] == "registration") & (df["destination"].isna()), "destination"] = 7

print(df[df["event_type"] == "registration"]["destination"].value_counts(dropna=False))

#Paso 29: verificar assistance sin destination
print(df[(df["event_type"] == "assistance") & (df["destination"].isna())])
print()
print(df[df["event_type"] == "assistance"]["destination"].value_counts(dropna=False))

print()
#Paso 30: verificar assistance con duration_min informado
print(df[(df["event_type"] == "assistance") & (df["duration_min"].notna())])

#Paso 31: verificar si cada unidad de maquina en assistance tiene una celda fija
print(df[df["event_type"] == "assistance"].groupby("resource")["destination"].unique())

#Paso 32: completar destination faltante en assistance usando la celda fija del resource
mapa_celdas = df[(df["event_type"] == "assistance") & (df["destination"].notna())].drop_duplicates("resource").set_index("resource")["destination"]

mascara_dest_faltante = (df["event_type"] == "assistance") & (df["destination"].isna())
df.loc[mascara_dest_faltante, "destination"] = df.loc[mascara_dest_faltante, "resource"].map(mapa_celdas)

print(df[df["event_type"] == "assistance"]["destination"].isna().sum())

#Paso 33: contar cuantas filas assistance tienen duration_min informado
print((df[df["event_type"] == "assistance"]["duration_min"].notna()).sum())

#Paso 34: limpiar duration_min residual en assistance (no le corresponde segun el diccionario)
df.loc[(df["event_type"] == "assistance") & (df["duration_min"].notna()), "duration_min"] = pd.NA

print("assistance con duration_min informado:", (df[df["event_type"] == "assistance"]["duration_min"].notna()).sum())

#Paso 35: verificar supply_pickup completados sin destination
print(df[(df["event_type"] == "supply_pickup") & (df["outcome"] == "completed") & (df["destination"].isna())][["resource"]].value_counts())

print()
print(df[df["event_type"] == "supply_pickup"].groupby("resource")["destination"].unique())

#Paso 36: completar destination faltante en supply_pickup usando el resource (towels->44, water->48)
mapa_insumos = {"towels": 44, "water": 48}

mascara_supply = (df["event_type"] == "supply_pickup") & (df["destination"].isna())
df.loc[mascara_supply, "destination"] = df.loc[mascara_supply, "resource"].map(mapa_insumos)

print(df[df["event_type"] == "supply_pickup"]["destination"].isna().sum())
print(df.groupby("resource")["destination"].unique().loc[["towels", "water"]])

#Paso 37: verificar la fila de supply_pickup con outcome empty
print(df[(df["event_type"] == "supply_pickup") & (df["outcome"] == "empty")])

#Paso 38: reclasificar la fila mal etiquetada de supply_pickup a stockout
mascara_mal_etiquetada = (df["event_type"] == "supply_pickup") & (df["outcome"] == "empty")
df.loc[mascara_mal_etiquetada, "event_type"] = "stockout"

print(df["event_type"].value_counts())
print(df[(df["event_type"] == "supply_pickup")]["outcome"].unique())

#Paso 38: guardar el dataframe limpio en un csv nuevo
df.to_csv("log_operacional_limpio.csv", index=False)
