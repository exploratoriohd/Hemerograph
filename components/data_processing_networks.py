# components/data_processing_networks.py
import pandas as pd
import networkx as nx
from networkx.algorithms import community
import streamlit as st

@st.cache_data
def crear_red_bimodal(df, col_nodos_tipo1='Revista', col_nodos_tipo2='Colaborador', cache_key=None):
    """Crea una red bimodal a partir de un DataFrame."""
    B = nx.Graph()
    nodos1 = df[col_nodos_tipo1].dropna().unique()
    nodos2 = df[col_nodos_tipo2].dropna().unique()
    B.add_nodes_from(nodos1, bipartite=0)
    B.add_nodes_from(nodos2, bipartite=1)
    edges = df[[col_nodos_tipo1, col_nodos_tipo2]].dropna().to_numpy()
    B.add_edges_from(edges)
    return B

@st.cache_data
def calcular_metricas_red(_G, calcular_intermediacion=False, cache_key=None):
    """Calcula métricas clave. La intermediación es opcional y aproximada."""
    if _G.number_of_nodes() == 0:
        return {"Nodos": 0, "Conexiones": 0, "Densidad": 0}, pd.DataFrame()

    metricas_globales = {
        "Nodos": _G.number_of_nodes(),
        "Conexiones": _G.number_of_edges(),
        "Densidad": nx.density(_G)
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
    
    tipos = {node: data.get('bipartite', -1) for node, data in _G.nodes(data=True)}
    df_metricas_nodos['Tipo'] = df_metricas_nodos['Nodo'].map(tipos).map({0: 'Revista', 1: 'Colaborador', -1: 'Indefinido'})
    
    return metricas_globales, df_metricas_nodos.sort_values(by='Grado_Centralidad', ascending=False)

@st.cache_data
def proyectar_y_detectar_comunidades(_G, cache_key=None):
    """Proyecta la red y detecta comunidades."""
    nodos_colaboradores = [n for n, d in _G.nodes(data=True) if d.get('bipartite') == 1]
    if not nodos_colaboradores:
        return None
    G_proyectada = nx.bipartite.projected_graph(_G, nodos_colaboradores)
    # comunidades = community.louvain_communities(G_proyectada, seed=123)
    # comunidades = community.greedy_modularity_communities(G_proyectada)
    comunidades = community.greedy_modularity_communities(G_proyectada)
    return {nodo: i for i, com in enumerate(comunidades) for nodo in com}