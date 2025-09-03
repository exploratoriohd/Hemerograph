import streamlit as st
import pandas as pd
from components.data_loader import list_available_datasets, load_selected_datasets
from components.data_type import corregir_tipos_de_datos
from components.data_processing import calcular_frecuencia_colaboradores, preparar_csv_para_descarga
from components.data_processing_bio import cargar_datos_biograficos, crear_dataset_unico, identificar_colaboradores

# --- DEFINICIONES PARA CONSISTENCIA DE ESQUEMAS ---
CORE_COLUMNS = [
    "Colaborador", "Título", "Revista",
    "Fecha Publicación", "Fascículo",
    "Tipología", "Idioma", "Idioma Original", "Traducción", "Traductor"
]

RENAMING_MAP = {
    # Colaborador
    "Autor": "Colaborador", "Author": "Colaborador", "Nombre del Autor": "Colaborador", "AUTOR": "Colaborador", "Contributor": "Colaborador",
    # Título Artículo
    "Título": "Título", "Title": "Título", "Artículo": "Título", "TITULO": "Título", "Titulo": "Título", "Title": "Título", 
    # Nombre Revista
    "Magazine": "Revista", "Journal": "Revista", "NombreR": "Revista", "Revista": "Revista",
    # Año Publicación (si la columna original es solo el año)
    "Año": "Fecha Publicación", "Year": "Fecha Publicación", "ANIO": "Fecha Publicación", "Fecha-ISO": "Fecha Publicación", "Calculable_Issue_Date": "Fecha Publicación", "Fecha.ISO": "Fecha Publicación",
    # Si tienes "Fecha Publicación" y necesitas extraer el año, eso se haría después de renombrar.
    # "Fecha Publicación": "Fecha Publicación", # Mantener para posible extracción de año luego
    # Número 
    "Fasciculo":"Fascículo", "Issue": "Fascículo", "NumFasciculo": "Fascículo",
    # Tipo Publicación
    "Tipología": "Tipo Publicación", "Género Textual": "Tipo Publicación", "Categoría": "Tipo Publicación", "Tipo": "Tipología", "Type": "Tipología",
    # Sección Original
    # "Sección": "Sección Original", "Seccion": "Sección Original", "Nombre de Sección": "Sección Original",
    "Lengua": "Idioma", "Language": "Idioma",
    "Lengua Original": "Idioma Original", "Original Language": "Idioma Original", "LenguaOriginal": "Idioma Original",
    "Traduccion": "Traducción",
    "Translator": "Traductor", "Traductor": "Traductor"

}
# --- FIN DE DEFINICIONES DE ESQUEMAS ---

st.set_page_config(page_title="Hemerograph - Configuración", layout="wide")
st.title("📚 Dashboard de revistas culturales y literarias")
st.header("🏠 Configuración de datos para el análisis")

# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
default_session_states = {
    'combined_data_df_initial': None,
    'selected_columns_for_analysis': [],
    'previous_column_schema': [], # <-- Rastrear cambios en columnas
    'data_sources_names': [],
    'initial_load_and_align_complete': False,
    'integrate_bio_checkbox_state': False, # Para controlar el checkbox explícitamente
    'bio_data_processing_done': False, # Para saber si el bloque de bio se ejecutó
    'bio_data_successfully_integrated': False,
    'datos_biograficos_raw_df': None,
    'df_listo_para_seleccion_cols': None,
}

for key, default_value in default_session_states.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
# --- FIN DE LA INICIALIZACIÓN ---

# --- PASO 1: Carga Inicial y Alineación de Esquemas (Barra Lateral) ---
with st.sidebar:
    st.header("Paso 1: Carga inicial de datasets")
    uploaded_files_list = st.file_uploader("Sube tus archivos CSV:", type="csv", accept_multiple_files=True, key="file_uploader_main")
    DATA_PATH_EXAMPLES = "data/models/"
    try:
        example_files_available = list_available_datasets(path=DATA_PATH_EXAMPLES)
    except Exception:
        example_files_available = []
    selected_example_names = st.multiselect("O selecciona datasets de ejemplo:", options=example_files_available, key="example_multiselect_main")
    keep_unmapped_columns = st.checkbox("¿Conservar columnas no mapeadas/no esenciales?", value=True, key="keep_unmapped_main_cb") # Renombrada clave

    if st.button("1. Cargar y alinear datasets seleccionados", key="load_align_button_main"):
        all_dataframes_to_process = []
        current_data_sources_names_list = []

        if uploaded_files_list:
            for uploaded_file_obj in uploaded_files_list:
                try:
                    df = pd.read_csv(uploaded_file_obj)
                    all_dataframes_to_process.append(df)
                    current_data_sources_names_list.append(f"Subido: {uploaded_file_obj.name}")
                except Exception as e:
                    st.error(f"Error al leer '{uploaded_file_obj.name}': {e}")
        
        if selected_example_names:
            try:
                loaded_examples_dict = load_selected_datasets(selected_example_names, path=DATA_PATH_EXAMPLES)
                for name, df_example in loaded_examples_dict.items():
                    all_dataframes_to_process.append(df_example)
                    current_data_sources_names_list.append(f"Ejemplo: {name}.csv")
            except Exception as e:
                st.error(f"Error al cargar datasets de ejemplo: {e}")

        if all_dataframes_to_process:
            aligned_dfs_list = []
            st.write("--- Alineando esquemas... ---") # Feedback en la sidebar
            for i, df_original in enumerate(all_dataframes_to_process):
                source_name = current_data_sources_names_list[i]
                st.caption(f"Procesando: {source_name}")
                df_aligned = pd.DataFrame()
                original_cols_data = {col_name: df_original[col_name] for col_name in df_original.columns}
                used_original_cols_for_core = set()

                for core_col in CORE_COLUMNS:
                    mapped_found = False
                    for original_col_name_map, target_core_name_map in RENAMING_MAP.items():
                        if target_core_name_map == core_col and original_col_name_map in original_cols_data:
                            if original_col_name_map not in used_original_cols_for_core:
                                df_aligned[core_col] = original_cols_data[original_col_name_map]
                                used_original_cols_for_core.add(original_col_name_map)
                                mapped_found = True
                                break
                    if not mapped_found and core_col in original_cols_data:
                        if core_col not in used_original_cols_for_core:
                            df_aligned[core_col] = original_cols_data[core_col]
                            used_original_cols_for_core.add(core_col)
                            mapped_found = True
                    if not mapped_found:
                        df_aligned[core_col] = pd.NA
                
                if keep_unmapped_columns:
                    for original_col_name_extra, data_series_extra in original_cols_data.items():
                        if original_col_name_extra not in used_original_cols_for_core:
                            final_extra_col_name = RENAMING_MAP.get(original_col_name_extra, original_col_name_extra)
                            if final_extra_col_name not in df_aligned.columns:
                                df_aligned[final_extra_col_name] = data_series_extra
                            elif final_extra_col_name == original_col_name_extra and original_col_name_extra not in df_aligned.columns:
                                df_aligned[original_col_name_extra] = data_series_extra
                aligned_dfs_list.append(df_aligned)
            
            if aligned_dfs_list:
                st.session_state.combined_data_df_initial = pd.concat(aligned_dfs_list, ignore_index=True, join='outer')
                st.session_state.combined_data_df_initial = corregir_tipos_de_datos(st.session_state.combined_data_df_initial)

                st.session_state.data_sources_names = current_data_sources_names_list
                st.session_state.initial_load_and_align_complete = True
                st.session_state.df_listo_para_seleccion_cols = st.session_state.combined_data_df_initial.copy()
                st.session_state.selected_columns_for_analysis = st.session_state.df_listo_para_seleccion_cols.columns.tolist()
                # Resetear flags de bio
                st.session_state.integrate_bio_checkbox_state = False 
                st.session_state.bio_data_processing_done = False
                st.session_state.bio_data_successfully_integrated = False
                st.success(f"{len(st.session_state.data_sources_names)} dataset(s) cargados y alineados.")
                st.rerun()
            else:
                st.warning("No se pudieron alinear los datasets.")
        else:
            st.warning("No se seleccionaron o cargaron datasets válidos.")

        cache_key = "_".join(sorted([f"{file.name}_{file.size}" for file in uploaded_files_list])) if uploaded_files_list else ""
        cache_key += "_".join(sorted(selected_example_names)) #  Incorporar también los ejemplos
        st.session_state['data_cache_key'] = cache_key

# --- CUERPO PRINCIPAL DE LA APLICACIÓN ---
if not st.session_state.get('initial_load_and_align_complete', False):
    st.info("👋 ¡Bienvenido! Comienza por cargar tus datasets en la barra lateral (Paso 1).")
else: # Paso 1 completado, mostrar Paso 2 y 3
    st.markdown("---")
    st.header("Paso 1 Completado: Dataset inicial cargado y alineado")
    st.info(f"Fuentes: {', '.join(st.session_state.data_sources_names)}")
    st.write("Vista previa del dataset combinado inicial (primeras filas):")
    st.dataframe(st.session_state.combined_data_df_initial.head())

    st.markdown("---")
    st.header("Paso 2: Integración opcional de datos biográficos")
    
    # Usamos session_state para el checkbox para que su estado persista correctamente
    st.session_state.integrate_bio_checkbox_state = st.checkbox(
        "¿Intentar cargar e integrar datos biográficos?",
        value=st.session_state.integrate_bio_checkbox_state, # Usar el valor de session_state
        key="integrate_bio_cb_main" # Renombrada clave
    )

    # Lógica de integración bio solo se ejecuta si el checkbox está marcado
    # y si el estado base (df_initial) no ha cambiado de forma que requiera re-evaluación.
    if st.session_state.integrate_bio_checkbox_state:
        st.markdown("Intentando integrar datos biográficos...") # Feedback
        df_initial_for_bio = st.session_state.combined_data_df_initial.copy()

        if 'Colaborador' not in df_initial_for_bio.columns:
            st.error("La columna 'Colaborador' es necesaria para la fusión biográfica, pero no se encontró.")
            st.session_state.bio_data_successfully_integrated = False
            st.session_state.df_listo_para_seleccion_cols = df_initial_for_bio # Fallback
        else:
            with st.spinner("Cargando y fusionando datos biográficos..."):
                try:
                    bio_df_raw = cargar_datos_biograficos()
                    st.session_state.datos_biograficos_raw_df = bio_df_raw
                    
                    df_merged_con_bio = crear_dataset_unico(df_initial_for_bio, bio_df_raw)
                    # st.session_state.df_listo_para_seleccion_cols = df_merged_con_bio.copy()
                    st.session_state.df_listo_para_seleccion_cols = corregir_tipos_de_datos(df_merged_con_bio).copy()
                    st.session_state.bio_data_successfully_integrated = True
                    st.success("Datos biográficos fusionados con éxito.")
                    # st.dataframe(df_merged_con_bio)

                    global_colab_freq_df = calcular_frecuencia_colaboradores(df_initial_for_bio)
                    colabs_encontrados_df, colabs_no_encontrados_df = identificar_colaboradores(global_colab_freq_df, bio_df_raw)
                  

                    # --- Procesamiento y visualización de COLABORADORES ENCONTRADOS ---
                    st.subheader(f"Colaboradores identificados en con datos biográficos")

                    st.dataframe(colabs_encontrados_df)
                    st.metric("Total identificados:", len(colabs_encontrados_df))
                    
                    # --- Procesamiento y visualización de COLABORADORES NO ENCONTRADOS (VERSIÓN FINAL) ---
                    st.subheader(f"Colaboradores NO identificados con datos biográficos")

                    st.dataframe(colabs_no_encontrados_df)
                    st.metric("Total no identificados", len(colabs_no_encontrados_df))

                except Exception as e:
                    st.error(f"Error durante la integración biográfica: {e}")                
                    st.session_state.bio_data_successfully_integrated = False
                    st.session_state.df_listo_para_seleccion_cols = st.session_state.combined_data_df_initial.copy()
                    raise
        st.session_state.bio_data_processing_done = True # Marcar que este bloque se ejecutó

    else: # Checkbox de bio no está marcado
        # Si se desmarcó o nunca se marcó, usar el DF inicial
        st.session_state.df_listo_para_seleccion_cols = st.session_state.combined_data_df_initial.copy()
        if st.session_state.bio_data_processing_done and st.session_state.bio_data_successfully_integrated:
             st.info("Integración de datos biográficos desactivada. Trabajando con el dataset inicial.")
        st.session_state.bio_data_successfully_integrated = False
        st.session_state.bio_data_processing_done = True # Se considera que la decisión (no integrar) está procesada


    # --- PASO 3: Selección Final de Columnas para Análisis ---
    if st.session_state.df_listo_para_seleccion_cols is not None:
        st.markdown("---")
        st.header("Paso 3: Selección final de Columnas para el análisis")
        
        current_df_for_selection = st.session_state.df_listo_para_seleccion_cols
        all_cols = current_df_for_selection.columns.tolist()

        # Si las opciones del multiselect (all_cols) han cambiado, o si la selección actual es inválida
        # o si es la primera vez que se muestra después de un cambio de DF, resetear el default.
        previous_selected_cols_valid = all(col in all_cols for col in st.session_state.selected_columns_for_analysis)

        # if not st.session_state.selected_columns_for_analysis or not previous_selected_cols_valid:
        #     st.session_state.selected_columns_for_analysis = all_cols # Default a todas las columnas del DF actual

        if set(all_cols) != set(st.session_state.previous_column_schema):
            # Si cambió (ej. se añadieron datos bio), reseteamos la selección al total de columnas
            st.session_state.selected_columns_for_analysis = all_cols
            st.session_state.previous_column_schema = all_cols
            
        selected_cols_widget = st.multiselect(
            "Selecciona las columnas finales que se usarán en las páginas de análisis:",
            options=all_cols,
            default=st.session_state.selected_columns_for_analysis,
            key="final_column_selector_main_app"
        )

        if selected_cols_widget != st.session_state.selected_columns_for_analysis:
            st.session_state.selected_columns_for_analysis = selected_cols_widget
            st.rerun() 

        if st.session_state.selected_columns_for_analysis:
            st.success("🎉 ¡Configuración de datos completada! Ya puedes navegar a las páginas de análisis y visualización desde la barra lateral.")
            st.caption("Vista previa del dataset final que se usará en los análisis (primeras filas):")
            st.dataframe(current_df_for_selection[st.session_state.selected_columns_for_analysis].head())

             # DataFrame final para análisis y descarga
            df_final_trabajo = current_df_for_selection[st.session_state.selected_columns_for_analysis]
            
            # st.caption("Vista previa del dataset final que se usará en los análisis (primeras filas):")
            # st.dataframe(df_final_trabajo.head())

            st.session_state['final_df_to_analyze'] = df_final_trabajo

            # --- BOTÓN DE DESCARGA ---
            st.markdown("---") # Separador
            st.subheader("📥 Descargar dataset procesado")

            csv_data = preparar_csv_para_descarga(df_final_trabajo)

            if csv_data:
                st.download_button(
                    label="Descargar dataset como CSV",
                    data=csv_data,
                    file_name="dataset_procesado_hemerograph.csv", # Nombre del archivo sugerido
                    mime="text/csv",
                    key="download_csv_main_app"
                )
            else:
                st.warning("No hay datos seleccionados para descargar.")
            # --- FIN DEL BOTÓN DE DESCARGA ---
        
        else:
            st.warning("Debes seleccionar al menos una columna para continuar a las páginas de análisis.")
    else:
        # Este caso no debería ocurrir si initial_load_and_align_complete es True
        st.warning("El dataset base para la selección de columnas no está listo. Completa el Paso 1.")



st.markdown("---")
st.header("Navegar a hacia las visualizaciones")
st.markdown("Continúa tu análisis explorando los datos.")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    st.page_link("pages/dashboard.py", label="**Dashboard Integrado**", icon="📊", use_container_width=True)

with col_nav2:
    st.page_link("pages/mapas.py", label="**Análisis Geográfico y Mapas**", icon="🗺️", use_container_width=True)

with col_nav3:
    st.page_link("pages/redes.py", label="**Análisis de Redes**", icon="🕸️", use_container_width=True)

