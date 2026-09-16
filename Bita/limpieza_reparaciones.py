import pandas as pd

#Paso 1: cargar el archivo y verificar estado inicial
df = pd.read_csv('log_reparaciones_historico.csv', sep=';', encoding='utf-8-sig')

# Verificación inicial
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print('Duplicados repair_id:', df['repair_id'].duplicated().sum())
print('Duplicados filas completas:', df.duplicated().sum())

#Paso 2: arreglar las comas decimales en las columnas numéricas
for col in ['failure_time', 'repair_duration_min']:
    df[col] = df[col].str.replace(',', '.').astype(float)

print(df[['failure_time', 'repair_duration_min']].describe())

#Paso 3: verificar categoría inválida en machine_type
print(df['machine_type'].unique())
print(df[df['machine_type'] == 'registro_erroneo'])

#Paso 4: reclasificar el registro_erroneo a lat_pulldown usando el unit_id
df.loc[df['machine_type'] == 'registro_erroneo', 'machine_type'] = 'lat_pulldown'

print(df['machine_type'].unique())
print(df.loc[168])

#Paso 5: verificar el valor 99 en cell
print(df[df['cell'] == 99])
print(df[df['unit_id'] == 'shoulder_press-01']['cell'].unique())

#Paso 6: corregir el valor sentinela 99 en cell usando el unit_id
df.loc[(df['unit_id'] == 'shoulder_press-01') & (df['cell'] == 99), 'cell'] = 49

print(df.groupby('unit_id')['cell'].unique())
print(df.loc[1220])

#Paso 7: verificar duraciones negativas en repair_duration_min
print(df[df['repair_duration_min'] < 0])

#Paso 8: corregir duraciones negativas en repair_duration_min tomando el valor absoluto
df.loc[df['repair_duration_min'] < 0, 'repair_duration_min'] = df.loc[df['repair_duration_min'] < 0, 'repair_duration_min'].abs()

print(df.loc[[812, 871]])
print(df['repair_duration_min'].describe())

#Paso 9: validación final
print('Nulos:', df.isnull().sum().sum())
print('Duplicados repair_id:', df['repair_id'].duplicated().sum())
print('machine_type:', sorted(df['machine_type'].unique()))
print('Rango failure_time:', df['failure_time'].min(), '-', df['failure_time'].max())
print('Rango repair_duration_min:', df['repair_duration_min'].min(), '-', df['repair_duration_min'].max())
print('cell únicos por unit_id, todos con largo 1:', (df.groupby('unit_id')['cell'].nunique() == 1).all())

#Paso 10: exportar el archivo limpio
df.to_csv('log_reparaciones_limpio.csv', index=False)
