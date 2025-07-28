# components/data_processing_networks.py
import pandas as pd
import igraph as ig
import streamlit as st
try:
    import leidenalg as la
    LEIDENALG_INSTALLED = True
except ImportError:
    LEIDENALG_INSTALLED = False

# @st.cache_data
# def crear_red_bimodal_ig(df, col_nodos_tipo1='Revista', col_nodos_tipo2='Colaborador', cache_key=None):
#     """
#     Crea una red bimodal usando igraph, manejando correctamente el mapeo de nombres a IDs numéricos.
#     """
#     df_edges = df[[col_nodos_tipo1, col_nodos_tipo2]].dropna().copy()

#     # --- CORRECCIÓN CLAVE: Limpiar espacios en blanco ---
#     df_edges[col_nodos_tipo1] = df_edges[col_nodos_tipo1].astype(str).str.strip()
#     df_edges[col_nodos_tipo2] = df_edges[col_nodos_tipo2].astype(str).str.strip()
    
#     # 1. Crear un catálogo de todos los nodos únicos (vértices)
#     nodos_tipo1_names = df_edges[col_nodos_tipo1].unique()
#     nodos_tipo2_names = df_edges[col_nodos_tipo2].unique()
    
#     # Crear un DataFrame de vértices con sus nombres y tipos
#     vertices_tipo1 = pd.DataFrame({'name': nodos_tipo1_names, 'type': 0}) # 0 para Revistas
#     vertices_tipo2 = pd.DataFrame({'name': nodos_tipo2_names, 'type': 1}) # 1 para Colaboradores
#     df_vertices = pd.concat([vertices_tipo1, vertices_tipo2]).drop_duplicates(subset=['name']).reset_index(drop=True)

#     # 2. Usar igraph.Graph.DataFrame, que maneja la conversión de nombres a IDs automáticamente
#     #    'vertices=df_vertices' le da a igraph el catálogo de todos los nodos y sus atributos.
#     #    'use_vids=False' le dice que los nombres en el df de aristas son los nombres de los vértices.
#     g = ig.Graph.DataFrame(df_edges, directed=False, vertices=df_vertices, use_vids=False)
    
#     return g
@st.cache_data
def crear_red_bimodal_ig(df, col_nodos_tipo1='Revista', col_nodos_tipo2='Colaborador', cache_key=None):
    """
    Crea una red bimodal usando igraph, con una limpieza de datos exhaustiva para evitar inconsistencias.
    """
    df_edges = df[[col_nodos_tipo1, col_nodos_tipo2]].dropna().copy()
    
    # --- CORRECCIÓN DEFINITIVA: Limpieza de datos en el origen ---
    # Eliminar espacios en blanco al principio y al final de TODOS los nombres.
    df_edges[col_nodos_tipo1] = df_edges[col_nodos_tipo1].astype(str).str.strip()
    df_edges[col_nodos_tipo2] = df_edges[col_nodos_tipo2].astype(str).str.strip()
    
    # Eliminar cualquier fila donde los nombres hayan quedado vacíos después de la limpieza
    df_edges = df_edges[(df_edges[col_nodos_tipo1] != '') & (df_edges[col_nodos_tipo2] != '')]
    
    # 1. Crear el catálogo de vértices a partir de los datos YA limpios
    nodos_tipo1_names = df_edges[col_nodos_tipo1].unique()
    nodos_tipo2_names = df_edges[col_nodos_tipo2].unique()
    
    vertices_tipo1 = pd.DataFrame({'name': nodos_tipo1_names, 'type': 0})
    vertices_tipo2 = pd.DataFrame({'name': nodos_tipo2_names, 'type': 1})
    df_vertices = pd.concat([vertices_tipo1, vertices_tipo2]).drop_duplicates(subset=['name']).reset_index(drop=True)

    # 2. Crear el grafo usando el método robusto de igraph
    g = ig.Graph.DataFrame(df_edges, directed=False, vertices=df_vertices, use_vids=False)
    
    return g


@st.cache_data
def calcular_metricas_red_ig(_g, calcular_intermediacion=False, cache_key=None):
    """Calcula métricas clave de una red igraph."""
    if _g.vcount() == 0:
        return {"Nodos": 0, "Conexiones": 0, "Densidad": 0}, pd.DataFrame()

    metricas_globales = {"Nodos": _g.vcount(), "Conexiones": _g.ecount(), "Densidad": _g.density()}
    # degree_centrality = _g.degree(normalized=True)
     # Se calcula el grado bruto y luego se normaliza manualmente.
    raw_degree = _g.degree()
    num_nodos = _g.vcount()
    degree_centrality = [d / (num_nodos - 1) for d in raw_degree] if num_nodos > 1 else [0] * num_nodos
    betweenness_centrality = _g.betweenness(directed=False) if calcular_intermediacion else [0] * _g.vcount()

    df_metricas_nodos = pd.DataFrame({
        'Nodo': _g.vs['name'], # 'name' fue asignado al crear el grafo
        'Tipo': ['Revista' if t == 0 else 'Colaborador' for t in _g.vs['type']], # 'type' también fue asignado
        'Grado_Centralidad': degree_centrality,
        'Intermediacion': betweenness_centrality
    })
    
    return metricas_globales, df_metricas_nodos.sort_values(by='Grado_Centralidad', ascending=False)


@st.cache_data
def proyectar_y_detectar_comunidades_ig(_g, algoritmo='multilevel', cache_key=None):
    """
    Detects communities using different algorithms. Includes the corrected method
    for Leiden on bipartite networks.
    """
    if _g.vcount() == 0:
        return None, "Grafo vacío."

    mapa_comunidad = {}
    
    # --- MÉTODO LEIDEN BIPARTITO ---
    if algoritmo == 'leiden':
        if not LEIDENALG_INSTALLED:
            return None, "La librería 'leidenalg' no está instalada."
        
        st.info("Ejecutando el algoritmo de Leiden directamente sobre la red bimodal...")
        
        particion_bipartita = la.RBConfigurationVertexPartition(
            _g,
            initial_membership=_g.vs['type'],
            weights=None
        )
        
        optimizador = la.Optimiser()
        
        # --- CORRECCIÓN CLAVE ---
        # La función modifica 'particion_bipartita' in-place y devuelve el score.
        # No necesitamos guardar el return value.
        optimizador.optimise_partition(particion_bipartita, n_iterations=-1)
        
        # Leemos la membresía del objeto original que fue modificado.
        mapa_comunidad = {_g.vs[i]['name']: membresia for i, membresia in enumerate(particion_bipartita.membership)}
        # --- FIN DE LA CORRECCIÓN ---

        return mapa_comunidad, None

    # --- MÉTODOS BASADOS EN PROYECCIÓN (sin cambios) ---
    st.info(f"Proyectando la red para el algoritmo '{algoritmo}'...")
    if 'type' not in _g.vertex_attributes() or len(_g.vs.select(type_eq=1)) == 0:
        return None, "No hay nodos 'Colaborador' para proyectar."
        
    g_proyectada = _g.bipartite_projection(types='type', which=1)
    
    if g_proyectada.vcount() == 0:
        return None, "La red proyectada está vacía."

    if algoritmo == 'multilevel':
        comunidades = g_proyectada.community_multilevel()
    elif algoritmo == 'walktrap':
        comunidades = g_proyectada.community_walktrap().as_clustering()
    elif algoritmo == 'fastgreedy':
        comunidades = g_proyectada.community_fastgreedy().as_clustering()
    else:
        comunidades = g_proyectada.community_multilevel()
    
    mapa_comunidad = {g_proyectada.vs[i]['name']: membresia for i, membresia in enumerate(comunidades.membership)}
    
    return mapa_comunidad, None