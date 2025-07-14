import streamlit as st
import pandas as pd

# def estandarizar_paises_con_geocodigo(df, col_pais_origen='PaisOrigen', ruta_mapeo='data/world.csv', col_pais_mapeo='nombre_pais', col_geocodigo_mapeo='geo_code'):
#     """
#     Estandariza los nombres de los países a un geocódigo usando un archivo CSV de mapeo externo.

#     Args:
#         df (pd.DataFrame): DataFrame de entrada.
#         col_pais_origen (str): Columna en df con los nombres de los países a mapear.
#         ruta_mapeo (str): Ruta al archivo CSV con el mapeo.
#         col_pais_mapeo (str): Columna en el archivo de mapeo con los nombres de país (ej. en español).
#         col_geocodigo_mapeo (str): Columna en el archivo de mapeo con los geocódigos (ej. 'geo_code').

#     Returns:
#         pd.DataFrame: DataFrame original con una columna 'geocode' añadida.
#     """
#     if col_pais_origen not in df.columns:
#         st.warning(f"Advertencia: La columna '{col_pais_origen}' no se encuentra en el DataFrame.")
#         return df

#     try:
#         df_mapeo = pd.read_csv(ruta_mapeo, encoding='utf-8')
#     except FileNotFoundError:
#         st.error(f"Error: El archivo de mapeo no se encontró en '{ruta_mapeo}'.")
#         return df

#     if col_pais_mapeo not in df_mapeo.columns or col_geocodigo_mapeo not in df_mapeo.columns:
#         st.error(f"Error: El archivo '{ruta_mapeo}' debe contener las columnas '{col_pais_mapeo}' y '{col_geocodigo_mapeo}'.")
#         return df

#     df_copy = df.copy()
#     df_copy[col_pais_origen] = df_copy[col_pais_origen].astype(str).str.strip()
#     df_mapeo[col_pais_mapeo] = df_mapeo[col_pais_mapeo].astype(str).str.strip()
    
#     df_mapeo_reducido = df_mapeo[[col_pais_mapeo, col_geocodigo_mapeo]].drop_duplicates()
    
#     df_estandarizado = pd.merge(
#         df_copy, df_mapeo_reducido,
#         left_on=col_pais_origen,
#         right_on=col_pais_mapeo,
#         how='left'
#     )
    
#     # Renombrar la columna del geocódigo a un nombre estándar ('geocode') para uso interno
#     if col_geocodigo_mapeo != 'geocode':
#         df_estandarizado.rename(columns={col_geocodigo_mapeo: 'geocode'}, inplace=True)
        
#     paises_no_mapeados = df_estandarizado[df_estandarizado['geocode'].isnull()][col_pais_origen].unique()
#     if len(paises_no_mapeados) > 0:
#         print(f"Advertencia: Países no encontrados en el archivo de mapeo: {list(paises_no_mapeados)}")

#     return df_estandarizado


def calcular_metricas_por_pais(df, metrica='colaboradores_unicos', col_pais='PaisOrigen', col_colaborador='Colaborador'):
    """Calcula métricas agregadas por país."""
    if col_pais not in df.columns or col_colaborador not in df.columns:
        return pd.DataFrame()
    
    df_valid = df.dropna(subset=[col_pais, col_colaborador])
    
    if metrica == 'colaboradores_unicos':
        # Contar colaboradores únicos por país
        resultado = df_valid.groupby(col_pais)[col_colaborador].nunique().reset_index()
        resultado.columns = [col_pais, 'Valor']
    elif metrica == 'colaboraciones_totales':
        # Contar filas (colaboraciones) totales por país
        resultado = df_valid.groupby(col_pais).size().reset_index(name='Valor')
    else:
        resultado = pd.DataFrame()
        
    return resultado.sort_values(by='Valor', ascending=False)


# def procesar_datos_geograficos_con_regiones(df_datos, df_world, col_pais_datos='PaisOrigen', col_pais_world='NAME_ES', col_iso_world='ISO_A3_EH', col_region_world='REGION_WB', pais_central=None, paises_a_aislar=None, grupos_personalizados=None):
#     """
#     Enriquece el DataFrame principal con información geográfica y regional de un archivo 'world',
#     y luego aplica una clasificación regional dinámica y personalizable.

#     Jerarquía de Clasificación:
#     1. País Central -> 2. Países Aislados -> 3. Grupos Personalizados -> 4. Región Base de world.csv

#     Returns:
#         pd.DataFrame: DataFrame enriquecido con columnas 'geocode', 'Region_Base' y la columna final 'Region'.
#     """
#     if col_pais_datos not in df_datos.columns:
#         print(f"Advertencia: La columna '{col_pais_datos}' no se encuentra en el DataFrame de datos.")
#         return df_datos

#     # 1. Enriquecer los datos fusionando con el archivo world.csv
#     # Usamos un 'left merge' para conservar todas las filas del dataset de datos original.
#     df_enriquecido = pd.merge(
#         df_datos,
#         df_world[[col_pais_world, col_iso_world, col_region_world]],
#         left_on=col_pais_datos,
#         right_on=col_pais_world,
#         how='left'
#     )
#     # Renombrar las nuevas columnas para tener nombres estándar y limpios
#     df_enriquecido.rename(columns={col_iso_world: 'geocode', col_region_world: 'Region_Base'}, inplace=True)

#     # 2. Aplicar la clasificación dinámica para crear la columna final 'Region'
#     if paises_a_aislar is None: paises_a_aislar = []
#     if grupos_personalizados is None: grupos_personalizados = {}
    
#     pais_a_grupo_personalizado = {
#         pais: nombre_grupo 
#         for nombre_grupo, paises in grupos_personalizados.items() 
#         for pais in paises
#     }

#     def asignar_region_final(row):
#         pais_actual = row[col_pais_datos]
        
#         if pd.notna(pais_actual):
#             if pais_actual == pais_central: return f"CENTRAL: {pais_actual}"
#             if pais_actual in paises_a_aislar: return pais_actual
#             if pais_actual in pais_a_grupo_personalizado: return pais_a_grupo_personalizado[pais_actual]
        
#         # Por defecto, usar la región base de world.csv
#         return row.get('Region_Base', "Sin Región Asignada")

#     df_enriquecido['Region'] = df_enriquecido.apply(asignar_region_final, axis=1)
    
#     return df_enriquecido

def enriquecer_con_geo_info(df_datos, df_world, col_pais_datos='PaisOrigen', col_pais_world='NAME_ES', col_iso_world='ISO_A3_EH', col_region_world='REGION_WB'):
    """
    Toma el dataframe de datos y lo enriquece con el geocode y la región base desde el archivo world.
    """
    if col_pais_datos not in df_datos.columns:
        print(f"Advertencia: La columna '{col_pais_datos}' no se encuentra en los datos.")
        return df_datos

    df_enriquecido = pd.merge(
        df_datos,
        df_world[[col_pais_world, col_iso_world, col_region_world]],
        left_on=col_pais_datos,
        right_on=col_pais_world,
        how='left'
    )
    df_enriquecido.rename(columns={col_iso_world: 'geocode', col_region_world: 'Region_Base'}, inplace=True)
    
    # Informar sobre países que no se pudieron mapear
    paises_no_mapeados = df_enriquecido[df_enriquecido['geocode'].isnull()][col_pais_datos].unique()
    if len(paises_no_mapeados) > 0:
        print(f"Advertencia: Países no encontrados en el archivo de mapeo 'world.csv': {list(paises_no_mapeados)}")
        
    return df_enriquecido


def aplicar_clasificacion_dinamica(df_enriquecido, col_pais_datos='PaisOrigen', pais_central=None, paises_a_aislar=None, grupos_personalizados=None):
    """
    Aplica la jerarquía de clasificación regional sobre un DataFrame que ya tiene una 'Region_Base'.
    """
    if paises_a_aislar is None: paises_a_aislar = []
    if grupos_personalizados is None: grupos_personalizados = {}

    pais_a_grupo_personalizado = {pais: nombre_grupo for nombre_grupo, paises in grupos_personalizados.items() for pais in paises}

    def asignar_region_final(row):
        pais_actual = row[col_pais_datos]
        if pd.notna(pais_actual):
            if pais_actual == pais_central: return f"CENTRAL: {pais_actual}"
            if pais_actual in paises_a_aislar: return pais_actual
            if pais_actual in pais_a_grupo_personalizado: return pais_a_grupo_personalizado[pais_actual]
        return row.get('Region_Base', "Sin Región Asignada")

    df_resultado = df_enriquecido.copy()
    df_resultado['Region'] = df_resultado.apply(asignar_region_final, axis=1)
    return df_resultado


# En data_processing.py

# def clasificacion_regional_dinamica(df, col_pais='PaisOrigen', pais_central=None, paises_a_aislar=None, grupos_personalizados=None):
#     """
#     Aplica una clasificación regional dinámica y personalizable.
    
#     Prioridad de clasificación:
#     1. País Central.
#     2. Países a Aislar individualmente.
#     3. Grupos Personalizados definidos por el usuario.
#     4. Reglas de clasificación por defecto.
#     """
#     if paises_a_aislar is None:
#         paises_a_aislar = []
#     if grupos_personalizados is None:
#         grupos_personalizados = {}

#     # Crear un mapa inverso para búsqueda rápida: {'País': 'NombreDelGrupo'}
#     pais_a_grupo_personalizado = {
#         pais: nombre_grupo 
#         for nombre_grupo, paises in grupos_personalizados.items() 
#         for pais in paises
#     }

#     def clasificar(pais):
#         # Regla 1: País Central
#         if pais is not None and pais == pais_central:
#             return f"CENTRAL: {pais}"

#         # Regla 2: Países Aislados
#         if pais is not None and pais in paises_a_aislar:
#             return pais

#         # Regla 3: Grupos Personalizados
#         if pais is not None and pais in pais_a_grupo_personalizado:
#             return pais_a_grupo_personalizado[pais]

#         # Regla 4: Clasificación por defecto
#         hispanoamerica = ["Mexico", "Argentina", "Colombia", "Chile", "Peru", "Ecuador", "Venezuela",
#                           "Uruguay", "Paraguay", "Bolivia", "Cuba", "Dominican Rep.", "Guatemala",
#                           "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Puerto Rico"]
#         europa = ["France", "Germany", "Italy", "Belgium", "Netherlands", "Switzerland", "Austria", 
#                   "Sweden", "Norway", "Denmark", "Russia", "Ukraine", "Poland", "Hungary", "Romania"]

#         if pais in ["United States", "United States of America", "United Kingdom", "Ireland"]: return "EE.UU.-Reino Unido-Irlanda"
#         if pais == "Spain": return "España"
#         if pais in hispanoamerica: return "Hispanoamérica"
#         if pais in ["Brazil", "Portugal"]: return "Portugal-Brasil"
#         if pais in europa: return "Resto de Europa"
#         return "Otras Regiones"

#     if col_pais not in df.columns:
#         return df
    
#     df_copy = df.copy()
#     df_copy['Region'] = df_copy[col_pais].apply(clasificar)
#     return df_copy


# def crear_regiones_geograficas(df_datos, df_world_regions, col_geocodigo_datos, col_geocodigo_world, col_region_world, col_pais_datos, pais_central=None, paises_a_aislar=None, grupos_personalizados=None):
#     """
#     Clasifica los datos en regiones geográficas con una jerarquía de personalización.
#     Jerarquía: 1. País Central -> 2. Países Aislados -> 3. Grupos Personalizados -> 4. Región Base del archivo world.
    
#     Args:
#         df_datos (pd.DataFrame): Tu DataFrame principal (ya estandarizado con geocódigos).
#         df_world_regions (pd.DataFrame): El DataFrame cargado desde world.csv.
#         col_geocodigo_datos (str): Nombre de la columna de geocódigos en tus datos.
#         col_geocodigo_world (str): Nombre de la columna de geocódigos en el archivo world.
#         col_region_world (str): Nombre de la columna de regiones en el archivo world.
#         col_pais_datos (str): Nombre de la columna con los nombres de países originales.
#         pais_central (str, optional): El país a tratar como 'CENTRAL'.
#         paises_a_aislar (list, optional): Lista de países a tratar individualmente.
#         grupos_personalizados (dict, optional): Diccionario de grupos personalizados. E.g., {'Cono Sur': ['Argentina', 'Chile']}.

#     Returns:
#         pd.DataFrame: DataFrame con una nueva columna 'Region' que contiene la clasificación final.
#     """
#     if paises_a_aislar is None: paises_a_aislar = []
#     if grupos_personalizados is None: grupos_personalizados = {}

#     # 1. Fusionar los datos principales con las regiones base del archivo world.csv
#     df_con_region_base = pd.merge(
#         df_datos,
#         df_world_regions[[col_geocodigo_world, col_region_world]],
#         left_on=col_geocodigo_datos,
#         right_on=col_geocodigo_world,
#         how='left'
#     )
#     # Rellenar regiones no encontradas con un valor por defecto
#     df_con_region_base[col_region_world] = df_con_region_base[col_region_world].fillna('Sin Región Asignada')


#     # 2. Crear mapa inverso para grupos personalizados para una búsqueda eficiente
#     pais_a_grupo_personalizado = {
#         pais: nombre_grupo 
#         for nombre_grupo, paises in grupos_personalizados.items() 
#         for pais in paises
#     }

#     # 3. Función para aplicar la jerarquía de clasificación a cada fila
#     def asignar_region_final(row):
#         pais_actual = row[col_pais_datos]
        
#         if pais_actual is not None:
#             # Prioridad 1: País Central
#             if pais_actual == pais_central:
#                 return f"CENTRAL: {pais_actual}"
#             # Prioridad 2: Países Aislados
#             if pais_actual in paises_a_aislar:
#                 return pais_actual
#             # Prioridad 3: Grupos Personalizados
#             if pais_actual in pais_a_grupo_personalizado:
#                 return pais_a_grupo_personalizado[pais_actual]
        
#         # Prioridad 4 (por defecto): La región base del archivo world.csv
#         return row[col_region_world]

#     # Aplicar la función a cada fila para crear la columna final 'Region'
#     df_con_region_base['Region'] = df_con_region_base.apply(asignar_region_final, axis=1)
    
#     return df_con_region_base

# def agregar_clasificacion_regional(df, col_pais='PaisOrigen'):
#     """Aplica una clasificación regional a los países, basada en la lógica proporcionada."""
    
#     def clasificar(pais):
#         # Esta lógica está adaptada de tu script mapa_gaceta_literaria.py
#         if pais in ["United States of America", "United Kingdom", "Ireland"]: return "EE.UU.-Reino Unido-Irlanda"
#         if pais == "Spain": return "España"
#         if pais in ["Mexico", "Argentina", "Colombia", "Chile", "Peru", "Ecuador", "Venezuela",
#                     "Uruguay", "Paraguay", "Bolivia", "Cuba", "Dominican Rep.", "Guatemala",
#                     "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Puerto Rico"]: return "Hispanoamérica"
#         if pais in ["Brazil", "Portugal"]: return "Portugal-Brasil"
#         # Simplificando el resto para el ejemplo
#         europa = ["France", "Germany", "Italy", "Belgium", "Netherlands", "Switzerland", "Austria", "Sweden", "Norway", "Denmark", "Russia"]
#         if pais in europa: return "Resto de Europa"
#         return "Otras Regiones"

#     if col_pais not in df.columns:
#         return df
    
#     df_copy = df.copy()
#     df_copy['Region'] = df_copy[col_pais].apply(clasificar)
#     return df_copy


def calcular_distribucion_geo_variable(df, var_categorica, valor_seleccionado, col_pais='PaisOrigen'):
    """Filtra el df por un valor de una variable y cuenta las ocurrencias por país."""
    if var_categorica not in df.columns or col_pais not in df.columns:
        return pd.DataFrame()
        
    df_filtrado = df[df[var_categorica] == valor_seleccionado]
    resultado = df_filtrado.groupby(col_pais).size().reset_index(name='Valor')
    return resultado.sort_values(by='Valor', ascending=False)

def agregar_clasificacion_regional(df, col_pais='PaisOrigen'):
    """Aplica una clasificación regional a los países, basada en la lógica proporcionada."""
    
    def clasificar(pais):
        # Esta lógica está adaptada de tu script mapa_gaceta_literaria.py
        # ¡Puedes personalizar estas regiones como quieras!
        hispanoamerica = ["Mexico", "Argentina", "Colombia", "Chile", "Peru", "Ecuador", "Venezuela",
                          "Uruguay", "Paraguay", "Bolivia", "Cuba", "Dominican Rep.", "Guatemala",
                          "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Puerto Rico"]
        europa = ["France", "Germany", "Italy", "Belgium", "Netherlands", "Switzerland", "Austria", 
                  "Sweden", "Norway", "Denmark", "Russia", "Ukraine", "Poland", "Hungary", "Romania"]

        if pais in ["United States", "United States of America", "United Kingdom", "Ireland"]: return "EE.UU.-Reino Unido-Irlanda"
        if pais == "Spain": return "España"
        if pais in hispanoamerica: return "Hispanoamérica"
        if pais in ["Brazil", "Portugal"]: return "Portugal-Brasil"
        if pais in europa: return "Resto de Europa"
        if pais == "Greenland": return "Otras Regiones" # Groenlandia es un caso especial
        return "Otras Regiones"

    if col_pais not in df.columns:
        return df
    
    df_copy = df.copy()
    # Primero aplicamos el mapeo de español a inglés si es necesario (asumiendo que clasificar() espera inglés)
    # Esta es la misma lógica de la función estandarizar_paises_con_geocodigo, que ya aplica esto.
    # Por lo tanto, el DataFrame que reciba esta función ya debería tener nombres en inglés o estandarizados.
    df_copy['Region'] = df_copy[col_pais].apply(clasificar)
    return df_copy


def calcular_metricas_por_region(df, col_region='Region', col_colaborador='Colaborador'):
    """Calcula el número de colaboradores únicos y colaboraciones totales por región."""
    if col_region not in df.columns or col_colaborador not in df.columns:
        return pd.DataFrame()
    
    # Calcular ambas métricas a la vez usando el método .agg()
    metricas_region = df.groupby(col_region).agg(
        Colaboradores_Unicos=(col_colaborador, 'nunique'),
        Colaboraciones_Totales=(col_colaborador, 'size')
    ).reset_index().sort_values(by='Colaboraciones_Totales', ascending=False)
    
    return metricas_region

def calcular_distribucion_geo_variable(df, col_categorica, valor_seleccionado, col_pais='PaisOrigen', col_geocodigo='geocode'):
    """
    Filtra un DataFrame por un valor específico de una variable categórica y
    luego calcula la frecuencia de esa ocurrencia por país.

    Args:
        df (pd.DataFrame): DataFrame de entrada (debe tener geocódigos y la columna categórica).
        col_categorica (str): La columna categórica a filtrar (ej. 'Tipología').
        valor_seleccionado: El valor específico a contar (ej. 'Ensayo').
        col_pais (str): Columna con los nombres de los países.
        col_geocodigo (str): Columna con los geocódigos.

    Returns:
        pd.DataFrame: DataFrame con geocódigo, nombre de país y la frecuencia ('Valor') del ítem seleccionado.
    """
    # Verificar que las columnas necesarias existan
    if not all(c in df.columns for c in [col_categorica, col_pais, col_geocodigo]):
        return pd.DataFrame()

    # Filtrar el DataFrame por el valor seleccionado en la columna categórica
    df_filtrado = df[df[col_categorica] == valor_seleccionado]

    if df_filtrado.empty:
        return pd.DataFrame()

    # Agrupar por país y contar las ocurrencias
    resultado = df_filtrado.groupby([col_geocodigo, col_pais]).size().reset_index(name='Valor')
    return resultado.sort_values(by='Valor', ascending=False)