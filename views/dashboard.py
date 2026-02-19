# pages/3_Dashboard_Integrado.py
import streamlit as st
import pandas as pd
import plotly.express as px
from components.data_processing import *
from components.visualization import (
    crear_grafico_conexiones, 
    crear_grafico_frecuencia, 
    crear_grafico_evolucion,
    crear_grafico_barras_apiladas_h
)

# --- CONSTANTES ---
ETIQUETAS_ANONIMOS = ["Anónimo", "Anonymous", "n.I.", "Redacción"]

st.set_page_config(page_title="Hemerograph - Dashboard de visualización", layout="wide")
st.title("📊 Dashboard integrado: visualización de datos de revistas culturales y literarias")

# --- Carga y Verificación de Datos ---
# Estos datos vienen del preprocesamiento en app.py
df_listo = st.session_state.get('df_listo_para_seleccion_cols')
selected_cols = st.session_state.get('selected_columns_for_analysis')
bio_data_disponible = st.session_state.get('bio_data_successfully_integrated', False)

if df_listo is None or not selected_cols:
    st.warning("Primero debes cargar, configurar y seleccionar columnas en la página de 'Inicio'.")
    st.info("Navega a la página principal para comenzar.")
    st.stop() # Detiene la ejecución de esta página si los datos base no están listos

# DataFrame base para este dashboard
df_dashboard_base = df_listo[selected_cols].copy()

st.sidebar.header("Filtros del dashboard")

# --- PREPARACIÓN DE LA COLUMNA DE FECHA ---
# Asumimos que la columna se llama "Fecha Publicación"
columna_fecha = "Fecha Publicación" 

if columna_fecha in df_dashboard_base.columns:
    # Convertir a datetime, los errores se vuelven NaT (Not a Time)
    df_dashboard_base[columna_fecha] = pd.to_datetime(df_dashboard_base[columna_fecha], errors='coerce')
    # Eliminar filas donde la fecha no pudo ser convertida (opcional, pero bueno para los filtros)
    df_dashboard_base.dropna(subset=[columna_fecha], inplace=True)
else:
    st.sidebar.warning(f"La columna '{columna_fecha}' no se encuentra en los datos seleccionados. No se podrá filtrar por fecha.")

# --- FILTROS ---
# Obtener listas únicas para los filtros (sin NaNs y ordenadas)
# Asegurarse de que las columnas de filtro existan en el df_dashboard_base

lista_revistas = []
if 'Revista' in df_dashboard_base.columns:
    lista_revistas = sorted(df_dashboard_base['Revista'].dropna().unique())

lista_colaboradores = []
if 'Colaborador' in df_dashboard_base.columns:
    lista_colaboradores = sorted(df_dashboard_base['Colaborador'].dropna().unique())


# --- Nuevo Filtro de Rango de Fechas ---
min_fecha_disponible = None
max_fecha_disponible = None
fecha_inicio_seleccionada = None
fecha_fin_seleccionada = None

if columna_fecha in df_dashboard_base.columns and not df_dashboard_base[columna_fecha].empty:
    min_fecha_disponible = df_dashboard_base[columna_fecha].min()
    max_fecha_disponible = df_dashboard_base[columna_fecha].max()

    # Asegurarse que min y max sean fechas válidas antes de pasarlas al widget
    if pd.notna(min_fecha_disponible) and pd.notna(max_fecha_disponible):
        st.sidebar.markdown("##### Filtrar por rango de fechas de publicación:")
        
        # Usamos dos st.date_input para un rango
        col1_fecha, col2_fecha = st.sidebar.columns(2)
        with col1_fecha:
            fecha_inicio_seleccionada = st.date_input(
                "Desde:",
                value=min_fecha_disponible,
                min_value=min_fecha_disponible,
                max_value=max_fecha_disponible,
                key='fecha_inicio_dashboard'
            )
        with col2_fecha:
            fecha_fin_seleccionada = st.date_input(
                "Hasta:",
                value=max_fecha_disponible,
                min_value=min_fecha_disponible, # min_value puede ser la fecha de inicio seleccionada para asegurar coherencia
                max_value=max_fecha_disponible,
                key='fecha_fin_dashboard'
            )
        
        # Validar que la fecha de inicio no sea posterior a la fecha de fin
        if fecha_inicio_seleccionada and fecha_fin_seleccionada and fecha_inicio_seleccionada > fecha_fin_seleccionada:
            st.sidebar.error("La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.")
            # Podrías resetear una de las fechas o impedir la aplicación del filtro
            # Por ahora, el filtro simplemente no se aplicará correctamente si esto ocurre.
            # O mejor, no permitir que se aplique si el rango no es válido.
            fecha_inicio_seleccionada = None # Invalida el filtro si el rango no es correcto
            fecha_fin_seleccionada = None

lista_sexo = []
if bio_data_disponible and 'Sexo' in df_dashboard_base.columns:
    lista_sexo = sorted(df_dashboard_base['Sexo'].dropna().unique())

# --- Widgets de Filtro en la Sidebar ---
selected_revistas = st.sidebar.multiselect(
    "Filtrar por revista(s):",
    options=lista_revistas,
    default=[], 
    key="filtro_revistas_dashboard"
)

selected_colaboradores = st.sidebar.multiselect(
    "Filtrar por colaborador(es):",
    options=lista_colaboradores,
    default=[],
    key="filtro_colaboradores_dashboard"
)

selected_sexo_list = [] # Renombrar para evitar conflicto con 'selected_sexo'
if bio_data_disponible and lista_sexo: # Mostrar solo si hay datos bio y la columna Sexo existe
    selected_sexo_list = st.sidebar.multiselect(
        "Filtrar por sexo:",
        options=lista_sexo,
        default=[],
        key="filtro_sexo_dashboard"
    )

# --- Aplicar Filtros al DataFrame ---
df_filtrado = df_dashboard_base.copy() # Empezar con una copia del df base

if selected_revistas and 'Revista' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Revista'].isin(selected_revistas)]
if selected_colaboradores and 'Colaborador' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Colaborador'].isin(selected_colaboradores)]
if selected_sexo_list and bio_data_disponible and 'Sexo' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Sexo'].isin(selected_sexo_list)]


# Aplicar filtro de fecha si las fechas seleccionadas son válidas
if fecha_inicio_seleccionada and fecha_fin_seleccionada and (columna_fecha in df_filtrado.columns):
    # Asegurarse de que la columna de fecha en df_filtrado sea datetime para la comparación
    # (ya debería serlo por la conversión al principio de la página)
    if pd.api.types.is_datetime64_any_dtype(df_filtrado[columna_fecha]):
        df_filtrado = df_filtrado[
            (df_filtrado[columna_fecha] >= pd.to_datetime(fecha_inicio_seleccionada)) &
            (df_filtrado[columna_fecha] <= pd.to_datetime(fecha_fin_seleccionada))
        ]
    else:
        st.warning(f"La columna '{columna_fecha}' no es de tipo fecha. No se pudo aplicar el filtro de fecha.")


st.markdown("---")
st.header("Visualizaciones")

if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles con los filtros seleccionados. Por favor, ajuste los filtros en la barra lateral.")
else:
    st.info(f"Mostrando análisis para **{len(df_filtrado)}** registros después de aplicar filtros.")
    
    # --- AQUÍ COMENZAREMOS A AÑADIR LOS GRÁFICOS PASO A PASO ---
    st.markdown("### Área de visualizaciones")

# --- PASO 1: GRÁFICO DE FRECUENCIA DE COLABORADORES APILADO POR TIPOLOGÍA TEXTUAL ---
    st.markdown("---") # Separador visual
    st.subheader("1. Colaboradores más activos y sus tipologías textuales")

    col_colaborador = "Colaborador" 
    col_tipologia = "Tipología"    # O "Tipo Publicación", según tu CORE_COLUMNS

    if col_colaborador in df_filtrado.columns and col_tipologia in df_filtrado.columns:
        
        # --- Checkbox para descartar anónimos ANTES de este gráfico específico ---
        # Usar una clave única para el checkbox para evitar conflictos
        descartar_anonimos_tipologia = st.checkbox(
            "Descartar colaboraciones anónimas para este gráfico", 
            value=True,  # Por defecto, descartar anónimos
            key="cb_anonimos_tipologia"
        )

        df_para_grafico_tipologia = df_filtrado.copy() # Trabajar con una copia para no alterar df_filtrado globalmente
        num_anonimos_descartados_tipologia = 0

        if descartar_anonimos_tipologia:
            # Usar la lista de etiquetas para identificar anónimos
            es_anonimo = df_para_grafico_tipologia[col_colaborador].isin(ETIQUETAS_ANONIMOS)
            num_anonimos_descartados_tipologia = es_anonimo.sum()
            
            # Filtrar para quitar los anónimos
            df_para_grafico_tipologia = df_para_grafico_tipologia[~es_anonimo] # ~ invierte la condición booleana

            if num_anonimos_descartados_tipologia > 0:
                st.metric(label="Colaboraciones anónimas descartadas (para este gráfico)", value=num_anonimos_descartados_tipologia)
            else:
                st.info("No se encontraron colaboraciones anónimas para descartar con la etiqueta 'Anónimo' o 'Anonymous'.")
        
        # Ahora usar df_para_grafico_tipologia para el resto de la lógica del gráfico
        if not df_para_grafico_tipologia.empty:
            try:
                # Contar publicaciones por colaborador y tipología del df ya filtrado (o no) de anónimos
                colab_tipologia_counts = df_para_grafico_tipologia.groupby([col_colaborador, col_tipologia]).size().reset_index(name='Frecuencia')

                # Calcular el total de publicaciones por colaborador para identificar a los más activos
                total_pubs_por_colab = colab_tipologia_counts.groupby(col_colaborador)['Frecuencia'].sum().sort_values(ascending=False)
                
                if not total_pubs_por_colab.empty:
                    num_colaboradores_disponibles = len(total_pubs_por_colab)
                    num_top_colabs_tipologia = 0 # Inicializar

                    if num_colaboradores_disponibles == 1:
                        # Si solo hay un colaborador, no necesitamos un slider para elegir "top N".
                        # Simplemente mostramos ese único colaborador.
                        st.info("Solo hay 1 colaborador disponible para mostrar con los filtros y opciones actuales.")
                        num_top_colabs_tipologia = 1
                    elif num_colaboradores_disponibles > 1:
                        # Si hay más de un colaborador, mostramos el slider.
                        # El valor mínimo del slider será 1.
                        # El valor máximo será el número de colaboradores disponibles (limitado a 50 por legibilidad).
                        slider_min_val = 1
                        slider_max_val = min(50, num_colaboradores_disponibles)
                        
                        # El valor por defecto puede ser 15 o el máximo disponible si es menor.
                        default_slider_val = min(15, slider_max_val)

                        num_top_colabs_tipologia = st.slider(
                            "Número de colaboradores 'Top' a mostrar en el gráfico de tipologías:",
                            min_value=slider_min_val,
                            max_value=slider_max_val, 
                            value=default_slider_val, # Asegurar que value <= max_value
                            key="slider_top_colabs_tipologia_v2", # Nueva clave por si acaso
                            help=f"Puedes seleccionar entre {slider_min_val} y {slider_max_val} colaboradores."
                        )
                    else: # num_colaboradores_disponibles es 0 (aunque if not total_pubs_por_colab.empty ya lo cubre)
                        st.info("No hay colaboradores para mostrar.")
                        # No se procede a graficar si num_top_colabs_tipologia sigue siendo 0

                    if num_top_colabs_tipologia > 0: # Solo proceder si hay algo que mostrar
                        top_colaboradores_nombres = total_pubs_por_colab.head(num_top_colabs_tipologia).index
                        df_grafico_colab_tipologia_final = colab_tipologia_counts[colab_tipologia_counts[col_colaborador].isin(top_colaboradores_nombres)]

                    if not df_grafico_colab_tipologia_final.empty:
                        # Crear el gráfico de barras apiladas
                        fig_colab_tipologia = px.bar(
                            df_grafico_colab_tipologia_final,
                            x='Frecuencia',
                            y=col_colaborador,
                            orientation='h',
                            color=col_tipologia,
                            title=f"Distribución de tipologías textuales para el top {num_top_colabs_tipologia} colaboradores",
                            labels={
                                col_colaborador: "Colaborador",
                                'Frecuencia': "Número de publicaciones",
                                col_tipologia: "Tipología textual"
                            },
                            barmode='stack'
                        )
                        
                        # Ajustar el layout para que el colaborador con más frecuencia esté arriba
                        fig_colab_tipologia.update_layout(
                            yaxis={'categoryorder': 'total ascending'}, # Ordena las barras por la frecuencia
                            xaxis_title="Número de publicaciones",
                            yaxis_title="Colaborador"
                        )
                        st.plotly_chart(fig_colab_tipologia, use_container_width=True)
                    else:
                        st.info("No hay suficientes datos para mostrar el gráfico de frecuencia de colaboradores por tipología con los filtros y selecciones actuales.")
                else:
                    st.info("No hay colaboradores para mostrar después de aplicar los filtros (y posiblemente descartar anónimos).")


            except Exception as e:
                st.error(f"Error al generar el gráfico de frecuencia por tipología: {e}")
                st.exception(e)
        else: # Si df_para_grafico_tipologia está vacío después de descartar anónimos (o si df_filtrado original lo estaba)
             st.info("No hay datos para mostrar después de aplicar los filtros (y posiblemente descartar anónimos).")
    else:
        missing_cols_tipologia = []
        if col_colaborador not in df_filtrado.columns:
            missing_cols_tipologia.append(col_colaborador)
        if col_tipologia not in df_filtrado.columns:
            missing_cols_tipologia.append(col_tipologia)
        st.warning(f"Faltan las columnas necesarias ({', '.join(missing_cols_tipologia)}) en los datos seleccionados para este gráfico.")

    # --- FIN PASO 1 ---


    # --- PASO 2: GRÁFICO DE AUTORES MEJOR CONECTADOS (NÚMERO DE REVISTAS) ---
    st.markdown("---")
    st.subheader("2. Colaboradores mejor conectados (por número de revistas distintas en las que aparecen)")

    # Nombres de las columnas en tu DataFrame principal. 
    # 'Revista' es el nombre que estandarizamos en app.py con CORE_COLUMNS y RENAMING_MAP.
    col_colaborador = "Colaborador"
    col_revista = "Revista"

    # Verificar si las columnas necesarias están disponibles
    if col_colaborador in df_filtrado.columns and col_revista in df_filtrado.columns:   
        try:
            # 1. Procesar los datos usando nuestra función externa
            datos_conexiones = calcular_conexiones_autor(df_filtrado, col_autor=col_colaborador, col_revista=col_revista)

            # 2. Reutilizar el checkbox de anónimos para filtrar los resultados
            if st.session_state.get('cb_anonimos_tipologia', True):
                datos_conexiones = datos_conexiones[~datos_conexiones[col_colaborador].isin(ETIQUETAS_ANONIMOS)]

            if not datos_conexiones.empty:
                num_autores_disponibles = len(datos_conexiones)

                # 3. Widget para seleccionar el "Top N" (con la lógica anti-error que ya implementamos)
                if num_autores_disponibles == 1:
                    st.info("Solo hay 1 autor conectado disponible para mostrar.")
                    num_top_conectados = 1
                else:
                    max_slider_val = min(50, num_autores_disponibles)
                    num_top_conectados = st.slider(
                        "Número de autores mejor conectados a mostrar:",
                        min_value=1,
                        max_value=max_slider_val,
                        value=min(15, max_slider_val),
                        key="slider_top_conectados_v2"
                    )
                
                # 4. Crear y mostrar el gráfico usando nuestra función de visualización
                fig_conexiones = crear_grafico_conexiones(datos_conexiones, top_n=num_top_conectados)
                
                if fig_conexiones:
                    st.plotly_chart(fig_conexiones, use_container_width=True)
                else:
                    st.info("No hay datos para mostrar en el gráfico de conexiones con la selección actual.")
            
            else:
                st.info("No hay datos de autores conectados para mostrar con los filtros aplicados.")

        except Exception as e:
            st.error(f"Error al generar el gráfico de autores conectados: {e}")
            st.exception(e)
    else:
        st.warning(f"Se necesitan las columnas '{col_colaborador}' y '{col_revista}' para este análisis.")

    # --- FIN PASO 2 ---

    # --- PASO 3: GRÁFICO DE TIPOLOGÍAS TEXTUALES MÁS POPULARES ---
    st.markdown("---")
    st.subheader("3. Tipologías textuales más populares")

    col_tipologia = "Tipología"

    if col_tipologia in df_filtrado.columns:
        try:
            # 1. Procesar los datos
            datos_frecuencia_tipologia = calcular_frecuencia_tipologia(df_filtrado, col_tipologia=col_tipologia)

            if not datos_frecuencia_tipologia.empty:
                num_tipologias_disponibles = len(datos_frecuencia_tipologia)
                num_top_tipologias = 0 # Inicializar

                # 2. Lógica condicional para el widget del "Top N"
                if num_tipologias_disponibles == 1:
                    st.info("Solo hay 1 tipología disponible para mostrar con los filtros actuales.")
                    num_top_tipologias = 1
                elif num_tipologias_disponibles > 1:
                    # Si hay más de una, mostrar el slider con un rango válido
                    max_slider_val = min(25, num_tipologias_disponibles)
                    default_slider_val = min(10, max_slider_val)
                    num_top_tipologias = st.slider(
                        "Número de tipologías a mostrar:",
                        min_value=1,
                        max_value=max_slider_val,
                        value=default_slider_val,
                        key="slider_top_tipologias_v3" # Actualizar clave por si acaso
                    )
                
                # 3. Crear y mostrar el gráfico solo si hay algo que mostrar
                if num_top_tipologias > 0:
                    titulo_grafico = f"Top {num_top_tipologias} Tipologías textuales más populares"
                    fig_tipologias = crear_grafico_frecuencia(
                        datos_frecuencia_tipologia, 
                        top_n=num_top_tipologias,
                        col_categoria=col_tipologia,
                        titulo=titulo_grafico
                    )
                    if fig_tipologias:
                        st.plotly_chart(fig_tipologias, use_container_width=True)
                # Si num_top_tipologias es 0, no se hace nada, lo cual es correcto.
            
            else:
                st.info("No hay datos de tipologías para mostrar con los filtros aplicados.")

        except Exception as e:
            st.error(f"Error al generar el gráfico de tipologías populares: {e}")
            st.exception(e)
    else:
        st.warning(f"Se necesita la columna '{col_tipologia}' para este análisis.")

    # --- FIN PASO 3 ---

    # --- PASO 4: GRÁFICO DE EVOLUCIÓN DE TIPOLOGÍAS POR AÑO ---
    st.markdown("---")
    st.subheader("4. Evolución de tipologías textuales a lo largo del tiempo")

    col_tipologia = "Tipología"
    col_fecha = "Fecha Publicación"

    if col_tipologia in df_filtrado.columns and col_fecha in df_filtrado.columns:      
        try:
            # 1. Procesar los datos de evolución
            datos_evolucion = calcular_evolucion_tipologia_por_ano(df_filtrado, col_fecha=col_fecha, col_tipologia=col_tipologia)

            if not datos_evolucion.empty:
                # 2. Permitir al usuario filtrar las tipologías a mostrar en el gráfico
                #    para evitar que sea demasiado denso.
                
                # Obtener la lista de todas las tipologías disponibles en los datos filtrados
                lista_tipologias_disponibles = sorted(datos_evolucion[col_tipologia].unique())
                
                # Seleccionar por defecto las 5 más frecuentes en general
                top_5_tipologias = df_filtrado[col_tipologia].value_counts().nlargest(5).index.tolist()
                
                tipologias_seleccionadas = st.multiselect(
                    "Selecciona las tipologías a visualizar en el gráfico de evolución:",
                    options=lista_tipologias_disponibles,
                    default=top_5_tipologias, # Sugerir las 5 más populares por defecto
                    key="multiselect_evolucion_tipologia"
                )

                if tipologias_seleccionadas:
                    # Filtrar los datos de evolución para mostrar solo las tipologías seleccionadas
                    df_grafico_evolucion = datos_evolucion[datos_evolucion[col_tipologia].isin(tipologias_seleccionadas)]

                    # 3. Crear y mostrar el gráfico
                    titulo_evolucion = "Evolución de tipologías textuales seleccionadas por año"
                    fig_evolucion = crear_grafico_evolucion(
                        df_grafico_evolucion,
                        col_ano='Año',
                        col_categoria=col_tipologia,
                        titulo=titulo_evolucion
                    )

                    if fig_evolucion:
                        st.plotly_chart(fig_evolucion, use_container_width=True)
                    else:
                        st.info("No hay datos para mostrar en el gráfico de evolución con las tipologías seleccionadas.")
                else:
                    st.info("Por favor, seleccione al menos una tipología para visualizar su evolución.")
            else:
                st.info("No hay datos de evolución de tipologías para mostrar con los filtros aplicados.")

        except Exception as e:
            st.error(f"Error al generar el gráfico de evolución: {e}")
            st.exception(e)
    else:
        st.warning(f"Se necesitan las columnas '{col_tipologia}' y '{col_fecha}' para este análisis.")

    # --- FIN PASO 4 ---

    # --- PASO 5 y 6: ANÁLISIS DE TRADUCCIONES ---
    st.markdown("---")
    st.subheader("5. Análisis de traducciones")

    # Columnas requeridas para estos análisis
    col_traduccion = 'Traducción'
    col_traductor = 'Traductor'
    col_tipologia_trad = 'Tipología'
    col_autor_trad = 'Colaborador'

    # Solo mostrar esta sección si las columnas existen en los datos seleccionados
    if all(col in df_filtrado.columns for col in [col_traduccion, col_traductor, col_tipologia_trad, col_autor_trad]):
        try:
            # 1. Procesar los datos (la función ahora devuelve 3 DataFrames)
            df_frec_traductores, df_frec_tipologias_trad, df_frec_autores_trad = analizar_traducciones(
                df_filtrado,
                col_traduccion=col_traduccion,
                col_traductor=col_traductor,
                col_tipologia=col_tipologia_trad,
                col_autor=col_autor_trad
            )
            
            # Layout en dos columnas para los gráficos sobre personas
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Traductores más frecuentes")
                # Checkbox para anónimos
                descartar_trad_anon = st.checkbox("Descartar traductores anónimos", value=True, key="cb_trad_anon_v2")
                
                df_traductores_filtrado = df_frec_traductores.copy()
                if descartar_trad_anon and not df_traductores_filtrado.empty:
                    filtro_anon = df_traductores_filtrado['Traductor'].isin(ETIQUETAS_ANONIMOS)
                    num_anon = df_traductores_filtrado[filtro_anon]['Frecuencia'].sum()
                    if num_anon > 0:
                        st.metric(label="Traductores anónimos descartadas:", value=int(num_anon))
                    df_traductores_filtrado = df_traductores_filtrado[~filtro_anon]

                if not df_traductores_filtrado.empty:
                    num_traductores = len(df_traductores_filtrado)
                    if num_traductores == 1:
                        st.info("Solo hay 1 traductor para mostrar.")
                        num_top_traductores = 1
                    else:
                        num_top_traductores = st.slider(
                            "Número de traductores a mostrar:", 1, min(25, num_traductores), min(10, num_traductores),
                            key="slider_top_traductores_v2"
                        )
                    fig_traductores = crear_grafico_frecuencia(df_traductores_filtrado, num_top_traductores, 'Traductor', 'Frecuencia', f"Top {num_top_traductores} Traductores")
                    if fig_traductores: st.plotly_chart(fig_traductores, use_container_width=True)
                else:
                    st.info("No hay datos de traductores para mostrar.")

            with col2:
                st.markdown("##### Autores más traducidos")
                # Checkbox para anónimos
                descartar_autor_anon = st.checkbox("Descartar autores anónimos", value=True, key="cb_autor_anon_v2")

                df_autores_filtrado = df_frec_autores_trad.copy()
                if descartar_autor_anon and not df_autores_filtrado.empty:
                    filtro_anon_autor = df_autores_filtrado['Colaborador'].isin(ETIQUETAS_ANONIMOS)
                    num_anon_autor = df_autores_filtrado[filtro_anon_autor]['Frecuencia'].sum()
                    if num_anon_autor > 0:
                        st.metric(label="Autores anónimos descartados:", value=int(num_anon_autor))
                    df_autores_filtrado = df_autores_filtrado[~filtro_anon_autor]

                if not df_autores_filtrado.empty:
                    num_autores = len(df_autores_filtrado)
                    if num_autores == 1:
                        st.info("Solo hay 1 autor traducido para mostrar.")
                        num_top_autores = 1
                    else:
                        num_top_autores = st.slider(
                            "Número de autores traducidos a mostrar:", 1, min(25, num_autores), min(10, num_autores),
                            key="slider_top_autores_trad"
                        )
                    fig_autores_trad = crear_grafico_frecuencia(df_autores_filtrado, num_top_autores, 'Colaborador', 'Frecuencia', f"Top {num_top_autores} autores más traducidos")
                    if fig_autores_trad: st.plotly_chart(fig_autores_trad, use_container_width=True)
                else:
                    st.info("No hay datos de autores traducidos para mostrar.")

            st.markdown("---") # Separador antes del último gráfico
            st.markdown("##### Tipologías más traducidas")
            if not df_frec_tipologias_trad.empty:
                num_tipologias = len(df_frec_tipologias_trad)
                if num_tipologias == 1:
                    st.info("Solo hay 1 tipología traducida para mostrar.")
                    num_top_tipos_trad = 1
                else:
                    num_top_tipos_trad = st.slider(
                        "Número de tipologías traducidas a mostrar:", 1, min(25, num_tipologias), min(10, num_tipologias),
                        key="slider_top_tipos_trad_v2"
                    )
                fig_tipos_trad = crear_grafico_frecuencia(df_frec_tipologias_trad, num_top_tipos_trad, 'Tipología', 'Frecuencia', f"Top {num_top_tipos_trad} Tipologías Traducidas")
                if fig_tipos_trad: st.plotly_chart(fig_tipos_trad, use_container_width=True)
            else:
                st.info("No hay datos de tipologías en las publicaciones marcadas como traducción.")
        
        except Exception as e:
            st.error(f"Error al generar los análisis de traducción: {e}")
            st.exception(e)
    else:
        st.info("Para ver el análisis de traducciones, asegúrate de que las columnas 'Traducción', 'Traductor', 'Tipología' y 'Colaborador' estén seleccionadas en la página de Inicio y presentes en los datos.")

        # --- FIN PASO 5 y 6 ---

    st.markdown("---")
    st.subheader("Análisis de traducciones por revista")

    col_revista_trad = 'Revista'
    col_traduccion_trad = 'Traducción'
    col_tipologia_trad = 'Tipología'

    if all(col in df_filtrado.columns for col in [col_revista_trad, col_traduccion_trad, col_tipologia_trad]):
        try:
            df_traducciones_revista = calcular_traducciones_por_revista(
                df_filtrado, 
                col_revista=col_revista_trad, 
                col_traduccion=col_traduccion_trad,
                col_tipologia=col_tipologia_trad
            )
            
            if not df_traducciones_revista.empty:
                # 1. Obtener la lista de revistas únicas, ya ordenadas por la función de procesamiento
                revistas_disponibles = df_traducciones_revista['Revista'].unique()
                num_revistas_disponibles = len(revistas_disponibles)
                
                num_top_revistas = 0 # Inicializar
                
                # 2. Lógica para mostrar el slider solo si hay más de una revista
                if num_revistas_disponibles > 1:
                    slider_max_val = min(50, num_revistas_disponibles)
                    default_slider_val = min(10, slider_max_val)
                    num_top_revistas = st.slider(
                        "Número de revistas a mostrar:", 1, slider_max_val, default_slider_val,
                        key="slider_top_revistas_traducciones_stacked"
                    )
                elif num_revistas_disponibles == 1:
                    # Si solo hay una revista, la mostramos sin slider
                    num_top_revistas = 1

                # 3. Filtrar el DataFrame para mostrar solo las N revistas seleccionadas
                if num_top_revistas > 0:
                    # Seleccionar los nombres de las N revistas top
                    revistas_top_n = revistas_disponibles[:num_top_revistas]
                    # Filtrar el DataFrame original para incluir solo esas revistas
                    df_para_grafico = df_traducciones_revista[df_traducciones_revista['Revista'].isin(revistas_top_n)]

                # 4. Crear y mostrar el gráfico
                fig_traducciones_revista = crear_grafico_barras_apiladas_h(
                    df_para_grafico,
                    col_x='Total_Traducciones',
                    col_y='Revista',
                    col_color='Tipología',
                    titulo='Total de Traducciones por Revista y Tipología',
                    label_x='Número de Traducciones',
                    label_y='Revista'
                )
                if fig_traducciones_revista:
                    st.plotly_chart(fig_traducciones_revista, use_container_width=True)

            else:
                st.info("No se encontraron publicaciones marcadas como 'Traducción' con los filtros actuales.")

        except Exception as e:
            st.error(f"Ocurrió un error al generar el gráfico de traducciones por revista: {e}")
    else:
        st.warning(f"Para este análisis se requieren las columnas '{col_revista_trad}' y '{col_traduccion_trad}'.")


# --- GRÁFICO DE EVOLUCIÓN DE TRADUCCIONES POR TIPOLOGÍA ---
st.markdown("---")
st.subheader("Evolución de traducciones por tipología a lo largo del tiempo")

col_tipologia_trad_evo = "Tipología"
col_fecha_trad_evo = "Fecha Publicación"
col_traduccion_trad_evo = "Traducción"

if all(col in df_filtrado.columns for col in [col_tipologia_trad_evo, col_fecha_trad_evo, col_traduccion_trad_evo]):      
    try:
        # 1. Procesar los datos con la nueva función
        datos_evolucion_trad = calcular_evolucion_traducciones_por_tipologia(
            df_filtrado, 
            col_fecha=col_fecha_trad_evo, 
            col_tipologia=col_tipologia_trad_evo,
            col_traduccion=col_traduccion_trad_evo
        )

        if not datos_evolucion_trad.empty:
            # 2. Permitir al usuario filtrar las tipologías a mostrar
            lista_tipologias_trad_disponibles = sorted(datos_evolucion_trad[col_tipologia_trad_evo].unique())
            
            # Seleccionar por defecto las 5 más frecuentes
            top_5_tipologias_trad = datos_evolucion_trad.groupby(col_tipologia_trad_evo)['Frecuencia'].sum().nlargest(5).index.tolist()
            
            tipologias_seleccionadas_trad = st.multiselect(
                "Selecciona las tipologías a visualizar en el gráfico de evolución de traducciones:",
                options=lista_tipologias_trad_disponibles,
                default=top_5_tipologias_trad,
                key="multiselect_evolucion_traducciones"
            )

            if tipologias_seleccionadas_trad:
                df_grafico_evolucion_trad = datos_evolucion_trad[datos_evolucion_trad[col_tipologia_trad_evo].isin(tipologias_seleccionadas_trad)]

                # 3. Reutilizar la función de visualización existente
                titulo_evolucion_trad = "Evolución de tipologías en traducciones por año"
                fig_evolucion_trad = crear_grafico_evolucion(
                    df_grafico_evolucion_trad,
                    col_ano='Año',
                    col_categoria=col_tipologia_trad_evo,
                    titulo=titulo_evolucion_trad
                )

                if fig_evolucion_trad:
                    st.plotly_chart(fig_evolucion_trad, use_container_width=True)
            else:
                st.info("Por favor, selecciona al menos una tipología para visualizar su evolución en las traducciones.")
        else:
            st.info("No hay datos de evolución de traducciones para mostrar con los filtros aplicados.")

    except Exception as e:
        st.error(f"Error al generar el gráfico de evolución de traducciones: {e}")
else:
    st.warning(f"Se necesitan las columnas '{col_tipologia_trad_evo}', '{col_fecha_trad_evo}' y '{col_traduccion_trad_evo}' para este análisis.")

# --- FIN DEL NUEVO GRÁFICO ---


# --- NUEVO GRÁFICO: IDIOMAS MÁS TRADUCIDOS POR TIPOLOGÍA ---
st.markdown("---")
st.subheader("Idiomas originales más traducidos por tipología textual")

col_idioma_orig = 'Idioma Original'
col_tipologia = 'Tipología'
col_traduccion = 'Traducción'

if all(c in df_filtrado.columns for c in [col_idioma_orig, col_tipologia, col_traduccion]):
    try:
        df_idioma_tipologia = calcular_traducciones_idioma_por_tipologia(
            df_filtrado,
            col_idioma=col_idioma_orig,
            col_tipologia=col_tipologia,
            col_traduccion=col_traduccion
        )

        if not df_idioma_tipologia.empty:
            idiomas_disponibles = df_idioma_tipologia[col_idioma_orig].unique()
            num_idiomas_disponibles = len(idiomas_disponibles)
            num_top_idiomas = 0
            
            if num_idiomas_disponibles > 1:
                num_top_idiomas = st.slider("Número de idiomas a mostrar:", 1, min(25, num_idiomas_disponibles), min(10, num_idiomas_disponibles), key="slider_idiomas_tipologia")
            elif num_idiomas_disponibles == 1:
                num_top_idiomas = 1

            if num_top_idiomas > 0:
                idiomas_top_n = idiomas_disponibles[:num_top_idiomas]
                df_grafico_idioma = df_idioma_tipologia[df_idioma_tipologia[col_idioma_orig].isin(idiomas_top_n)]
                
                fig_idioma_tipologia = crear_grafico_barras_apiladas_h(
                    df_grafico_idioma,
                    col_x='Frecuencia',
                    col_y='Idioma Original',
                    col_color='Tipología',
                    titulo='Distribución de tipologías por idioma original traducido',
                    label_x='Número de traducciones',
                    label_y='Idioma original'
                )
                if fig_idioma_tipologia: st.plotly_chart(fig_idioma_tipologia, use_container_width=True)
        else:
            st.info("No hay datos de idiomas en las publicaciones marcadas como traducción.")
    except Exception as e:
        st.error(f"Error al generar el gráfico de idiomas por tipología: {e}")
else:
    st.info(f"Para este análisis se requieren las columnas '{col_idioma_orig}', '{col_tipologia}' y '{col_traduccion}'.")

st.markdown("---")
st.header("Navegar a otras visualizaciones")
st.markdown("Continúa tu análisis explorando otras perspectivas de los datos.")

col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    st.page_link("views/mapas.py", label="**Análisis Geográfico y Mapas**", icon="🗺️", use_container_width=True)

with col_nav2:
    st.page_link("views/redes.py", label="**Análisis de Redes**", icon="🕸️", use_container_width=True)
