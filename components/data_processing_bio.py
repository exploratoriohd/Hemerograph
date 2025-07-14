import streamlit as st
import numpy as np
import pandas as pd


def cargar_datos_biograficos():
    """
    Carga y fusiona dos dataframes con información biográfica, priorizando los datos 
    de datos_biograficos_bd, utilizando la lógica de concatenación y drop_duplicates.

    Returns:
        DataFrame fusionado con las columnas especificadas y datos priorizados.
    """
    try:
        # --- 1. Carga de los archivos CSV ---
        datos_biograficos_bd = pd.read_csv("data/colaboradores_datos_biograficos.csv", encoding="utf-8")
        datos_biograficos_rc = pd.read_csv("data/colaboradores_revistas_culturales.csv", encoding="utf-8")

        # --- 2. Preparación y Limpieza (basado en tu lógica) ---
        
        # Renombrar 'Origen' a 'PaisOrigen' en ambos DataFrames si existe
        for df in [datos_biograficos_bd, datos_biograficos_rc]:
            if 'Origen' in df.columns:
                df.rename(columns={'Origen': 'PaisOrigen'}, inplace=True)
            # Limpieza de la clave de fusión
            if 'Colaborador' in df.columns:
                df['Colaborador'] = df['Colaborador'].astype(str).str.strip()
                df.dropna(subset=['Colaborador'], inplace=True)

        # Seleccionar y asegurar columnas en datos_biograficos_bd
        columnas_bd = ['Colaborador', 'Seudonimo', 'Sexo', 'PaisOrigen', 'Nacimiento', 'Muerte', 'Fuente']
        for col in columnas_bd:
            if col not in datos_biograficos_bd.columns:
                datos_biograficos_bd[col] = np.nan
        df_bd_seleccionado = datos_biograficos_bd[columnas_bd].copy()

        # Seleccionar y asegurar columnas en datos_biograficos_rc
        columnas_rc = ['Colaborador', 'Seudonimo', 'Sexo', 'PaisOrigen', 'Nacimiento', 'Muerte', 'Fuente']
        for col in columnas_rc:
            if col not in datos_biograficos_rc.columns:
                datos_biograficos_rc[col] = np.nan
        df_rc_seleccionado = datos_biograficos_rc[columnas_rc].copy()

        # Reemplazar celdas vacías o con solo espacios por NaN para una fusión limpia
        df_bd_seleccionado.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df_rc_seleccionado.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        # --- 3. Lógica de Fusión con Prioridad (tu método) ---
        
        # Añadir una columna de origen para facilitar la eliminación de duplicados
        df_bd_seleccionado['Origen_DF'] = 'BD'
        df_rc_seleccionado['Origen_DF'] = 'RC'

        # Concatenar los dos dataframes
        df_concatenado = pd.concat([df_bd_seleccionado, df_rc_seleccionado], ignore_index=True)

        # Ordenar por Origen_DF para que 'BD' (la fuente prioritaria) esté primero.
        df_concatenado['Origen_DF'] = pd.Categorical(df_concatenado['Origen_DF'], categories=['BD', 'RC'], ordered=True)
        df_concatenado = df_concatenado.sort_values('Origen_DF')

        # Eliminar duplicados basándose en 'Colaborador', manteniendo la primera aparición (que será de 'BD')
        df_fusionado = df_concatenado.drop_duplicates(subset=['Colaborador'], keep='first')

        # Eliminar la columna temporal
        df_fusionado = df_fusionado.drop(columns=['Origen_DF'])

        return df_fusionado.reset_index(drop=True)

    except FileNotFoundError as e:
        st.error(f"ERROR: No se encontró un archivo CSV. Detalle: {e}")
        return pd.DataFrame()
    except Exception as ex:
        st.error(f"ERROR INESPERADO en 'cargar_datos_biograficos': {ex}")
        return pd.DataFrame()

def identificar_colaboradores(colaboradores_revistas, datos_biograficos):
    try:
        """
        Identifica colaboradores encontrados y no encontrados en los datos biográficos.

        Args:
            colaboradores_revistas (pd.DataFrame): DataFrame con los colaboradores de las revistas.
            datos_biograficos (pd.DataFrame): DataFrame con los datos biográficos.

        Returns:
            pd.DataFrame, pd.DataFrame: DataFrames de colaboradores encontrados y no encontrados.
        """
        # Identificar colaboradores no encontrados
        colaboradores_no_encontrados = colaboradores_revistas[~colaboradores_revistas["Colaborador"].isin(datos_biograficos["Colaborador"])]

        # Identificar colaboradores encontrados
        colaboradores_encontrados = colaboradores_revistas[colaboradores_revistas["Colaborador"].isin(datos_biograficos["Colaborador"])]

        return colaboradores_encontrados, colaboradores_no_encontrados
    except ValueError as ve:
        print(f"ERROR DENTRO DE cargar_datos_biograficos (ValueError): {ve}")
        # Aquí podrías imprimir el estado de los DataFrames justo antes del error si sabes dónde podría estar.
        # import traceback
        # traceback.print_exc() # Esto podría forzar una traza más explícita
        raise # Vuelve a lanzar el error para que Streamlit lo maneje
    except Exception as ex:
        print(f"ERROR DENTRO DE cargar_datos_biograficos (Otro Error): {ex}")
        # import traceback
        # traceback.print_exc()
        raise


def crear_dataset_unico(combined_dataset, datos_biograficos):
    try:
        """
        Fusiona el dataset combinado de revistas con los datos biográficos.
        Si existen columnas con el mismo nombre en ambos datasets (además de 'Colaborador'),
        se prioriza y conserva la versión proveniente de 'datos_biograficos'.

        Args:
            combined_dataset (pd.DataFrame): Datos de revistas combinados.
            datos_biograficos (pd.DataFrame): Datos biográficos de los colaboradores.

        Returns:
            pd.DataFrame: Dataset único con información combinada y consolidada, sin sufijos _x/_y.
        """
        # Asegurarse de que 'Colaborador' existe en ambos DataFrames
        if 'Colaborador' not in combined_dataset.columns:
            raise ValueError("El 'combined_dataset' debe tener una columna 'Colaborador' para la fusión.")
        if 'Colaborador' not in datos_biograficos.columns:
            raise ValueError("Los 'datos_biograficos' deben tener una columna 'Colaborador' para la fusión.")

        # Crear copias para trabajar de forma segura sin modificar los DataFrames originales
        left_df = combined_dataset.copy()
        right_df = datos_biograficos.copy()

        # 1. Identificar columnas con nombres superpuestos (excluyendo la clave de fusión 'Colaborador')
        overlapping_cols = [col for col in right_df.columns if col in left_df.columns and col != 'Colaborador']
        
        # Notificar al usuario (opcional, pero útil para depuración)
        # if overlapping_cols:
        #     print(f"Columnas superpuestas encontradas: {overlapping_cols}. Se usará la versión de los datos biográficos.")

        # 2. Eliminar las columnas superpuestas del DataFrame de la izquierda (el de revistas)
        #    Esto asegura que las versiones de 'datos_biograficos' sean las que prevalezcan.
        if overlapping_cols:
            left_df = left_df.drop(columns=overlapping_cols)

        # 3. Realizar la fusión. Ahora no habrá conflictos de nombres y no se crearán sufijos _x/_y.
        #    Se usa un 'left merge' para asegurar que todas las filas del dataset de revistas se conserven.
        dataset_unico = pd.merge(left_df, right_df, on="Colaborador", how="left")
        
        # 4. (Opcional pero recomendado) Reordenar las columnas para una mejor legibilidad.
        #    Poner 'Colaborador' y las columnas biográficas importantes al principio.
        cols_bio_principales = ['Sexo', 'PaisOrigen', 'Nacimiento', 'Muerte', 'Fuente', 'Seudonimo']
        
        # Construir la lista final de columnas en el orden deseado
        final_ordered_cols = ['Colaborador']
        
        # Añadir las columnas biográficas principales que existan en el resultado
        final_ordered_cols.extend([col for col in cols_bio_principales if col in dataset_unico.columns])
        
        # Añadir el resto de las columnas que no han sido añadidas aún
        final_ordered_cols.extend([col for col in dataset_unico.columns if col not in final_ordered_cols])
        
        # Aplicar el nuevo orden de columnas
        dataset_unico = dataset_unico[final_ordered_cols]
            
        return dataset_unico
    except ValueError as ve:
        print(f"ERROR DENTRO DE cargar_datos_biograficos (ValueError): {ve}")
        # Aquí podrías imprimir el estado de los DataFrames justo antes del error si sabes dónde podría estar.
        # import traceback
        # traceback.print_exc() # Esto podría forzar una traza más explícita
        raise # Vuelve a lanzar el error para que Streamlit lo maneje
    except Exception as ex:
        print(f"ERROR DENTRO DE cargar_datos_biograficos (Otro Error): {ex}")
        # import traceback
        # traceback.print_exc()
        raise

# def convertir_csv(df):
#     return df.to_csv(index=False).encode("utf-8")

def convertir_csv(df, nombre_archivo="dataset_convertido.csv"):
    """
    Convierte un DataFrame a CSV y lo ofrece para descarga en Streamlit.

    Args:
        df (pd.DataFrame): DataFrame a convertir.
        nombre_archivo (str): Nombre del archivo CSV para la descarga.
    """
    # Comprobar si df es un DataFrame y si no está vacío
    if isinstance(df, pd.DataFrame) and not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Descargar {nombre_archivo}",
            data=csv,
            file_name=nombre_archivo,
            mime='text/csv',
        )
    else:
        st.warning("No hay datos para descargar o el input no es un DataFrame válido.")
