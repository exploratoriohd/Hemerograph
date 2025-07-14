import pandas as pd
import numpy as np

# Para que pandas muestre todas las columnas al imprimir
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("="*30)
print("INICIO DE DIAGNÓSTICO DETALLADO")
print("="*30)

try:
    # --- PASO A: Cargar el primer archivo (_bd) ---
    print("\n[PASO A] Cargando 'colaboradores_datos_biograficos.csv'...")
    df_bd = pd.read_csv("data/colaboradores_datos_biograficos.csv", encoding="utf-8")
    print(f"-> Encontradas {len(df_bd)} filas y {len(df_bd.columns)} columnas.")
    print("-> Primeras 2 filas:")
    print(df_bd.head(2))

    # --- PASO B: Cargar el segundo archivo (_rc) ---
    print("\n[PASO B] Cargando 'colaboradores_revistas_culturales.csv'...")
    df_rc = pd.read_csv("data/colaboradores_revistas_culturales.csv", encoding="utf-8")
    print(f"-> Encontradas {len(df_rc)} filas y {len(df_rc.columns)} columnas.")
    print("-> Primeras 2 filas:")
    print(df_rc.head(2))

    # --- PASO C: Estandarización de columnas ---
    print("\n[PASO C] Estandarizando columnas...")
    columnas_requeridas = ["Colaborador", "Fuente", "Seudonimo", "Sexo", "PaisOrigen", "Nacimiento", "Muerte"]
    
    # Estandarizar BD
    df_bd_std = df_bd.iloc[:, :len(columnas_requeridas)].copy()
    df_bd_std.columns = columnas_requeridas
    
    # Estandarizar RC
    df_rc_std = pd.DataFrame()
    for col in columnas_requeridas:
        # Buscamos la columna, sin importar mayúsculas/minúsculas
        col_encontrada = next((c for c in df_rc.columns if c.lower() == col.lower()), None)
        if col_encontrada:
            df_rc_std[col] = df_rc[col_encontrada]
        else:
            df_rc_std[col] = np.nan # Si no existe, la crea vacía

    print("-> Columnas estandarizadas. Verificando 'PaisOrigen' en ambos DataFrames:")
    print(f"   - 'PaisOrigen' en BD (primeros valores): {list(df_bd_std['PaisOrigen'].dropna().head(3))}")
    print(f"   - 'PaisOrigen' en RC (primeros valores): {list(df_rc_std['PaisOrigen'].dropna().head(3))}")
    
    # --- PASO D: Limpieza de la clave de fusión ---
    print("\n[PASO D] Limpiando la columna 'Colaborador'...")
    df_bd_std['Colaborador'] = df_bd_std['Colaborador'].astype(str).str.strip()
    df_rc_std['Colaborador'] = df_rc_std['Colaborador'].astype(str).str.strip()
    
    # --- PASO E: Fusión (Merge) ---
    print("\n[PASO E] Realizando la fusión 'outer'...")
    df_fusionado = pd.merge(
        df_bd_std,
        df_rc_std,
        on="Colaborador",
        how="outer",
        suffixes=('_bd', '_rc'),
        indicator=True
    )
    print(f"-> Filas después de la fusión: {len(df_fusionado)}")
    print("-> Conteo del origen de las filas ('_merge'):")
    print(df_fusionado['_merge'].value_counts())

    # --- PASO F: Consolidación de 'PaisOrigen' ---
    print("\n[PASO F] Consolidando la columna 'PaisOrigen'...")
    df_fusionado['PaisOrigen_bd'] = df_fusionado['PaisOrigen_bd'].replace(r'^\s*$', np.nan, regex=True)
    df_fusionado['PaisOrigen_rc'] = df_fusionado['PaisOrigen_rc'].replace(r'^\s*$', np.nan, regex=True)
    df_fusionado['PaisOrigen_Consolidado'] = df_fusionado['PaisOrigen_bd'].combine_first(df_fusionado['PaisOrigen_rc'])
    
    print("-> Vista previa de la consolidación (mostrando filas donde el origen era solo de 'rc'):")
    vista_previa = df_fusionado[df_fusionado['_merge'] == 'right_only'][['Colaborador', 'PaisOrigen_bd', 'PaisOrigen_rc', 'PaisOrigen_Consolidado']]
    print(vista_previa.head(10))

    # --- PASO G: Comprobación Final ---
    print("\n[PASO G] Realizando comprobación final...")
    num_paises_consolidados = df_fusionado['PaisOrigen_Consolidado'].notna().sum()
    print(f"-> Número TOTAL de filas con 'PaisOrigen' después de consolidar: {num_paises_consolidados}")
    
    print(f"\n--- Buscando al colaborador de prueba: 'Max Aub' en el DataFrame FUSIONADO ---")
    registro_prueba = df_fusionado[df_fusionado['Colaborador'] == 'Max Aub']
    if not registro_prueba.empty:
        print("¡Colaborador de prueba ENCONTRADO en el DataFrame fusionado!")
        print(registro_prueba[['Colaborador', 'PaisOrigen_bd', 'PaisOrigen_rc', 'PaisOrigen_Consolidado']])
    else:
        print("ADVERTENCIA: 'Max Aub' no se encontró en la columna 'Colaborador' después de la fusión.")

except Exception as e:
    print(f"\n\n¡¡¡SE PRODUJO UN ERROR DURANTE LA PRUEBA!!!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*30)
print("FIN DEL DIAGNÓSTICO")
print("="*30)