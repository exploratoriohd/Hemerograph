# # pages/redes.py
# import streamlit as st
# import pandas as pd
# import networkx as nx
# from components.data_processing_networks import (
#     crear_red_bimodal, 
#     calcular_metricas_red, 
#     proyectar_y_detectar_comunidades
# )
# from components.visualization_networks import visualizar_red_pyvis, visualizar_red_estatica
# import streamlit.components.v1 as components

# st.set_page_config(page_title="Análisis de Redes", layout="wide")
# st.title("🕸️ Análisis de Redes de Colaboración")

# # # --- Inicialización del Estado de la Sesión ---
# # if 'graph_data' not in st.session_state:
# #     st.session_state.graph_data = None

# # --- Inicialización del Estado ---
# if 'analysis_results' not in st.session_state:
#     st.session_state.analysis_results = None

# # --- Carga y Preparación de Datos ---
# # df_listo = st.session_state.get('processed_df')
# df_listo = st.session_state.get('final_df_to_analyze')
# # data_cache_key = st.session_state.get('data_cache_key')

# # --- Carga y Verificación de Datos ---
# # Este es el único punto de entrada. Buscamos la clave que app.py SÍ está guardando.
# # df_listo = st.session_state.get('df_listo_para_seleccion_cols')

# if df_listo is None or df_listo.empty:
#     st.warning("Primero debes cargar y procesar los datos en la página de '🏠 Inicio'.")
#     st.info("Asegúrate de haber hecho clic en el botón 'Cargar y Procesar Archivos' en la página principal.")
#     st.stop()

# # --- Preparación de Datos para la Página ---
# df_redes_base = df_listo.copy()
# COL_REVISTA, COL_COLABORADOR, COL_FECHA = 'Revista', 'Colaborador', 'Fecha Publicación'

# # Verificar que las columnas esenciales para esta página existan
# columnas_necesarias = [COL_REVISTA, COL_COLABORADOR, COL_FECHA]
# columnas_faltantes = [col for col in columnas_necesarias if col not in df_redes_base.columns]

# if columnas_faltantes:
#     st.error(f"El dataset actual no contiene las siguientes columnas requeridas para el análisis de redes: **{', '.join(columnas_faltantes)}**. Por favor, asegúrate de que estén presentes en tus datos de origen o selecciónalas en la página de 'Inicio'.")
#     st.stop()

# # Preparación de la columna de Año
# if 'Año' not in df_redes_base.columns:
#     df_redes_base['Año'] = pd.to_datetime(df_redes_base[COL_FECHA], errors='coerce').dt.year
#     df_redes_base.dropna(subset=['Año'], inplace=True)
#     df_redes_base['Año'] = df_redes_base['Año'].astype(int)

# # --- Controles en la Sidebar ---
# st.sidebar.header("Filtros y Opciones para la Red")

# anos_disponibles = sorted(df_redes_base['Año'].unique())
# if anos_disponibles:
#     range_ano_seleccionado = st.sidebar.slider("1. Filtrar por Rango de Años:", anos_disponibles[0], anos_disponibles[-1], (anos_disponibles[0], anos_disponibles[-1]))
# else:
#     range_ano_seleccionado = None

# lista_revistas_red = sorted(df_redes_base[COL_REVISTA].dropna().unique())
# revistas_seleccionadas_red = st.sidebar.multiselect("2. Filtrar por revista(s):", lista_revistas_red, default=lista_revistas_red[:min(5, len(lista_revistas_red))])

# st.sidebar.markdown("---")
# # st.sidebar.header("Opciones de Análisis y Rendimiento")
# # limit_nodes = st.sidebar.checkbox("Limitar nodos en la visualización", value=True)
# # max_nodos = st.sidebar.number_input("Máximo de nodos a mostrar:", min_value=10, max_value=2000, value=300, step=50, disabled=not limit_nodes)
# # calc_modularidad = st.sidebar.checkbox("Calcular modularidad (comunidades)", value=True)
# # calc_interm = st.sidebar.checkbox("Calcular intermediación (lento)", value=False)
# # use_physics = st.sidebar.checkbox("Habilitar simulación física (lento)", value=False)
# st.sidebar.header("Opciones de análisis")
# calc_modularidad = st.sidebar.checkbox("Calcular modularidad (comunidades)", value=True)
# calc_interm = st.sidebar.checkbox("Calcular intermediación (lento)", value=False)
# limit_nodes = st.sidebar.checkbox("Limitar nodos en la visualización estática", value=True)
# max_nodos_static = st.sidebar.number_input("Máximo de nodos (vista estática):", 10, 1000, 150, 25, disabled=not limit_nodes)


# # --- Lógica Principal con Botón ---
# # st.header("Configuración del Análisis de Red")
# # if not revistas_seleccionadas_red:
# #     st.warning("Por favor, selecciona al menos una revista para empezar.")
# # else:
# #     if st.button("🚀 Generar Análisis de Red", type="primary", use_container_width=True):
# #         df_filtrado = df_redes_base.copy()
# #         if range_ano_seleccionado:
# #             df_filtrado = df_filtrado[
# #                 (df_filtrado['Año'] >= range_ano_seleccionado[0]) &
# #                 (df_filtrado['Año'] <= range_ano_seleccionado[1])
# #             ]
# #         if revistas_seleccionadas_red:
# #             df_filtrado = df_filtrado[df_filtrado[COL_REVISTA].isin(revistas_seleccionadas_red)]

# #         if df_filtrado.empty:
# #             st.warning("No hay datos para los filtros seleccionados.")
# #             st.session_state.graph_data = None
# #         else:
# #             with st.spinner("Realizando análisis..."):
# #                 G_completo = crear_red_bimodal(df_filtrado, COL_REVISTA, COL_COLABORADOR)
# #                 metricas_globales, df_metricas_nodos = calcular_metricas_red(G_completo, calc_interm)
# #                 mapa_comunidades = proyectar_y_detectar_comunidades(G_completo) if calc_modularidad else None
                
# #                 st.session_state.graph_data = {
# #                     "G_completo": G_completo, "metricas_globales": metricas_globales,
# #                     "df_metricas_nodos": df_metricas_nodos, "mapa_comunidades": mapa_comunidades,
# #                     "periodo": f"{range_ano_seleccionado[0]}-{range_ano_seleccionado[1]}" if range_ano_seleccionado else "Completo"
# #                 }

# st.header("Análisis de Red")
# if st.button("🚀 Generar análisis de Red", type="primary", use_container_width=True):
#     df_filtrado = df_redes_base.copy()
#     if range_ano_seleccionado:
#         df_filtrado = df_filtrado[
#             (df_filtrado['Año'] >= range_ano_seleccionado[0]) &
#             (df_filtrado['Año'] <= range_ano_seleccionado[1])
#         ]
#     if revistas_seleccionadas_red:
#         df_filtrado = df_filtrado[df_filtrado[COL_REVISTA].isin(revistas_seleccionadas_red)]

#     if df_filtrado.empty:
#         st.warning("No hay datos para los filtros seleccionados.")
#         st.session_state.graph_data = None
#     else:
#         with st.spinner("Realizando análisis..."):
#             G_completo = crear_red_bimodal(df_filtrado, COL_REVISTA, COL_COLABORADOR)
#             metricas_globales, df_metricas_nodos = calcular_metricas_red(G_completo, calc_interm)
#             mapa_comunidades = proyectar_y_detectar_comunidades(G_completo) if calc_modularidad else None
            
#             st.session_state.graph_data = {
#                 "G_completo": G_completo, "metricas_globales": metricas_globales,
#                 "df_metricas_nodos": df_metricas_nodos, "mapa_comunidades": mapa_comunidades,
#                 "periodo": f"{range_ano_seleccionado[0]}-{range_ano_seleccionado[1]}" if range_ano_seleccionado else "Completo"
#             }

#     if df_filtrado.empty:
#         st.warning("No hay datos para los filtros seleccionados.")
#         st.session_state.analysis_results = None
#     else:
#         with st.spinner("Realizando análisis..."):
#             # 1. Crear grafo y calcular métricas y comunidades
#             G_completo = crear_red_bimodal(df_filtrado)
#             metricas_globales, df_metricas_nodos = calcular_metricas_red(G_completo, calc_interm)
#             mapa_comunidades = proyectar_y_detectar_comunidades(G_completo) if calc_modularidad else None
            
#             # 2. Guardar todo en el estado de la sesión
#             st.session_state.analysis_results = {
#                 "G_completo": G_completo,
#                 "metricas_globales": metricas_globales,
#                 "df_metricas_nodos": df_metricas_nodos,
#                 "mapa_comunidades": mapa_comunidades
#             }

# # --- Visualización de Resultados ---
# # Esta sección ahora se ejecuta fuera del botón y lee los datos desde el estado de la sesión.
# # if st.session_state.graph_data:
# #     # Recuperar datos de la sesión
# #     data = st.session_state.graph_data
    
# #     st.header(f"Resultados para el Período {data['periodo']}")

# if st.session_state.analysis_results:
#     # Recuperar datos de la sesión
#     results = st.session_state.analysis_results
#     G_completo = results["G_completo"]
#     df_metricas_nodos = results["df_metricas_nodos"]

#     st.header("Resultados del análisis")   

#     # Mostrar Métricas Globales
#     st.subheader("Métricas globales de la red completa")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Nodos totales", f"{results['metricas_globales']['Nodos']:,}")
#     col2.metric("Conexiones totales", f"{results['metricas_globales']['Conexiones']:,}")
#     col3.metric("Densidad de la Red", f"{results['metricas_globales']['Densidad']:.4f}")
    
#     # --- Vista Previa Estática ---
#     st.subheader("Vista previa rápida de la red")
#     G_visual_static = G_completo
#     df_metricas_static = df_metricas_nodos
    
#     if limit_nodes and G_completo.number_of_nodes() > max_nodos_static:
#         nodos_importantes = df_metricas_nodos.head(max_nodos_static)['Nodo'].tolist()
#         G_visual_static = G_completo.subgraph(nodos_importantes)
#         df_metricas_static = df_metricas_nodos[df_metricas_nodos['Nodo'].isin(nodos_importantes)]
    
#     fig_estatica = visualizar_red_estatica(G_visual_static, df_metricas_static, results["mapa_comunidades"])
    
#     if fig_estatica:
#         st.pyplot(fig_estatica)
    
#     # --- Visualización Interactiva (Bajo Demanda) ---
#     with st.expander("🔬 Abrir visualización interactiva avanzada"):
#         st.info("El grafo interactivo cargará con la simulación física desactivada por defecto para un mejor rendimiento. Usa el panel de control inferior para activarla o cambiar el algoritmo de distribución.")
        
#         # Generar el HTML del grafo completo
#         with st.spinner("Generando visualización interactiva..."):
#              html_source = visualizar_red_pyvis(G_completo, df_metricas_nodos, results["mapa_comunidades"], physics_enabled=False)
        
#         # Mostrarlo
#         components.html(html_source, height=800, scrolling=True)

#     # --- Tablas de Datos ---
#     st.subheader("Tabla completa de métricas por nodo")
#     st.dataframe(df_metricas_nodos)
#     if results["mapa_comunidades"]:
#         st.subheader("Resultados del análisis de comunidades")
#         df_comunidades = pd.DataFrame(results["mapa_comunidades"].items(), columns=['Colaborador', 'ID_Comunidad'])
#         st.dataframe(df_comunidades.sort_values(by='ID_Comunidad'))
# else:
#     st.info("Utiliza los controles y haz clic en 'Generar Análisis de Red' para empezar.")

# pages/redes.py
import streamlit as st
import pandas as pd
from components.data_processing_networks import (
    crear_red_bimodal, 
    calcular_metricas_red, 
    proyectar_y_detectar_comunidades
)
from components.visualization_networks import visualizar_red_estatica, visualizar_red_pyvis
import streamlit.components.v1 as components

st.set_page_config(page_title="Análisis de Redes", layout="wide")
st.title("🕸️ Análisis de Redes de Colaboración")

# --- Inicialización del Estado ---
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- Carga y Preparación de Datos ---
# df_listo = st.session_state.get('processed_df')
df_listo = st.session_state.get('final_df_to_analyze')

if df_listo is None:
    st.warning("Primero debes cargar y configurar los datos en la página de '🏠 Inicio'.")
    st.stop()

df_redes_base = df_listo.copy()
COL_REVISTA, COL_COLABORADOR, COL_FECHA = 'Revista', 'Colaborador', 'Fecha Publicación'

if 'Año' not in df_redes_base.columns and COL_FECHA in df_redes_base.columns:
    df_redes_base['Año'] = pd.to_datetime(df_redes_base[COL_FECHA], errors='coerce').dt.year
    df_redes_base.dropna(subset=['Año'], inplace=True)
    df_redes_base['Año'] = df_redes_base['Año'].astype(int)

# --- Controles en la Sidebar ---
st.sidebar.header("Filtros y Opciones para la Red")
anos_disponibles = sorted(df_redes_base['Año'].unique()) if 'Año' in df_redes_base else []
if anos_disponibles:
    range_ano_seleccionado = st.sidebar.slider("1. Filtrar por Rango de Años:", anos_disponibles[0], anos_disponibles[-1], (anos_disponibles[0], anos_disponibles[-1]))
lista_revistas_red = sorted(df_redes_base[COL_REVISTA].dropna().unique())
revistas_seleccionadas_red = st.sidebar.multiselect("2. Filtrar por revista(s):", lista_revistas_red, default=lista_revistas_red[:min(5, len(lista_revistas_red))])

st.sidebar.markdown("---")
st.sidebar.header("Opciones de Análisis y Rendimiento")
limit_nodes = st.sidebar.checkbox("Limitar nodos en la visualización estática", value=True)
max_nodos_static = st.sidebar.number_input("Máximo de nodos (vista estática):", 10, 1000, 150, 25, disabled=not limit_nodes)
calc_modularidad = st.sidebar.checkbox("Calcular modularidad (comunidades)", value=True)
calc_interm = st.sidebar.checkbox("Calcular intermediación (lento)", value=False)

# --- Lógica Principal con Botón ---
st.header("Configuración del Análisis de Red")
if not revistas_seleccionadas_red:
    st.warning("Por favor, selecciona al menos una revista para empezar.")
else:
    if st.button("🚀 Generar Análisis de Red", type="primary", use_container_width=True):
        df_filtrado = df_redes_base[
            (df_redes_base[COL_REVISTA].isin(revistas_seleccionadas_red)) &
            (df_redes_base['Año'] >= range_ano_seleccionado[0]) &
            (df_redes_base['Año'] <= range_ano_seleccionado[1])
        ]
        if df_filtrado.empty:
            st.warning("No hay datos para los filtros seleccionados.")
            st.session_state.analysis_results = None
        else:
            with st.spinner("Realizando análisis..."):
                # --- CORRECCIÓN CLAVE: Crear una llave de caché única ---
                cache_key = f"{range_ano_seleccionado[0]}-{range_ano_seleccionado[1]}_{'_'.join(sorted(revistas_seleccionadas_red))}"
                
                # Pasar la llave a todas las funciones cacheadas
                G_completo = crear_red_bimodal(df_filtrado, cache_key=cache_key)
                metricas_globales, df_metricas_nodos = calcular_metricas_red(G_completo, calc_interm, cache_key=cache_key)
                mapa_comunidades = proyectar_y_detectar_comunidades(G_completo, cache_key=cache_key) if calc_modularidad else None
                
                st.session_state.analysis_results = {
                    "G_completo": G_completo, "metricas_globales": metricas_globales,
                    "df_metricas_nodos": df_metricas_nodos, "mapa_comunidades": mapa_comunidades
                }

# --- Visualización de Resultados ---
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    G_completo = results["G_completo"]
    df_metricas_nodos = results["df_metricas_nodos"]

    st.header("Resultados del Análisis")
    st.subheader("Métricas Globales de la Red Completa")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos Totales", f"{results['metricas_globales']['Nodos']:,}")
    col2.metric("Conexiones Totales", f"{results['metricas_globales']['Conexiones']:,}")
    col3.metric("Densidad de la Red", f"{results['metricas_globales']['Densidad']:.4f}")
    
    st.subheader("Vista Previa Rápida de la Red")
    G_visual_static = G_completo
    df_metricas_static = df_metricas_nodos
    if limit_nodes and G_completo.number_of_nodes() > max_nodos_static:
        nodos_importantes = df_metricas_nodos.head(max_nodos_static)['Nodo'].tolist()
        G_visual_static = G_completo.subgraph(nodos_importantes)
        df_metricas_static = df_metricas_nodos[df_metricas_nodos['Nodo'].isin(nodos_importantes)]
    
    fig_estatica = visualizar_red_estatica(G_visual_static, df_metricas_static, results["mapa_comunidades"])
    if fig_estatica:
        st.pyplot(fig_estatica)
    
    with st.expander("🔬 Abrir Visualización Interactiva Avanzada"):
        st.info("Usa el panel de control inferior para activar la simulación física, cambiar el algoritmo de distribución y más.")
        with st.spinner("Generando visualización interactiva..."):
             html_source = visualizar_red_pyvis(G_completo, df_metricas_nodos, results["mapa_comunidades"], physics_enabled=False)
        components.html(html_source, height=800, scrolling=True)

    st.subheader("Tabla Completa de Métricas por Nodo")
    st.dataframe(df_metricas_nodos)
    if results["mapa_comunidades"]:
        st.subheader("Resultados del Análisis de Comunidades")
        df_comunidades = pd.DataFrame(results["mapa_comunidades"].items(), columns=['Colaborador', 'ID_Comunidad'])
        st.dataframe(df_comunidades.sort_values(by='ID_Comunidad'))