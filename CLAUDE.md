# CLAUDE.md

Guía para trabajar en este repositorio con Claude Code (u otro asistente). Ver también `ROADMAP.md` para el estado del proyecto y las prioridades de desarrollo.

## Qué es este proyecto

Hemerograph es una aplicación **Streamlit multipágina** para análisis y visualización de datos de revistas culturales y literarias: carga y normalización de datasets heterogéneos, cruce con datos biográficos de colaboradores, dashboards de frecuencia/evolución/traducción, mapas coropléticos y análisis de redes de colaboración.

## Comandos principales

```bash
# Activar entorno virtual (ya existe en ./venv)
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Git Bash / bash):
source venv/Scripts/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación (localhost:8501 por defecto)
streamlit run app.py
```

No hay actualmente comandos de test, lint o build configurados (ver `ROADMAP.md`, deuda técnica — no hay `pytest`, no hay CI). Si se agregan, documentarlos aquí.

## Arquitectura

### Punto de entrada y navegación
`app.py` es solo un router: usa `st.navigation` para registrar las páginas de `views/` (`inicio`, `dashboard`, `mapas`, `redes`). Toda la lógica vive en `views/` y `components/`.

- **Decisión**: la navegación multipágina se hace con `st.Page` / `st.navigation` (API moderna de Streamlit ≥1.36), no con la convención antigua de carpeta `pages/`. Los archivos conservan referencias a `pages/` solo en comentarios de cabecera obsoletos (deuda pendiente, ver roadmap).

### Flujo de datos entre páginas
No hay base de datos ni backend: **`st.session_state` es el único mecanismo de paso de datos entre páginas**. El flujo es secuencial y obligatorio:

1. `views/inicio.py` — cargar CSVs (subidos o de ejemplo en `data/models/`), alinear esquemas heterogéneos contra `CORE_COLUMNS` usando el diccionario `RENAMING_MAP`, opcionalmente fusionar con datos biográficos, y dejar seleccionadas las columnas finales.
2. `views/dashboard.py`, `views/mapas.py`, `views/redes.py` leen de `st.session_state` (claves como `df_listo_para_seleccion_cols`, `selected_columns_for_analysis`, `final_df_to_analyze`, `bio_data_successfully_integrated`) y **se detienen con `st.stop()`** si esas claves no están listas, redirigiendo al usuario a "Inicio".

- **Decisión**: normalizar esquemas de entrada en un único punto (`inicio.py` + `CORE_COLUMNS`/`RENAMING_MAP`) en vez de que cada página interprete columnas crudas. Cualquier nueva fuente de datos con nombres de columna distintos se resuelve ampliando `RENAMING_MAP`, no tocando las páginas de análisis.
- **Implicación para cambios futuros**: si se agrega una página nueva, debe seguir el mismo patrón (leer de `session_state`, hacer `st.stop()` si falta el dataset base) para no duplicar lógica de carga.

### Separación vista / procesamiento / visualización
Cada dominio (dashboard, mapas, redes, datos biográficos) sigue el mismo patrón de tres capas:

- `components/data_processing*.py` — funciones puras sobre DataFrames (agregaciones, cálculo de métricas). Sin llamadas a `st.*`.
- `components/visualization*.py`, `components/maps_viz.py` — construcción de figuras (Plotly/Matplotlib/pyvis) a partir de DataFrames ya procesados. Sin lógica de negocio.
- `views/*.py` — orquestación: widgets de Streamlit, llamadas a `data_processing` y `visualization`, manejo de `session_state`.

- **Decisión**: mantener esta separación al añadir funcionalidad nueva — no meter cálculos de pandas directamente en los archivos de `views/`, ni construir figuras dentro de `data_processing*.py`.

### Redes de colaboración (`views/redes.py`)
- **Decisión**: el grafo bimodal (revista–colaborador) se construye y analiza con **igraph** (no NetworkX) por rendimiento, incluyendo detección de comunidades (Leiden como algoritmo por defecto, con Louvain/walktrap/fastgreedy como alternativas). Solo se convierte a **NetworkX** al final, exclusivamente para las funciones de visualización que lo requieren (`components/visualization_networks.py`).
- Las funciones costosas de `data_processing_networks.py` están cacheadas con `@st.cache_data` usando una `cache_key` explícita construida a partir de los filtros activos (años, revistas seleccionadas) — no confiar en el hashing automático de Streamlit sobre DataFrames grandes.

### Datos geográficos (`views/mapas.py`)
- **Decisión**: la resolución país → código ISO/región se hace vía un archivo de referencia versionado (`data/world.csv`, con columnas `ISO_A3_EH`, `REGION_WB`, `NAME_ES`), no vía una API externa ni geocodificación en tiempo real. Cualquier país nuevo en los datos de origen que no aparezca en `world.csv` no se podrá mapear.

### Datos de ejemplo
`data/models/*.csv` contiene datasets de revistas ya normalizados que se ofrecen como "ejemplos" seleccionables en `inicio.py` (vía `components/data_loader.py`). Estos archivos están versionados directamente en Git (algunos de tamaño considerable) — ver `ROADMAP.md` sobre mover esto a Git LFS si el corpus sigue creciendo.

## Convenciones a seguir

- **Idioma**: nombres de variables, funciones y mensajes de UI están en **español** en toda la base de código (`calcular_frecuencia_colaboradores`, `df_filtrado`, etc.). Mantener esa convención al agregar código nuevo.
- **Claves de `session_state` y de widgets (`key=...`)**: usar nombres descriptivos y sufijos de versión cuando se reemplaza un widget existente (patrón ya usado: `slider_top_conectados_v2`) para evitar colisiones de estado entre reruns.
- **No dejar código muerto comentado**: el repo tiene varios bloques de código antiguo comentado en lugar de eliminado (ver `ROADMAP.md`, Fase 1). Si se toca un archivo con ese patrón, aprovechar para eliminar el código comentado en vez de sumarle más.
- **`requirements.txt` debe guardarse en UTF-8**, no en UTF-16. En PowerShell, `pip freeze > requirements.txt` genera UTF-16 por defecto; usar `pip freeze | Out-File -Encoding utf8 requirements.txt` o `pip list --format=freeze > requirements.txt` desde Git Bash.
- **Manejo de errores en `views/`**: el patrón actual envuelve cada bloque de visualización en `try/except Exception` + `st.exception(e)` para que un error en una sección no tumbe toda la página. Al agregar secciones nuevas, seguir el mismo patrón, pero evitar que oculte errores de programación (ej. variables no inicializadas) — inicializar explícitamente las variables usadas fuera de condicionales antes del `try`.
