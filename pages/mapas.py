# pages/4_Mapas.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Importar las funciones desde los nuevos módulos
from components.maps import (
    enriquecer_con_geo_info, 
    aplicar_clasificacion_dinamica,
    calcular_distribucion_geo_variable
)
from components.maps_viz import crear_mapa_coropletico

st.set_page_config(page_title="Hemerograph - Visualizaciones Geoespaciales", layout="wide")
st.title("🗺️ Visualizaciones geoespaciales y regionales")

# --- Carga y Verificación de Datos (Una sola vez para toda la página) ---
df_listo = st.session_state.get('df_listo_para_seleccion_cols')
selected_cols = st.session_state.get('selected_columns_for_analysis')

if df_listo is None or not selected_cols:
    st.warning("Primero debes cargar y configurar los datos en la página de '🏠 Inicio'.")
    st.stop()

df_dashboard_base = df_listo[selected_cols].copy()
COLUMNA_PAIS_ORIGINAL = 'PaisOrigen'
COLUMNA_REVISTA = 'Revista'
COLUMNA_COLABORADOR = 'Colaborador'

# Carga de Archivos de Mapeo
try:
    df_world = pd.read_csv('data/world.csv', encoding='utf-8')
    if 'ISO_A3_EH' not in df_world.columns or 'REGION_WB' not in df_world.columns or 'NAME_ES' not in df_world.columns:
        st.error("El archivo 'world.csv' debe contener 'ISO_A3_EH', 'REGION_WB' y 'NAME_ES'.")
        st.stop()
except FileNotFoundError:
    st.error("Archivo 'data/world.csv' no encontrado. Es necesario para la clasificación.")
    st.stop()

# --- Filtro Global y Estandarización (Se hace una vez para toda la página) ---
st.sidebar.header("Filtros globales para mapas")
df_filtrado_mapas = df_dashboard_base.copy()
if COLUMNA_REVISTA in df_dashboard_base.columns:
    lista_revistas_global = sorted(df_dashboard_base[COLUMNA_REVISTA].dropna().unique())
    revistas_seleccionadas_global = st.sidebar.multiselect("Filtrar todos los mapas por revista(s):", lista_revistas_global)
    if revistas_seleccionadas_global:
        df_filtrado_mapas = df_dashboard_base[df_dashboard_base[COLUMNA_REVISTA].isin(revistas_seleccionadas_global)]

# Creación del DataFrame base estandarizado para usar en todas las pestañas
df_enriquecido = pd.DataFrame()
if COLUMNA_PAIS_ORIGINAL in df_filtrado_mapas.columns:
    df_enriquecido = enriquecer_con_geo_info(
        df_datos=df_filtrado_mapas, df_world=df_world,
        col_pais_datos=COLUMNA_PAIS_ORIGINAL, col_pais_world='NAME_ES', col_iso_world='ISO_A3_EH', col_region_world='REGION_WB'
    )
else:
    st.error(f"La columna '{COLUMNA_PAIS_ORIGINAL}' no se encuentra en los datos. No se pueden generar mapas.")
    st.stop()

# ==============================================================================
# CREACIÓN DE PESTAÑAS PARA CADA TIPO DE MAPA
# ==============================================================================
if df_enriquecido.empty:
    st.warning("No hay datos geográficos para mostrar con los filtros aplicados.")
else:
    tab1, tab2, tab3 = st.tabs(["Estadísticas Generales", "Análisis Regional Dinámico", "Playground Geo-Temático"])

    # --- PESTAÑA 1: MAPA DE ESTADÍSTICAS GENERALES ---
    with tab1:
        st.header("Mapa de estadísticas generales por país")
        st.write("Visualiza la distribución geográfica de los colaboradores o de sus contribuciones totales.")
        col_a, col_b = st.columns([2, 1])
        with col_a: metrica_seleccionada_t1 = st.radio("Métrica:", ('Colaboradores Únicos', 'Colaboraciones Totales'), key="radio_mapa1", horizontal=True)
        with col_b: usar_log_t1 = st.checkbox("Usar escala logarítmica", value=True, key="check_log_mapa1")
        
        agg_func_t1 = 'nunique' if metrica_seleccionada_t1 == 'Colaboradores Únicos' else 'size'
        df_metricas_t1 = df_enriquecido.groupby(['geocode', COLUMNA_PAIS_ORIGINAL]).agg(Valor=(COLUMNA_COLABORADOR, agg_func_t1)).reset_index()
        
        fig_mapa1 = crear_mapa_coropletico(
        df_mapa=df_metricas_t1, 
        col_geocodigo='geocode', 
        col_color='Valor', 
        col_pais_hover=COLUMNA_PAIS_ORIGINAL,
        titulo=f"{metrica_seleccionada_t1} por país", 
        usar_escala_log=usar_log_t1,
        # 1. Especificar qué mostrar/ocultar en el hover
        hover_data_config={'geocode': False, 'Valor': True},
        # 2. Renombrar la etiqueta 'Valor' por una más descriptiva
        labels={'Valor': metrica_seleccionada_t1}
    )
        # fig_mapa1 = crear_mapa_coropletico(
        #     df_mapa=df_metricas_t1, col_geocodigo='geocode', col_color='Valor', col_pais_hover=COLUMNA_PAIS_ORIGINAL,
        #     titulo=f"{metrica_seleccionada_t1} por País", usar_escala_log=usar_log_t1
        # )
        if fig_mapa1: st.plotly_chart(fig_mapa1, use_container_width=True)

    # --- PESTAÑA 2: MAPA DE ANÁLISIS REGIONAL DINÁMICO ---
    with tab2:
        st.header("Análisis Regional Dinámico y Personalizado")
        st.write("Crea tus propias agrupaciones geográficas y visualiza sus métricas agregadas.")
        
        lista_paises_disponibles = sorted(df_enriquecido[COLUMNA_PAIS_ORIGINAL].dropna().unique())
        st.markdown("##### 1. Define tus grupos de análisis")
        pais_central_seleccionado = st.selectbox("A. Selecciona un país central:", [None] + lista_paises_disponibles, format_func=lambda x: 'Ninguno' if x is None else x)
        paises_aislados_seleccionados = st.multiselect("B. Aísla otros países:", [p for p in lista_paises_disponibles if p != pais_central_seleccionado])
        
        with st.expander("C. Crea subgrupos personalizados"):
            paises_disponibles_para_grupos = set(lista_paises_disponibles)
            if pais_central_seleccionado: paises_disponibles_para_grupos -= {pais_central_seleccionado}
            paises_disponibles_para_grupos -= set(paises_aislados_seleccionados)
            nombre_grupo_1 = st.text_input("Nombre del subgrupo 1:")
            paises_grupo_1 = st.multiselect("Países para el subgrupo 1:", options=sorted(list(paises_disponibles_para_grupos)), key="g1_map2")
            paises_disponibles_para_grupos -= set(paises_grupo_1)
            nombre_grupo_2 = st.text_input("Nombre del subgrupo 2:")
            paises_grupo_2 = st.multiselect("Países para el subgrupo 2:", options=sorted(list(paises_disponibles_para_grupos)), key="g2_map2")

        grupos_personalizados_finales = {}
        if nombre_grupo_1 and paises_grupo_1: grupos_personalizados_finales[nombre_grupo_1] = paises_grupo_1
        if nombre_grupo_2 and paises_grupo_2: grupos_personalizados_finales[nombre_grupo_2] = paises_grupo_2

        st.markdown("##### 2. Selecciona una métrica y visualiza")
        metrica_regional_seleccionada = st.radio("Métrica a visualizar:", ('Colaboraciones Totales', 'Colaboradores Únicos'), key="radio_mapa2", horizontal=True)
        
        df_con_regiones = aplicar_clasificacion_dinamica(df_enriquecido, COLUMNA_PAIS_ORIGINAL, pais_central_seleccionado, paises_aislados_seleccionados, grupos_personalizados_finales)
        agg_func_t2 = 'size' if metrica_regional_seleccionada == 'Colaboraciones Totales' else 'nunique'
        stats_por_region = df_con_regiones.groupby('Region').agg(Valor_Region=(COLUMNA_COLABORADOR, agg_func_t2)).reset_index()
        stats_por_pais = df_con_regiones.groupby(['geocode', COLUMNA_PAIS_ORIGINAL, 'Region']).agg(Valor_Pais=(COLUMNA_COLABORADOR, agg_func_t2)).reset_index()
        df_para_mapa2 = pd.merge(stats_por_pais, stats_por_region, on='Region', how='left')

        col_mapa, col_stats = st.columns([3, 2])
        with col_mapa:
            fig_mapa2 = crear_mapa_coropletico(df_para_mapa2, 'geocode', 'Valor_Region', 'PaisOrigen', f"{metrica_regional_seleccionada} por Región", hover_data_config={'Region': True, 'Valor_Pais': True}, usar_escala_log=True)
            if fig_mapa2:
                fig_mapa2.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Región: %{customdata[0]}<br>Valor (País): %{customdata[1]}<extra></extra>', customdata=df_para_mapa2[['Region', 'Valor_Pais']])
                st.plotly_chart(fig_mapa2, use_container_width=True)
        with col_stats:
            fig_stats = px.bar(stats_por_region, x='Valor_Region', y='Region', orientation='h', title=f"Comparativa: {metrica_regional_seleccionada}", text_auto=True)
            fig_stats.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title=None, xaxis_title=metrica_regional_seleccionada)
            st.plotly_chart(fig_stats, use_container_width=True)

    # --- PESTAÑA 3: MAPA DE EXPERIMENTACIÓN (PLAYGROUND) ---
    with tab3:
        st.header("Playground Geo-Temático")
        st.write("Explora la distribución geográfica de diferentes variables categóricas de tu dataset.")
        
        opciones_columnas = [col for col in ['Tipología', 'Sexo', 'Revista'] if col in df_enriquecido.columns]
        if opciones_columnas:
            columna_a_analizar = st.selectbox("1. Selecciona la variable a explorar:", opciones_columnas)
            lista_valores = sorted(df_enriquecido[columna_a_analizar].dropna().unique())
            valor_a_mapear = st.selectbox(f"2. Selecciona el valor de '{columna_a_analizar}':", lista_valores)
            
            if st.button("Generar Mapa del Playground"):
                df_playground = calcular_distribucion_geo_variable(df_enriquecido, columna_a_analizar, valor_a_mapear, COLUMNA_PAIS_ORIGINAL, 'geocode')
                if not df_playground.empty:
                    fig_playground = crear_mapa_coropletico(df_playground, 'geocode', 'Valor', COLUMNA_PAIS_ORIGINAL, f"Distribución de '{valor_a_mapear}' ({columna_a_analizar})", usar_escala_log=True)
                    if fig_playground: st.plotly_chart(fig_playground, use_container_width=True)
                else:
                    st.info(f"No se encontraron registros de '{valor_a_mapear}' para los filtros actuales.")


    
st.markdown("---")
st.header("Navegar a otras visualizaciones")
st.markdown("Continúa tu análisis explorando otras perspectivas de los datos.")

col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    st.page_link("pages/dashboard.py", label="**Dashboard Integrado**", icon="📊", use_container_width=True)

with col_nav2:
    st.page_link("pages/redes.py", label="**Análisis de Redes**", icon="🕸️", use_container_width=True)
