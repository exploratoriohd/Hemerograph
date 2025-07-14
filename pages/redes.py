import streamlit as st
import pandas as pd
import networkx as nx
import streamlit.components.v1 as components

# Importar nuestras funciones optimizadas
from components.data_processing_networks import (
    crear_red_bimodal, 
    calcular_metricas_red, 
    proyectar_red_unimodal, 
    detectar_comunidades_louvain
)
from components.visualization_networks import visualizar_red_pyvis

st.set_page_config(page_title="Análisis de Redes", layout="wide")
st.title("🕸️ Análisis de Redes de Colaboración")

# --- Inicialización de Estado ---
if 'graph_G' not in st.session_state:
    st.session_state.graph_G = None
if 'df_metricas_nodos' not in st.session_state:
    st.session_state.df_metricas_nodos = None

# --- Carga y Verificación de Datos ---
df_listo = st.session_state.get('df_listo_para_seleccion_cols')
selected_cols = st.session_state.get('selected_columns_for_analysis')

if df_listo is None or not selected_cols:
    st.warning("Primero debes cargar y configurar los datos en la página de '🏠 Inicio'.")
    st.stop()

df_redes_base = df_listo[selected_cols].copy()
COL_REVISTA, COL_COLABORADOR, COL_FECHA = 'Revista', 'Colaborador', 'Fecha Publicación'

if not all(col in df_redes_base.columns for col in [COL_REVISTA, COL_COLABORADOR, COL_FECHA]):
    st.error(f"Se necesitan las columnas '{COL_REVISTA}', '{COL_COLABORADOR}' y '{COL_FECHA}'.")
    st.stop()

# --- Preparación de columna de Año ---
try:
    df_redes_base['Año'] = pd.to_datetime(df_redes_base[COL_FECHA], errors='coerce').dt.year
    df_redes_base.dropna(subset=['Año'], inplace=True)
    df_redes_base['Año'] = df_redes_base['Año'].astype(int)
except Exception as e:
    st.error(f"Error al procesar la columna de fechas '{COL_FECHA}': {e}")
    st.stop()

# --- Controles en la Sidebar ---
st.sidebar.header("Filtros y Opciones para la Red")

# Filtro de Año
anos_disponibles = sorted(df_redes_base['Año'].unique())
if anos_disponibles:
    min_ano, max_ano = anos_disponibles[0], anos_disponibles[-1]
    range_ano_seleccionado = st.sidebar.slider("Filtrar por Rango de Años:", min_ano, max_ano, (min_ano, max_ano))
else:
    range_ano_seleccionado = None

# Filtro de Revistas
lista_revistas_red = sorted(df_redes_base[COL_REVISTA].dropna().unique())
revistas_seleccionadas_red = st.sidebar.multiselect("Filtrar por revista(s):", lista_revistas_red, default=lista_revistas_red[:min(5, len(lista_revistas_red))])

# Opciones de Rendimiento
st.sidebar.markdown("---")
st.sidebar.header("Opciones de Rendimiento")
calc_interm = st.sidebar.checkbox("Calcular intermediación (lento)", value=False, help="Activa el cálculo de la métrica 'Intermediación'.")
use_physics = st.sidebar.checkbox("Habilitar simulación física", value=True, help="Activa la animación del grafo. Desactívalo si la red es muy grande.")

# --- Lógica Principal con Botón ---
st.header("1. Generar Grafo Principal")
st.write("Selecciona los filtros y opciones en la barra lateral y luego haz clic en el botón.")

if not revistas_seleccionadas_red:
    st.warning("Por favor, selecciona al menos una revista en la barra lateral.")
else:
    if st.button("Generar Red y Calcular Métricas", key="btn_generar_red"):
        df_filtrado_red = df_redes_base[df_redes_base[COL_REVISTA].isin(revistas_seleccionadas_red)]
        if range_ano_seleccionado:
            df_filtrado_red = df_filtrado_red[(df_filtrado_red['Año'] >= range_ano_seleccionado[0]) & (df_filtrado_red['Año'] <= range_ano_seleccionado[1])]

        if df_filtrado_red.empty:
            st.warning("No hay datos para el período y las revistas seleccionadas.")
        else:
            with st.spinner("Construyendo red y calculando métricas..."):
                G = crear_red_bimodal(df_filtrado_red, col_nodos_tipo1=COL_REVISTA, col_nodos_tipo2=COL_COLABORADOR)
                metricas_globales, df_metricas_nodos = calcular_metricas_red(G, calcular_intermediacion=calc_interm)
                st.session_state.graph_G = G
                st.session_state.df_metricas_nodos = df_metricas_nodos

            st.header(f"Resultados para el Período {range_ano_seleccionado[0]}-{range_ano_seleccionado[1]}" if range_ano_seleccionado else "Resultados de la Red")
            col1, col2, col3 = st.columns(3)
            col1.metric("Nodos Totales", f"{metricas_globales['Nodos']:,}")
            col2.metric("Conexiones Totales", f"{metricas_globales['Conexiones']:,}")
            col3.metric("Densidad de la Red", f"{metricas_globales['Densidad']:.4f}")
    
# --- Mostrar Grafo y Métricas si han sido generados ---
if st.session_state.get('graph_G'):
    st.subheader("Visualización del Grafo Interactivo")
    with st.spinner("Generando visualización..."):
        html_source = visualizar_red_pyvis(st.session_state.graph_G, st.session_state.df_metricas_nodos, physics_enabled=use_physics)
        if html_source: components.html(html_source, height=800)
    
    st.subheader("Métricas por Nodo")
    st.dataframe(st.session_state.df_metricas_nodos)

    # --- Sección de Análisis de Modularidad ---
    st.markdown("---")
    st.header("2. Análisis de Comunidades (Modularidad)")
    st.write("Este análisis se ejecutará sobre la red generada arriba.")
    with st.expander("Ejecutar análisis de comunidades"):
        if st.button("Detectar Comunidades de Colaboradores"):
            with st.spinner("Proyectando red y detectando comunidades..."):
                try:
                    G = st.session_state.graph_G # Usar el grafo guardado
                    df_metricas_nodos = st.session_state.df_metricas_nodos # Usar métricas guardadas
                    
                    nodos_colaboradores = [n for n, d in G.nodes(data=True) if d['bipartite'] == 1]
                    G_colaboradores = proyectar_red_unimodal(G, nodos_colaboradores)
                    mapa_comunidades = detectar_comunidades_louvain(G_colaboradores)
                    
                    st.success(f"¡Análisis completado! Se encontraron **{len(set(mapa_comunidades.values()))}** comunidades distintas.")
                    
                    st.subheader("Grafo Bimodal Coloreado por Comunidad")
                    html_source_comunidades = visualizar_red_pyvis(G, df_metricas_nodos, comunidades=mapa_comunidades)
                    if html_source_comunidades:
                        components.html(html_source_comunidades, height=800)
                    
                    df_comunidades = pd.DataFrame(mapa_comunidades.items(), columns=['Colaborador', 'ID_Comunidad'])
                    st.subheader("Miembros de cada Comunidad")
                    st.dataframe(df_comunidades.sort_values(by='ID_Comunidad'))
                except Exception as e:
                    st.error(f"Ocurrió un error durante el análisis de comunidades: {e}")        
else:
    st.info("Haz clic en 'Generar Red y Calcular Métricas' para empezar.")