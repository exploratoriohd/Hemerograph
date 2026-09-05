# Hoja de ruta — Hemerograph

_Generado a partir de una revisión del estado del código y el historial de Git el 2026-09-05, en la rama `filtros`._

## 1. Resumen del estado actual

**Qué es:** una app Streamlit multipágina (`app.py` → `views/inicio.py`, `dashboard.py`, `mapas.py`, `redes.py`) para analizar corpus de revistas culturales/literarias: carga de CSVs, normalización de esquema, cruce con datos biográficos, dashboards de frecuencia/evolución/traducción, mapas coropléticos y análisis de redes de colaboración (igraph + Leiden + pyvis).

**Lo implementado:**
- **Inicio** (`views/inicio.py`): carga múltiple de CSV (subidos o de ejemplo en `data/models/`), mapeo de columnas heterogéneas a un esquema `CORE_COLUMNS` vía `RENAMING_MAP`, integración opcional de datos biográficos, selección final de columnas y descarga del dataset procesado. Todo el estado vive en `st.session_state`.
- **Dashboard** (`views/dashboard.py`, ~812 líneas, en edición activa en la rama `filtros`): filtros por revista/colaborador/sexo/fecha, y ~9 bloques de visualización (tipologías, colaboradores conectados, evolución temporal, traducciones por revista/idioma/tipología).
- **Mapas** (`views/mapas.py`): 3 pestañas — estadísticas por país, agrupaciones regionales dinámicas definidas por el usuario, y un "playground" geo-temático.
- **Redes** (`views/redes.py`): construcción de grafo bimodal con igraph, detección de comunidades (Leiden/Louvain/walktrap/fastgreedy), métricas globales/por nodo, visualización estática (matplotlib) e interactiva (pyvis).
- Cacheo con `@st.cache_data` en las funciones pesadas de redes.

**Cambios en curso (rama `filtros`, sin commitear al momento de esta revisión):** opción de resaltar un colaborador específico en el gráfico de "mejor conectados" (`highlight_item` en `crear_grafico_conexiones`), con bloques de código viejo comentados en lugar de eliminados.

## 2. Deuda técnica, bugs y huecos de pruebas

**Bugs / riesgos concretos:**
1. **`requirements.txt` estaba en UTF-16** (con BOM `FF FE`, probablemente generado con `pip freeze > requirements.txt` en PowerShell). `pip install -r requirements.txt` falla en Linux/Mac/CI/Streamlit Cloud tal como estaba.
2. **`views/dashboard.py` (bloque "Paso 1")** — `df_grafico_colab_tipologia_final` solo se define dentro de la rama `if num_top_colabs_tipologia > 0:`, pero se lee justo después. Si `num_top_colabs_tipologia` queda en 0, la variable no existe y lanza `NameError` (enmascarado por el `try/except Exception` general del bloque).
3. **`try/except Exception` + `st.exception(e)`** repetido en cada bloque del dashboard: oculta bugs de programación tratándolos igual que "no hay datos", y hace el debugging más lento.
4. `views/mapas.py` usa `hovertext` en customdata de Plotly sin definirlo explícitamente en `crear_mapa_coropletico` — riesgo menor de mostrar valores vacíos en el hover.

**Deuda técnica estructural:**
- **Sin pruebas automatizadas** de ningún tipo (no hay `tests/`, no hay `pytest` en `requirements.txt`; el único archivo de test histórico, `test_data_bio.py`, fue borrado en el commit "Add dataset"). Toda la capa `components/data_processing*.py` (~1300 líneas combinadas) no tiene cobertura.
- **Sin CI/CD** (no hay `.github/workflows` ni linting configurado).
- **Código muerto comentado en vez de eliminado**: patrón recurrente en `visualization.py`, `dashboard.py` y `redes.py`. Dificulta la lectura y aumenta el tamaño de archivos ya grandes.
- **`views/dashboard.py` con 800+ líneas** en un solo archivo, con lógica de UI, filtrado y llamado a gráficos entremezclada — candidato claro a dividirse en funciones/módulos por sección.
- **Estado compartido vía `st.session_state` sin contrato documentado**: cada vista lee claves como `df_listo_para_seleccion_cols`, `final_df_to_analyze`, `bio_data_successfully_integrated` sin una capa central que documente qué debe existir; genera acoplamiento implícito entre páginas.
- **`RENAMING_MAP`** (en `views/inicio.py`) tiene una entrada duplicada (`"Title": "Título"`) — indica que el diccionario crece de forma ad-hoc sin revisión.
- **Datasets de ejemplo pesados versionados en Git** (`data/models/*.csv`, uno de ~31k líneas) — infla el repo; sin Git LFS ni carga diferida.
- **Manejo de archivos subidos sin límites de tamaño ni validación de esquema mínimo** antes de intentar procesarlos.
- Vestigios de la migración `pages/` → `views/` (commit `eab21a9 FIX`): comentarios como `# pages/redes.py`, `# pages/4_Mapas.py` siguen encabezando los archivos actuales.

## 3. Hoja de ruta priorizada

### Fase 1 — Inmediato
1. **Corregir `requirements.txt`**: regenerarlo en UTF-8 (actualmente está en UTF-16, ver sección de deuda técnica) y añadir un pin de versión de Python si se despliega en Streamlit Cloud.
2. **Cerrar el trabajo en curso de la rama `filtros`**: eliminar los bloques comentados (código viejo) en `visualization.py` y `dashboard.py` en vez de dejarlos muertos, y commitear.
3. **Arreglar el bug de `df_grafico_colab_tipologia_final` no definida** en `dashboard.py` (inicializarla como `pd.DataFrame()` antes del `if`).
4. **Reemplazar `except Exception` genéricos** por manejo más específico donde sea barato hacerlo, al menos en los bloques nuevos que se toquen.

### Fase 2 — Corto plazo (próximas 2–4 semanas)
1. **Introducir pruebas unitarias** para la capa de procesamiento de datos (`components/data_processing*.py`, `data_loader.py`, `maps.py`): son funciones puras sobre DataFrames, ideales para `pytest` + `pandas.testing`. Empezar por las funciones de red (`calcular_metricas_red_ig`, detección de comunidades) y por el mapeo de esquemas (`RENAMING_MAP`), que son las más propensas a romperse silenciosamente con nuevos datasets.
2. **CI básico**: workflow de GitHub Actions que instale `requirements.txt` y corra los tests en cada PR — habría atrapado el bug de codificación inmediatamente.
3. **Refactorizar `views/dashboard.py`**: extraer cada sección numerada (1–8) a una función `render_seccion_x(df, ...)` en un módulo `components/dashboard_sections.py`, dejando la vista como orquestador delgado.
4. **Documentar el contrato de `st.session_state`** entre páginas (qué claves produce `inicio.py`, qué consumen `dashboard.py`/`mapas.py`/`redes.py`).
5. **Limpiar comentarios "pages/"** obsoletos y la entrada duplicada en `RENAMING_MAP`.
6. **Gestión de datos**: mover los CSV de ejemplo grandes a Git LFS o a un storage externo, si el repo va a seguir creciendo con más revistas digitalizadas.

### Fase 3 — Futuro (mediano plazo)
1. **Preparar para producción/despliegue compartido**: revisar límites de memoria con datasets grandes en `st.session_state` y considerar persistencia en disco/DB para no perder trabajo al refrescar.
2. **Autenticación/control de acceso**, si los datos biográficos o el corpus tienen restricciones de uso (Streamlit soporta `st.login`/OIDC desde la versión 1.42+, ya usada en el proyecto).
3. **Optimización de rendimiento en redes grandes**: el cálculo de intermediación (ya señalado como "lento" en la propia UI) y el layout de pyvis pueden necesitar paralelización o precómputo en background para corpus con miles de colaboradores.
4. **Internacionalización real del esquema de columnas**: evaluar un enfoque declarativo (config YAML por fuente de datos) en vez de un diccionario Python que crece indefinidamente.
5. **Exportación/reportes**: además de la descarga CSV actual, exportar gráficos/dashboards completos a PDF o HTML estático para compartir hallazgos sin requerir que el destinatario abra la app.
