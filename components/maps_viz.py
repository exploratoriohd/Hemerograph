import pandas as pd
import plotly.express as px
import numpy as np


def crear_mapa_coropletico(df_mapa, col_geocodigo, col_color, col_pais_hover, titulo, locationmode='ISO-3', usar_escala_log=False, hover_data_config=None, labels=None):
    """
    Crea un mapa coroplético interactivo, robusto y completo, con soporte para labels personalizados.
    """
    if df_mapa.empty or col_geocodigo not in df_mapa.columns:
        return None
    
    df_para_graficar = df_mapa.copy()
    col_a_usar_para_color = col_color
    barra_color_titulo = "Valor"

    if usar_escala_log:
        col_a_usar_para_color = f"{col_color}_log"
        df_para_graficar[col_a_usar_para_color] = np.log1p(df_para_graficar[col_color])
        barra_color_titulo = "Valor (Escala Log)"
        if hover_data_config is None: hover_data_config = {}
        hover_data_config[col_a_usar_para_color] = False

    fig = px.choropleth(
        df_para_graficar,
        locations=col_geocodigo,
        locationmode=locationmode,
        color=col_a_usar_para_color,
        hover_name=col_pais_hover,
        hover_data=hover_data_config,
        color_continuous_scale=px.colors.sequential.YlGnBu,
        title=titulo,
        labels=labels if labels else {} # <-- Aplicamos los labels personalizados aquí
    )
    
    fig.update_geos(
        visible=False, resolution=50,
        showcountries=True, countrycolor="DimGray",
        showland=True, landcolor="lightgray",
        showocean=True, oceancolor="azure"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar=dict(title=barra_color_titulo)
    )
    return fig

# def crear_mapa_coropletico(df_mapa, col_geocodigo, col_color, col_pais_hover, titulo, locationmode='ISO-3', usar_escala_log=False, hover_data_config=None):
#     """
#     Crea un mapa coroplético interactivo, permitiendo una configuración de hover personalizada.
#     """
#     if df_mapa.empty or col_geocodigo not in df_mapa.columns:
#         return None
    
#     df_para_graficar = df_mapa.copy()
#     col_a_usar_para_color = col_color
#     barra_color_titulo = "Valor"

#     if usar_escala_log:
#         col_a_usar_para_color = f"{col_color}_log"
#         df_para_graficar[col_a_usar_para_color] = np.log1p(df_para_graficar[col_color])
#         barra_color_titulo = "Valor (Escala Log)"
#         # Si usamos log, es bueno ocultar la columna de log del hover por defecto
#         if hover_data_config and col_a_usar_para_color in hover_data_config:
#              pass # El usuario tiene control total
#         elif hover_data_config is None:
#              hover_data_config = {}
#         hover_data_config[col_a_usar_para_color] = False

#     fig = px.choropleth(
#         df_para_graficar,
#         locations=col_geocodigo,
#         locationmode=locationmode,
#         color=col_a_usar_para_color,
#         hover_name=col_pais_hover,
#         hover_data=hover_data_config, # Usar el diccionario de configuración directamente
#         color_continuous_scale=px.colors.sequential.YlGnBu,
#         title=titulo
#     )
    
#     fig.update_geos(showcountries=True, countrycolor="DimGray", showland=True, landcolor="lightgray", showocean=True, oceancolor="azure")
#     fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, coloraxis_colorbar=dict(title=barra_color_titulo))
    
#     return fig

# def crear_mapa_coropletico(df_mapa, col_geocodigo, col_color, col_pais_hover, titulo, locationmode='ISO-3', usar_escala_log=False, hover_data_extra=None):
#     """
#     Crea un mapa coroplético interactivo. Dibuja un mapa mundial completo como base
#     y colorea los países para los que existen datos.

#     Args:
#         df_mapa (pd.DataFrame): DataFrame con datos procesados.
#         col_geocodigo (str): Columna con los geocódigos (ej. 'geocode' que contiene 'ESP').
#         col_color (str): Columna con el valor numérico para el color.
#         col_pais_hover (str): Columna con el nombre del país para el hover.
#         titulo (str): Título del mapa.
#         locationmode (str): Modo de localización de Plotly (ej. 'ISO-3').
#         usar_escala_log (bool): Si es True, aplica una escala logarítmica.
#     """
#     if df_mapa.empty or col_geocodigo not in df_mapa.columns:
#         return None
    
#     df_para_graficar = df_mapa.copy()
#     col_a_usar_para_color = col_color
#     barra_color_titulo = "Valor"

#     if usar_escala_log:
#         col_a_usar_para_color = f"{col_color}_log"
#         df_para_graficar[col_a_usar_para_color] = np.log1p(df_para_graficar[col_color])
#         barra_color_titulo = "Valor (Escala Log)"

#     # Configuración de hover más flexible
#     hover_data_config = {
#         col_color: True,
#         col_geocodigo: False
#     }
#     if usar_escala_log:
#         hover_data_config[col_a_usar_para_color] = False
    
#     # Añadir columnas extra al hover si se proporcionan
#     if hover_data_extra:
#         for col in hover_data_extra:
#             if col in df_para_graficar.columns:
#                 hover_data_config[col] = True

#     fig = px.choropleth(
#         df_para_graficar,
#         locations=col_geocodigo,
#         locationmode=locationmode,
#         color=col_a_usar_para_color,
#         hover_name=col_pais_hover,
#         hover_data=hover_data_config, # Usar configuración de hover flexible
#         color_continuous_scale=px.colors.sequential.YlGnBu,
#         title=titulo
#     )
# # --- Ajustes Finales de Estética (MODIFICADOS) ---
#     # Esta sección ahora se encarga de dibujar el mapa base completo.
#     fig.update_geos(
#         visible=False,
#         resolution=50,
#         showcountries=True, countrycolor="DimGray", # Dibuja las fronteras de TODOS los países en gris oscuro
#         showland=True, landcolor="lightgray",     # Rellena la tierra de los países SIN DATOS en gris claro
#         showocean=True, oceancolor="azure"           # Color del océano
#     )
    
#     fig.update_layout(
#         margin={"r":0,"t":40,"l":0,"b":0},
#         coloraxis_colorbar=dict(title=barra_color_titulo)
#     )
    
#     return fig
