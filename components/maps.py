# components/data_processing_maps.py
import pandas as pd
import streamlit as st

def enriquecer_con_geo_info(df_datos, df_world, col_pais_datos='PaisOrigen', col_pais_world='NAME_ES', col_iso_world='ISO_A3', col_region_world='REGION_WB'):
    """
    Toma el dataframe de datos y lo enriquece con el geocode y la región base desde el archivo world.csv.
    Esta es la función de estandarización principal.
    """
    if col_pais_datos not in df_datos.columns:
        st.warning(f"Advertencia: La columna de origen '{col_pais_datos}' no se encuentra en el DataFrame.")
        return pd.DataFrame()

    df_enriquecido = pd.merge(
        df_datos,
        df_world[[col_pais_world, col_iso_world, col_region_world]],
        left_on=col_pais_datos,
        right_on=col_pais_world,
        how='left'
    )
    df_enriquecido.rename(columns={col_iso_world: 'geocode', col_region_world: 'Region_Base'}, inplace=True)
    
    paises_no_mapeados = df_enriquecido[df_enriquecido['geocode'].isnull()][col_pais_datos].unique()
    if len(paises_no_mapeados) > 0:
        print(f"Advertencia: Países no encontrados en 'world.csv': {list(paises_no_mapeados)}")
        
    return df_enriquecido.dropna(subset=['geocode'])

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

def calcular_metricas_por_region(df, col_region='Region', col_colaborador='Colaborador'):
    """Calcula el número de colaboradores únicos y colaboraciones totales por región."""
    if col_region not in df.columns or col_colaborador not in df.columns: return pd.DataFrame()
    metricas_region = df.groupby(col_region).agg(
        Colaboradores_Unicos=(col_colaborador, 'nunique'),
        Colaboraciones_Totales=(col_colaborador, 'size')
    ).reset_index().sort_values(by='Colaboraciones_Totales', ascending=False)
    return metricas_region

def calcular_distribucion_geo_variable(df, col_categorica, valor_seleccionado, col_pais='PaisOrigen', col_geocodigo='geocode'):
    """Filtra un DataFrame y calcula la frecuencia de una ocurrencia por país."""
    if not all(c in df.columns for c in [col_categorica, col_pais, col_geocodigo]): return pd.DataFrame()
    df_filtrado = df[df[col_categorica] == valor_seleccionado]
    if df_filtrado.empty: return pd.DataFrame()
    resultado = df_filtrado.groupby([col_geocodigo, col_pais]).size().reset_index(name='Valor')
    return resultado.sort_values(by='Valor', ascending=False)