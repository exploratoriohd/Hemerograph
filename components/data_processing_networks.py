import streamlit as st # Necesitamos importar streamlit para usar el caché
import pandas as pd
import networkx as nx
from networkx.algorithms import community


@st.cache_data
def crear_red_bimodal(df, col_nodos_tipo1='Revista', col_nodos_tipo2='Colaborador'):
    """Crea una red bimodal a partir de un DataFrame."""
    B = nx.Graph()
    nodos1 = df[col_nodos_tipo1].dropna().unique()
    nodos2 = df[col_nodos_tipo2].dropna().unique()
    B.add_nodes_from(nodos1, bipartite=0)
    B.add_nodes_from(nodos2, bipartite=1)
    edges = df[[col_nodos_tipo1, col_nodos_tipo2]].dropna().to_numpy()
    B.add_edges_from(edges)
    return B

# @st.cache_data
# def calcular_metricas_red(_G, calcular_intermediacion=False):
#     """
#     Calcula métricas clave de una red. El cálculo de la intermediación es opcional y aproximado.
#     """
#     if _G.number_of_nodes() == 0:
#         return {"Nodos": 0, "Conexiones": 0, "Densidad": 0}, pd.DataFrame()

#     metricas_globales = {
#         "Nodos": _G.number_of_nodes(),
#         "Conexiones": _G.number_of_edges(),
#         "Densidad": nx.density(_G)
#     }
    
#     degree_centrality = nx.degree_centrality(_G)
    
#     # Lógica condicional que responde al checkbox
#     if calcular_intermediacion:
#         # Usamos una aproximación para que el cálculo sea rápido
#         k_nodos = min(500, _G.number_of_nodes() // 2) if _G.number_of_nodes() > 1000 else None
#         betweenness_centrality = nx.betweenness_centrality(_G, k=k_nodos, seed=123)
#     else:
#         # Por defecto, es instantáneo y asigna 0.
#         betweenness_centrality = {node: 0 for node in _G.nodes()}

#     df_metricas_nodos = pd.DataFrame({
#         'Nodo': list(_G.nodes()),
#         'Grado_Centralidad': list(degree_centrality.values()),
#         'Intermediacion': list(betweenness_centrality.values())
#     })
    
#     if nx.is_bipartite(_G):
#         tipos = {node: data.get('bipartite', -1) for node, data in _G.nodes(data=True)}
#         df_metricas_nodos['Tipo'] = df_metricas_nodos['Nodo'].map(tipos).map({0: 'Revista', 1: 'Colaborador'})
    
#     return metricas_globales, df_metricas_nodos.sort_values(by='Grado_Centralidad', ascending=False)

@st.cache_data
def calcular_metricas_red(_G, calcular_intermediacion=False):
    """
    Calcula métricas clave de una red. Esta versión asegura que la columna 'Tipo'
    siempre se cree a partir de los atributos del nodo.
    """
    if _G.number_of_nodes() == 0:
        return {"Nodos": 0, "Conexiones": 0, "Densidad": 0}, pd.DataFrame()

    metricas_globales = {
        "Nodos": _G.number_of_nodes(), "Conexiones": _G.number_of_edges(), "Densidad": nx.density(_G)
    }
    degree_centrality = nx.degree_centrality(_G)
    
    if calcular_intermediacion:
        k_nodos = min(500, _G.number_of_nodes() // 2) if _G.number_of_nodes() > 1000 else None
        betweenness_centrality = nx.betweenness_centrality(_G, k=k_nodos, seed=123)
    else:
        betweenness_centrality = {node: 0 for node in _G.nodes()}

    df_metricas_nodos = pd.DataFrame({
        'Nodo': list(_G.nodes()),
        'Grado_Centralidad': list(degree_centrality.values()),
        'Intermediacion': list(betweenness_centrality.values())
    })
    
    # --- LÓGICA CORREGIDA PARA LA COLUMNA 'Tipo' ---
    # Ya no dependemos de nx.is_bipartite. Directamente usamos el atributo que
    # asignamos al crear el grafo en 'crear_red_bimodal'.
    tipos = {node: data.get('bipartite', -1) for node, data in _G.nodes(data=True)}
    df_metricas_nodos['Tipo'] = df_metricas_nodos['Nodo'].map(tipos).map({0: 'Revista', 1: 'Colaborador', -1: 'Indefinido'})
    # --- FIN DE LA CORRECCIÓN ---
    
    return metricas_globales, df_metricas_nodos.sort_values(by='Grado_Centralidad', ascending=False)

@st.cache_data
def proyectar_red_unimodal(_B, nodos_a_proyectar):
    """Proyecta una red bimodal en una red unimodal."""
    return nx.bipartite.projected_graph(_B, nodos_a_proyectar)

@st.cache_data
def detectar_comunidades_louvain(_G_unimodal):
    """Detecta comunidades en un grafo unimodal usando el algoritmo de Louvain."""
    comunidades = community.louvain_communities(_G_unimodal, seed=123)
    mapa_comunidad = {nodo: i for i, com in enumerate(comunidades) for nodo in com}
    return mapa_comunidad