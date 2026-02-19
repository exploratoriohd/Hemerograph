# pages/redes.py
import streamlit as st
import pandas as pd
import networkx as nx
from components.data_processing_networks import (
    crear_red_bimodal_ig, 
    calcular_metricas_red_ig, 
    proyectar_y_detectar_comunidades_ig
)
from components.visualization_networks import visualizar_red_estatica, visualizar_red_pyvis
import streamlit.components.v1 as components

st.set_page_config(page_title="Hemerograph - Análisis de Redes", layout="wide")
st.title("🕸️ Análisis de redes de colaboración")

# --- Inicialización del Estado ---
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- Carga y Preparación de Datos ---
# df_listo = st.session_state.get('processed_df')
df_listo = st.session_state.get('final_df_to_analyze')

if df_listo is None:
    st.warning("Primero debe cargar y configurar los datos en la página de '🏠 Inicio'.")
    st.stop()

df_redes_base = df_listo.copy()
COL_REVISTA, COL_COLABORADOR, COL_FECHA = 'Revista', 'Colaborador', 'Fecha Publicación'

if 'Año' not in df_redes_base.columns and COL_FECHA in df_redes_base.columns:
    df_redes_base['Año'] = pd.to_datetime(df_redes_base[COL_FECHA], errors='coerce').dt.year
    df_redes_base.dropna(subset=['Año'], inplace=True)
    df_redes_base['Año'] = df_redes_base['Año'].astype(int)

# --- Controles en la Sidebar ---
st.sidebar.header("Filtros y opciones para la red")
anos_disponibles = sorted(df_redes_base['Año'].unique()) if 'Año' in df_redes_base else []
if anos_disponibles:
     range_ano_seleccionado = st.sidebar.slider("1. Filtrar por rango de años:", anos_disponibles[0], anos_disponibles[-1], (anos_disponibles[0], anos_disponibles[-1]))
lista_revistas_red = sorted(df_redes_base[COL_REVISTA].dropna().unique())
revistas_seleccionadas_red = st.sidebar.multiselect("2. Filtrar por revista(s):", lista_revistas_red, default=lista_revistas_red[:min(5, len(lista_revistas_red))])

st.sidebar.markdown("---")
st.sidebar.header("Opciones de limpieza y análisis")
exclude_anonyms = st.sidebar.checkbox("Excluir 'Anónimos'", value=True, help="Excluye las entradas donde el colaborador es 'Anónimo' o 'Anonym' del análisis.")

st.sidebar.markdown("---")
st.sidebar.header("Opciones de análisis y rendimiento")
limit_nodes = st.sidebar.checkbox("Limitar nodos en la visualización estática", value=True)
max_nodos_static = st.sidebar.number_input("Máximo de nodos (vista estática):", 10, 1000, 150, 25, disabled=not limit_nodes)
calc_modularidad = st.sidebar.checkbox("Calcular modularidad (comunidades)", value=True)
calc_interm = st.sidebar.checkbox("Calcular intermediación (lento)", value=False)

# --- WIDGET DE ALGORITMOS ACTUALIZADO ---
algoritmo_comunidad = st.sidebar.selectbox(
    "Algoritmo de comunidad:",
    options=['leiden', 'multilevel', 'walktrap', 'fastgreedy'], # Nuevas opciones
    index=0, # 'leiden' por defecto por ser el más robusto
    help="""
    - **leiden**: (Recomendado) El más robusto. Opera directamente sobre la red bimodal.
    - **multilevel**: Rápido y bueno para la mayoría de los casos (algoritmo de Louvain).
    - **walktrap**: Bueno para encontrar comunidades bien definidas.
    - **fastgreedy**: Un enfoque jerárquico rápido.
    """,
    disabled=not calc_modularidad
)


# --- Lógica Principal con Botón ---
st.header("Configuración del análisis de la red")
if not revistas_seleccionadas_red:
    st.warning("Por favor, selecciona al menos una revista para empezar.")
else:
    if st.button("Generar análisis de red", type="primary", use_container_width=True):
        df_filtrado = df_redes_base[
            (df_redes_base[COL_REVISTA].isin(revistas_seleccionadas_red)) &
            (df_redes_base['Año'] >= range_ano_seleccionado[0]) &
            (df_redes_base['Año'] <= range_ano_seleccionado[1])
        ]

        if exclude_anonyms:
            anonym_labels = ['anónimo', 'anonymous', 'Anónimo', 'Anonymous', 'Redacción']
            # Filtrar filas donde el colaborador (en minúsculas) no esté en nuestra lista de anónimos
            df_filtrado = df_filtrado[~df_filtrado[COL_COLABORADOR].astype(str).str.lower().isin(anonym_labels)]

        if df_filtrado.empty:
            st.warning("No hay datos para los filtros seleccionados.")
            st.session_state.analysis_results = None
        else:
            with st.spinner("Realizando análisis con igraph..."):
                cache_key = f"{range_ano_seleccionado[0]}-{range_ano_seleccionado[1]}_{'_'.join(sorted(revistas_seleccionadas_red))}"
                
                # 1. Crear el grafo base con igraph (rápido)
                G_ig = crear_red_bimodal_ig(df_filtrado, COL_REVISTA, COL_COLABORADOR, cache_key=cache_key)
                # G_ig = crear_red_bimodal_ig(df_filtrado, COL_REVISTA, COL_COLABORADOR)

                
                
                mapa_comunidades, error_msg = None, None
                if calc_modularidad:
                    mapa_comunidades, error_msg = proyectar_y_detectar_comunidades_ig(G_ig, algoritmo=algoritmo_comunidad, cache_key=cache_key)
                    # mapa_comunidades, error_msg = proyectar_y_detectar_comunidades_ig(G_ig, algoritmo=algoritmo_comunidad)

                metricas_globales, df_metricas_nodos = calcular_metricas_red_ig(G_ig, calc_interm, cache_key=cache_key)
                # metricas_globales, df_metricas_nodos = calcular_metricas_red_ig(G_ig, calc_interm)


                # # 2. Calcular modularidad y métricas con igraph (rápido)
                # mapa_comunidades = proyectar_y_detectar_comunidades_ig(G_ig, cache_key=cache_key) if calc_modularidad else None
                # metricas_globales, df_metricas_nodos = calcular_metricas_red_ig(G_ig, calc_interm, cache_key=cache_key)
                
                # --- CORRECCIÓN DEFINITIVA: Conversión Robusta a NetworkX ---
                G_nx = nx.Graph()
                
                # 1. Añadir nodos con sus nombres de texto y atributos
                for v in G_ig.vs:
                    G_nx.add_node(v['name'], bipartite=v['type']) # El nodo es el nombre (ej. "Revista X")

                # 2. Añadir las aristas usando los nombres de texto
                edges_with_names = [(G_ig.vs[e.source]['name'], G_ig.vs[e.target]['name']) for e in G_ig.es]
                G_nx.add_edges_from(edges_with_names)
                # --- FIN DE LA CORRECCIÓN ---

                # 4. Guardar resultados en el estado de la sesión
                st.session_state.analysis_results = {
                    "G_completo": G_nx, # Guardamos la versión networkx, ahora 100% compatible
                    "metricas_globales": metricas_globales,
                    "df_metricas_nodos": df_metricas_nodos,
                    "mapa_comunidades": mapa_comunidades
                }
            st.success("Análisis con igraph completado.")

# --- Visualización de Resultados ---
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    G_completo = results["G_completo"]
    df_metricas_nodos = results["df_metricas_nodos"]

    st.header("Resultados del análisis")
    st.subheader("Métricas Globales de la Red Completa")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos totales", f"{results['metricas_globales']['Nodos']:,}")
    col2.metric("Conexiones totales", f"{results['metricas_globales']['Conexiones']:,}")
    col3.metric("Densidad de la red", f"{results['metricas_globales']['Densidad']:.4f}")
    
    st.subheader("Vista previa de la red")
    G_visual_static = G_completo
    df_metricas_static = df_metricas_nodos
    if limit_nodes and G_completo.number_of_nodes() > max_nodos_static:
        nodos_importantes = df_metricas_nodos.head(max_nodos_static)['Nodo'].tolist()
        G_visual_static = G_completo.subgraph(nodos_importantes)
        df_metricas_static = df_metricas_nodos[df_metricas_nodos['Nodo'].isin(nodos_importantes)]
    
    fig_estatica = visualizar_red_estatica(G_visual_static, df_metricas_static, results["mapa_comunidades"])
    if fig_estatica:
        st.pyplot(fig_estatica)
    
    with st.expander("🔬 Abrir visualización interactiva avanzada"):
        st.info("Usa el panel de control inferior para activar la simulación física, cambiar el algoritmo de distribución y más.")
        with st.spinner("Generando visualización interactiva..."):
            #  html_source = visualizar_red_pyvis(G_completo, df_metricas_nodos, results["mapa_comunidades"], physics_enabled=False)
            html_source = visualizar_red_pyvis(G_completo, df_metricas_nodos, results["mapa_comunidades"])
        components.html(html_source, height=800, scrolling=True)

    st.subheader("Tabla de métricas por nodo")
    st.dataframe(df_metricas_nodos)
    # if results["mapa_comunidades"]:
    #     st.subheader("Resultados del Análisis de Comunidades")
    #     df_comunidades = pd.DataFrame(results["mapa_comunidades"].items(), columns=['Colaborador', 'ID_Comunidad'])
    #     st.dataframe(df_comunidades.sort_values(by='ID_Comunidad'))

        # --- Mostrar tabla de comunidades si se calculó ---
    if results["mapa_comunidades"]:
        st.subheader("Resultados del análisis de comunidades")
        df_comunidades = pd.DataFrame(results["mapa_comunidades"].items(), columns=['Nodo', 'ID_Comunidad'])
        # Ahora la tabla puede contener revistas y colaboradores si se usó Leiden
        st.dataframe(df_comunidades.sort_values(by='ID_Comunidad'))
    # Si hubo un mensaje de error en la detección de comunidades, mostrarlo
    elif 'error_msg' in results and results['error_msg']:
        st.subheader("Resultados del análisis de comunidades")
        st.error(results['error_msg'])

    
st.markdown("---")
st.header("Navegar a otras visualizaciones")
st.markdown("Continúa tu análisis explorando otras perspectivas de los datos.")

col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    st.page_link("views/dashboard.py", label="**Dashboard Integrado**", icon="📊", use_container_width=True)

with col_nav2:
    st.page_link("views/mapas.py", label="**Análisis Geógrafico y Mapas**", icon="🗺️", use_container_width=True)
