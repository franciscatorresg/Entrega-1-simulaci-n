import pandas as pd

#Carga de los archivos limpios y verificacion del estado inicial
df_op = pd.read_csv('log_operacional_limpio.csv')
df_rep = pd.read_csv('log_reparaciones_limpio.csv')

print(df_op.shape)
print(df_op['event_type'].value_counts())
print(df_rep.shape)



##Tipo de rutina seleccionada Ri considerando una observacion por visita.
#Paso 1: verificar los valores de routine dentro de las filas de visita
print(df_op[df_op['event_type'] == 'visit']['routine'].value_counts())
print(df_op[df_op['event_type'] == 'visit']['routine'].isnull().sum())

#Paso 2: extraer y exportar el subconjunto de Ri (tipo de rutina, una obs. por visita)
#me quedo con las filas event_type == 'visit' y las columnas day_id, user_id, profile, routine
df_rutina = df_op[df_op['event_type'] == 'visit'][['day_id', 'user_id', 'profile', 'routine']]
print(df_rutina.shape)
print(df_rutina.head())

df_rutina.to_csv('rutina.csv', index=False)



##Duraci´on efectiva de los ejercicios de fuerza completados, SFij, en minutos.
#Paso 1: verificar los valores de outcome dentro de las filas de ejercicio
print(df_op[df_op['event_type'] == 'exercise']['outcome'].value_counts())

#Paso 2: filtrar exercise completados (completed y completed_failed) y descartar duracion nula
df_fuerza = df_op[(df_op['event_type'] == 'exercise') & (df_op['outcome'].isin(['completed', 'completed_failed']))]
print('antes de sacar nulos:', df_fuerza.shape)
df_fuerza = df_fuerza[df_fuerza['duration_min'].notnull()]
print('despues de sacar nulos:', df_fuerza.shape)
print(df_fuerza['outcome'].value_counts())

#Paso 3: seleccionar columnas finales y exportar el subconjunto de SFij
df_fuerza = df_fuerza[['day_id', 'user_id', 'event_id', 'resource', 'routine', 'assistance', 'outcome', 'duration_min', 'profile']]
print(df_fuerza.shape)
print(df_fuerza.head())

df_fuerza.to_csv('fuerza.csv', index=False)



##Duraci´on efectiva de las sesiones de cardio realizadas, SCi , en minutos.
#Paso 1: verificar los valores de outcome dentro de las filas de cardio
print(df_op[df_op['event_type'] == 'cardio']['outcome'].value_counts())

#Paso 2: filtrar cardio completados (completed y completed_failed) y descartar duracion nula
df_cardio = df_op[(df_op['event_type'] == 'cardio') & (df_op['outcome'].isin(['completed', 'completed_failed']))]
print('antes de sacar nulos:', df_cardio.shape)
df_cardio = df_cardio[df_cardio['duration_min'].notnull()]
print('despues de sacar nulos:', df_cardio.shape)
print(df_cardio['outcome'].value_counts())

#Paso 3: seleccionar columnas finales y exportar el subconjunto de SCi
df_cardio = df_cardio[['day_id', 'user_id', 'event_id', 'routine', 'profile', 'outcome', 'duration_min']]
print(df_cardio.shape)
print(df_cardio.head())

df_cardio.to_csv('cardio.csv', index=False)



##Tiempo de reparaci´on de las m´aquinas, Srepf , en minutos.
#Para esta variable no inlcui un filtro aparte porque el log de reparaciones ya es lo suficientemente especifico... no hay nada que filtrar





