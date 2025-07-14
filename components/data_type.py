import streamlit as st
import pandas as pd

def corregir_tipos_de_datos(df):
    """
    Corrige los tipos de datos para columnas específicas en el DataFrame.
    """
    if df is None:
        return None

    df_corregido = df.copy()
    columnas_de_ano = ["Año Publicación", "Nacimiento", "Muerte"]

    for col_ano in columnas_de_ano:
        if col_ano in df_corregido.columns:
            # Guardar el estado original para depuración si es necesario
            # original_series = df_corregido[col_ano].copy()
            
            # Paso 1: Convertir todo lo posible a numérico, lo que no se pueda será NaN
            df_corregido[col_ano] = pd.to_numeric(df_corregido[col_ano], errors='coerce')
            
            # Paso 2: Intentar convertir a Int64 (entero anulable de Pandas)
            # Este tipo maneja NaN de forma nativa dentro de un tipo entero.
            if not df_corregido[col_ano].isnull().all(): # Solo intentar si no son todos NaN
                try:
                    # Antes de convertir a Int64, si hay flotantes, podríamos redondearlos
                    # si sabemos que deberían ser enteros (ej. años no deberían tener decimales).
                    # Esto es opcional y depende de tus datos.
                    # df_corregido[col_ano] = df_corregido[col_ano].round(0) # Redondear a 0 decimales

                    df_corregido[col_ano] = df_corregido[col_ano].astype('Int64')
                except Exception as e_int:
                    st.warning(
                        f"Columna '{col_ano}': No se pudo convertir directamente a Int64 (entero anulable) después de to_numeric. "
                        f"Error: {e_int}. La columna podría contener flotantes o NaN. "
                        "Streamlit intentará manejarla, pero revisa los datos si esperabas solo enteros."
                    )
                    # Si la conversión a Int64 falla, la columna ya es numérica (posiblemente float con NaN)
                    # Arrow podría manejar esto mejor que un 'object' type con floats mixtos.
            # else:
                # Si la columna es toda NaN después de to_numeric, dejarla así. Int64 la manejaría bien.
                # df_corregido[col_ano] = df_corregido[col_ano].astype('Int64') # Podría funcionar también

    # Ejemplo para columnas de texto explícitas (esto puede ayudar a Arrow)
    columnas_de_texto = ["Colaborador", "Título Artículo", "Nombre Revista", "Fuente", "Seudonimo", "Tipo Publicación", "PaisOrigen"] # "PaisOrigen" podría ser texto
    for col_texto in columnas_de_texto:
        if col_texto in df_corregido.columns:
            # Rellenar NaN con string vacío ANTES de convertir a str, para evitar "nan" como string literal.
            df_corregido[col_texto] = df_corregido[col_texto].fillna('').astype(str)
            
    return df_corregido