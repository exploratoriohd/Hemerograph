from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import random

def visualizar_red_pyvis(G, df_metricas_nodos, comunidades=None, physics_enabled=True):
    """
    Crea una visualización interactiva de una red usando Pyvis.
    Ahora puede colorear los nodos según las comunidades detectadas.
    """
    if G.number_of_nodes() == 0:
        return "<p>El grafo no tiene nodos para visualizar.</p>"

    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=True, cdn_resources='in_line')
    
    # Generar colores para las comunidades si se proporcionan
    colores_comunidad = {}
    if comunidades:
        num_comunidades = len(set(comunidades.values()))
        # Generar una lista de colores aleatorios y vistosos
        lista_colores = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(num_comunidades)]
        for i in range(num_comunidades):
            colores_comunidad[i] = lista_colores[i]

    for index, row in df_metricas_nodos.iterrows():
        node_id = str(row['Nodo'])
        
        # --- LÓGICA CORREGIDA PARA EL TÍTULO Y COLOR ---
        tipo_nodo = row.get('Tipo', 'Indefinido') # Usar .get() para un acceso seguro
        
        title = f"<b>{node_id}</b><br>Tipo: {tipo_nodo}"
        # Añadir otras métricas al título del hover
        if 'Grado_Centralidad' in row:
            title += f"<br>Centralidad: {row['Grado_Centralidad']:.3f}"
        if 'Intermediacion' in row and row['Intermediacion'] > 0:
            title += f"<br>Intermediación: {row['Intermediacion']:.3f}"
        
        value = row.get('Grado_Centralidad', 0) * 150
        
        # Asignar color por comunidad o, si no, por tipo de nodo
        if comunidades and node_id in comunidades:
            id_comunidad = comunidades[node_id]
            # ... (código de color de comunidad sin cambios) ...
            title += f"<br>Comunidad: {id_comunidad}"
        else:
            # Color por defecto basado en el tipo de nodo
            color = "#00a0e9" if tipo_nodo == 'Revista' else "#e94f00" 
        # --- FIN DE LA CORRECCIÓN ---
        
    # for index, row in df_metricas_nodos.iterrows():
    #     node_id = str(row['Nodo'])
    #     title = f"<b>{node_id}</b><br>Tipo: {row['Tipo']}"
    #     value = row['Grado_Centralidad'] * 150
        
    #     # Asignar color: por comunidad si existe, si no, por tipo de nodo
    #     if comunidades and node_id in comunidades:
    #         id_comunidad = comunidades[node_id]
    #         color = colores_comunidad.get(id_comunidad, "#808080") # Gris si hay algún error
    #         title += f"<br>Comunidad: {id_comunidad}"
    #     else: # Comportamiento original si no hay análisis de comunidad
    #         color = "#00a0e9" if row['Tipo'] == 'Revista' else "#e94f00"
            
        net.add_node(node_id, label=node_id, title=title, value=value, color=color)

    for edge in G.edges():
        net.add_edge(str(edge[0]), str(edge[1]))

    net.show_buttons(filter_=['physics'])
    
    # --- Lógica de Física Optimizada ---
    if physics_enabled:
        # Muestra los botones para que el usuario pueda jugar con la física
        net.show_buttons(filter_=['physics'])
    else:
        # Desactiva la física para una carga instantánea
        net.toggle_physics(False)

    try:
        html_source = net.generate_html()
        return html_source
    except Exception as e:
        return f"<p>Error al generar el grafo HTML: {e}</p>"