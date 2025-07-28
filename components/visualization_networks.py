# # components/visualization_networks.py
# from pyvis.network import Network
# import networkx as nx
# import streamlit.components.v1 as components
# import random
# import matplotlib.pyplot as plt

# def visualizar_red_estatica(G, df_metricas_nodos, comunidades=None):
#     """
#     Crea una visualización ESTÁTICA de la red usando Matplotlib.
#     Es muy rápida y sirve como vista previa.
#     """
#     if G.number_of_nodes() == 0:
#         return None

#     # Usar un layout que tiende a agrupar nodos (force-directed)
#     pos = nx.spring_layout(G, seed=123, iterations=50)
    
#     # Crear la figura de Matplotlib
#     # plt.style.use('dark_background')
#     plt.style.use('fast')

#     fig, ax = plt.subplots(figsize=(16, 12))

#     # Colores por comunidad o por tipo
#     node_colors = []
#     if comunidades:
#         num_comunidades = len(set(comunidades.values()))
#         lista_colores = plt.cm.get_cmap('viridis', num_comunidades)
#         for node in G.nodes():
#             if node in comunidades:
#                 node_colors.append(lista_colores(comunidades[node]))
#             else: # Revistas (no tienen comunidad)
#                 node_colors.append("#00a0e9") # Color azul para revistas
#     else:
#         tipos_nodos = {row['Nodo']: row['Tipo'] for _, row in df_metricas_nodos.iterrows()}
#         for node in G.nodes():
#             color = "#00a0e9" if tipos_nodos.get(node) == 'Revista' else "#e94f00"
#             node_colors.append(color)

#     # Tamaño del nodo basado en su centralidad
#     node_sizes = [df_metricas_nodos[df_metricas_nodos['Nodo'] == n]['Grado_Centralidad'].values[0] * 5000 + 50 for n in G.nodes()]

#     # Dibujar la red
#     nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax)
#     nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8, ax=ax)
#     # nx.draw_networkx_labels(G, pos, font_size=8, font_color='white', ax=ax)
#     nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', ax=ax)


#     ax.set_title("Vista Previa Estática de la Red", color='white')
#     plt.axis('off')
#     return fig

# def visualizar_red_pyvis(G, df_metricas_nodos, comunidades=None, physics_enabled=False):
#     """
#     Crea una visualización INTERACTIVA, con el panel de control siempre visible
#     y la física desactivada por defecto para un rendimiento óptimo.
#     """
#     if G.number_of_nodes() == 0: return "<p>El grafo no tiene nodos para visualizar.</p>"

#     # net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='in_line')
#     net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='remote')
    
#     # --- Configuración por defecto: ForceAtlas2 ---
#     net.force_atlas_2based(gravity=-10, central_gravity=0.005, spring_length=100, spring_strength=0.08, damping=0.4)
    
#     # Esta línea activa el panel de configuración en la parte inferior del grafo
#     # net.show_buttons(filter_=['physics', 'layout', 'nodes', 'edges'])
#     net.show_buttons(filter_=['search_nodes', 'reset'])

#     # Por defecto, la física está desactivada
#     net.toggle_physics(physics_enabled)
    
#     # # El resto de la lógica para añadir nodos, colores y aristas es la misma
#     colores_comunidad = {}
#     if comunidades:
#         num_comunidades = len(set(comunidades.values()))
#         lista_colores = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(num_comunidades)]
#         colores_comunidad = {i: color for i, color in enumerate(lista_colores)}

#     # El grafo G que recibe ahora es de networkx y tiene los atributos que le pasamos
#     for node_id, attrs in G.nodes(data=True):
#         # node_id es el nombre con prefijo (ej. 'C_Juan Perez')
#         # attrs es un diccionario con {'label': 'Juan Perez', 'bipartite': 1}
        
#         label_display = str(attrs.get('label', node_id)) # Usar el nombre original
#         tipo_nodo_num = attrs.get('bipartite', -1)
#         tipo_nodo = 'Revista' if tipo_nodo_num == 0 else 'Colaborador'
        
#         # Obtener métricas desde el DataFrame usando el nombre original
#         metricas_nodo = df_metricas_nodos[df_metricas_nodos['Nodo'] == label_display]
#         if metricas_nodo.empty: continue
            
#         grado_cent = metricas_nodo['Grado_Centralidad'].values[0]
#         interm_cent = metricas_nodo['Intermediacion'].values[0]
        
#         title = f"<b>{label_display}</b><br>Tipo: {tipo_nodo}<br>Centralidad: {grado_cent:.3f}"
#         if interm_cent > 0: title += f"<br>Intermediación: {interm_cent:.3f}"
        
#         value = grado_cent * 150
        
#         if comunidades and label_display in comunidades:
#             id_comunidad = comunidades[label_display]
#             color = colores_comunidad.get(id_comunidad, "#808080")
#             title += f"<br>Comunidad: {id_comunidad}"
#         else:
#             color = "#00a0e9" if tipo_nodo == 'Revista' else "#e94f00"
            
#         # Usar el ID único con prefijo para el nodo, pero la etiqueta sin prefijo para mostrar
#         net.add_node(node_id, label=label_display, title=title, value=value, color=color)

#         for edge in G.edges():
#             net.add_edge(str(edge[0]), str(edge[1]))
    
#     try:
#         return net.generate_html()
#     except Exception as e:
#         return f"<p>Error al generar el grafo HTML: {e}</p>"


# components/visualization_networks.py
from pyvis.network import Network
import streamlit.components.v1 as components
import random
import matplotlib.pyplot as plt
import networkx as nx

def visualizar_red_estatica(G, df_metricas_nodos, comunidades=None):
    """Crea una visualización ESTÁTICA de la red usando Matplotlib."""
    if G.number_of_nodes() == 0:
        return None
    pos = nx.spring_layout(G, seed=123, iterations=50)
    plt.style.use('fast')
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Pre-procesar métricas para un acceso rápido
    metricas_dict = df_metricas_nodos.set_index('Nodo').to_dict('index')
    
    node_colors = []
    if comunidades:
        num_comunidades = len(set(comunidades.values()))
        lista_colores = plt.cm.get_cmap('viridis', num_comunidades)
        for node in G.nodes():
            if node in comunidades:
                node_colors.append(lista_colores(comunidades[node]))
            else:
                node_colors.append("#00a0e9")
    else:
        for node in G.nodes():
            color = "#00a0e9" if metricas_dict.get(node, {}).get('Tipo') == 'Revista' else "#e94f00"
            node_colors.append(color)

    node_sizes = [metricas_dict.get(n, {}).get('Grado_Centralidad', 0) * 5000 + 50 for n in G.nodes()]
    
    nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax, edge_color="black")
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', ax=ax)
    ax.set_title("Vista estática de la Red", color='black')
    plt.axis('off')
    return fig

def visualizar_red_pyvis(G, df_metricas_nodos, comunidades=None):
    """
    Versión final y robusta. Itera sobre los nodos del grafo para garantizar la consistencia.
    """
    if G.number_of_nodes() == 0:
        return "<p>El grafo no tiene nodos para visualizar.</p>"

    # net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='in_line')
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='remote', select_menu=True)
    
    # --- Configuración por defecto: ForceAtlas2 ---
    net.force_atlas_2based(gravity=-10, central_gravity=0.005, spring_length=100, spring_strength=0.08, damping=0.4)
    
    net.toggle_physics(False)

    net.show_buttons(filter_=['physics'])
    
    # if physics_enabled:
    #     net.force_atlas_2based()
    #     # net.force_atlas_2based(gravity=-10, central_gravity=0.005, spring_length=100, spring_strength=0.08, damping=0.4)
    # else:
    #     net.toggle_physics(False)

    colores_comunidad = {}
    if comunidades:
        num_comunidades = len(set(comunidades.values()))
        lista_colores = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(num_comunidades)]
        colores_comunidad = {i: color for i, color in enumerate(lista_colores)}

    # Crear un diccionario de métricas para una búsqueda rápida y eficiente
    metricas_dict = df_metricas_nodos.set_index('Nodo').to_dict('index')

    # --- CORRECCIÓN CLAVE: Iterar sobre G.nodes() como fuente de verdad ---
    for node_id in G.nodes():
        node_id_str = str(node_id)
        metricas_nodo = metricas_dict.get(node_id_str)
        
        # Si un nodo del grafo no tiene métricas (caso muy raro), lo saltamos
        if not metricas_nodo:
            continue

        tipo_nodo = metricas_nodo.get('Tipo', 'Indefinido')
        grado_cent = metricas_nodo.get('Grado_Centralidad', 0)
        interm_cent = metricas_nodo.get('Intermediacion', 0)

        title = f"<b>{node_id_str}</b><br>Tipo: {tipo_nodo}<br>Centralidad (Grado): {grado_cent:.3f}"
        if interm_cent > 0:
            title += f"<br>Intermediación: {interm_cent:.3f}"
        
        value = grado_cent * 150
        
        if comunidades and node_id_str in comunidades:
            id_comunidad = comunidades[node_id_str]
            color = colores_comunidad.get(id_comunidad, "#808080")
            title += f"<br>Comunidad: {id_comunidad}"
        else:
            color = "#00a0e9" if tipo_nodo == 'Revista' else "#e94f00"
            
        net.add_node(node_id_str, label=node_id_str, title=title, value=value, color=color)

    # Añadir aristas después de que todos los nodos garantizados están en su sitio
    for edge in G.edges():
        net.add_edge(str(edge[0]), str(edge[1]))
    
    try:
        return net.generate_html()
    except Exception as e:
        return f"<p>Error al generar el grafo HTML: {e}</p>"