import pandas as pd

def calcular_frecuencia_colaboradores(df):
    """
    Calcula la frecuencia de colaboradores en el conjunto de datos.
    
    Args:
        df (pd.DataFrame): DataFrame con la columna "Colaborador".
    
    Returns:
        pd.DataFrame: Tabla con columnas "Colaborador" y "Frecuencia", ordenada en orden descendente.
    """
    # Contar la frecuencia de cada colaborador
    colaboradores_freq = df["Colaborador"].value_counts().reset_index()
    
    # Renombrar las columnas para mayor claridad
    colaboradores_freq.columns = ["Colaborador", "Frecuencia"]
    
    return colaboradores_freq



# DELETE ANONYMS
def eliminar_anonimos(df, anonimo_label="Anónimo"):
    """
    Filtra y elimina las entradas de colaboradores anónimos.

    Args:
        df (pd.DataFrame): DataFrame con las columnas "Colaborador" y "Frecuencia".
        anonimo_label (str): Nombre que identifica a los colaboradores anónimos (por defecto, "Anónimo").

    Returns:
        pd.DataFrame, int: DataFrame sin colaboradores anónimos y la frecuencia total de los anónimos eliminados.
    """
    # Extraer la frecuencia total de los anónimos
    anonimos_frecuencia = df.loc[df["Colaborador"] == anonimo_label, "Frecuencia"].sum()

    # Filtrar el DataFrame eliminando los anónimos
    df_filtrado = df[df["Colaborador"] != anonimo_label].reset_index(drop=True)

    return df_filtrado, anonimos_frecuencia


def obtener_mejores_conectados(revistas_datos_bio, output_file="top_75_mejor_conectados.csv"):
    # Seleccionar columnas relevantes
    colaboradores_conecciones = revistas_datos_bio[['Colaborador', 'PaisOrigen_x', 'NombreR', 'Tipo']].copy()

    # Filtrar "Anónimo" y contar conexiones por colaborador, revista y país
    colaboradores_conecciones = (
        colaboradores_conecciones[colaboradores_conecciones["Colaborador"] != "Anónimo"]
        .groupby(['Colaborador', 'NombreR', 'PaisOrigen_x'])
        .size()
        .reset_index(name='count')
    )

    # Contar el número de revistas distintas en las que aparece cada colaborador
    total_conecciones = (
        colaboradores_conecciones.groupby("Colaborador")["NombreR"]
        .nunique()
        .reset_index(name="Conecciones")
    )

    # Seleccionar los 75 colaboradores mejor conectados
    top_75_mejor_conectados = total_conecciones.nlargest(75, "Conecciones")["Colaborador"]

    # Filtrar solo los mejor conectados
    top_mejor_conectados = colaboradores_conecciones[
        colaboradores_conecciones["Colaborador"].isin(top_75_mejor_conectados)
    ]

    # Fusionar con total de conexiones y ordenar por número de conexiones
    top_mejor_conectados = (
        top_mejor_conectados.merge(total_conecciones, on="Colaborador")
        .sort_values(by=["Conecciones", "Colaborador"], ascending=[False, True])
    )

    # Guardar el resultado en un archivo CSV
    top_mejor_conectados.to_csv(output_file, encoding="utf-8", index=False)

    return top_mejor_conectados


def obtener_colaboradores_mejor_conectados(revistas_datos_bio):
    """
    Filtra y obtiene los 25 colaboradores con más conexiones en distintas revistas.
    """
    # Seleccionamos las columnas necesarias
    colaboradores_completo = revistas_datos_bio[['Colaborador', 'NombreR']].copy()

    # Contamos en cuántas publicaciones aparece cada autor en cada revista
    conexion_colaborador_revistas = (
        colaboradores_completo.groupby(['Colaborador', 'NombreR'])
        .size()
        .reset_index(name='count')
    )

    # Agrupamos por colaborador, sumando total de revistas en las que apareció
    conexion_colaborador_revistas = (
        conexion_colaborador_revistas.groupby("Colaborador")["NombreR"]
        .nunique()
        .reset_index(name="Nro_conexiones")
    )

    # Ordenamos los datos en orden descendente según el número de conexiones
    conexion_colaborador_revistas = conexion_colaborador_revistas.sort_values(
        by="Nro_conexiones", ascending=False
    )

    # Eliminamos a los colaboradores anónimos
    conexion_colaborador_revistas = conexion_colaborador_revistas.query("Colaborador != 'Anónimo'")

    # Extraemos los 25 colaboradores mejor conectados
    colaboradores_mejor_conectados = conexion_colaborador_revistas.head(25)

    return colaboradores_mejor_conectados

def calcular_conexiones_autor(df, col_autor='Colaborador', col_revista='Revista'):
    """
    Calcula el número de revistas únicas en las que cada colaborador ha participado.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        col_autor (str): El nombre de la columna del autor/colaborador.
        col_revista (str): El nombre de la columna de la revista.

    Returns:
        pd.DataFrame: Un DataFrame con las columnas [col_autor, 'Nro_Conexiones'],
                      ordenado por el número de conexiones en orden descendente.
    """
    # Verificar que las columnas necesarias existan
    if col_autor not in df.columns or col_revista not in df.columns:
        # Devolver un DataFrame vacío con la estructura esperada si faltan columnas
        return pd.DataFrame({col_autor: [], 'Nro_Conexiones': []})
    
    # Eliminar filas donde el autor o la revista sean nulos para evitar contarlos
    df_valid = df.dropna(subset=[col_autor, col_revista])
    
    if df_valid.empty:
        return pd.DataFrame({col_autor: [], 'Nro_Conexiones': []})
        
    # Agrupar por colaborador y contar el número de revistas únicas
    conexiones = (
        df_valid.groupby(col_autor)[col_revista]
        .nunique()
        .reset_index(name="Nro_Conexiones")
        .sort_values(by="Nro_Conexiones", ascending=False)
    )
    
    return conexiones


def calcular_frecuencia_tipologia(df, col_tipologia='Tipología'):
    """
    Calcula la frecuencia de cada valor en una columna de tipología textual.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        col_tipologia (str): El nombre de la columna que contiene las tipologías.

    Returns:
        pd.DataFrame: Un DataFrame con las columnas [col_tipologia, 'Frecuencia'],
                      ordenado por frecuencia en orden descendente.
    """
    if col_tipologia not in df.columns:
        return pd.DataFrame({col_tipologia: [], 'Frecuencia': []})

    df_valid = df.dropna(subset=[col_tipologia])
    
    if df_valid.empty:
        return pd.DataFrame({col_tipologia: [], 'Frecuencia': []})

    frecuencia = (
        df_valid[col_tipologia]
        .value_counts()
        .reset_index()
    )
    # value_counts() nombra las columnas como el nombre de la serie y 'count'. Estandarizamos.
    frecuencia.columns = [col_tipologia, 'Frecuencia']
    
    return frecuencia

def calcular_evolucion_tipologia_por_ano(df, col_fecha='Fecha Publicación', col_tipologia='Tipología'):
    """
    Calcula la frecuencia de cada tipología textual para cada año, extrayendo el año
    de una columna de fecha (que puede estar en formato ISO YYYY-MM-DD).

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        col_fecha (str): El nombre de la columna que contiene la fecha.
        col_tipologia (str): El nombre de la columna de la tipología.

    Returns:
        pd.DataFrame: Un DataFrame con las columnas ['Año', 'Tipología', 'Frecuencia'].
    """
    # Verificar que las columnas necesarias existan
    if col_fecha not in df.columns or col_tipologia not in df.columns:
        return pd.DataFrame({'Año': [], col_tipologia: [], 'Frecuencia': []})

    # Crear una copia para evitar modificar el DataFrame original (SettingWithCopyWarning)
    df_valid = df.copy()

    # 1. Convertir la columna de fecha a formato datetime de Pandas.
    #    'errors=coerce' convertirá cualquier fecha con formato incorrecto en NaT (Not a Time).
    df_valid[col_fecha] = pd.to_datetime(df_valid[col_fecha], errors='coerce')
    
    # 2. Eliminar filas donde la fecha no se pudo convertir (NaT) o la tipología es nula.
    df_valid.dropna(subset=[col_fecha, col_tipologia], inplace=True)

    if df_valid.empty:
        return pd.DataFrame({'Año': [], col_tipologia: [], 'Frecuencia': []})

    # 3. Extraer el año de la columna de fecha y crear una nueva columna 'Año'.
    df_valid['Año'] = df_valid[col_fecha].dt.year
    
    # 4. Agrupar por el nuevo 'Año' y por tipología, y contar las ocurrencias.
    evolucion = (
        df_valid.groupby(['Año', col_tipologia])
        .size()
        .reset_index(name="Frecuencia")
        .sort_values(by='Año') # Ordenar por año para el gráfico de líneas
    )
    
    return evolucion


def analizar_traducciones(df, col_traduccion='Traducción', col_traductor='Traductor', col_tipologia='Tipología', col_autor='Colaborador'):
    """
    Analiza datos para obtener frecuencia de traductores, tipologías traducidas y autores traducidos.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        col_traduccion (str): Columna que indica si es traducción.
        col_traductor (str): Columna de traductores.
        col_tipologia (str): Columna de tipologías.
        col_autor (str): Columna de autores/colaboradores.

    Returns:
        tuple: (df_frec_traductores, df_frec_tipologias, df_frec_autores_traducidos)
    """
    # DataFrames vacíos para devolver en caso de que no se pueda procesar
    df_frec_traductores_vacio = pd.DataFrame({'Traductor': [], 'Frecuencia': []})
    df_frec_tipologias_vacio = pd.DataFrame({'Tipología': [], 'Frecuencia': []})
    df_frec_autores_vacio = pd.DataFrame({'Colaborador': [], 'Frecuencia': []})

    # Verificar que las columnas clave existan
    if col_traduccion not in df.columns:
        return df_frec_traductores_vacio, df_frec_tipologias_vacio, df_frec_autores_vacio

    # Identificar las traducciones de forma robusta
    mascara_traduccion = df[col_traduccion].astype(str).str.strip().str.lower() == 'sí'
    df_traducciones = df[mascara_traduccion]

    if df_traducciones.empty:
        return df_frec_traductores_vacio, df_frec_tipologias_vacio, df_frec_autores_vacio
    
    # --- 1. Frecuencia de Traductores ---
    if col_traductor in df_traducciones.columns:
        df_validos = df_traducciones.dropna(subset=[col_traductor])
        df_validos = df_validos[df_validos[col_traductor].astype(str).str.strip() != '']
        frec_traductores = df_validos[col_traductor].value_counts().reset_index()
        frec_traductores.columns = ['Traductor', 'Frecuencia']
    else:
        frec_traductores = df_frec_traductores_vacio

    # --- 2. Frecuencia de Tipologías Traducidas ---
    if col_tipologia in df_traducciones.columns:
        df_validos = df_traducciones.dropna(subset=[col_tipologia])
        frec_tipologias = df_validos[col_tipologia].value_counts().reset_index()
        frec_tipologias.columns = ['Tipología', 'Frecuencia']
    else:
        frec_tipologias = df_frec_tipologias_vacio
        
    # --- 3. Frecuencia de Autores más Traducidos (NUEVO) ---
    if col_autor in df_traducciones.columns:
        df_validos = df_traducciones.dropna(subset=[col_autor])
        df_validos = df_validos[df_validos[col_autor].astype(str).str.strip() != '']
        frec_autores_traducidos = df_validos[col_autor].value_counts().reset_index()
        frec_autores_traducidos.columns = ['Colaborador', 'Frecuencia']
    else:
        frec_autores_traducidos = df_frec_autores_vacio

    return frec_traductores, frec_tipologias, frec_autores_traducidos


def preparar_csv_para_descarga(df):
    """
    Convierte un DataFrame a formato CSV (bytes) para ser usado con st.download_button.

    Args:
        df (pd.DataFrame): El DataFrame a convertir.

    Returns:
        bytes: Los datos del DataFrame como CSV en formato bytes, o None si el df está vacío o no es válido.
    """
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df.to_csv(index=False).encode('utf-8')
    return None
