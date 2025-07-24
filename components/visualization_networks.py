# components/visualization_networks.py
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import random
import matplotlib.pyplot as plt

def visualizar_red_estatica(G, df_metricas_nodos, comunidades=None):
    """
    Crea una visualización ESTÁTICA de la red usando Matplotlib.
    Es muy rápida y sirve como vista previa.
    """
    if G.number_of_nodes() == 0:
        return None

    # Usar un layout que tiende a agrupar nodos (force-directed)
    pos = nx.spring_layout(G, seed=123, iterations=50)
    
    # Crear la figura de Matplotlib
    # plt.style.use('dark_background')
    plt.style.use('fast')

    fig, ax = plt.subplots(figsize=(16, 12))

    # Colores por comunidad o por tipo
    node_colors = []
    if comunidades:
        num_comunidades = len(set(comunidades.values()))
        lista_colores = plt.cm.get_cmap('viridis', num_comunidades)
        for node in G.nodes():
            if node in comunidades:
                node_colors.append(lista_colores(comunidades[node]))
            else: # Revistas (no tienen comunidad)
                node_colors.append("#00a0e9") # Color azul para revistas
    else:
        tipos_nodos = {row['Nodo']: row['Tipo'] for _, row in df_metricas_nodos.iterrows()}
        for node in G.nodes():
            color = "#00a0e9" if tipos_nodos.get(node) == 'Revista' else "#e94f00"
            node_colors.append(color)

    # Tamaño del nodo basado en su centralidad
    node_sizes = [df_metricas_nodos[df_metricas_nodos['Nodo'] == n]['Grado_Centralidad'].values[0] * 5000 + 50 for n in G.nodes()]

    # Dibujar la red
    nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8, ax=ax)
    # nx.draw_networkx_labels(G, pos, font_size=8, font_color='white', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', ax=ax)


    ax.set_title("Vista Previa Estática de la Red", color='white')
    plt.axis('off')
    return fig

def visualizar_red_pyvis(G, df_metricas_nodos, comunidades=None, physics_enabled=False):
    """
    Crea una visualización INTERACTIVA, con el panel de control siempre visible
    y la física desactivada por defecto para un rendimiento óptimo.
    """
    if G.number_of_nodes() == 0: return "<p>El grafo no tiene nodos para visualizar.</p>"

    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='in_line')
    
    # Esta línea activa el panel de configuración en la parte inferior del grafo
    net.show_buttons(filter_=['physics', 'layout', 'nodes', 'edges'])
    
    # Por defecto, la física está desactivada
    net.toggle_physics(physics_enabled)
    
    # El resto de la lógica para añadir nodos, colores y aristas es la misma
    colores_comunidad = {}
    if comunidades:
        num_comunidades = len(set(comunidades.values()))
        lista_colores = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(num_comunidades)]
        colores_comunidad = {i: color for i, color in enumerate(lista_colores)}

    for _, row in df_metricas_nodos.iterrows():
        node_id = str(row['Nodo'])
        tipo_nodo = row.get('Tipo', 'Indefinido')
        title = f"<b>{node_id}</b><br>Tipo: {tipo_nodo}<br>Centralidad: {row.get('Grado_Centralidad', 0):.3f}"
        if row.get('Intermediacion', 0) > 0: title += f"<br>Intermediación: {row['Intermediacion']:.3f}"
        value = row.get('Grado_Centralidad', 0) * 150
        
        if comunidades and node_id in comunidades:
            id_comunidad = comunidades[node_id]
            color = colores_comunidad.get(id_comunidad, "#808080")
            title += f"<br>Comunidad: {id_comunidad}"
        else:
            color = "#00a0e9" if tipo_nodo == 'Revista' else "#e94f00"
            
        net.add_node(node_id, label=node_id, title=title, value=value, color=color)

    for edge in G.edges():
        net.add_edge(str(edge[0]), str(edge[1]))
    
    try:
        return net.generate_html()
    except Exception as e:
        return f"<p>Error al generar el grafo HTML: {e}</p>"