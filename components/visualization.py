import plotly.express as px

def colaboradores_genero_total(dataset):
    """
    Crea la tabla de colaboradores por género y calcula la frecuencia de colaboraciones por autor.

    Args:
        combined_dataset (pd.DataFrame): Datos de revistas combinados con información biográfica.

    Returns:
        pd.DataFrame: DataFrame con información de género y colaboración de los autores.
    """
    # Filtramos las columnas relevantes
    colaboradores_genero = dataset[['Colaborador', 'Tipo']]
    colaboradores_genero = colaboradores_genero.groupby(['Colaborador', 'Tipo']).size().reset_index(name='n')

    # Filtrar colaboradores no anónimos

    colaboradores_genero = colaboradores_genero[colaboradores_genero['Colaborador'] != "Anónimo"]
    
    # Total de colaboraciones por autor
    total_colaboraciones_genero = colaboradores_genero.groupby(['Colaborador', 'Tipo']).agg({'n': 'sum'}).reset_index()
    
    # Top 100 colaboradores por número total de textos
    #top_100_colaboradores = total_colaboraciones_genero.nlargest(100, 'n')['Colaborador']

    # Filtrar top colaboradores
    #top_colaboradores_revistas_genero = colaboradores_genero[colaboradores_genero['Colaborador'].isin(top_100_colaboradores)]
    #top_colaboradores_revistas_genero = top_colaboradores_revistas_genero.groupby('Colaborador').agg({'n': 'sum'}).reset_index()

    # Total textos por autor
    #total_textos_por_autor = colaboradores_genero.groupby('Colaborador').agg({'n': 'sum'}).reset_index()

    # Top 25 autores con más textos
    #top_25_autores = total_textos_por_autor.nlargest(25, 'n')['Colaborador']
    top_25_autores = total_colaboraciones_genero.nlargest(25, 'n')['Colaborador']

    # Filtrar los datos para obtener los top 25 autores
    top_colaboradores_revistas = colaboradores_genero[colaboradores_genero['Colaborador'].isin(top_25_autores)]
    #top_colaboradores_revistas = top_colaboradores_revistas[top_colaboradores_revistas['Colaborador'] != "Anónimo"]
    top_colaboradores_revistas = top_colaboradores_revistas.groupby(['Colaborador', 'Tipo']).agg({'n': 'sum'}).reset_index()
    
    #top_colaboradores_revistas = top_colaboradores_revistas.sort_values(by="n", ascending=False)

    return top_colaboradores_revistas


def crear_grafico_barras_apiladas(top_colaboradores_revistas):
    """
    Crea un gráfico de barras apiladas mostrando el número de textos por autor y tipología textual.

    Args:
        top_colaboradores_revistas (pd.DataFrame): Datos de los autores más prolíficos.

    Returns:
        plotly.graph_objs._figure.Figure: Gráfico de barras apiladas de colaboraciones por autor y género.
    """
    # Crear gráfico de barras apiladas
    figura = px.bar(
        top_colaboradores_revistas,
        x="n",
        y="Colaborador",
        orientation="h",
        color="Tipo",
        text="n",
        labels={'n': 'Número de textos', 'Colaborador': 'Autor'},
        title="Número de textos por colaborador y tipología textual",
        template="plotly_white",
    )
    figura.update_layout(
        barmode='stack',
        yaxis={'categoryorder':'total ascending'},
        xaxis_title='Número de textos',
        yaxis_title='Colaborador',
        yaxis_tickfont=dict(size=8),
        legend_title=dict(text='Tipología')
    )

    return figura


def visualizar_mejores_conectados(colaboradores_mejor_conectados):
    """
    Genera un gráfico de barras horizontales de los colaboradores mejor conectados.
    """
    # Ordenamos los colaboradores por número de conexiones en orden descendente
    colaboradores_mejor_conectados = colaboradores_mejor_conectados.sort_values(
        by="Nro_conexiones", ascending=True
    )

    # Creamos la figura con Plotly Express
    figura = px.bar(
        colaboradores_mejor_conectados,
        x="Nro_conexiones",
        y="Colaborador",
        orientation="h",
        text="Nro_conexiones",
        labels={"Nro_conexiones": "Número de revistas en las que aparece", "Colaborador": "Autor"},
        title="Colaborador mejor conectado",
        template="plotly_white"
    )

    # Ajustes adicionales
    figura.update_layout(
        xaxis_title="Número de revistas en las que aparece",
        yaxis_title="Colaborador",
        yaxis=dict(tickfont=dict(size=8))
    )

    return figura

def crear_grafico_conexiones(df_conexiones, top_n=15, col_entidad='Colaborador', col_conexiones='Nro_Conexiones'):
    """
    Crea un gráfico de barras horizontales para mostrar entidades mejor conectadas.

    Args:
        df_conexiones (pd.DataFrame): DataFrame con la entidad y su número de conexiones.
        top_n (int): El número de las N entidades principales a mostrar.
        col_entidad (str): Nombre de la columna de la entidad (ej. 'Colaborador').
        col_conexiones (str): Nombre de la columna del conteo de conexiones.

    Returns:
        plotly.graph_objs._figure.Figure: La figura de Plotly para mostrar.
    """
    if df_conexiones.empty or top_n == 0:
        return None # Devuelve nada si no hay datos para graficar

    # Seleccionar el top N
    df_top = df_conexiones.head(top_n)
    
    # Título y etiquetas dinámicas
    titulo = f"Top {len(df_top)} {col_entidad}es por Número de Revistas Distintas"
    label_eje_x = "Número de Revistas Distintas"
    label_eje_y = col_entidad

    fig = px.bar(
        df_top,
        x=col_conexiones,
        y=col_entidad,
        orientation='h',
        title=titulo,
        labels={col_conexiones: label_eje_x, col_entidad: label_eje_y},
        text=col_conexiones
    )
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'}, # Los más conectados arriba
        xaxis_title=label_eje_x,
        yaxis_title=label_eje_y
    )
    
    return fig

def crear_grafico_frecuencia(df_frecuencia, top_n=10, col_categoria='Categoría', col_valor='Frecuencia', titulo="Gráfico de Frecuencia"):
    """
    Crea un gráfico de barras verticales para mostrar la frecuencia de categorías.

    Args:
        df_frecuencia (pd.DataFrame): DataFrame con la categoría y su frecuencia.
        top_n (int): El número de las N categorías principales a mostrar.
        col_categoria (str): Nombre de la columna de la categoría.
        col_valor (str): Nombre de la columna del conteo/frecuencia.
        titulo (str): Título del gráfico.

    Returns:
        plotly.graph_objs._figure.Figure: La figura de Plotly para mostrar.
    """
    if df_frecuencia.empty or top_n == 0:
        return None

    df_top = df_frecuencia.head(top_n)

    fig = px.bar(
        df_top,
        x=col_categoria,
        y=col_valor,
        title=titulo,
        labels={col_categoria: col_categoria, col_valor: "Número de Publicaciones"},
        text_auto=True # Muestra el valor directamente sobre las barras
    )
    
    fig.update_layout(
        xaxis_title=col_categoria,
        yaxis_title="Número de Publicaciones",
        xaxis={'categoryorder':'total descending'} # Ordenar por frecuencia
    )
    
    return fig

def crear_grafico_evolucion(df_evolucion, col_ano='Año Publicación', col_valor='Frecuencia', col_categoria='Tipología', titulo="Evolución de Tipologías por Año"):
    """
    Crea un gráfico de líneas para mostrar la evolución de categorías a lo largo del tiempo.

    Args:
        df_evolucion (pd.DataFrame): DataFrame con año, categoría y valor.
        col_ano (str): Nombre de la columna del año.
        col_valor (str): Nombre de la columna del valor/frecuencia.
        col_categoria (str): Nombre de la columna de la categoría (para colorear las líneas).
        titulo (str): Título del gráfico.

    Returns:
        plotly.graph_objs._figure.Figure: La figura de Plotly para mostrar.
    """
    if df_evolucion.empty:
        return None

    fig = px.line(
        df_evolucion,
        x=col_ano,
        y=col_valor,
        color=col_categoria,
        title=titulo,
        labels={
            col_ano: "Año de Publicación",
            col_valor: "Número de Publicaciones",
            col_categoria: "Tipología Textual"
        },
        markers=True # Añadir marcadores a los puntos de datos para mayor claridad
    )
    
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Número de Publicaciones",
        legend_title_text='Tipología'
    )
    
    return fig


# # VISUALIZACIÓN DE MAPAS

# def crear_mapa_coropletico(df_mapa, col_pais, col_color, titulo, hover_name_col=None):
#     """
#     Crea un mapa coroplético interactivo.

#     Args:
#         df_mapa (pd.DataFrame): DataFrame con los datos a mapear.
#         col_pais (str): Nombre de la columna con los nombres de los países.
#         col_color (str): Nombre de la columna que determinará el color de los países.
#         titulo (str): Título del mapa.
#         hover_name_col (str, optional): Columna para mostrar al pasar el mouse. Defaults to col_pais.

#     Returns:
#         plotly.graph_objs._figure.Figure: La figura de Plotly para mostrar.
#     """
#     if df_mapa.empty:
#         return None
        
#     if hover_name_col is None:
#         hover_name_col = col_pais

#     fig = px.choropleth(
#         df_mapa,
#         locations=col_pais,
#         locationmode='country names', # Plotly puede reconocer nombres de países en inglés
#         color=col_color,
#         hover_name=hover_name_col,
#         hover_data={col_pais: False, col_color: True}, # Personalizar datos del hover
#         color_continuous_scale=px.colors.sequential.Plasma, # Escala de colores
#         title=titulo
#     )
    
#     fig.update_layout(
#         margin={"r":0,"t":40,"l":0,"b":0}, # Márgenes ajustados
#         geo=dict(
#             showframe=False,
#             showcoastlines=False,
#             projection_type='equirectangular' # O 'natural earth'
#         )
#     )
#     return fig